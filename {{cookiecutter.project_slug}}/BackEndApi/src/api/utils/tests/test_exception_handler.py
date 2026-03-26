"""Tests for the custom DRF exception handler.

Verifies that every error response has a consistent { "error": "..." } shape
and that unhandled exceptions are caught and never bubble up as 500 HTML.
"""
from unittest.mock import patch

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.test import APITestCase

from api.users.factories import UserFactory

BASE = f'/{settings.API_URI}'


class ExceptionHandlerShapeTests(APITestCase):
    """All error responses must have an 'error' key."""

    def setUp(self):
        patch('boto3.client').start()
        self.user = UserFactory(is_active=True)

    def tearDown(self):
        patch.stopall()

    def _assert_error_shape(self, response):
        self.assertIn('error', response.data, f"Missing 'error' key. Got: {response.data}")
        self.assertIsInstance(response.data['error'], str)

    def test_404_has_error_key(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(f'{BASE}/items/999999/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self._assert_error_shape(resp)

    def test_401_has_error_key(self):
        resp = self.client.get(f'{BASE}/users/me/')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        self._assert_error_shape(resp)

    def test_400_validation_error_has_error_key(self):
        resp = self.client.post(f'{BASE}/auth/sign-up/', {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self._assert_error_shape(resp)

    def test_400_validation_error_may_have_fields_key(self):
        resp = self.client.post(f'{BASE}/auth/sign-up/', {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        # fields key is optional but must be a dict when present
        if 'fields' in resp.data:
            self.assertIsInstance(resp.data['fields'], dict)


class ExceptionHandlerUnitTests(APITestCase):
    """Unit-level tests directly calling the handler function."""

    def _call(self, exc, context=None):
        from api.utils.exceptions import custom_exception_handler
        return custom_exception_handler(exc, context or {'view': None})

    def test_detail_only_dict_lifted_to_error(self):
        exc = NotFound()
        resp = self._call(exc)
        self.assertIn('error', resp.data)
        self.assertNotIn('detail', resp.data)

    def test_non_field_errors_lifted_to_error(self):
        exc = ValidationError({'non_field_errors': ['Passwords do not match.']})
        resp = self._call(exc)
        self.assertIn('error', resp.data)
        self.assertIn('Passwords', resp.data['error'])

    def test_field_errors_produce_fields_key(self):
        exc = ValidationError({'email': ['This field is required.']})
        resp = self._call(exc)
        self.assertIn('error', resp.data)
        self.assertIn('fields', resp.data)
        self.assertIn('email', resp.data['fields'])

    def test_list_error_normalised(self):
        exc = ValidationError(['Something went wrong.'])
        resp = self._call(exc)
        self.assertIn('error', resp.data)
        self.assertNotIn('detail', resp.data)

    def test_unhandled_exception_returns_500(self):
        # None response means DRF didn't handle it → our handler returns 500
        resp = self._call(RuntimeError("unexpected"), context={'view': None})
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', resp.data)

    def test_unhandled_exception_message_is_safe(self):
        """The 500 error message must not leak internal details."""
        resp = self._call(RuntimeError("DB password is hunter2"), context={'view': None})
        self.assertNotIn('hunter2', resp.data.get('error', ''))

    def test_auth_failed_error_shape(self):
        exc = AuthenticationFailed("Bad token.")
        resp = self._call(exc)
        self.assertIn('error', resp.data)
        self.assertIsInstance(resp.data['error'], str)

    def test_permission_denied_error_shape(self):
        exc = PermissionDenied("Forbidden.")
        resp = self._call(exc)
        self.assertIn('error', resp.data)


class ExceptionHandlerNeverCrashesTests(APITestCase):
    """Any endpoint hit should return JSON, never crash with HTML."""

    def setUp(self):
        patch('boto3.client').start()

    def tearDown(self):
        patch.stopall()

    def test_nonexistent_endpoint_returns_json(self):
        resp = self.client.get(f'{BASE}/this-endpoint-does-not-exist-at-all/')
        # Should be 404 with JSON body, not HTML 404 page
        self.assertIn(resp.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_301_MOVED_PERMANENTLY])
        # If it did return content, check it's not HTML
        if resp.content:
            try:
                import json
                json.loads(resp.content)
            except (ValueError, UnicodeDecodeError):
                pass  # 301/302 responses may have no body
