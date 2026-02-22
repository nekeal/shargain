from django.conf import settings
from django.db import transaction
from django.utils import timezone

from shargain.subscriptions.dto import PlanLimitsDTO
from shargain.subscriptions.models import Plan, UserSubscription
from shargain.subscriptions.signals import (
    SubscriptionChangedEvent,
    subscription_downgraded,
    subscription_upgraded,
)


class SubscriptionService:
    @staticmethod
    def _get_or_create_default_plan() -> Plan:
        default_plan = Plan.objects.default().first()
        if default_plan:
            return default_plan

        return Plan.objects.create(
            name="Free",
            slug="free",
            max_urls=settings.QUOTA_FREE_TIER_MAX_URLS,
            max_offers_per_target=settings.QUOTA_FREE_TIER_OFFERS_PER_TARGET,
            is_default=True,
            is_active=True,
            display_order=0,
        )

    @staticmethod
    def _get_plan_by_slug(plan_slug: str) -> Plan:
        if plan_slug == "free":
            return SubscriptionService._get_or_create_default_plan()

        if plan := Plan.objects.filter(slug=plan_slug).first():
            return plan

        raise Plan.DoesNotExist(f"Plan with slug '{plan_slug}' does not exist")

    @staticmethod
    def get_user_subscription(user_id: int) -> UserSubscription | None:
        return UserSubscription.objects.active().select_related("plan").filter(user_id=user_id).first()

    @staticmethod
    def get_user_plan_limits(user_id: int) -> PlanLimitsDTO:
        subscription = SubscriptionService.get_user_subscription(user_id=user_id)
        if not subscription:
            default_plan = SubscriptionService._get_or_create_default_plan()
            subscription = SubscriptionService.assign_plan(user_id=user_id, plan_slug=default_plan.slug)

        plan = subscription.plan

        if not plan.is_active:
            default_plan = SubscriptionService._get_or_create_default_plan()
            subscription = SubscriptionService.assign_plan(user_id=user_id, plan_slug=default_plan.slug)
            plan = subscription.plan

        return PlanLimitsDTO.from_plan(plan)

    @staticmethod
    @transaction.atomic
    def assign_plan(user_id: int, plan_slug: str) -> UserSubscription:
        new_plan = SubscriptionService._get_plan_by_slug(plan_slug=plan_slug)
        now = timezone.now()

        previous_subscription = (
            UserSubscription.objects.active()
            .select_related("plan")
            .filter(user_id=user_id)
            .order_by("-started_at")
            .first()
        )
        previous_plan = previous_subscription.plan if previous_subscription else None

        if previous_plan and previous_plan.id == new_plan.id:
            return previous_subscription

        if previous_subscription:
            previous_subscription.is_active = False
            previous_subscription.expires_at = now
            previous_subscription.save(update_fields=["is_active", "expires_at", "updated_at"])

        new_subscription = UserSubscription.objects.create(
            user_id=user_id,
            plan=new_plan,
            started_at=now,
            expires_at=None,
            is_active=True,
        )

        if previous_plan:
            event = SubscriptionChangedEvent(
                user_id=user_id,
                previous_plan_slug=previous_plan.slug,
                plan_limits=PlanLimitsDTO.from_plan(new_plan),
            )
            if new_plan.display_order < previous_plan.display_order:
                subscription_upgraded.send(sender=SubscriptionService, event=event)
            elif new_plan.display_order > previous_plan.display_order:
                subscription_downgraded.send(sender=SubscriptionService, event=event)

        return new_subscription
