import logging
from datetime import timedelta
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.db import transaction
from django.db.models import BooleanField, ExpressionWrapper, Q
from django.utils import timezone

from shargain.offers.models import Offer

logger = logging.getLogger(__name__)


def is_olx_offer_closed(response):
    if response.url.endswith("#from404"):
        return True
    soup = BeautifulSoup(response.content, "html.parser")
    offer_removed_box = soup.select("#offer_removed_by_user")
    if offer_removed_box:
        return True
    return False


def is_otomoto_offer_closed(response):
    if response.status_code == 404:
        return True
    return False


def is_offer_closed(url):
    try:
        response = requests.get(url)
    except ConnectionResetError:
        logger.exception(f"Connection error for {url}")
        return url, None, False
    if "olx.pl" in url:
        return url, response, is_olx_offer_closed(response)
    if "otomoto.pl" in url:
        return url, response, is_otomoto_offer_closed(response)
    return url, response, False


@shared_task
def check_for_closed_offers():
    offers_to_check = Offer.objects.filter(closed_at=None)
    print("START CHECKING OFFERS")
    for offer in offers_to_check:
        url, response, closed = is_offer_closed(offer.url)
        print(url)
        offer.source_html.save("", BytesIO(response.content))
        if closed:
            print(f"{offer.url} is CLOSED")
            offer.closed_at = timezone.now()
        offer.save()


@shared_task
@transaction.atomic()
def get_offer_source_html(pk=None):
    if pk:
        return
    if not pk:
        offer = (
            Offer.objects.select_for_update(skip_locked=True)
            .filter(created_at__gte=timezone.localtime() - timedelta(days=31))
            .opened()
            .annotate(
                source_html_exists=ExpressionWrapper(
                    ~Q(source_html=""), output_field=BooleanField()
                )
            )
            .order_by("source_html_exists", "last_check_at")[0]
        )
    logger.info("Checking offer [id=%s]", offer.id)
    response = requests.get(offer.url)
    if response.status_code == 403:
        logger.error("Url [url=%s] returned 403 status code", offer.url)
    offer.source_html.save("", BytesIO(response.content), save=False)
    offer.last_check_at = timezone.localtime()
    offer.save(update_fields=["last_check_at", "source_html"])
    logger.info("Offer [id=%s] updated succesfully", offer.id)
