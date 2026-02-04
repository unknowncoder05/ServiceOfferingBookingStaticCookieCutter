# Django
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

# Utilities
from api.users.auth.external_token.providers import ExternalAuthenticationTokenProviders, send_token
from api.users.auth.external_token.token import random_token
from api.users.enums import ExternalAuthenticationTokenType
# Models
from api.users.models.user import User
from api.utils.models import BaseModel


class ExternalAuthenticationToken(BaseModel):
    provider = models.CharField(
        choices=ExternalAuthenticationTokenProviders.choices,
        default=ExternalAuthenticationTokenProviders.SMS,
        max_length=5,
        blank=False
    )
    type = models.CharField(
        choices=ExternalAuthenticationTokenType.choices,
        default=ExternalAuthenticationTokenType.SIGN_IN,
        max_length=5,
        blank=False
    )
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='external_authentication_token',
                             null=False, blank=False)
    token = models.CharField(default=random_token, max_length=16, blank=True)

    @classmethod
    def get_phone_valid_tokens(cls, phone_number, type):
        token_validity_range = now() - settings.AUTHENTICATION_EXTERNAL_TOKEN_EXPIRY
        return cls.objects.filter(user__phone_number=phone_number, created__gte=token_validity_range, type=type)


@receiver(post_save, sender=User)
def auth_sign_up_token_created(sender, instance: User, created, *args, **kwargs):
    if created and not instance.is_active:
        auth_token = ExternalAuthenticationToken(user=instance, provider=instance.preferred_provider,
                                                 type=ExternalAuthenticationTokenType.VALIDATE_ACCOUNT)
        auth_token.save()


@receiver(post_save, sender=ExternalAuthenticationToken)
def auth_token_created(sender, instance: ExternalAuthenticationToken, *args, **kwargs):
    send_token(instance.user.phone_number, instance.token, instance.type, instance.provider,
               instance.user.preferred_language_code)
