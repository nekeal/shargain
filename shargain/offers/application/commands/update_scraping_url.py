from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import ScrapingUrlDTO
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist
from shargain.offers.models import ScrapingUrl


def update_scraping_url(actor: Actor, url_id: int, name: str) -> ScrapingUrlDTO:
    try:
        url = ScrapingUrl.objects.get(id=url_id, scraping_target__owner=actor.user_id)
    except ScrapingUrl.DoesNotExist as e:
        raise ScrapingUrlDoesNotExist() from e

    url.name = name
    url.save(update_fields=["name"])
    return ScrapingUrlDTO.from_orm(url)
