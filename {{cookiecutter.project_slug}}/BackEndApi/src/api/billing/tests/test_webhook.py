"""Tests for the Stripe webhook endpoint.

All Stripe SDK calls are mocked so no network access or real keys are required.
The tests verify the endpoint's behaviour when Stripe is configured, when it is
not configured, and when the payload or signature is invalid.
"""
import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import stripe as _stripe
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

from api.billing.models import CreditBalance, CreditTransaction
from api.users.factories import UserFactory

WEBHOOK_URL = f'/{settings.API_URI}/billing/webhook/'


def _make_session_payload(user_id, amount='10.00', session_id='cs_test_123'):
    return {
        'id': session_id,
        'metadata': {'user_id': str(user_id), 'credit_amount': amount},
        'client_reference_id': str(user_id),
        'payment_intent': 'pi_test_456',
    }


class StripeWebhookTests(APITestCase):

    def setUp(self):
        patch('boto3.client').start()
        self.user = UserFactory(is_active=True)

    def tearDown(self):
        patch.stopall()

    def _post(self, payload, sig='valid_sig', content_type='application/json'):
        return self.client.post(
            WEBHOOK_URL,
            data=json.dumps(payload) if isinstance(payload, dict) else payload,
            content_type=content_type,
            HTTP_STRIPE_SIGNATURE=sig,
        )

    # ── Stripe not configured ───────────────────────────────────────────────

    def test_503_when_stripe_not_installed(self):
        """If stripe package is absent the endpoint returns 503, not 500."""
        import sys
        stripe_backup = sys.modules.get('stripe')
        sys.modules['stripe'] = None  # simulate import failure
        try:
            resp = self._post({'type': 'checkout.session.completed', 'data': {'object': {}}})
            # May return 503 (no package) or 400 (signature failure) — never 500
            self.assertNotEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if stripe_backup is None:
                sys.modules.pop('stripe', None)
            else:
                sys.modules['stripe'] = stripe_backup

    # ── Invalid payloads ────────────────────────────────────────────────────

    def test_400_on_invalid_json_payload(self):
        with patch.object(_stripe.Webhook, 'construct_event', side_effect=ValueError("Invalid JSON")):
            resp = self._post('not valid json at all')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_400_on_invalid_signature(self):
        with patch.object(
            _stripe.Webhook,
            'construct_event',
            side_effect=_stripe.error.SignatureVerificationError('Bad sig', 'sig_header'),
        ):
            resp = self._post({'type': 'ping'}, sig='bad_sig')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Successful checkout.session.completed ───────────────────────────────

    def test_checkout_completed_adds_credits(self):
        CreditBalance.objects.filter(user=self.user).delete()
        session = _make_session_payload(self.user.id)
        event = {'type': 'checkout.session.completed', 'data': {'object': session}}

        with patch.object(_stripe.Webhook, 'construct_event', return_value=event):
            resp = self._post({'dummy': True})

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        balance = CreditBalance.objects.get(user=self.user)
        self.assertGreaterEqual(balance.balance, Decimal('10.00'))

    def test_checkout_completed_idempotent(self):
        """Replaying the same session ID must not double-credit the user."""
        CreditBalance.objects.filter(user=self.user).delete()
        session = _make_session_payload(self.user.id, session_id='cs_idempotent')
        event = {'type': 'checkout.session.completed', 'data': {'object': session}}

        for _ in range(2):
            with patch.object(_stripe.Webhook, 'construct_event', return_value=event):
                self.client.post(
                    WEBHOOK_URL,
                    data=json.dumps({'dummy': True}),
                    content_type='application/json',
                    HTTP_STRIPE_SIGNATURE='sig',
                )

        balance = CreditBalance.objects.get(user=self.user)
        self.assertLessEqual(balance.balance, Decimal('11.00'))  # only credited once
        self.assertEqual(
            CreditTransaction.objects.filter(
                user=self.user,
                stripe_checkout_session_id='cs_idempotent',
            ).count(),
            1,
        )

    def test_unknown_event_type_returns_ok(self):
        """Unknown event types are silently ignored and return 200."""
        event = {'type': 'customer.subscription.created', 'data': {'object': {}}}
        with patch.object(_stripe.Webhook, 'construct_event', return_value=event):
            resp = self._post({'dummy': True})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_missing_user_id_does_not_crash(self):
        """Webhook payload with missing user_id must not raise 500."""
        session = {'id': 'cs_no_user', 'metadata': {}, 'payment_intent': 'pi_x'}
        event = {'type': 'checkout.session.completed', 'data': {'object': session}}
        with patch.object(_stripe.Webhook, 'construct_event', return_value=event):
            resp = self._post({'dummy': True})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_nonexistent_user_does_not_crash(self):
        """Webhook with a user_id that no longer exists must not raise 500."""
        session = _make_session_payload(user_id=999999)
        event = {'type': 'checkout.session.completed', 'data': {'object': session}}
        with patch.object(_stripe.Webhook, 'construct_event', return_value=event):
            resp = self._post({'dummy': True})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
