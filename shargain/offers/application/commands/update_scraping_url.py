from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import ScrapingUrlDTO, WaypointData
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist
from shargain.offers.models import ScrapingUrl


def update_scraping_url(
    actor: Actor,
    url_id: int,
    name: str | None = None,
    filters: dict | None = None,
    show_location_map_in_notifications: bool | None = None,
    waypoints: list[WaypointData] | None = None,
) -> ScrapingUrlDTO:
    try:
        url = ScrapingUrl.objects.get(id=url_id, scraping_target__owner=actor.user_id)
    except ScrapingUrl.DoesNotExist as e:
        raise ScrapingUrlDoesNotExist() from e

    update_fields = []
    if name is not None:
        url.name = name
        update_fields.append("name")
    if filters is not None:
        url.filters = filters
        update_fields.append("filters")
    if show_location_map_in_notifications is not None:
        url.show_location_map_in_notifications = show_location_map_in_notifications
        update_fields.append("show_location_map_in_notifications")
    if waypoints is not None:
        url.waypoints = waypoints
        update_fields.append("waypoints")

    if update_fields:
        url.save(update_fields=update_fields)
    return ScrapingUrlDTO.from_orm(url)
