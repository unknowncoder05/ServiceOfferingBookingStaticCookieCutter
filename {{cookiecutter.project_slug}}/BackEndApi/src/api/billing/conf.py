"""Billing app settings — all Stripe and credit configuration lives here."""
from django.conf import settings


class BillingSettings:
    @property
    def stripe_secret_key(self):
        return getattr(settings, 'STRIPE_SECRET_KEY', '')

    @property
    def stripe_webhook_secret(self):
        return getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    @property
    def stripe_success_url(self):
        return getattr(
            settings, 'STRIPE_SUCCESS_URL',
            'http://localhost:3000/settings/billing?session_id={CHECKOUT_SESSION_ID}',
        )

    @property
    def stripe_cancel_url(self):
        return getattr(
            settings, 'STRIPE_CANCEL_URL',
            'http://localhost:3000/settings/billing?cancelled=true',
        )

    @property
    def credit_minimum_balance(self):
        return getattr(settings, 'CREDIT_MINIMUM_BALANCE', '0.00')

    @property
    def credit_cost_markup(self):
        return getattr(settings, 'CREDIT_COST_MARKUP', '1.0')


billing_settings = BillingSettings()
