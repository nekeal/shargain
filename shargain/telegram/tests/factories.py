import factory

from shargain.accounts.tests.factories import UserFactory
from shargain.telegram.models import TelegramRegisterToken


class TelegramRegisterTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TelegramRegisterToken

    user = factory.SubFactory(UserFactory)
    register_token = factory.Faker("sha1")
    is_used = False
