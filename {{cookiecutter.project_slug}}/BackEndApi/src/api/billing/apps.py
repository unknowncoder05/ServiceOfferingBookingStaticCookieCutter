"""Billing app configuration."""
from django.apps import AppConfig


class BillingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.billing'
    verbose_name = 'Billing'

    def ready(self):
        from . import signals  # noqa: F401
