"""Item serializers — REST API serialization for Item model."""
from rest_framework import serializers

from api.items.models import Item
from api.users.serializers import UserSerializer


class ItemSerializer(serializers.ModelSerializer):
    """Full item serializer with nested owner for read operations."""

    owner = UserSerializer(read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'name',
            'description',
            'status',
            'owner',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class ItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new Items (owner set from request.user)."""

    class Meta:
        model = Item
        fields = [
            'name',
            'description',
            'status',
            'metadata',
        ]


class ItemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id',
            'name',
            'status',
            'owner_name',
            'created_at',
        ]
