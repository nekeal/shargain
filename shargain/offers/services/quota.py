import abc
from dataclasses import dataclass
from datetime import datetime

from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from shargain.offers.models import OfferQuota, ScrappingTarget


class AbstractQuotaInfo(abc.ABC):
    """Abstract base class for quota information."""

    @property
    @abc.abstractmethod
    def id(self) -> int | None: ...

    @property
    @abc.abstractmethod
    def remaining_offers(self) -> int | float: ...

    @property
    @abc.abstractmethod
    def is_exhausted(self) -> bool: ...


@dataclass(frozen=True)
class QuotaInfo(AbstractQuotaInfo):
    """Data class representing quota information."""

    _model: OfferQuota

    @property
    def id(self) -> int:
        return self._model.pk

    @property
    def remaining_offers(self) -> int | float:
        """Number of offers that can still be created in the current period."""
        if self._model.max_offers_per_period is None:  # Unlimited offers
            return float("inf")
        return max(0, self._model.max_offers_per_period - self._model.used_offers_count)

    @property
    def is_exhausted(self) -> bool:
        """Whether the quota limit has been reached."""
        if self._model.max_offers_per_period is None:
            return False
        return self._model.used_offers_count >= self._model.max_offers_per_period


@dataclass(frozen=True)
class InfiniteQuotaInfo(AbstractQuotaInfo):
    id = None
    remaining_offers: float = float("inf")
    is_exhausted: bool = False


class QuotaService:
    """
    Facade for all quota-related operations.
    This is the sole public interface for the quota system.
    """

    @staticmethod
    def get_active_quota(target: ScrappingTarget) -> AbstractQuotaInfo:
        """
        Get the single currently active quota object for a given target
        """
        now = timezone.now()
        active_quota = (
            OfferQuota.objects.filter(target=target, period_start__lte=now)
            .filter(Q(period_end__gt=now) | Q(period_end__isnull=True))
            .order_by("-period_start")
            .first()
        )

        if active_quota:
            return QuotaInfo(_model=active_quota)
        return InfiniteQuotaInfo()

    @staticmethod
    @transaction.atomic
    def set_new_quota(
        target: ScrappingTarget,
        max_offers_per_period: int | None,
        period_start: datetime,
        period_end: datetime | None,
        used_offers_count: int = 0,
    ) -> OfferQuota:
        """
        Idempotently create or update an OfferQuota record.

        Args:
            target: The target the quota is for
            max_offers_per_period: Maximum number of offers allowed in the period (None for unlimited)
            period_start: Start of the quota period
            period_end: End of the quota period (None for indefinite)
            used_offers_count: Current count of used offers (default: 0)

        Returns:
            The created or updated OfferQuota object

        Raises:
            ValueError: If the new quota period overlaps with an existing one
        """
        if period_end is not None:
            overlapping_quota = (
                OfferQuota.objects.filter(
                    target=target,
                    period_start__lt=period_end,
                )
                .filter(Q(period_end__gt=period_start) | Q(period_end__isnull=True))
                .exclude(period_start=period_start, period_end=period_end)
                .first()
            )
        else:
            overlapping_quota = (
                OfferQuota.objects.filter(
                    target=target,
                    period_start__lt=period_start,
                )
                .filter(Q(period_end__gt=period_start) | Q(period_end__isnull=True))
                .exclude(period_start=period_start, period_end__isnull=True)
                .first()
            )

        if overlapping_quota:
            if overlapping_quota.period_end:
                overlap_end_str = str(overlapping_quota.period_end)
            else:
                overlap_end_str = "Indefinite"
            raise ValueError(
                "Cannot create quota: Period overlaps with existing quota\n"
                f"from {overlapping_quota.period_start} to {overlap_end_str}"
            )

        quota, created = OfferQuota.objects.update_or_create(
            target=target,
            defaults={
                "max_offers_per_period": max_offers_per_period,
                "period_start": period_start,
                "period_end": period_end,
                "used_offers_count": used_offers_count,
            },
        )
        return quota

    @staticmethod
    @transaction.atomic
    def increment_usage(quota_id: int | None, increment_by: int = 1) -> bool:
        """
        Increment the used offers count for the given quota.
        """
        if quota_id is None:
            return True
        OfferQuota.objects.filter(pk=quota_id).update(used_offers_count=F("used_offers_count") + increment_by)
        return True

    @staticmethod
    def is_quota_available(target: ScrappingTarget) -> bool:
        """
        Check if the target has available quota.
        """
        quota = QuotaService.get_active_quota(target)

        if quota is None:
            return True

        return not quota.is_exhausted
