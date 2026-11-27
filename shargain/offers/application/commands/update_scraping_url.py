from urllib.parse import urlparse

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


def _validate_url_update(existing_url: str, new_url: str) -> None:
    if len(new_url) > 1024:
        raise ValueError("URL must be at most 1024 characters")
    existing_parts = urlparse(existing_url)
    new_parts = urlparse(new_url)
    if (
        new_parts.scheme,
        new_parts.netloc,
        new_parts.path or "/",
        new_parts.params,
        new_parts.fragment,
    ) != (
        existing_parts.scheme,
        existing_parts.netloc,
        existing_parts.path or "/",
        existing_parts.params,
        existing_parts.fragment,
    ):
        raise ValueError("Only query parameters can be modified")


def _apply_simple_updates(scraping_url: ScrapingUrl, updates: dict[str, object]) -> list[str]:
    update_fields = []
    for field, value in updates.items():
        if value is not None:
            setattr(scraping_url, field, value)
            update_fields.append(field)
    return update_fields


def update_scraping_url(
    actor: Actor,
    url_id: int,
    target_id: int | None = None,
    url: str | None = None,
    name: str | None = None,
    filters: dict | None | ClearFilters = None,
    show_location_map_in_notifications: bool | None = None,
    send_map_in_notifications: bool | None = None,
    waypoints: list[WaypointData] | None = None,
    notification_fields: dict | None = None,
) -> ScrapingUrlDTO:
    scraping_url = _get_scraping_url(actor.user_id, url_id, target_id)

    if not can_manage_urls(actor.user_id, scraping_url.scraping_target):
        raise TargetPermissionDenied()

    if url is not None:
        _validate_url_update(scraping_url.url, url)

    target_url = url if url is not None else scraping_url.url
    if isinstance(filters, dict):
        filters = validate_filters_for_url(filters, target_url)

    update_fields = _apply_simple_updates(
        scraping_url,
        {
            "url": url,
            "name": name,
            "show_location_map_in_notifications": show_location_map_in_notifications,
            "send_map_in_notifications": send_map_in_notifications,
            "waypoints": waypoints,
            "notification_fields": (
                NotificationFieldsSelection(**notification_fields) if notification_fields is not None else None
            ),
        },
    )
    if filters is not None:
        scraping_url.filters = None if filters is CLEAR_FILTERS else filters
        update_fields.append("filters")

    if update_fields:
        scraping_url.save(update_fields=update_fields)
    return ScrapingUrlDTO.from_orm(scraping_url)
