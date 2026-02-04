"""
Tests for Item API views.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.items.models import Item
from api.items.tests.factories import ItemFactory
from api.users.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestItemViewSet:
    """Tests for ItemViewSet."""

    @pytest.fixture
    def api_client(self):
        """Return an API client."""
        return APIClient()

    @pytest.fixture
    def user(self):
        """Return a test user."""
        return UserFactory()

    @pytest.fixture
    def authenticated_client(self, api_client, user):
        """Return an authenticated API client."""
        api_client.force_authenticate(user=user)
        return api_client

    def test_list_items_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot list items."""
        url = reverse('items-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_items_authenticated(self, authenticated_client, user):
        """Test listing items for authenticated user."""
        # Create items for this user
        item1 = ItemFactory(owner=user)
        item2 = ItemFactory(owner=user)
        # Create item for another user (should not appear)
        ItemFactory()

        url = reverse('items-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_item(self, authenticated_client, user):
        """Test creating a new item."""
        url = reverse('items-list')
        data = {
            'name': 'New Item',
            'description': 'A test item',
            'status': 'draft',
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Item.objects.filter(owner=user, name='New Item').exists()

    def test_retrieve_item(self, authenticated_client, user):
        """Test retrieving a specific item."""
        item = ItemFactory(owner=user)
        url = reverse('items-detail', kwargs={'pk': item.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == item.name

    def test_retrieve_other_users_item(self, authenticated_client):
        """Test that users cannot retrieve other users' items."""
        other_item = ItemFactory()  # Different owner
        url = reverse('items-detail', kwargs={'pk': other_item.pk})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_item(self, authenticated_client, user):
        """Test updating an item."""
        item = ItemFactory(owner=user, name='Original Name')
        url = reverse('items-detail', kwargs={'pk': item.pk})
        data = {'name': 'Updated Name'}

        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.name == 'Updated Name'

    def test_delete_item(self, authenticated_client, user):
        """Test deleting an item."""
        item = ItemFactory(owner=user)
        url = reverse('items-detail', kwargs={'pk': item.pk})

        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Item.objects.filter(pk=item.pk).exists()

    def test_archive_action(self, authenticated_client, user):
        """Test the archive custom action."""
        item = ItemFactory(owner=user, status=Item.Status.ACTIVE)
        url = reverse('items-archive', kwargs={'pk': item.pk})

        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.status == Item.Status.ARCHIVED

    def test_activate_action(self, authenticated_client, user):
        """Test the activate custom action."""
        item = ItemFactory(owner=user, status=Item.Status.DRAFT)
        url = reverse('items-activate', kwargs={'pk': item.pk})

        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.status == Item.Status.ACTIVE
