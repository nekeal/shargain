"""
Data Transfer Objects for the offers application layer.

These DTOs are used for transferring data between the application service layer
and the presentation layer (e.g., API views).
"""

import dataclasses
from datetime import datetime
from typing import Self, TypedDict

from shargain.offers.field_extraction import NotificationFieldsSelection
from shargain.offers.models import ScrapingUrl, ScrappingTarget


class WaypointData(TypedDict):
    name: str
    lat: float
    lon: float


@dataclasses.dataclass(frozen=True)
class ScrapingUrlDTO:
    """Data Transfer Object for ScrapingUrl."""

    id: int
    url: str
    name: str
    is_active: bool
    last_checked_at: str | None = None
    filters: dict | None = None
    show_location_map_in_notifications: bool = False
    send_map_in_notifications: bool = True
    waypoints: list[WaypointData] | None = None
    notification_fields: NotificationFieldsSelection | None = None

    @classmethod
    def from_orm(cls, url: ScrapingUrl, last_checked_at: str | None = None) -> Self:
        """Create a DTO from a ScrapingUrl model instance."""
        return cls(
            id=url.id,
            url=url.url,
            name=url.name,
            is_active=url.is_active,
            last_checked_at=last_checked_at,
            filters=url.filters,
            show_location_map_in_notifications=url.show_location_map_in_notifications,
            send_map_in_notifications=url.send_map_in_notifications,
            waypoints=url.waypoints,
            notification_fields=url.notification_fields.model_dump(mode="json") if url.notification_fields else None,
        )


@dataclasses.dataclass(frozen=True)
class TargetDTO:
    """Data Transfer Object for ScrappingTarget."""

    id: int
    name: str
    is_active: bool
    enable_notifications: bool
    notification_config_id: int | None
    urls: list[ScrapingUrlDTO]

    @classmethod
    def from_orm(cls, target: ScrappingTarget, url_ids_to_timestamps: dict[int, str] | None = None) -> Self:
        """Create a DTO from a ScrappingTarget model instance."""
        if url_ids_to_timestamps is None:
            url_ids_to_timestamps = {}

        urls = [
            ScrapingUrlDTO.from_orm(url, last_checked_at=url_ids_to_timestamps.get(url.id))
            for url in target.scrapingurl_set.all()
        ]
        return cls(
            id=target.id,
            name=target.name,
            is_active=target.is_active,
            enable_notifications=target.enable_notifications,
            notification_config_id=target.notification_config_id,
            urls=urls,
        )


@dataclasses.dataclass(frozen=True)
class OfferState:
    offer_id: int
    seen_at: datetime | None
    liked_at: datetime | None

    @property
    def is_seen(self) -> bool:
        return self.seen_at is not None

    @property
    def is_liked(self) -> bool:
        return self.liked_at is not None


@dataclasses.dataclass(frozen=True)
class OfferAttribute:
    name: str
    label: str
    type: str
    unit: str | None
    value: bool | int | float | str
    display: str | None = None


@dataclasses.dataclass(frozen=True)
class OfferLocation:
    name: str | None
    map_url: str | None
    latitude: float | None
    longitude: float | None
    is_exact: bool


@dataclasses.dataclass(frozen=True)
class PublicOffer:
    id: int
    url: str
    title: str
    price: int | None
    main_image_url: str | None
    published_at: datetime | None
    created_at: datetime
    closed_at: datetime | None
    list_url: str
    is_seen: bool
    seen_at: datetime | None
    is_liked: bool
    liked_at: datetime | None
    attributes: list[OfferAttribute]
    location: OfferLocation | None


@dataclasses.dataclass(frozen=True)
class PublicOfferPage:
    count: int
    items: list[PublicOffer]
