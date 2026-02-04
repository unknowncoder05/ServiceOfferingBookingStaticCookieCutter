# Utilities
import random

import factory
from faker import Factory as FakerFactory

from api.users.roles import UserRoles

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.User'

    class Params:
        with_transactions = factory.Trait(
            transaction_1=factory.RelatedFactory('api.investments.factories.TransactionsFactory', 'created_by'))

    first_name = factory.Faker('first_name')

    middle_name = factory.Faker('first_name')

    phone_number = factory.Sequence(lambda n: f'+1555{n:07d}')

    public = factory.Faker('boolean')

    last_name = factory.Faker('last_name')

    email = factory.LazyAttribute(lambda p: f'{p.first_name.lower()}.{p.last_name.lower()}@mail.com')

    username = factory.LazyAttribute(lambda p: p.email)

    dob = factory.Faker('date_between')

    role = factory.LazyAttribute(lambda _: random.choice(list(UserRoles._value2member_map_.values())))
