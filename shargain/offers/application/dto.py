"""
Data Transfer Objects for the offers application layer.

These DTOs are used for transferring data between the application service layer
and the presentation layer (e.g., API views).
"""

import dataclasses
from typing import Self

from shargain.offers.models import ScrapingUrl, ScrappingTarget


@dataclasses.dataclass(frozen=True)
class ScrapingUrlDTO:
    """Data Transfer Object for ScrapingUrl."""

    id: int
    url: str
    name: str
    is_active: bool
    last_checked_at: str | None = None
    filters: dict | None = None

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
