from shargain.commons.application.actor import Actor
from shargain.offers.application.access import can_manage_urls
from shargain.offers.application.dto import ScrapingUrlDTO
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist, TargetPermissionDenied
from shargain.offers.models import ScrapingUrl


def set_scraping_url_active_status(actor: Actor, url_id: int, target_id: int, is_active: bool) -> ScrapingUrlDTO:
    """
    Sets the active status of a scraping URL.
    """
    try:
        url = (
            ScrapingUrl.objects.for_user(actor.user_id)
            .select_related("scraping_target")
            .get(id=url_id, scraping_target__id=target_id)
        )
    except ScrapingUrl.DoesNotExist as e:
        raise ScrapingUrlDoesNotExist() from e

    if not can_manage_urls(actor.user_id, url.scraping_target):
        raise TargetPermissionDenied()

    url.is_active = is_active
    url.save(update_fields=["is_active"])
    return ScrapingUrlDTO.from_orm(url)
