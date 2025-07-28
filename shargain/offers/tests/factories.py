import factory
from faker import Faker

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.models import ScrapingUrl, ScrappingTarget

fake = Faker()


class ScrappingTargetFactory(factory.django.DjangoModelFactory):
    name = factory.LazyFunction(lambda: f"Target - {fake.word().title()}")
    enable_notifications = True
    is_active = True
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = ScrappingTarget


class ScrapingUrlFactory(factory.django.DjangoModelFactory):
    url = factory.LazyFunction(lambda: f"https://example.com/{fake.word()}")
    scraping_target = factory.SubFactory(ScrappingTargetFactory)

    class Meta:
        model = ScrapingUrl
