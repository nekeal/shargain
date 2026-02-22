from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.dispatch import receiver
from django.utils import timezone

from shargain.offers.models import ScrappingTarget
from shargain.offers.signals import offers_batch_created
from shargain.quotas.models import OfferQuota, ScrapingUrlQuota
from shargain.quotas.services.quota import QuotaService
from shargain.subscriptions.signals import (
    SubscriptionChangedEvent,
    subscription_downgraded,
    subscription_upgraded,
)


@receiver(offers_batch_created)
def handle_offers_created(sender, user_id: int, target_id: int, count: int, **kwargs):
    QuotaService.record_offers_created(user_id=user_id, target_id=target_id, count=count)


@receiver(subscription_upgraded)
@transaction.atomic
def handle_subscription_upgraded(
    sender,
    event: SubscriptionChangedEvent,
    **kwargs,
):
    del sender, kwargs
    period_start = timezone.now()
    period_end = period_start + timedelta(days=settings.QUOTA_PERIOD_DAYS)

    url_quota, _ = ScrapingUrlQuota.objects.get_or_create(
        user_id=event.user_id,
        defaults={"max_urls": event.plan_limits.max_urls},
    )
    url_quota.max_urls = event.plan_limits.max_urls
    url_quota.save(update_fields=["max_urls", "updated_at"])

    active_quotas = list(OfferQuota.objects.for_user(user_id=event.user_id).active())
    active_quota_ids = [quota.id for quota in active_quotas]
    if active_quota_ids:
        OfferQuota.objects.filter(id__in=active_quota_ids).update(
            auto_renew=False,
            period_end=period_start,
        )

    target_ids = {target.id for target in ScrappingTarget.objects.filter(owner_id=event.user_id)}
    is_free_tier = event.plan_limits.plan_slug == "free"
    for target_id in target_ids:
        OfferQuota.objects.create(
            user_id=event.user_id,
            target_id=target_id,
            max_offers_per_period=event.plan_limits.max_offers_per_target,
            used_offers_count=0,
            period_start=period_start,
            period_end=period_end,
            auto_renew=True,
            is_free_tier=is_free_tier,
        )


@receiver(subscription_downgraded)
@transaction.atomic
def handle_subscription_downgraded(
    sender,
    event: SubscriptionChangedEvent,
    **kwargs,
):
    del sender, kwargs
    url_quota, _ = ScrapingUrlQuota.objects.get_or_create(
        user_id=event.user_id,
        defaults={"max_urls": event.plan_limits.max_urls},
    )
    url_quota.max_urls = event.plan_limits.max_urls
    url_quota.save(update_fields=["max_urls", "updated_at"])
