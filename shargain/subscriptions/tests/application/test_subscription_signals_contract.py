import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.subscriptions.dto import PlanLimitsDTO
from shargain.subscriptions.services.subscription import SubscriptionService
from shargain.subscriptions.signals import (
    SubscriptionChangedEvent,
    subscription_downgraded,
    subscription_upgraded,
)
from shargain.subscriptions.tests.factories import PlanFactory


@pytest.mark.django_db
def test_assign_plan_emits_upgrade_signal_with_contract_payload():
    user = UserFactory()
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

    received = []

    def _receiver(sender, **kwargs):
        received.append(kwargs)

    subscription_upgraded.connect(_receiver, weak=False)
    try:
        SubscriptionService.assign_plan(user_id=user.id, plan_slug="plus")
    finally:
        subscription_upgraded.disconnect(_receiver)

    assert len(received) == 1
    payload = received[0]
    assert isinstance(payload["event"], SubscriptionChangedEvent)
    assert payload["event"].user_id == user.id
    assert payload["event"].previous_plan_slug == "free"
    assert isinstance(payload["event"].plan_limits, PlanLimitsDTO)
    assert payload["event"].plan_limits.plan_slug == "plus"


@pytest.mark.django_db
def test_assign_plan_emits_downgrade_signal_with_contract_payload():
    user = UserFactory()
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

    received = []

    def _receiver(sender, **kwargs):
        received.append(kwargs)

    subscription_downgraded.connect(_receiver, weak=False)
    try:
        SubscriptionService.assign_plan(user_id=user.id, plan_slug="free")
    finally:
        subscription_downgraded.disconnect(_receiver)

    assert len(received) == 1
    payload = received[0]
    assert isinstance(payload["event"], SubscriptionChangedEvent)
    assert payload["event"].user_id == user.id
    assert payload["event"].previous_plan_slug == "plus"
    assert isinstance(payload["event"].plan_limits, PlanLimitsDTO)
    assert payload["event"].plan_limits.plan_slug == "free"
