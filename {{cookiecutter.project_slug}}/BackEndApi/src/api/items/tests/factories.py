"""
Item test factories using Factory Boy.

Provides easy creation of test instances with realistic data.
"""
import factory
from factory.django import DjangoModelFactory

from api.items.models import Item
from api.users.factories import UserFactory


class ItemFactory(DjangoModelFactory):
    """Factory for creating Item instances in tests."""

    class Meta:
        model = Item

    name = factory.Sequence(lambda n: f'Test Item {n}')
    description = factory.Faker('paragraph')
    status = Item.Status.DRAFT
    owner = factory.SubFactory(UserFactory)
    metadata = factory.LazyFunction(dict)


class ActiveItemFactory(ItemFactory):
    """Factory for creating active Item instances."""
    status = Item.Status.ACTIVE


class ArchivedItemFactory(ItemFactory):
    """Factory for creating archived Item instances."""
    status = Item.Status.ARCHIVED
