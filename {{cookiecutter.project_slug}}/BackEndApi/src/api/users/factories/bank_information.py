# Utilities

import factory
from faker import Factory as FakerFactory

from api.users.factories import UserFactory

faker = FakerFactory.create()


class BankFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.Bank'


class BankAccountTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.BankAccountType'

    name = factory.Faker('first_name')


class BankInformationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.BankInformation'

    user = factory.SubFactory(UserFactory)
    bank = factory.SubFactory(BankFactory)
    account_type = factory.SubFactory(BankAccountTypeFactory)
    file = factory.django.FileField(data="bk")
    account = factory.Faker('random_number', digits=10)
