from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import ScrapingUrlDTO
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist
from shargain.offers.models import ScrapingUrl


def set_scraping_url_active_status(actor: Actor, url_id: int, target_id: int, is_active: bool) -> ScrapingUrlDTO:
    """
    Sets the active status of a scraping URL.
    """
    try:
        url = ScrapingUrl.objects.get(id=url_id, scraping_target__id=target_id, scraping_target__owner=actor.user_id)
    except ScrapingUrl.DoesNotExist as e:
        raise ScrapingUrlDoesNotExist() from e

    url.is_active = is_active
    url.save(update_fields=["is_active"])
    return ScrapingUrlDTO.from_orm(url)
