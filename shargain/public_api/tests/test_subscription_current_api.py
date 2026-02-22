import pytest
from django.test import Client

from shargain.accounts.tests.factories import UserFactory
from shargain.subscriptions.services.subscription import SubscriptionService
from shargain.subscriptions.tests.factories import PlanFactory


@pytest.mark.django_db
def test_get_current_subscription_requires_authentication():
    client = Client()

    response = client.get("/api/public/subscription/current")

    assert response.status_code == 401


@pytest.mark.django_db
def test_get_current_subscription_returns_contract_shape():
    user = UserFactory()
    plan = PlanFactory(
        name="Free",
        slug="free",
        max_urls=3,
        max_offers_per_target=50,
        is_default=True,
        is_active=True,
        display_order=0,
    )
    SubscriptionService.assign_plan(user_id=user.id, plan_slug=plan.slug)

    client = Client()
    client.force_login(user)

    response = client.get("/api/public/subscription/current")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"planName", "planSlug", "maxUrls", "maxOffersPerTarget", "startedAt", "expiresAt"}
    assert payload["planName"] == "Free"
    assert payload["planSlug"] == "free"
    assert payload["maxUrls"] == 3
    assert payload["maxOffersPerTarget"] == 50
    assert payload["startedAt"] is not None
    assert payload["expiresAt"] is None
