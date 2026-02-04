"""
Item models - Example CRUD module demonstrating Django model patterns.

This module provides a simple Item model that can be used as a starting point
for building your own models. It demonstrates:
- User ownership (ForeignKey to User)
- Timestamps (created_at, updated_at)
- Status field with choices
- JSON metadata field
- String representation
- Ordering
"""
from django.db import models
from django.conf import settings


class Item(models.Model):
    """
    Example Item model with common field patterns.

    Attributes:
        name: The item's display name
        description: Optional detailed description
        status: Current status (draft, active, archived)
        owner: The user who owns this item
        metadata: Flexible JSON field for additional data
        created_at: When the item was created
        updated_at: When the item was last modified
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='items',
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return self.name
