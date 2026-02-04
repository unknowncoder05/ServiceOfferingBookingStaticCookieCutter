"""
Item views - REST API endpoints for Item model.

This module demonstrates common ViewSet patterns:
- ModelViewSet for full CRUD operations
- Permission classes for access control
- Filtering queryset by owner
- Different serializers for different actions
- Custom actions with @action decorator
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.items.models import Item
from api.items.serializers import (
    ItemSerializer,
    ItemCreateSerializer,
    ItemListSerializer,
)


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Item CRUD operations.

    Provides standard list, create, retrieve, update, destroy actions.
    Items are filtered to only show those owned by the current user.

    list:
        Return all items owned by the current user.

    create:
        Create a new item owned by the current user.

    retrieve:
        Return a specific item by ID.

    update:
        Update an existing item.

    partial_update:
        Partially update an existing item.

    destroy:
        Delete an item.

    archive:
        Custom action to archive an item.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return items owned by the current user."""
        return Item.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ItemListSerializer
        elif self.action == 'create':
            return ItemCreateSerializer
        return ItemSerializer

    def perform_create(self, serializer):
        """Set the owner to the current user when creating."""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive an item.

        Sets the item's status to 'archived'.
        """
        item = self.get_object()
        item.status = Item.Status.ARCHIVED
        item.save(update_fields=['status', 'updated_at'])
        return Response(ItemSerializer(item).data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate an item.

        Sets the item's status to 'active'.
        """
        item = self.get_object()
        item.status = Item.Status.ACTIVE
        item.save(update_fields=['status', 'updated_at'])
        return Response(ItemSerializer(item).data)
