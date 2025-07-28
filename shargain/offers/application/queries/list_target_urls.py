from __future__ import annotations

import dataclasses

from shargain.offers.application.actor import Actor
from shargain.offers.models import ScrapingUrl


@dataclasses.dataclass
class ListTargetUrlsQuery:
    target_id: int


@dataclasses.dataclass
class ScrapingUrlDTO:
    id: int
    url: str

    @classmethod
    def from_orm(cls, url: ScrapingUrl) -> ScrapingUrlDTO:
        return cls(id=url.id, url=url.url)


def list_target_urls(query: ListTargetUrlsQuery, actor: Actor) -> list[ScrapingUrlDTO]:
    urls = ScrapingUrl.objects.filter(scraping_target_id=query.target_id, scraping_target__owner=actor.user_id)
    return [ScrapingUrlDTO.from_orm(url) for url in urls]
