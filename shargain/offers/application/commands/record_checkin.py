from django.core.exceptions import ObjectDoesNotExist

from shargain.offers.models import ScrapingCheckin, ScrapingUrl


def record_checkin(scraping_url_id: int, offers_count: int, new_offers_count: int) -> ScrapingCheckin:
    """
    Records a check-in for a scraping URL.

    Args:
        scraping_url_id: The ID of the ScrapingUrl object.
        offers_count: The total number of offers received in this check-in.
        new_offers_count: The number of new offers received in this check-in.

    Returns:
        The created ScrapingCheckin object.

    Raises:
        ObjectDoesNotExist: If the ScrapingUrl with the given ID does not exist.
    """
    try:
        scraping_url = ScrapingUrl.objects.get(id=scraping_url_id)
    except ScrapingUrl.DoesNotExist:
        raise ObjectDoesNotExist(f"ScrapingUrl with id {scraping_url_id} does not exist") from None

    checkin = ScrapingCheckin.objects.create(
        scraping_url=scraping_url, offers_count=offers_count, new_offers_count=new_offers_count
    )

    return checkin
