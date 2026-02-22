import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.subscriptions.models import UserSubscription
from shargain.subscriptions.services.subscription import SubscriptionService
from shargain.subscriptions.tests.factories import PlanFactory


@pytest.mark.django_db
def test_user_without_subscription_gets_default_plan_limits_and_active_subscription():
    user = UserFactory()
    PlanFactory(
        name="Free",
        slug="free",
        max_urls=3,
        max_offers_per_target=50,
        is_default=True,
        is_active=True,
        display_order=0,
    )

    limits = SubscriptionService.get_user_plan_limits(user_id=user.id)

    assert limits.plan_slug == "free"
    assert limits.max_urls == 3
    assert limits.max_offers_per_target == 50

    assert UserSubscription.objects.filter(user=user, is_active=True, plan__slug="free").exists()
