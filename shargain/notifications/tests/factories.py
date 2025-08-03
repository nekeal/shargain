import factory
from factory.declarations import Sequence, SubFactory

from shargain.accounts.tests.factories import UserFactory
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig


class NotificationConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NotificationConfig
        django_get_or_create = ("name",)

    name = Sequence(lambda n: f"Notification Config {n}")
    channel = NotificationChannelChoices.TELEGRAM
    webhook_url = "https://example.com/webhook"
    owner = SubFactory(UserFactory)
    chatid = "1234567890"
