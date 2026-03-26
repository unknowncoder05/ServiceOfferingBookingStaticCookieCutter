"""Password reset and account recovery views.

All four endpoints dispatch to the correct serializer based on PASSWORD_RESET_METHOD:
  email   → uid/token link delivered by email
  otp     → OTP code delivered via user's preferred channel
  console → OTP code always printed to the console (local dev)

Endpoints (all AllowAny, all POST):
  /auth/forgot-password/   — request a password reset
  /auth/reset-password/    — confirm reset with token + new password
  /auth/request-recovery/  — request recovery for an inactive/deleted account
  /auth/confirm-recovery/  — confirm recovery with token + new password (reactivates account)
"""
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.users.conf import users_settings
from api.users.serializers.password_reset import (
    ConfirmRecoveryEmailSerializer,
    ConfirmRecoveryOtpSerializer,
    ForgotPasswordConsoleSerializer,
    ForgotPasswordEmailSerializer,
    ForgotPasswordOtpSerializer,
    RequestRecoveryConsoleSerializer,
    RequestRecoveryEmailSerializer,
    RequestRecoveryOtpSerializer,
    ResetPasswordEmailSerializer,
    ResetPasswordOtpSerializer,
)

_FORGOT = {
    'email': ForgotPasswordEmailSerializer,
    'otp': ForgotPasswordOtpSerializer,
    'console': ForgotPasswordConsoleSerializer,
}
_RESET = {
    'email': ResetPasswordEmailSerializer,
    'otp': ResetPasswordOtpSerializer,
    'console': ResetPasswordOtpSerializer,
}
_REQUEST_RECOVERY = {
    'email': RequestRecoveryEmailSerializer,
    'otp': RequestRecoveryOtpSerializer,
    'console': RequestRecoveryConsoleSerializer,
}
_CONFIRM_RECOVERY = {
    'email': ConfirmRecoveryEmailSerializer,
    'otp': ConfirmRecoveryOtpSerializer,
    'console': ConfirmRecoveryOtpSerializer,
}


class PasswordResetViewSet(GenericViewSet):

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            url_path='forgot-password')
    def forgot_password(self, request):
        method = users_settings.password_reset_method
        serializer = _FORGOT.get(method, ForgotPasswordEmailSerializer)(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('If the account exists, instructions have been sent.')})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            url_path='reset-password')
    def reset_password(self, request):
        method = users_settings.password_reset_method
        serializer = _RESET.get(method, ResetPasswordEmailSerializer)(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('Password has been reset successfully.')})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            url_path='request-recovery')
    def request_recovery(self, request):
        method = users_settings.password_reset_method
        serializer = _REQUEST_RECOVERY.get(method, RequestRecoveryEmailSerializer)(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('If the account exists, recovery instructions have been sent.')})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            url_path='confirm-recovery')
    def confirm_recovery(self, request):
        method = users_settings.password_reset_method
        serializer = _CONFIRM_RECOVERY.get(method, ConfirmRecoveryEmailSerializer)(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('Account recovered successfully.')})
