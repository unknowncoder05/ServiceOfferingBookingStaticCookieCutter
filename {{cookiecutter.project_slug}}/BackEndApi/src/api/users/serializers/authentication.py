"""Authentication serializers"""

from datetime import datetime, timedelta

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
# Rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# Serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenRefreshSerializer, PasswordField
from rest_framework_simplejwt.tokens import RefreshToken

# Utilities
from api.users.auth.external_token.providers import ExternalAuthenticationTokenProviders
# Models
from api.users.models import User, ExternalAuthenticationToken, ExternalAuthenticationTokenType
from api.users.service.email_service import EmailService


class RequestAuthenticationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, write_only=True)
    provider = serializers.ChoiceField(choices=ExternalAuthenticationTokenProviders.choices, required=False, default=ExternalAuthenticationTokenProviders.CONSOLE)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if not attrs['phone_number'].startswith('+'):
            raise serializers.ValidationError(
                {"phone_number": "Phone number should start with a + and the country code"})

        # get user from phone
        user_queryset = User.objects.filter(phone_number=attrs['phone_number'], is_active=True, deleted=False)
        if not user_queryset:
            raise serializers.ValidationError(
                {"phone_number": _("Invalid number, check it or register")})  # TODO: proper 404 error
        user = user_queryset.first()
        attrs['user'] = user

        # set provider to preferred if not specified
        if not attrs.get('provider'):
            attrs['provider'] = user.preferred_provider

        return attrs

    def create(self, validated_data):
        ExternalAuthenticationToken.objects.create(
            user=validated_data['user'],
            provider=validated_data['provider'],
            type=ExternalAuthenticationTokenType.SIGN_IN
        )

        return {
            'provider': validated_data['provider']
        }


class AccountActivateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, write_only=True)

    token = serializers.CharField(required=True, write_only=True)

    success = serializers.CharField(read_only=True)

    user_id = serializers.CharField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        phone_number = attrs['phone_number']
        token = attrs['token']

        token_validity_range = datetime.today() - timedelta(days=30)
        external_token_queryset = ExternalAuthenticationToken.objects.filter(
            user__phone_number=phone_number,
            created__gte=token_validity_range,
            type=ExternalAuthenticationTokenType.VALIDATE_ACCOUNT,
        )

        if not external_token_queryset:
            raise serializers.ValidationError({"token": "Invalid or has expired"})

        external_token = external_token_queryset.first()
        if external_token.token != token:
            raise serializers.ValidationError({"token": "Invalid or has expired"})

        attrs['external_token'] = external_token

        return attrs

    def create(self, validated_data):
        external_token = validated_data['external_token']
        user = external_token.user
        user.is_active = True
        user.save()
        external_token.delete()
        return dict(success=True, user_id=user.id)


class RequestAccountActivateSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, write_only=True)
    provider = serializers.ChoiceField(choices=ExternalAuthenticationTokenProviders.choices, required=False)
    first_request = serializers.BooleanField(required=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # get user from phone
        user_queryset = User.objects.filter(phone_number=attrs['phone_number'])
        if not user_queryset:
            raise serializers.ValidationError({"phone_number": _("User not found")})  # TODO: proper 404 error
        user = user_queryset.first()
        attrs['user'] = user

        # check if user is active
        if user.is_active:
            raise serializers.ValidationError({"phone_number": _("User is already active")})

        # set provider to preferred if not specified
        if not attrs.get('provider'):
            attrs['provider'] = user.preferred_provider
        return attrs

    def create(self, validated_data):
        # get and delete previous user tokens
        phone_number = validated_data['phone_number']
        external_token_queryset = ExternalAuthenticationToken.get_phone_valid_tokens(phone_number=phone_number,
                                                                                     type=ExternalAuthenticationTokenType.VALIDATE_ACCOUNT)

        if external_token_queryset:
            external_token_queryset.delete()

        ExternalAuthenticationToken.objects.create(
            user=validated_data['user'],
            provider=validated_data['provider'],
            type=ExternalAuthenticationTokenType.VALIDATE_ACCOUNT
        )

        return {
            'provider': validated_data['provider']
        }


class SignUpSerializer(serializers.ModelSerializer):
    """
    Sign up form serializer with email and password
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message=_("This email already exists."))]
    )
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'password_confirm', 'first_name', 'middle_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": _("Passwords do not match.")})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        validated_data['is_active'] = True
        user = User(**validated_data)
        user.set_password(password)
        user.username = user.email
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Simple email and password login serializer
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            from django.contrib.auth import authenticate
            user = authenticate(username=email, password=password)

            if not user:
                raise serializers.ValidationError(_("Invalid email or password."))

            if not user.is_active:
                raise serializers.ValidationError(_("User account is disabled."))

            attrs['user'] = user
        else:
            raise serializers.ValidationError(_("Must include email and password."))

        return attrs


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField()
        self.fields["password"] = PasswordField()

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.token_class(attrs["refresh"])
        data['refresh_expiry'] = refresh.payload['exp']
        data['access_expiry'] = refresh.access_token.payload['exp']
        return data


class CheckEmailOrPhone(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.filter(is_active=True), message=_(
            "This phone number already exists, please login."))])
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.filter(is_active=True), message=_(
            "This email already exists, please login."))])
