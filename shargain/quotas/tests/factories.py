from datetime import timedelta

import factory
from django.utils import timezone

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.tests.factories import ScrappingTargetFactory
from shargain.quotas.models import OfferQuota, ScrapingUrlQuota


class OfferQuotaFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    target = factory.SubFactory(ScrappingTargetFactory, owner=factory.SelfAttribute("..user"))
    max_offers_per_period = 50
    used_offers_count = 0
    period_start = factory.LazyFunction(timezone.now)
    period_end = factory.LazyAttribute(lambda o: o.period_start + timedelta(days=30))
    auto_renew = True
    is_free_tier = True

    class Meta:
        model = OfferQuota


class ScrapingUrlQuotaFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    max_urls = 3

    class Meta:
        model = ScrapingUrlQuota
