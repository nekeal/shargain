import factory
from django.contrib.auth import get_user_model

from shargain.telegram.models import TelegramRegisterToken


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True


class TelegramRegisterTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TelegramRegisterToken

    user = factory.SubFactory(UserFactory)
    register_token = factory.Faker("sha1")
    is_used = False
