# Utilities

import factory

from faker import Factory as FakerFactory

from api.users.factories import UserFactory

faker = FakerFactory.create()


class IdentityFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.IdentityFiles'

    user = factory.SubFactory(UserFactory)
    file = factory.django.FileField(data="Ha")
