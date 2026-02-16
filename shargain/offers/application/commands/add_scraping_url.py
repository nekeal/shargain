from __future__ import annotations

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import ScrapingUrlDTO
from shargain.offers.application.exceptions import QuotaExceeded, TargetDoesNotExist
from shargain.offers.models import ScrapingUrl, ScrappingTarget
from shargain.quotas.services.quota import QuotaService


def add_scraping_url(
    actor: Actor,
    url: str,
    target_id: int,
    name: str | None = None,
    filters: dict | None = None,
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
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as e:
        raise TargetDoesNotExist() from e

    if not QuotaService.check_can_add_url(user_id=actor.user_id, target_id=target.id):
        raise QuotaExceeded()

    scraping_url = ScrapingUrl.objects.create(url=url, scraping_target=target, name=name or "", filters=filters)
    return ScrapingUrlDTO.from_orm(scraping_url)
