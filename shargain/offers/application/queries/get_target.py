from __future__ import annotations

from django.db.models import Max, Prefetch

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import TargetDTO
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.models import ScrapingCheckin, ScrapingUrl, ScrappingTarget


def get_target(actor: Actor, target_id: int) -> TargetDTO:
    try:
        # Prefetch scraping URLs with their latest checkin timestamp
        latest_checkins = (
            ScrapingCheckin.objects.filter(
                scraping_url_id__in=ScrapingUrl.objects.filter(scraping_target_id=target_id).values_list(
                    "id", flat=True
                )
            )
            .values("scraping_url_id")
            .annotate(latest_timestamp=Max("timestamp"))
            .order_by()
        )

        url_ids_to_timestamps = {
            item["scraping_url_id"]: item["latest_timestamp"].isoformat() for item in latest_checkins
        }

        target = ScrappingTarget.objects.prefetch_related(
            Prefetch("scrapingurl_set", queryset=ScrapingUrl.objects.all())
        ).get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e

    return TargetDTO.from_orm(target, url_ids_to_timestamps)


def get_target_by_user(actor: Actor) -> TargetDTO:
    target_qs = ScrappingTarget.objects.filter(owner=actor.user_id).order_by("-id")

    if not (target := target_qs.first()):
        raise TargetDoesNotExist()

    # TODO: make it a method on queryset or sth
    latest_checkins = (
        ScrapingCheckin.objects.filter(scraping_url_id__in=target.scrapingurl_set.values_list("id", flat=True))
        .values("scraping_url_id")
        .annotate(latest_timestamp=Max("timestamp"))
        .order_by()
    )

    url_ids_to_timestamps = {item["scraping_url_id"]: item["latest_timestamp"].isoformat() for item in latest_checkins}

    target = (
        ScrappingTarget.objects.prefetch_related(Prefetch("scrapingurl_set", queryset=ScrapingUrl.objects.all()))
        .filter(owner=actor.user_id)
        .order_by("-id")
        .first()
    )

    if not target:
        raise TargetDoesNotExist()

    return TargetDTO.from_orm(target, url_ids_to_timestamps)
