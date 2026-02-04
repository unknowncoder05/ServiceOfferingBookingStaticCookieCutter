"""
Item services - Business logic layer for Item operations.

This module provides a service layer for complex business logic
that doesn't belong in views or models. Use this pattern when:
- Operations involve multiple models
- Complex validation is needed
- External services are called
- Logic needs to be reused across views

Example usage:
    from api.items.services import ItemService

    service = ItemService()
    items = service.get_user_items_by_status(user, 'active')
"""
from typing import List, Optional

from django.db.models import QuerySet
from django.contrib.auth import get_user_model

from api.items.models import Item


User = get_user_model()


class ItemService:
    """Service class for Item business logic."""

    def get_user_items(self, user: User) -> QuerySet[Item]:
        """Get all items for a user."""
        return Item.objects.filter(owner=user)

    def get_user_items_by_status(
        self,
        user: User,
        status: str
    ) -> QuerySet[Item]:
        """Get user items filtered by status."""
        return self.get_user_items(user).filter(status=status)

    def get_active_items(self, user: User) -> QuerySet[Item]:
        """Get all active items for a user."""
        return self.get_user_items_by_status(user, Item.Status.ACTIVE)

    def bulk_archive(self, user: User, item_ids: List[int]) -> int:
        """
        Archive multiple items at once.

        Args:
            user: The owner of the items
            item_ids: List of item IDs to archive

        Returns:
            Number of items archived
        """
        return Item.objects.filter(
            owner=user,
            id__in=item_ids
        ).update(status=Item.Status.ARCHIVED)

    def create_item(
        self,
        user: User,
        name: str,
        description: str = '',
        status: str = Item.Status.DRAFT,
        metadata: Optional[dict] = None
    ) -> Item:
        """
        Create a new item with the given parameters.

        Args:
            user: The owner of the item
            name: Item name
            description: Optional description
            status: Item status (default: draft)
            metadata: Optional metadata dict

        Returns:
            The created Item instance
        """
        return Item.objects.create(
            owner=user,
            name=name,
            description=description,
            status=status,
            metadata=metadata or {}
        )
