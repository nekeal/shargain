from datetime import timedelta

import factory
from django.utils import timezone
from faker import Faker

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.models import OfferQuota, ScrapingUrl, ScrappingTarget

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


class OfferQuotaFactory(factory.django.DjangoModelFactory):
    target = factory.SubFactory(ScrappingTargetFactory)
    max_offers_per_period = 10
    used_offers_count = 0
    period_start = factory.LazyFunction(lambda: timezone.now() - timedelta(days=1))
    period_end = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))

    class Meta:
        model = OfferQuota

    @classmethod
    def create_active(cls, **kwargs) -> OfferQuota:
        return cls.create(
            period_start=timezone.now() - timedelta(days=1),
            period_end=timezone.now() + timedelta(days=1),
            **kwargs,
        )

    @classmethod
    def create_expired(cls, **kwargs) -> OfferQuota:
        return cls.create(
            period_start=timezone.now() - timedelta(days=1),
            period_end=timezone.now() - timedelta(days=1),
            **kwargs,
        )

    @classmethod
    def create_future(cls, **kwargs) -> OfferQuota:
        return cls.create(
            period_start=timezone.now() + timedelta(days=1),
            period_end=timezone.now() + timedelta(days=2),
            **kwargs,
        )

    @classmethod
    def create_indefinite(cls, **kwargs) -> OfferQuota:
        """Create an indefinite quota with no end date."""
        return cls.create(
            period_start=timezone.now() - timedelta(days=1),
            period_end=None,
            **kwargs,
        )

    @classmethod
    def create_unlimited(cls, **kwargs) -> OfferQuota:
        """Create a quota with unlimited offers."""
        return cls.create(
            max_offers_per_period=None,
            period_start=timezone.now() - timedelta(days=1),
            period_end=timezone.now() + timedelta(days=1),
            **kwargs,
        )

    @classmethod
    def create_indefinite_unlimited(cls, **kwargs) -> OfferQuota:
        """Create an indefinite quota with unlimited offers."""
        return cls.create(
            max_offers_per_period=None,
            period_start=timezone.now() - timedelta(days=1),
            period_end=None,
            **kwargs,
        )
