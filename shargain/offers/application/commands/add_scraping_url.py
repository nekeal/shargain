from __future__ import annotations

from shargain.offers.application.actor import Actor
from shargain.offers.application.dto import ScrapingUrlDTO
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.models import ScrapingUrl, ScrappingTarget


def add_scraping_url(actor: Actor, url: str, target_id: int, name: str | None = None) -> ScrapingUrlDTO:
    """
    Adds a new scraping URL to the specified target.
    """
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e

    scraping_url = ScrapingUrl.objects.create(url=url, scraping_target=target, name=name or "")
    return ScrapingUrlDTO.from_orm(scraping_url)
