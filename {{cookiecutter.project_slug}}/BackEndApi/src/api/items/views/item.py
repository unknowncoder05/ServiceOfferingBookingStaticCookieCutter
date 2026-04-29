"""Item views — REST API endpoints for Item model."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.items.models import Item
from api.items.serializers import ItemListSerializer, ItemSerializer


class ItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Item CRUD operations.

    Items are filtered to only show those owned by the current user.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ItemListSerializer
        return ItemSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Set item status to archived."""
        item = self.get_object()
        item.status = Item.Status.ARCHIVED
        item.save(update_fields=['status', 'updated_at'])
        return Response(ItemSerializer(item).data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Set item status to active."""
        item = self.get_object()
        item.status = Item.Status.ACTIVE
        item.save(update_fields=['status', 'updated_at'])
        return Response(ItemSerializer(item).data)
