"""Users app settings — authentication, GitHub OAuth, WhatsApp, and AWS config."""
import os
from datetime import timedelta

from django.conf import settings


class UsersSettings:
    @property
    def external_token_expiry(self):
        return getattr(settings, 'AUTHENTICATION_EXTERNAL_TOKEN_EXPIRY', timedelta(hours=5))

    @property
    def external_token_formats(self):
        return getattr(settings, 'AUTHENTICATION_EXTERNAL_TOKEN_FORMATS', {})

    @property
    def app_name(self):
        return getattr(settings, 'APP_NAME', 'App')

    @property
    def github_client_id(self):
        return getattr(settings, 'GITHUB_CLIENT_ID', None)

    @property
    def github_client_secret(self):
        return getattr(settings, 'GITHUB_CLIENT_SECRET', None)

    @property
    def github_redirect_uri(self):
        return getattr(settings, 'GITHUB_REDIRECT_URI', 'http://localhost:3000/settings/github/callback')

    @property
    def github_oauth_scopes(self):
        return getattr(settings, 'GITHUB_OAUTH_SCOPES', ['repo', 'read:user', 'user:email'])

    @property
    def whatsapp_message_uri(self):
        return getattr(settings, 'WHATSAPP_MESSAGE_URI', None)

    @property
    def whatsapp_authorization_type(self):
        return getattr(settings, 'WHATSAPP_AUTHORIZATION_TYPE', 'Bearer')

    @property
    def whatsapp_authorization_token(self):
        return getattr(settings, 'WHATSAPP_AUTHORIZATION_TOKEN', None)

    @property
    def aws_region_name(self):
        return getattr(settings, 'AWS_REGION_NAME', '{{ cookiecutter.aws_region }}')

    @property
    def password_reset_method(self):
        """One of: 'email', 'otp', 'console'."""
        return getattr(settings, 'PASSWORD_RESET_METHOD', 'email')

    @property
    def password_reset_frontend_url(self):
        """Frontend URL that receives ?uid=...&token=... for the email reset flow."""
        return getattr(settings, 'PASSWORD_RESET_FRONTEND_URL', 'http://localhost:3000/reset-password')

    @property
    def account_recovery_frontend_url(self):
        """Frontend URL that receives ?uid=...&token=... for the email recovery flow."""
        return getattr(settings, 'ACCOUNT_RECOVERY_FRONTEND_URL', 'http://localhost:3000/recover-account')


users_settings = UsersSettings()
