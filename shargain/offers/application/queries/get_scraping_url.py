import dataclasses
from typing import Self

from shargain.offers.application.actor import Actor
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist
from shargain.offers.models import ScrapingUrl


@dataclasses.dataclass
class ScrapingUrlDTO:
    id: int
    url: str
    target_id: int

    @classmethod
    def from_orm(cls, url: ScrapingUrl) -> Self:
        return cls(id=url.pk, url=url.url, target_id=url.scraping_target_id)


def get_scraping_url(actor: Actor, url_id: int) -> ScrapingUrlDTO:
    """Retrieve a scraping URL by ID if the actor has permission.

    Args:
        actor: The actor performing the query
        url_id: ID of the URL to retrieve

    Returns:
        A dictionary containing the URL details if found and accessible.
    """
    try:
        url = ScrapingUrl.objects.get(id=url_id, scraping_target__owner=actor.user_id)
    except ScrapingUrl.DoesNotExist as e:
        raise ScrapingUrlDoesNotExist() from e

    return ScrapingUrlDTO.from_orm(url)
