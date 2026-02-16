from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone

from shargain.offers.tests.factories import ScrapingUrlFactory, ScrappingTargetFactory
from shargain.quotas.models import OfferQuota, ScrapingUrlQuota
from shargain.quotas.services.quota import QuotaService
from shargain.quotas.tests.factories import OfferQuotaFactory


@pytest.mark.django_db
class TestQuotaService:
    def test_scenario_no_quota_creates_free_tier_for_offers(self):
        target = ScrappingTargetFactory()

        assert QuotaService.check_can_create_offers(user_id=target.owner_id, target_id=target.id) is True

        quota = OfferQuota.objects.get(user_id=target.owner_id, target_id=target.id)
        assert quota.max_offers_per_period == settings.QUOTA_FREE_TIER_OFFERS_PER_TARGET
        assert quota.used_offers_count == 0
        assert quota.auto_renew is True
        assert quota.is_free_tier is True

    def test_scenario_active_quota_limit_reached_denies_creation(self):
        quota = OfferQuotaFactory(max_offers_per_period=2, used_offers_count=2)

        assert QuotaService.check_can_create_offers(user_id=quota.user_id, target_id=quota.target_id) is False

    def test_scenario_expired_auto_renew_quota_creates_new_period(self):
        now = timezone.now()
        quota = OfferQuotaFactory(
            period_start=now - timedelta(days=40),
            period_end=now - timedelta(days=10),
            used_offers_count=10,
            max_offers_per_period=10,
            auto_renew=True,
            is_free_tier=True,
        )

        assert QuotaService.check_can_create_offers(user_id=quota.user_id, target_id=quota.target_id) is True

        active = OfferQuota.objects.active().get(user_id=quota.user_id, target_id=quota.target_id)
        assert active.id != quota.id
        assert active.used_offers_count == 0
        assert active.max_offers_per_period == quota.max_offers_per_period
        assert active.auto_renew is True
        assert active.is_free_tier is True

    def test_scenario_expired_paid_quota_downgrades_to_free_tier(self):
        now = timezone.now()
        quota = OfferQuotaFactory(
            period_start=now - timedelta(days=40),
            period_end=now - timedelta(days=10),
            used_offers_count=0,
            max_offers_per_period=500,
            auto_renew=False,
            is_free_tier=False,
        )

        assert QuotaService.check_can_create_offers(user_id=quota.user_id, target_id=quota.target_id) is True

        active = OfferQuota.objects.active().get(user_id=quota.user_id, target_id=quota.target_id)
        assert active.id != quota.id
        assert active.max_offers_per_period == settings.QUOTA_FREE_TIER_OFFERS_PER_TARGET
        assert active.auto_renew is True
        assert active.is_free_tier is True

    def test_scenario_record_offers_created_increments_usage(self):
        quota = OfferQuotaFactory(max_offers_per_period=10, used_offers_count=1)

        QuotaService.record_offers_created(user_id=quota.user_id, target_id=quota.target_id, count=3)

        quota.refresh_from_db()
        assert quota.used_offers_count == 4

    def test_scenario_url_quota_created_and_enforced(self):
        target = ScrappingTargetFactory()
        second_target = ScrappingTargetFactory(owner=target.owner)

        assert QuotaService.check_can_add_url(user_id=target.owner_id, target_id=target.id) is True
        url_quota = ScrapingUrlQuota.objects.get(user_id=target.owner_id)
        assert url_quota.max_urls == settings.QUOTA_FREE_TIER_MAX_URLS

        for _ in range(settings.QUOTA_FREE_TIER_MAX_URLS):
            ScrapingUrlFactory(scraping_target=target)

        assert QuotaService.check_can_add_url(user_id=target.owner_id, target_id=target.id) is False
        assert QuotaService.check_can_add_url(user_id=target.owner_id, target_id=second_target.id) is True

    def test_scenario_get_quota_status_returns_scraping_and_offer_rows(self):
        target = ScrappingTargetFactory(name="Cars")
        OfferQuotaFactory(
            user=target.owner,
            target=target,
            max_offers_per_period=15,
            used_offers_count=4,
            is_free_tier=False,
            auto_renew=False,
        )
        ScrapingUrlFactory(scraping_target=target)

        status = QuotaService.get_quota_status(user_id=target.owner_id)

        assert len(status.quotas) == 2
        assert any(q.slug == "scraping_urls" and q.target_id == target.id and q.used == 1 for q in status.quotas)
        assert any(q.slug == "offers" and q.target_id == target.id and q.limit == 15 for q in status.quotas)
