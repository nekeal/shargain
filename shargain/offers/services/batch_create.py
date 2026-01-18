import logging
from collections import Counter

from shargain.notifications.services.notifications import NewOfferNotificationService
from shargain.offers.application.commands.record_checkin import record_checkin
from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget
from shargain.offers.serializers import OfferBatchCreateSerializer

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
    def simplify_url(url):  # currently not used
        if "olx.pl" in url:
            return url.rsplit("#")[0]
        return url

    def create(self, validated_data) -> list[tuple[Offer, bool]]:
        offers: list[tuple[Offer, bool]] = []
        for offer_data in validated_data["offers"]:
            offer_url = offer_data.pop("url")
            try:
                offer, created = Offer.objects.get_or_create(
                    url=offer_url,
                    target=validated_data["target"],
                    defaults=offer_data,
                )
            except Offer.MultipleObjectsReturned:
                offer, created = (
                    Offer.objects.filter(url=offer_url, target=validated_data["target"]).first(),  # type: ignore[assignment]
                    False,
                )
            offers.append((offer, created))
        return offers

    @staticmethod
    def _record_checkins(offers_data: list, created_offers: list[tuple[Offer, bool]], target: ScrappingTarget):
        """
        Record checkins for scraping URLs based on the list_url field of offers.
        """
        offers_count = Counter(offer.get("list_url") for offer in offers_data if offer.get("list_url"))
        new_offers_count = Counter([offer.list_url for offer, created in created_offers if created and offer.list_url])

        for list_url, count in offers_count.items():
            if not (
                scraping_url := ScrapingUrl.objects.filter(
                    url=list_url, scraping_target=target
                ).first()  # it's first instead of get because we don't care if user has duplicated urls
            ):
                logger.warning("Scraping URL %s does not exist for target %s", list_url, target)
                continue
            record_checkin(
                scraping_url_id=scraping_url.id,
                offers_count=count,
                new_offers_count=new_offers_count.get(list_url, 0),
            )

    def _notify(self, new_offers, scrapping_target):
        if new_offers and scrapping_target.notification_config and scrapping_target.enable_notifications:
            # Apply filters per scraping URL
            filtered_offers = self._apply_filters_by_url(new_offers, scrapping_target)

            if filtered_offers:
                self.notification_service_class(filtered_offers, scrapping_target).run()

    def _apply_filters_by_url(self, offers: list[Offer], scrapping_target: ScrappingTarget) -> list[Offer]:
        """Apply filters grouped by scraping URL.

        Args:
            offers: List of offers to filter
            scrapping_target: The scrapping target containing the offers

        Returns:
            List of filtered offers that pass all configured filters
        """
        from shargain.offers.services.filter_service import OfferFilterService

        # Group offers by their list_url (the scraping URL)
        offers_by_url: dict[str, list[Offer]] = {}
        for offer in offers:
            if offer.list_url not in offers_by_url:
                offers_by_url[offer.list_url] = []
            offers_by_url[offer.list_url].append(offer)

        # Fetch all relevant ScrapingUrl objects in a single query (prevents N+1)
        urls_to_fetch = offers_by_url.keys()
        scraping_urls = ScrapingUrl.objects.filter(url__in=urls_to_fetch, scraping_target=scrapping_target)
        url_to_filters_map = {sc_url.url: sc_url.filters for sc_url in scraping_urls}

        # Apply filters per URL
        filtered_offers = []
        for list_url, url_offers in offers_by_url.items():
            filters = url_to_filters_map.get(list_url)

            if filters:
                # Filters configured - apply them
                filter_service = OfferFilterService(filters)
                filtered_offers.extend(filter_service.apply_filters(url_offers))
            else:
                # No filters configured = include all offers
                filtered_offers.extend(url_offers)

        return filtered_offers
