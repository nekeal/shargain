from dataclasses import dataclass

import django.dispatch

from shargain.subscriptions.dto import PlanLimitsDTO


@dataclass(frozen=True)
class SubscriptionChangedEvent:
    user_id: int
    previous_plan_slug: str
    plan_limits: PlanLimitsDTO


subscription_upgraded = django.dispatch.Signal()
subscription_downgraded = django.dispatch.Signal()
