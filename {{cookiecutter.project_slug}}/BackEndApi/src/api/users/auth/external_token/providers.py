from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.users.enums import ExternalAuthenticationTokenType
from .console import send_console_message
from .sms import send_sms_message
from .whatsapp import send_whatsapp_token


class ExternalAuthenticationTokenProviders(models.TextChoices):
    WHATSAPP = 'WH', _('WhatsApp')
    SMS = 'SMS', _('SMS')
    CONSOLE = 'D', _('Console')


PROVIDERS = {
    ExternalAuthenticationTokenProviders.SMS: send_sms_message,
    ExternalAuthenticationTokenProviders.WHATSAPP: send_whatsapp_token,
    ExternalAuthenticationTokenProviders.CONSOLE: send_console_message,
}


def provider_get_token_message(provider, token, token_type):
    token_type_verbose_name = ExternalAuthenticationTokenType._value2member_map_[token_type]._name_
    if provider == ExternalAuthenticationTokenProviders.WHATSAPP:
        return dict(token_type_verbose_name=token_type_verbose_name, token=token)
    provider_verbose_name = ExternalAuthenticationTokenProviders._value2member_map_[provider]._name_

    return settings.AUTHENTICATION_EXTERNAL_TOKEN_FORMATS[provider_verbose_name.lower()][
        token_type_verbose_name.lower()].format(app_name=settings.APP_NAME, token=token)


def send_token(phone_number, token, token_type, provider, language_code="en_US"):
    if provider not in PROVIDERS:
        raise Exception(f'provider "{provider}" not supported')

    message = provider_get_token_message(provider, token, token_type)
    return PROVIDERS[provider](phone_number, message, language_code=language_code)
