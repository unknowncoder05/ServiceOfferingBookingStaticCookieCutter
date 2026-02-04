"""
Item serializers - REST API serialization for Item model.

This module demonstrates common serializer patterns:
- ModelSerializer for automatic field generation
- Read-only fields for computed/auto values
- Nested owner representation
- Create/update with current user
"""
from rest_framework import serializers

from api.items.models import Item
from api.users.serializers import UserSerializer


class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer for Item model with full details.

    Includes nested owner information for read operations.
    Owner is automatically set to the current user on create.
    """
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
    """
    Serializer for creating new Items.

    Excludes owner field as it's set automatically from request.user.
    """

    class Meta:
        model = Item
        fields = [
            'name',
            'description',
            'status',
            'metadata',
        ]


class ItemListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views.

    Excludes heavy fields like metadata for better performance.
    """
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
