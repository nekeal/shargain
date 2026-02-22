import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.tests.factories import ScrappingTargetFactory
from shargain.quotas.models import OfferQuota
from shargain.quotas.tests.factories import OfferQuotaFactory, ScrapingUrlQuotaFactory
from shargain.subscriptions.services.subscription import SubscriptionService
from shargain.subscriptions.tests.factories import PlanFactory


@pytest.mark.django_db
def test_upgrade_updates_url_quota_and_starts_new_offer_period_with_new_limits():
    user = UserFactory()
    target = ScrappingTargetFactory(owner=user)
    ScrapingUrlQuotaFactory(user=user, max_urls=3)
    previous_quota = OfferQuotaFactory(
        user=user,
        target=target,
        max_offers_per_period=50,
        used_offers_count=17,
        auto_renew=True,
        is_free_tier=True,
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

    SubscriptionService.assign_plan(user_id=user.id, plan_slug="free")
    SubscriptionService.assign_plan(user_id=user.id, plan_slug="plus")

    previous_quota.refresh_from_db()
    assert previous_quota.auto_renew is False

    latest_quota = (
        OfferQuota.objects.for_user_target(user_id=user.id, target_id=target.id).order_by("-period_start").first()
    )
    assert latest_quota is not None
    assert latest_quota.id != previous_quota.id
    assert latest_quota.max_offers_per_period == 200
    assert latest_quota.used_offers_count == 0
    assert latest_quota.is_free_tier is False

    user.scraping_url_quota.refresh_from_db()
    assert user.scraping_url_quota.max_urls == 10
