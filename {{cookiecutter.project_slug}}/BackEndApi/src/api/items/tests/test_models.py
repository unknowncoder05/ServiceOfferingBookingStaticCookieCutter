"""
Tests for Item models.
"""
import pytest
from django.db import IntegrityError

from api.items.models import Item
from api.items.tests.factories import ItemFactory, ActiveItemFactory


pytestmark = pytest.mark.django_db


class TestItemModel:
    """Tests for the Item model."""

    def test_create_item(self):
        """Test creating an item with required fields."""
        item = ItemFactory()
        assert item.pk is not None
        assert item.name.startswith('Test Item')
        assert item.status == Item.Status.DRAFT
        assert item.owner is not None

    def test_item_str(self):
        """Test string representation of item."""
        item = ItemFactory(name='My Test Item')
        assert str(item) == 'My Test Item'

    def test_item_default_status(self):
        """Test that default status is DRAFT."""
        item = ItemFactory()
        assert item.status == Item.Status.DRAFT

    def test_item_status_choices(self):
        """Test all status choices are valid."""
        for status_value, status_label in Item.Status.choices:
            item = ItemFactory(status=status_value)
            assert item.status == status_value

    def test_item_timestamps(self):
        """Test that timestamps are auto-populated."""
        item = ItemFactory()
        assert item.created_at is not None
        assert item.updated_at is not None

    def test_item_metadata_default(self):
        """Test that metadata defaults to empty dict."""
        item = ItemFactory()
        assert item.metadata == {}

    def test_item_metadata_json(self):
        """Test storing JSON in metadata field."""
        metadata = {'key': 'value', 'nested': {'a': 1}}
        item = ItemFactory(metadata=metadata)
        assert item.metadata == metadata

    def test_item_ordering(self):
        """Test items are ordered by created_at descending."""
        item1 = ItemFactory()
        item2 = ItemFactory()
        items = list(Item.objects.all())
        # Most recent first
        assert items[0] == item2
        assert items[1] == item1


class TestItemQuerySet:
    """Tests for Item querysets."""

    def test_filter_by_owner(self):
        """Test filtering items by owner."""
        item = ItemFactory()
        other_item = ItemFactory()  # Different owner

        user_items = Item.objects.filter(owner=item.owner)
        assert item in user_items
        assert other_item not in user_items

    def test_filter_by_status(self):
        """Test filtering items by status."""
        draft_item = ItemFactory(status=Item.Status.DRAFT)
        active_item = ActiveItemFactory()

        active_items = Item.objects.filter(status=Item.Status.ACTIVE)
        assert active_item in active_items
        assert draft_item not in active_items
