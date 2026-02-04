"""Users tests."""

from django.conf import settings
from rest_framework import status
# Django
from rest_framework.test import APITestCase

# Utils
from api.users.factories import UserFactory
# Models
from api.users.models import User
from api.users.roles import UserRoles
from api.utils.tests import DefaultTestHelper, response_error


# Users helper
class UserTestHelper(DefaultTestHelper):
    default_path = 'users'
    model_class = User
    factory = UserFactory
    sample_data = {
        'default': {
            'role': UserRoles.STANDARD,
        },
        'super_admin': {
            'role': UserRoles.ADMIN,
        },
        'john_doe': {
            'username': 'JDoe',
            'first_name': 'John',
            'middle_name': 'Anderson',
            'last_name': 'Doe',
            'email': 'jdoe@mail.com',
            'dob': '2000-01-01',
            'phone_number': '+14003002010',
            'password': 'SecurePassword#1',
        }
    }

    create_path = '/' + settings.API_URI + '/auth/sign-up/'
    auth_path = '/' + settings.API_URI + '/auth/token/'
    refresh_path = '/' + settings.API_URI + '/auth/token-refresh/'

    @classmethod
    def force_create(cls, client=None, data={}, sample_name='default', force_auth=False):
        # Create new Object with the given data
        sample = cls._get_data(data, sample_name)
        obj = cls.factory(**sample)

        if force_auth:
            if not client:
                raise Exception('for force auth, client is required')
            client.force_authenticate(user=obj)

        return obj

    @classmethod
    @response_error
    def create(cls, client, data=None, sample_name='default'):
        data = cls._get_data(data, sample_name)
        return client.post(cls.create_path, data, format='json')

    @classmethod
    def auth(cls, client, data=None):
        return client.post(cls.auth_path, data, format='json')

    @classmethod
    def refresh(cls, client, data=None):
        return client.post(cls.refresh_path, data, format='json')


from unittest.mock import patch

class AdminUserPostApiTestCase(APITestCase):

    def setUp(self):
        self.mock_boto3_client = patch('boto3.client').start()

    def tearDown(self):
        patch.stopall()

    def test_endpoint_responses_code(self):
        creation_request = UserTestHelper.create(self.client, sample_name='john_doe')
        self.assertEqual(creation_request.status_code, status.HTTP_200_OK)

        user_data = UserTestHelper.get_sample_data('john_doe')
        # list_request = UserTestHelper.auth(self.client,
        #                                    data=dict(phone_number=user_data['phone_number'],
        #                                              token=user_data['token']))
        # self.assertEqual(list_request.status_code, status.HTTP_200_OK)
        #
        # retrieve_request = UserTestHelper.refresh(self.client, data=dict(refresh=list_request.data['refresh']))
        # self.assertEqual(retrieve_request.status_code, status.HTTP_200_OK)

    #
    def test_object_creation(self):
        self.assertEqual(UserTestHelper.non_deleted_objects_count(), 0)
        UserTestHelper.create(self.client, sample_name='john_doe')
        self.assertEqual(UserTestHelper.non_deleted_objects_count(), 1)
