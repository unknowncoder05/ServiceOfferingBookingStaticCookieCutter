"""Billing models for a credit-based pay-as-you-go system."""
from decimal import Decimal

from django.conf import settings
from django.db import models


class CostTemplate(models.Model):
    """Per-operation pricing rules. Admin-configurable markup + optional fixed price.

    OPERATION_CHOICES is intentionally minimal. Extend it in your app by appending to
    CostTemplate.OPERATION_CHOICES before migrations run, or use a free-text operation_type
    by removing the choices= constraint if your set of operations is open-ended.
    """

    OPERATION_CHOICES = [
        ('generic', 'Generic Operation'),
    ]

    name = models.CharField(max_length=100)
    operation_type = models.CharField(
        max_length=50,
        choices=OPERATION_CHOICES,
        unique=True,
    )
    markup = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        default=Decimal('1.0'),
        help_text="Multiplier applied on top of the base cost (1.0 = no markup)",
    )
    price_per_unit = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Fixed price per unit in USD (optional; use for flat-rate billing)",
    )
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cost Template'
        verbose_name_plural = 'Cost Templates'

    def __str__(self):
        return f"{self.name} ({self.operation_type}) ×{self.markup}"


class BillingSettings(models.Model):
    """Singleton row for site-wide billing configuration.

    Edit via Django admin — only one row is ever created.
    """

    welcome_bonus = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="USD credited to every new user on signup. Set to 0 to disable.",
    )
    warning_threshold = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('5.00'),
        help_text="Balance falls below this → yellow warning indicator in the UI.",
    )
    critical_threshold = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text="Balance falls below this → red critical indicator in the UI.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Billing Settings'
        verbose_name_plural = 'Billing Settings'

    def __str__(self):
        return (
            f"Billing Settings — bonus ${self.welcome_bonus}, "
            f"warn ${self.warning_threshold}, crit ${self.critical_threshold}"
        )

    @classmethod
    def get(cls) -> 'BillingSettings':
        """Return (or create) the single settings instance."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class CreditBalance(models.Model):
    """Tracks current USD credit balance for a user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_balance',
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=0,
        help_text="Current USD credit balance",
    )
    total_deposited = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total USD deposited over lifetime",
    )
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=0,
        help_text="Total USD spent over lifetime",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Credit Balance'
        verbose_name_plural = 'Credit Balances'

    def __str__(self):
        return f"{self.user} — ${self.balance:.2f}"


class CreditTransaction(models.Model):
    """Append-only ledger of all credit changes."""

    TRANSACTION_TYPES = [
        ('purchase',            'Purchase'),
        ('admin_grant',         'Admin Grant'),
        ('execution_deduction', 'Execution Deduction'),
        ('chat_deduction',      'Chat Deduction'),
        ('refund',              'Refund'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_transactions',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        help_text="Positive = credit added, negative = credit deducted",
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        help_text="User's balance after this transaction",
    )
    transaction_type = models.CharField(
        max_length=30,
        choices=TRANSACTION_TYPES,
    )
    reference_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Optional external reference (e.g. execution ID, order ID)",
    )
    description = models.TextField(
        blank=True,
        default='',
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    stripe_checkout_session_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Used for idempotency on webhook processing",
    )
    context_type = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Optional label for the entity that triggered this transaction",
    )
    context_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional PK of the entity that triggered this transaction",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Credit Transaction'
        verbose_name_plural = 'Credit Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['stripe_checkout_session_id']),
            models.Index(fields=['context_type', 'context_id']),
        ]

    def __str__(self):
        sign = '+' if self.amount >= 0 else ''
        return f"{self.user} {sign}{self.amount:.6f} ({self.transaction_type})"
