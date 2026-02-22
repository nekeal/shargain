import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.tests.factories import ScrappingTargetFactory
from shargain.quotas.models import OfferQuota
from shargain.quotas.tests.factories import OfferQuotaFactory, ScrapingUrlQuotaFactory
from shargain.subscriptions.services.subscription import SubscriptionService
from shargain.subscriptions.tests.factories import PlanFactory


@pytest.mark.django_db
def test_downgrade_updates_url_quota_but_keeps_current_offer_period_active_until_renewal():
    user = UserFactory()
    target = ScrappingTargetFactory(owner=user)
    ScrapingUrlQuotaFactory(user=user, max_urls=10)
    paid_quota = OfferQuotaFactory(
        user=user,
        target=target,
        max_offers_per_period=200,
        used_offers_count=18,
        auto_renew=True,
        is_free_tier=False,
    )

    PlanFactory(
        name="Free",
        slug="free",
        max_urls=3,
        max_offers_per_target=50,
        is_default=True,
        is_active=True,
        display_order=20,
    )
    PlanFactory(
        name="Plus",
        slug="plus",
        max_urls=10,
        max_offers_per_target=200,
        is_default=False,
        is_active=True,
        display_order=10,
    )

    SubscriptionService.assign_plan(user_id=user.id, plan_slug="plus")
    SubscriptionService.assign_plan(user_id=user.id, plan_slug="free")

    paid_quota.refresh_from_db()
    assert paid_quota.max_offers_per_period == 200
    assert paid_quota.used_offers_count == 18

    active_period = OfferQuota.objects.for_user_target(user_id=user.id, target_id=target.id).active().get()
    assert active_period.id == paid_quota.id

    user.scraping_url_quota.refresh_from_db()
    assert user.scraping_url_quota.max_urls == 3
