"""Factories for creating test users and related models."""

import factory
from django.contrib.auth.hashers import make_password
from factory.declarations import LazyAttribute, LazyFunction
from faker import Faker

from shargain.accounts.models import CustomUser

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = CustomUser
        django_get_or_create = ("username",)

    username = LazyAttribute(lambda _: fake.user_name())
    email = LazyAttribute(lambda _: fake.email())
    password = LazyFunction(lambda: make_password("testpass123"))
    first_name = LazyFunction(fake.first_name)
    last_name = LazyFunction(fake.last_name)
    is_active = True
    is_staff = False
    is_superuser = False
