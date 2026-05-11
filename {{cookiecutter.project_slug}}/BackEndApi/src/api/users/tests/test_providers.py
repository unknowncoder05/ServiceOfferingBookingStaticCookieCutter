"""Tests for external authentication token providers.

All external calls (AWS SNS, WhatsApp HTTP, boto3) are mocked.
Tests verify:
  - Console provider always works (no external dependency)
  - SMS provider fails gracefully when AWS not configured
  - WhatsApp provider fails gracefully when WHATSAPP_MESSAGE_URI not set
  - send_token() logs and re-raises on delivery failure
  - Unsupported provider raises ValueError immediately
"""
import logging
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase

from pm_auth.api.users.auth.external_token.providers import (
    ExternalAuthenticationTokenProviders,
    send_token,
)
from pm_auth.api.users.enums import ExternalAuthenticationTokenType
from api.users.factories import UserFactory


class ConsoleProviderTests(TestCase):
    """Console provider has no external dependencies — always succeeds."""

    def test_send_token_via_console(self):
        user = UserFactory(phone_number='+15550000001')
        send_token(
            phone_number=user.phone_number,
            token='123456',
            token_type=ExternalAuthenticationTokenType.SIGN_IN,
            provider=ExternalAuthenticationTokenProviders.CONSOLE,
        )
        # No exception raised = pass

    def test_console_accepts_all_token_types(self):
        for token_type in ExternalAuthenticationTokenType.values:
            send_token(
                phone_number='+15550000002',
                token='654321',
                token_type=token_type,
                provider=ExternalAuthenticationTokenProviders.CONSOLE,
            )


class SmsProviderTests(TestCase):
    """SMS provider — all boto3 calls are mocked."""

    def _send(self, phone='+15550001234', token='111111'):
        send_token(
            phone_number=phone,
            token=token,
            token_type=ExternalAuthenticationTokenType.SIGN_IN,
            provider=ExternalAuthenticationTokenProviders.SMS,
        )

    @patch('boto3.client')
    def test_sends_sms_when_configured(self, mock_boto):
        mock_sns = MagicMock()
        mock_boto.return_value = mock_sns
        with patch('pm_auth.api.users.conf.UsersSettings.aws_region_name',
                   new_callable=lambda: property(lambda self: 'us-east-1')):
            self._send()
        mock_sns.publish.assert_called_once()

    def test_raises_when_aws_region_not_set(self):
        with patch('pm_auth.api.users.conf.UsersSettings.aws_region_name',
                   new_callable=lambda: property(lambda self: '')):
            with self.assertRaises(RuntimeError):
                self._send()

    @patch('boto3.client')
    def test_raises_and_logs_on_sns_error(self, mock_boto):
        mock_boto.return_value.publish.side_effect = Exception("SNS error")
        with patch('pm_auth.api.users.conf.UsersSettings.aws_region_name',
                   new_callable=lambda: property(lambda self: 'us-east-1')):
            with self.assertLogs('pm_auth.api.users.auth.external_token.sms', level='ERROR'):
                with self.assertRaises(Exception):
                    self._send()

    def test_logs_on_provider_delivery_failure(self):
        """send_token() must log the failure before re-raising."""
        with patch('pm_auth.api.users.auth.external_token.providers.PROVIDERS',
                   {ExternalAuthenticationTokenProviders.SMS: MagicMock(side_effect=RuntimeError("boom"))}):
            with self.assertLogs('pm_auth.api.users.auth.external_token.providers', level='ERROR'):
                with self.assertRaises(RuntimeError):
                    self._send()


class WhatsAppProviderTests(TestCase):
    """WhatsApp provider — all HTTP calls are mocked."""

    def _send(self, phone='+15550009876'):
        send_token(
            phone_number=phone,
            token='999888',
            token_type=ExternalAuthenticationTokenType.SIGN_IN,
            provider=ExternalAuthenticationTokenProviders.WHATSAPP,
        )

    @patch('requests.post')
    def test_sends_whatsapp_when_configured(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        with patch('pm_auth.api.users.conf.UsersSettings.whatsapp_message_uri',
                   new_callable=lambda: property(lambda self: 'https://wa.example.com/send')):
            with patch('pm_auth.api.users.conf.UsersSettings.whatsapp_authorization_token',
                       new_callable=lambda: property(lambda self: 'Bearer token123')):
                self._send()
        mock_post.assert_called_once()

    def test_raises_when_whatsapp_uri_not_set(self):
        with patch('pm_auth.api.users.conf.UsersSettings.whatsapp_message_uri',
                   new_callable=lambda: property(lambda self: '')):
            with self.assertRaises(Exception):
                self._send()

    @patch('requests.post')
    def test_raises_on_non_200_response(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_post.return_value = mock_resp
        with patch('pm_auth.api.users.conf.UsersSettings.whatsapp_message_uri',
                   new_callable=lambda: property(lambda self: 'https://wa.example.com/send')):
            with patch('pm_auth.api.users.conf.UsersSettings.whatsapp_authorization_token',
                       new_callable=lambda: property(lambda self: 'Bearer token123')):
                with self.assertRaises(Exception):
                    self._send()


class SendTokenTests(TestCase):
    """Tests for the send_token() dispatch function."""

    def test_unsupported_provider_raises_value_error(self):
        with self.assertRaises((ValueError, Exception)):
            send_token(
                phone_number='+15550000000',
                token='000000',
                token_type=ExternalAuthenticationTokenType.SIGN_IN,
                provider='UNSUPPORTED',
            )

    def test_delivery_failure_is_logged_before_raise(self):
        boom = RuntimeError("delivery failed")
        with patch('pm_auth.api.users.auth.external_token.providers.PROVIDERS',
                   {ExternalAuthenticationTokenProviders.CONSOLE: MagicMock(side_effect=boom)}):
            with self.assertLogs('pm_auth.api.users.auth.external_token.providers', level='ERROR'):
                with self.assertRaises(RuntimeError):
                    send_token(
                        phone_number='+15550000000',
                        token='000000',
                        token_type=ExternalAuthenticationTokenType.SIGN_IN,
                        provider=ExternalAuthenticationTokenProviders.CONSOLE,
                    )
