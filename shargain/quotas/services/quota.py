from dataclasses import dataclass
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import F
from django.utils import timezone

from shargain.offers.models import ScrapingUrl, ScrappingTarget
from shargain.quotas.models import OfferQuota, ScrapingUrlQuota


@dataclass(frozen=True)
class QuotaStatusItem:
    slug: str
    used: int
    limit: int
    target_id: int | None = None
    target_name: str | None = None
    period_end: str | None = None
    is_free_tier: bool | None = None


@dataclass(frozen=True)
class QuotaStatusResponse:
    quotas: list[QuotaStatusItem]


class QuotaService:
    @staticmethod
    def _period_bounds(start: datetime | None = None) -> tuple[datetime, datetime]:
        period_start = start or timezone.now()
        period_end = period_start + timedelta(days=settings.QUOTA_PERIOD_DAYS)
        return period_start, period_end

    @staticmethod
    def _create_free_offer_quota(user_id: int, target_id: int, start: datetime | None = None) -> OfferQuota:
        period_start, period_end = QuotaService._period_bounds(start=start)
        return OfferQuota.objects.create(
            user_id=user_id,
            target_id=target_id,
            max_offers_per_period=settings.QUOTA_FREE_TIER_OFFERS_PER_TARGET,
            used_offers_count=0,
            period_start=period_start,
            period_end=period_end,
            auto_renew=True,
            is_free_tier=True,
        )

    @staticmethod
    def _get_or_create_active_offer_quota(user_id: int, target_id: int) -> OfferQuota:
        now = timezone.now()
        active = OfferQuota.objects.for_user_target(user_id=user_id, target_id=target_id).active().first()
        if active:
            return active

        latest = (
            OfferQuota.objects.for_user_target(user_id=user_id, target_id=target_id)
            .order_by("-period_end", "-period_start")
            .first()
        )
        if not latest:
            return QuotaService._create_free_offer_quota(user_id=user_id, target_id=target_id, start=now)

        period_start, period_end = QuotaService._period_bounds(start=now)
        if latest.auto_renew:
            return OfferQuota.objects.create(
                user_id=user_id,
                target_id=target_id,
                max_offers_per_period=latest.max_offers_per_period,
                used_offers_count=0,
                period_start=period_start,
                period_end=period_end,
                auto_renew=latest.auto_renew,
                is_free_tier=latest.is_free_tier,
            )

        return QuotaService._create_free_offer_quota(user_id=user_id, target_id=target_id, start=now)

    @staticmethod
    def _get_or_create_url_quota(user_id: int) -> ScrapingUrlQuota:
        quota, _ = ScrapingUrlQuota.objects.get_or_create(
            user_id=user_id,
            defaults={"max_urls": settings.QUOTA_FREE_TIER_MAX_URLS},
        )
        return quota

    @staticmethod
    def check_can_create_offers(user_id: int, target_id: int) -> bool:
        quota = QuotaService._get_or_create_active_offer_quota(user_id=user_id, target_id=target_id)
        return quota.used_offers_count < quota.max_offers_per_period

    @staticmethod
    def record_offers_created(user_id: int, target_id: int, count: int) -> None:
        if count <= 0:
            return

        quota = QuotaService._get_or_create_active_offer_quota(user_id=user_id, target_id=target_id)
        OfferQuota.objects.filter(id=quota.id).update(used_offers_count=F("used_offers_count") + count)

    @staticmethod
    def check_can_add_url(user_id: int, target_id: int) -> bool:
        quota = QuotaService._get_or_create_url_quota(user_id=user_id)
        current_urls = ScrapingUrl.objects.filter(
            scraping_target_id=target_id,
            scraping_target__owner_id=user_id,
        ).count()
        return current_urls < quota.max_urls

    @staticmethod
    def set_new_quota(
        user_id: int,
        target_id: int,
        max_offers: int,
        period_start: datetime,
        period_end: datetime,
        auto_renew: bool = False,
        is_free_tier: bool = False,
    ) -> None:
        OfferQuota.objects.update_or_create(
            user_id=user_id,
            target_id=target_id,
            period_start=period_start,
            defaults={
                "max_offers_per_period": max_offers,
                "used_offers_count": 0,
                "period_end": period_end,
                "auto_renew": auto_renew,
                "is_free_tier": is_free_tier,
            },
        )

    @staticmethod
    def get_quota_status(user_id: int) -> QuotaStatusResponse:
        url_quota = QuotaService._get_or_create_url_quota(user_id=user_id)
        quotas: list[QuotaStatusItem] = []

        targets = ScrappingTarget.objects.filter(owner_id=user_id).order_by("id")
        for target in targets:
            current_target_urls = ScrapingUrl.objects.filter(scraping_target_id=target.id).count()
            quotas.append(
                QuotaStatusItem(
                    slug="scraping_urls",
                    used=current_target_urls,
                    limit=url_quota.max_urls,
                    target_id=target.id,
                    target_name=target.name,
                )
            )

            quota = QuotaService._get_or_create_active_offer_quota(user_id=user_id, target_id=target.id)
            quotas.append(
                QuotaStatusItem(
                    slug="offers",
                    used=quota.used_offers_count,
                    limit=quota.max_offers_per_period,
                    target_id=target.id,
                    target_name=target.name,
                    period_end=quota.period_end.isoformat(),
                    is_free_tier=quota.is_free_tier,
                )
            )

        return QuotaStatusResponse(quotas=quotas)
