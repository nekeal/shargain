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

    @classmethod
    def from_orm(cls, url: ScrapingUrl) -> Self:
        """Create a DTO from a ScrapingUrl model instance."""
        return cls(id=url.id, url=url.url, name=url.name, is_active=url.is_active)


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
    def from_orm(cls, target: ScrappingTarget) -> Self:
        """Create a DTO from a ScrappingTarget model instance."""
        urls = [ScrapingUrlDTO.from_orm(url) for url in target.scrapingurl_set.all()]
        return cls(
            id=target.id,
            name=target.name,
            is_active=target.is_active,
            enable_notifications=target.enable_notifications,
            notification_config_id=target.notification_config_id,
            urls=urls,
        )
