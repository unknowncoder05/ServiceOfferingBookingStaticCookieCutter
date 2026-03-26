"""Item services — business logic layer for Item operations."""
from typing import List, Optional

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from api.items.models import Item

User = get_user_model()


class ItemService:
    """Service class for Item business logic."""

    def get_user_items(self, user: User) -> QuerySet[Item]:
        return Item.objects.filter(owner=user)

    def get_user_items_by_status(self, user: User, status: str) -> QuerySet[Item]:
        return self.get_user_items(user).filter(status=status)

    def get_active_items(self, user: User) -> QuerySet[Item]:
        return self.get_user_items_by_status(user, Item.Status.ACTIVE)

    def bulk_archive(self, user: User, item_ids: List[int]) -> int:
        """Archive multiple items at once. Returns count archived."""
        return Item.objects.filter(
            owner=user,
            id__in=item_ids,
        ).update(status=Item.Status.ARCHIVED)

    def create_item(
        self,
        user: User,
        name: str,
        description: str = '',
        status: str = Item.Status.DRAFT,
        metadata: Optional[dict] = None,
    ) -> Item:
        return Item.objects.create(
            owner=user,
            name=name,
            description=description,
            status=status,
            metadata=metadata or {},
        )
