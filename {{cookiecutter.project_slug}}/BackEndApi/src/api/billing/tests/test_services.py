"""Tests for billing services — add_credits, deduct_credits, check_user_balance."""
from decimal import Decimal

import pytest

from api.billing.exceptions import InsufficientCreditsError
from api.billing.models import BillingSettings, CreditBalance, CreditTransaction
from api.billing.services import add_credits, check_user_balance, deduct_credits
from api.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestAddCredits:
    def test_adds_to_balance(self):
        user = UserFactory()
        add_credits(user, Decimal('10.00'))
        balance = CreditBalance.objects.get(user=user)
        assert balance.balance >= Decimal('10.00')

    def test_creates_transaction(self):
        user = UserFactory()
        txn = add_credits(user, Decimal('5.00'), transaction_type='purchase', description='test')
        assert txn.pk is not None
        assert txn.amount == Decimal('5.00')
        assert txn.transaction_type == 'purchase'
        assert txn.description == 'test'

    def test_balance_after_is_correct(self):
        user = UserFactory()
        # Ensure clean balance
        CreditBalance.objects.filter(user=user).delete()
        add_credits(user, Decimal('10.00'))
        txn = add_credits(user, Decimal('5.00'))
        assert txn.balance_after == Decimal('15.00')

    def test_updates_total_deposited(self):
        user = UserFactory()
        CreditBalance.objects.filter(user=user).delete()
        add_credits(user, Decimal('10.00'))
        add_credits(user, Decimal('3.00'))
        balance = CreditBalance.objects.get(user=user)
        assert balance.total_deposited == Decimal('13.00')

    def test_raises_on_non_positive_amount(self):
        user = UserFactory()
        with pytest.raises(ValueError):
            add_credits(user, Decimal('0.00'))
        with pytest.raises(ValueError):
            add_credits(user, Decimal('-1.00'))

    def test_idempotent_balance_creation(self):
        user = UserFactory()
        add_credits(user, Decimal('1.00'))
        add_credits(user, Decimal('1.00'))
        assert CreditBalance.objects.filter(user=user).count() == 1


class TestDeductCredits:
    def test_deducts_from_balance(self):
        user = UserFactory()
        CreditBalance.objects.filter(user=user).delete()
        add_credits(user, Decimal('20.00'))
        deduct_credits(user, Decimal('5.00'))
        balance = CreditBalance.objects.get(user=user)
        assert balance.balance == Decimal('15.00')

    def test_creates_negative_transaction(self):
        user = UserFactory()
        add_credits(user, Decimal('10.00'))
        txn = deduct_credits(user, Decimal('3.00'))
        assert txn.amount < 0

    def test_updates_total_spent(self):
        user = UserFactory()
        CreditBalance.objects.filter(user=user).delete()
        add_credits(user, Decimal('20.00'))
        deduct_credits(user, Decimal('5.00'))
        deduct_credits(user, Decimal('3.00'))
        balance = CreditBalance.objects.get(user=user)
        assert balance.total_spent == Decimal('8.00')

    def test_balance_can_go_negative(self):
        user = UserFactory()
        CreditBalance.objects.filter(user=user).delete()
        deduct_credits(user, Decimal('5.00'))
        balance = CreditBalance.objects.get(user=user)
        assert balance.balance < 0

    def test_applies_markup(self, settings):
        settings.CREDIT_COST_MARKUP = '2.0'
        user = UserFactory()
        CreditBalance.objects.filter(user=user).delete()
        add_credits(user, Decimal('20.00'))
        txn = deduct_credits(user, Decimal('5.00'))
        # markup=2.0 → effective deduction is $10
        assert txn.amount == Decimal('-10.00')

    def test_stores_context(self):
        user = UserFactory()
        txn = deduct_credits(user, Decimal('1.00'), context_type='item', context_id=42)
        assert txn.context_type == 'item'
        assert txn.context_id == 42

    def test_raises_on_non_positive_amount(self):
        user = UserFactory()
        with pytest.raises(ValueError):
            deduct_credits(user, Decimal('0.00'))


class TestCheckUserBalance:
    def test_passes_when_balance_sufficient(self):
        user = UserFactory()
        CreditBalance.objects.filter(user=user).delete()
        add_credits(user, Decimal('10.00'))
        balance = check_user_balance(user)
        assert balance is not None

    def test_raises_when_balance_zero(self):
        user = UserFactory()
        CreditBalance.objects.filter(user=user).delete()
        with pytest.raises(InsufficientCreditsError):
            check_user_balance(user)

    def test_staff_bypasses_check(self):
        user = UserFactory()
        user.is_staff = True
        user.save()
        CreditBalance.objects.filter(user=user).delete()
        # Should not raise even with zero balance
        balance = check_user_balance(user)
        assert balance is not None

    def test_superuser_bypasses_check(self):
        user = UserFactory()
        user.is_superuser = True
        user.save()
        CreditBalance.objects.filter(user=user).delete()
        balance = check_user_balance(user)
        assert balance is not None


class TestWelcomeBonusSignal:
    def test_credit_balance_created_on_user_creation(self):
        user = UserFactory()
        assert CreditBalance.objects.filter(user=user).exists()

    def test_welcome_bonus_granted_when_configured(self):
        settings_obj = BillingSettings.get()
        settings_obj.welcome_bonus = Decimal('5.00')
        settings_obj.save()

        user = UserFactory()
        balance = CreditBalance.objects.get(user=user)
        assert balance.balance >= Decimal('5.00')

        txn = CreditTransaction.objects.filter(
            user=user, transaction_type='admin_grant'
        ).first()
        assert txn is not None
        assert txn.amount == Decimal('5.00')

    def test_no_bonus_when_zero(self):
        settings_obj = BillingSettings.get()
        settings_obj.welcome_bonus = Decimal('0.00')
        settings_obj.save()

        user = UserFactory()
        assert not CreditTransaction.objects.filter(
            user=user, transaction_type='admin_grant'
        ).exists()
