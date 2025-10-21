import logging
from collections import Counter

from shargain.notifications.services.notifications import NewOfferNotificationService
from shargain.offers.application.commands.record_checkin import record_checkin
from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget
from shargain.offers.serializers import OfferBatchCreateSerializer
from shargain.offers.services.quota import QuotaService

logger = logging.getLogger(__name__)


class OfferBatchCreateService:
    serializer_class = OfferBatchCreateSerializer
    notification_service_class = NewOfferNotificationService

    def __init__(self, serializer_kwargs: dict, notify: bool = True):
        self._serializer_kwargs = serializer_kwargs

    def run(self):
        serializer = self.serializer_class(**self._serializer_kwargs)
        serializer.is_valid(raise_exception=True)
        offers: list[tuple[Offer, bool]] = self.create(serializer.validated_data)
        new_offers = [r[0] for r in filter(lambda x: x[1], offers)]
        self._notify(new_offers, serializer.validated_data["target"])

        self._record_checkins(serializer.validated_data["offers"], offers, serializer.validated_data["target"])

        return [offer.url for offer in new_offers]

    @staticmethod
    def simplify_url(url):
        if "olx.pl" in url:
            return url.rsplit("#")[0]
        return url

    def create(self, validated_data) -> list[tuple[Offer, bool]]:
        offers: list[tuple[Offer, bool]] = []
        target: ScrappingTarget = validated_data["target"]

        for offer_data in validated_data["offers"]:
            offer_url: str = offer_data.pop("url")
            try:
                existing_offer = Offer.objects.filter(url=offer_url, target=target).first()

                if existing_offer:
                    offers.append((existing_offer, False))
                else:
                    if QuotaService.is_quota_available(target):
                        offer, created = Offer.objects.get_or_create(
                            url=offer_url,
                            target=target,
                            defaults=offer_data,
                        )

                        if created:
                            quota = QuotaService.get_active_quota(target)
                            QuotaService.increment_usage(quota.id)

                        offers.append((offer, created))
                    else:
                        continue

            except Offer.MultipleObjectsReturned:
                if existing_offer := Offer.objects.filter(url=offer_url, target=target).first():
                    offers.append((offer, False))
        return offers

    @staticmethod
    def _record_checkins(offers_data: list, created_offers: list[tuple[Offer, bool]], target: ScrappingTarget):
        """Record checkins for scraping URLs."""
        offers_count = Counter(offer.get("list_url") for offer in offers_data if offer.get("list_url"))
        new_offers_count = Counter([offer.list_url for offer, created in created_offers if created and offer.list_url])

        for list_url, count in offers_count.items():
            if not (scraping_url := ScrapingUrl.objects.filter(url=list_url, scraping_target=target).first()):
                logger.warning("Scraping URL %s does not exist for target %s", list_url, target)
                continue
            record_checkin(
                scraping_url_id=scraping_url.id,
                offers_count=count,
                new_offers_count=new_offers_count.get(list_url, 0),
            )

    def _notify(self, new_offers, scrapping_target):
        if new_offers and scrapping_target.notification_config and scrapping_target.enable_notifications:
            self.notification_service_class(new_offers, scrapping_target).run()
