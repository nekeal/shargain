from shargain.commons.application.actor import Actor
from shargain.offers.application.access import can_manage_urls
from shargain.offers.application.exceptions import TargetPermissionDenied
from shargain.offers.models import ScrapingUrl


def delete_scraping_url(actor: Actor, url_id: int, target_id: int | None = None) -> None:
    """Delete a scraping URL by ID if the actor has permission.

    Args:
        actor: The actor performing the action
        url_id: ID of the URL to delete
        target_id: Optional ID of the target the URL must belong to
    """
    filters = {"id": url_id}
    if target_id is not None:
        filters["scraping_target_id"] = target_id
    try:
        url = ScrapingUrl.objects.for_user(actor.user_id).select_related("scraping_target").get(**filters)
    except ScrapingUrl.DoesNotExist:
        return

    if not can_manage_urls(actor.user_id, url.scraping_target):
        raise TargetPermissionDenied()

    url.delete()
