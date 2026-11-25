from __future__ import annotations

from shargain.commons.application.actor import Actor
from shargain.offers.application.access import can_manage_urls
from shargain.offers.application.dto import ScrapingUrlDTO, WaypointData
from shargain.offers.application.exceptions import QuotaExceeded, TargetDoesNotExist, TargetPermissionDenied
from shargain.offers.filtering import validate_filters_for_url
from shargain.offers.models import ScrapingUrl, ScrappingTarget
from shargain.quotas.services.quota import QuotaService


def add_scraping_url(
    actor: Actor,
    url: str,
    target_id: int,
    name: str | None = None,
    filters: dict | None = None,
    show_location_map_in_notifications: bool = False,
    send_map_in_notifications: bool = True,
    waypoints: list[WaypointData] | None = None,
) -> ScrapingUrlDTO:
    """
    Adds a new scraping URL to the specified target.

    Args:
        actor: The user performing the action
        url: The URL to scrape
        target_id: The target ID to add the URL to
        name: Optional name for the URL
        filters: Optional filter configuration for notifications
    """
    try:
        target = ScrappingTarget.objects.for_user(actor.user_id).get(id=target_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e

    if not can_manage_urls(actor.user_id, target):
        raise TargetPermissionDenied()

    filters = validate_filters_for_url(filters, url)

    target_owner_id = target.owner_id or actor.user_id
    if not QuotaService.check_can_add_url(user_id=target_owner_id, target_id=target.id):
        raise QuotaExceeded()

    scraping_url = ScrapingUrl.objects.create(
        url=url,
        scraping_target=target,
        name=name or "",
        filters=filters,
        show_location_map_in_notifications=show_location_map_in_notifications,
        send_map_in_notifications=send_map_in_notifications,
        waypoints=waypoints,
    )
    return ScrapingUrlDTO.from_orm(scraping_url)
