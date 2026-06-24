import logging
from collections import Counter

from opentelemetry import trace

from shargain.notifications.services.notifications import NewOfferNotificationService
from shargain.offers.application.commands.record_checkin import record_checkin
from shargain.offers.application.dto import WaypointData
from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget
from shargain.offers.serializers import OfferBatchCreateSerializer
from shargain.offers.services.geo_utils import haversine
from shargain.offers.signals import offers_batch_created
from shargain.quotas.services.quota import QuotaService

logger = logging.getLogger(__name__)


class OfferBatchCreateService:
    serializer_class = OfferBatchCreateSerializer
    notification_service_class = NewOfferNotificationService

    def __init__(self, serializer_kwargs: dict, notify: bool = True):
        self._serializer_kwargs = serializer_kwargs

    def run(self):
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("batch_create.run") as span:
            serializer = self.serializer_class(**self._serializer_kwargs)
            serializer.is_valid(raise_exception=True)
            target = serializer.validated_data["target"]
            span.set_attribute("target.id", str(target.id))
            if target.owner_id and not QuotaService.check_can_create_offers(
                user_id=target.owner_id, target_id=target.id
            ):
                return []
            offers: list[tuple[Offer, bool]] = self.create(serializer.validated_data)
            new_offers = [r[0] for r in filter(lambda x: x[1], offers)]
            span.set_attribute("offers.total", len(offers))
            span.set_attribute("offers.new", len(new_offers))
            self._notify(new_offers, target)

            self._record_checkins(serializer.validated_data["offers"], offers, target)
            if target.owner_id and new_offers:
                offers_batch_created.send(
                    sender=self.__class__,
                    user_id=target.owner_id,
                    target_id=target.id,
                    count=len(new_offers),
                )

            return [offer.url for offer in new_offers]

    @staticmethod
    def simplify_url(url):  # currently not used
        if "olx.pl" in url:
            return url.rsplit("#")[0]
        return url

    def create(self, validated_data) -> list[tuple[Offer, bool]]:
        tracer = trace.get_tracer(__name__)
        offers: list[tuple[Offer, bool]] = []
        for offer_data in validated_data["offers"]:
            offer_url = offer_data.pop("url")
            with tracer.start_as_current_span("batch_create.create_offer") as child:
                child.set_attribute("offer.url", offer_url)
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
                child.set_attribute("offer.created", created)
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
        if not (new_offers and scrapping_target.notification_config and scrapping_target.enable_notifications):
            return

        from shargain.notifications.services.notifications import NotificationMessageContext
        from shargain.offers.services.filter_service import OfferFilterService
        from shargain.offers.services.location_parsers import LocationParserFactory

        # Group offers by their list_url (the scraping URL)
        offers_by_url: dict[str, list[Offer]] = {}
        for offer in new_offers:
            offers_by_url.setdefault(offer.list_url, []).append(offer)

        # Log to verify if all offers have the same list_url
        unique_urls = list(offers_by_url.keys())
        logger.info(
            "BatchCreateService._notify received offers with %s unique list_urls: %s",
            len(unique_urls),
            unique_urls,
        )

        # Fetch all relevant ScrapingUrl objects in a single query (prevents N+1)
        scraping_urls = ScrapingUrl.objects.filter(url__in=unique_urls, scraping_target=scrapping_target)
        url_to_config_map = {sc_url.url: sc_url for sc_url in scraping_urls}

        # Apply filters and send notifications per URL
        for list_url, url_offers in offers_by_url.items():
            scraping_url = url_to_config_map.get(list_url)

            # Apply filters
            filtered_offers = url_offers
            if scraping_url and scraping_url.filters:
                filter_service = OfferFilterService(scraping_url.filters)
                filtered_offers = filter_service.apply_filters(url_offers)

            if not filtered_offers:
                continue

            # Parse location if opted-in
            message_contexts = []
            show_location = scraping_url.show_location_map_in_notifications if scraping_url else False

            waypoints: list[WaypointData] | None = scraping_url.waypoints if scraping_url else None  # type: ignore[assignment]

            for offer in filtered_offers:
                map_url, location_name, is_exact = None, None, False
                distances: list[tuple[str, float]] = []
                if show_location:
                    parser = LocationParserFactory.get_parser(offer.domain, offer.metadata)
                    map_url = parser.get_map_url()
                    location_name = parser.get_location_name()
                    is_exact = parser.is_location_exact()

                    coords = parser.get_coordinates()
                    if coords and waypoints:
                        distances = [
                            (
                                str(wp["name"]),
                                haversine(coords.lat, coords.lon, wp["lat"], wp["lon"]),
                            )
                            for wp in waypoints
                        ]

                message_contexts.append(
                    NotificationMessageContext(
                        offer=offer,
                        map_url=map_url,
                        location_name=location_name,
                        is_exact_location=is_exact,
                        distances=distances,
                    )
                )

            # Call notification service per group
            self.notification_service_class(message_contexts, scrapping_target).run()
