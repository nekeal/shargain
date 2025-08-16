from shargain.commons.application.actor import Actor
from shargain.offers.models import ScrapingUrl


def delete_scraping_url(actor: Actor, url_id: int) -> None:
    """Delete a scraping URL by ID if the actor has permission.

    Args:
        actor: The actor performing the action
        url_id: ID of the URL to delete
    """
    try:
        url = ScrapingUrl.objects.get(id=url_id, scraping_target__owner=actor.user_id)
    except ScrapingUrl.DoesNotExist:
        return
    url.delete()
