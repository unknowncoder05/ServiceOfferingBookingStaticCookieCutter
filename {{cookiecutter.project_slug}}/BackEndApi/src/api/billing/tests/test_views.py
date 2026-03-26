"""Tests for billing views — balance, transactions, checkout."""
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from api.billing.models import CreditBalance
from api.billing.services import add_credits, deduct_credits
from api.users.factories import UserFactory

pytestmark = pytest.mark.django_db

BALANCE_URL = f'/{settings.API_URI}/billing/balance/'
TRANSACTIONS_URL = f'/{settings.API_URI}/billing/transactions/'
CHECKOUT_URL = f'/{settings.API_URI}/billing/checkout/'


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestBalanceView:
    def test_requires_auth(self, client):
        response = client.get(BALANCE_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_balance(self, auth_client, user):
        CreditBalance.objects.filter(user=user).delete()
        add_credits(user, Decimal('10.00'))
        response = auth_client.get(BALANCE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert 'balance' in response.data
        assert Decimal(response.data['balance']) >= Decimal('10.00')

    def test_returns_thresholds(self, auth_client):
        response = auth_client.get(BALANCE_URL)
        assert 'warning_threshold' in response.data
        assert 'critical_threshold' in response.data

    def test_stripe_disabled_when_no_key(self, auth_client, settings):
        settings.STRIPE_SECRET_KEY = ''
        response = auth_client.get(BALANCE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['stripe_enabled'] is False

    def test_stripe_enabled_when_key_set(self, auth_client, settings):
        settings.STRIPE_SECRET_KEY = 'sk_test_fake'
        response = auth_client.get(BALANCE_URL)
        assert response.data['stripe_enabled'] is True

    def test_creates_balance_if_missing(self, auth_client, user):
        CreditBalance.objects.filter(user=user).delete()
        response = auth_client.get(BALANCE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert CreditBalance.objects.filter(user=user).exists()


class TestTransactionListView:
    def test_requires_auth(self, client):
        response = client.get(TRANSACTIONS_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_empty_list(self, auth_client, user):
        CreditBalance.objects.filter(user=user).delete()
        response = auth_client.get(TRANSACTIONS_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_returns_own_transactions_only(self, user):
        other_user = UserFactory()
        CreditBalance.objects.filter(user=user).delete()
        CreditBalance.objects.filter(user=other_user).delete()

        add_credits(user, Decimal('5.00'), description='mine')
        add_credits(other_user, Decimal('5.00'), description='theirs')

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(TRANSACTIONS_URL)
        assert response.status_code == status.HTTP_200_OK

        results = response.data.get('results', response.data)
        descriptions = [t['description'] for t in results]
        assert 'mine' in descriptions
        assert 'theirs' not in descriptions

    def test_transaction_fields(self, auth_client, user):
        CreditBalance.objects.filter(user=user).delete()
        add_credits(user, Decimal('7.00'), transaction_type='purchase', description='test txn')
        response = auth_client.get(TRANSACTIONS_URL)
        results = response.data.get('results', response.data)
        txn = next(t for t in results if t['description'] == 'test txn')
        assert 'amount' in txn
        assert 'balance_after' in txn
        assert 'transaction_type' in txn
        assert 'transaction_type_display' in txn
        assert 'created_at' in txn


class TestCheckoutView:
    def test_requires_auth(self, client):
        response = client.post(CHECKOUT_URL, {'amount': '10.00'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_returns_503_when_stripe_not_configured(self, auth_client, settings):
        settings.STRIPE_SECRET_KEY = ''
        response = auth_client.post(CHECKOUT_URL, {'amount': '10.00'}, format='json')
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data.get('billing_disabled') is True

    def test_validates_amount_minimum(self, auth_client, settings):
        settings.STRIPE_SECRET_KEY = 'sk_test_fake'
        response = auth_client.post(CHECKOUT_URL, {'amount': '0.50'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_validates_amount_maximum(self, auth_client, settings):
        settings.STRIPE_SECRET_KEY = 'sk_test_fake'
        response = auth_client.post(CHECKOUT_URL, {'amount': '9999.00'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_creates_session_when_stripe_configured(self, auth_client, settings):
        settings.STRIPE_SECRET_KEY = 'sk_test_fake'
        mock_session = type('S', (), {'url': 'https://checkout.stripe.com/pay/test', 'id': 'cs_test_123'})()
        with patch('api.billing.stripe_service.stripe.checkout.Session.create', return_value=mock_session):
            response = auth_client.post(CHECKOUT_URL, {'amount': '10.00'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'checkout_url' in response.data
        assert 'session_id' in response.data
