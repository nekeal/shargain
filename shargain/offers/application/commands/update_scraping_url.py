from shargain.commons.application.actor import Actor
from shargain.offers.application.access import can_manage_urls
from shargain.offers.application.dto import ScrapingUrlDTO, WaypointData
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist, TargetPermissionDenied
from shargain.offers.field_extraction import NotificationFieldsSelection
from shargain.offers.filtering import validate_filters_for_url
from shargain.offers.models import ScrapingUrl


class ClearFilters:
    """Sentinel distinguishing 'filters not provided' from 'filters explicitly cleared'."""


CLEAR_FILTERS = ClearFilters()


def _get_scraping_url(user_id: int, url_id: int, target_id: int | None) -> ScrapingUrl:
    filter_kwargs = {"id": url_id}
    if target_id is not None:
        filter_kwargs["scraping_target_id"] = target_id
    try:
        return ScrapingUrl.objects.for_user(user_id).select_related("scraping_target").get(**filter_kwargs)
    except ScrapingUrl.DoesNotExist as e:
        raise ScrapingUrlDoesNotExist() from e


def update_scraping_url(
    actor: Actor,
    url_id: int,
    target_id: int | None = None,
    name: str | None = None,
    filters: dict | None | ClearFilters = None,
    show_location_map_in_notifications: bool | None = None,
    send_map_in_notifications: bool | None = None,
    waypoints: list[WaypointData] | None = None,
    notification_fields: dict | None = None,
) -> ScrapingUrlDTO:
    url = _get_scraping_url(actor.user_id, url_id, target_id)

    if not can_manage_urls(actor.user_id, url.scraping_target):
        raise TargetPermissionDenied()

    if isinstance(filters, dict):
        filters = validate_filters_for_url(filters, url.url)

    update_fields = []
    if name is not None:
        url.name = name
        update_fields.append("name")
    if filters is not None:
        url.filters = None if filters is CLEAR_FILTERS else filters
        update_fields.append("filters")
    if show_location_map_in_notifications is not None:
        url.show_location_map_in_notifications = show_location_map_in_notifications
        update_fields.append("show_location_map_in_notifications")
    if send_map_in_notifications is not None:
        url.send_map_in_notifications = send_map_in_notifications
        update_fields.append("send_map_in_notifications")
    if waypoints is not None:
        url.waypoints = waypoints
        update_fields.append("waypoints")
    if notification_fields is not None:
        url.notification_fields = NotificationFieldsSelection(**notification_fields)
        update_fields.append("notification_fields")

    if update_fields:
        url.save(update_fields=update_fields)
    return ScrapingUrlDTO.from_orm(url)
