from django.db import models
from django.utils.translation import gettext_lazy as _


class ExternalAuthenticationTokenType(models.TextChoices):
    VALIDATE_ACCOUNT = 'VA', _('Validate account')
    SIGN_IN = 'SI', _('Sign in')
