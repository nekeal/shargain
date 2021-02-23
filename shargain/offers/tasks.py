import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone

from shargain.celery import app
from shargain.offers.models import Offer


def is_offer_closed(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    offer_removed_box = soup.select("#offer_removed_by_user")
    if offer_removed_box:
        return url, True
    return url, False


@shared_task
def check_for_closed_offers():
    offers_to_check = Offer.objects.filter(closed_at=None)
    print("START CHECKING OFFERS")
    for offer in offers_to_check:
        url, closed = is_offer_closed(offer.url)
        print(url)
        if closed:
            print(f"{offer.url} is CLOSED")
            offer.closed_at = timezone.now()
            offer.save()
