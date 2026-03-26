"""Password reset and account recovery serializers.

Three delivery methods, selected via PASSWORD_RESET_METHOD:
  email   — tokenised link sent to the user's email address
  otp     — short OTP code sent via the user's preferred channel (sms/whatsapp/console)
  console — like otp but always forces the console provider (good for local dev)

Email delivery is always wrapped in a try/except: a misconfigured or disabled
EMAIL_BACKEND will never crash the API — the error is logged so operators can
investigate, and the endpoint still returns 200 so the frontend flow is not broken.
"""
import logging

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

logger = logging.getLogger(__name__)
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.users.auth.external_token.providers import ExternalAuthenticationTokenProviders
from api.users.conf import users_settings
from api.users.enums import ExternalAuthenticationTokenType
from api.users.models import ExternalAuthenticationToken, User


# ── helpers ────────────────────────────────────────────────────────────────────

def _send_email(subject, message, recipient):
    from django.conf import settings
    try:
        send_mail(
            subject=str(subject),
            message=str(message),
            from_email=getattr(settings, 'EMAIL_NO_REPLY', 'noreply@app.com'),
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception:
        # Log the failure but do NOT re-raise.  A broken email backend
        # (wrong SMTP creds, disabled backend, network issue) must not
        # crash the API or reveal internal details to the client.
        logger.exception("Failed to send email to %s (subject: %s)", recipient, subject)


def _create_otp_token(user, token_type, provider):
    ExternalAuthenticationToken.objects.filter(user=user, type=token_type).delete()
    ExternalAuthenticationToken.objects.create(user=user, provider=provider, type=token_type)


def _validate_otp_token(phone_number, raw_token, token_type):
    qs = ExternalAuthenticationToken.get_phone_valid_tokens(
        phone_number=phone_number,
        type=token_type,
    )
    if not qs.exists() or qs.first().token != raw_token:
        raise serializers.ValidationError({'token': _('Invalid or expired token.')})
    return qs.first()


def _decode_uid(uid_str):
    try:
        return force_str(urlsafe_base64_decode(uid_str))
    except Exception:
        raise serializers.ValidationError({'uid': _('Invalid link.')})


# ── Password Reset — email ─────────────────────────────────────────────────────

class ForgotPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self._user = User.objects.get(email=value, is_active=True, deleted=False)
        except User.DoesNotExist:
            self._user = None  # silently no-op; don't reveal whether email exists
        return value

    def save(self):
        user = getattr(self, '_user', None)
        if not user:
            return
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = f"{users_settings.password_reset_frontend_url}?uid={uid}&token={token}"
        _send_email(
            subject=_('Reset your password'),
            message=_('Click the link to reset your password: %(url)s') % {'url': url},
            recipient=user.email,
        )


class ResetPasswordEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match.')})
        pk = _decode_uid(attrs['uid'])
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise serializers.ValidationError({'uid': _('Invalid reset link.')})
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({'token': _('Invalid or expired reset link.')})
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()


# ── Password Reset — OTP ───────────────────────────────────────────────────────

class ForgotPasswordOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    provider = serializers.ChoiceField(choices=ExternalAuthenticationTokenProviders.choices, required=False)

    def validate(self, attrs):
        try:
            user = User.objects.get(phone_number=attrs['phone_number'], is_active=True, deleted=False)
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone_number': _('No active account with this phone number.')})
        attrs['user'] = user
        attrs.setdefault('provider', user.preferred_provider)
        return attrs

    def save(self):
        _create_otp_token(
            self.validated_data['user'],
            ExternalAuthenticationTokenType.RESET_PASSWORD,
            self.validated_data['provider'],
        )


class ForgotPasswordConsoleSerializer(ForgotPasswordOtpSerializer):
    """Forces console delivery regardless of user preference — for local dev."""

    def validate(self, attrs):
        attrs['provider'] = ExternalAuthenticationTokenProviders.CONSOLE
        return super().validate(attrs)


class ResetPasswordOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match.')})
        attrs['token_obj'] = _validate_otp_token(
            attrs['phone_number'], attrs['token'],
            ExternalAuthenticationTokenType.RESET_PASSWORD,
        )
        return attrs

    def save(self):
        token_obj = self.validated_data['token_obj']
        token_obj.user.set_password(self.validated_data['new_password'])
        token_obj.user.save()
        token_obj.delete()


# ── Account Recovery — email ───────────────────────────────────────────────────

class RequestRecoveryEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.is_active and not user.deleted:
                raise serializers.ValidationError(_('This account is already active.'))
            self._user = user
        except User.DoesNotExist:
            self._user = None  # silently no-op
        return value

    def save(self):
        user = getattr(self, '_user', None)
        if not user:
            return
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = f"{users_settings.account_recovery_frontend_url}?uid={uid}&token={token}"
        _send_email(
            subject=_('Recover your account'),
            message=_('Click the link to recover your account: %(url)s') % {'url': url},
            recipient=user.email,
        )


class ConfirmRecoveryEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match.')})
        pk = _decode_uid(attrs['uid'])
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise serializers.ValidationError({'uid': _('Invalid recovery link.')})
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({'token': _('Invalid or expired recovery link.')})
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.is_active = True
        user.deleted = False
        user.set_password(self.validated_data['new_password'])
        user.save()


# ── Account Recovery — OTP ─────────────────────────────────────────────────────

class RequestRecoveryOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    provider = serializers.ChoiceField(choices=ExternalAuthenticationTokenProviders.choices, required=False)

    def validate(self, attrs):
        try:
            user = User.objects.get(phone_number=attrs['phone_number'])
            if user.is_active and not user.deleted:
                raise serializers.ValidationError({'phone_number': _('This account is already active.')})
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone_number': _('No account found with this phone number.')})
        attrs['user'] = user
        attrs.setdefault('provider', user.preferred_provider)
        return attrs

    def save(self):
        _create_otp_token(
            self.validated_data['user'],
            ExternalAuthenticationTokenType.RECOVER_ACCOUNT,
            self.validated_data['provider'],
        )


class RequestRecoveryConsoleSerializer(RequestRecoveryOtpSerializer):
    """Forces console delivery regardless of user preference — for local dev."""

    def validate(self, attrs):
        attrs['provider'] = ExternalAuthenticationTokenProviders.CONSOLE
        return super().validate(attrs)


class ConfirmRecoveryOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': _('Passwords do not match.')})
        attrs['token_obj'] = _validate_otp_token(
            attrs['phone_number'], attrs['token'],
            ExternalAuthenticationTokenType.RECOVER_ACCOUNT,
        )
        return attrs

    def save(self):
        token_obj = self.validated_data['token_obj']
        user = token_obj.user
        user.is_active = True
        user.deleted = False
        user.set_password(self.validated_data['new_password'])
        user.save()
        token_obj.delete()
