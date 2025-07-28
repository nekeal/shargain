from __future__ import annotations

import dataclasses

from shargain.offers.application.actor import Actor
from shargain.offers.models import ScrapingUrl, ScrappingTarget


@dataclasses.dataclass
class AddScrapingUrlCommand:
    url: str
    target_id: int


@dataclasses.dataclass
class ScrapingUrlDTO:
    id: int
    url: str
    target_id: int

    @classmethod
    def from_orm(cls, url: ScrapingUrl) -> ScrapingUrlDTO:
        return cls(id=url.id, url=url.url, target_id=url.scraping_target_id)


def add_scraping_url(command: AddScrapingUrlCommand, actor: Actor) -> ScrapingUrlDTO:
    try:
        target = ScrappingTarget.objects.get(id=command.target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist:
        raise ValueError("Target does not exist")

    url = ScrapingUrl.objects.create(
        url=command.url,
        scraping_target=target,
        name=command.url,  # Use url as name for now
    )
    return ScrapingUrlDTO.from_orm(url)
