import logging
from collections import Counter

from opentelemetry import trace

from shargain.notifications.services.notifications import NewOfferNotificationService, NotificationMessageContext
from shargain.offers.application.commands.record_checkin import record_checkin
from shargain.offers.field_extraction import ExtractedFieldEntry, ExtractedOffer
from shargain.offers.geo import Coordinates
from shargain.offers.location_parsers import LocationParserFactory
from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget
from shargain.offers.serializers import OfferBatchCreateSerializer
from shargain.offers.services.filter_snapshot import FilterSnapshotResult, OfferFilterSnapshotService
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
            snapshot_result = OfferFilterSnapshotService().apply(new_offers, target)
            self._notify(snapshot_result, target)

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
        target = validated_data["target"]
        offers_data_list = validated_data["offers"]

        seen_urls: set[str] = set()
        urls: list[str] = []
        all_offer_data: list[dict] = []
        for offer_data in offers_data_list:
            url = offer_data.pop("url")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            urls.append(url)
            all_offer_data.append(offer_data)

        with tracer.start_as_current_span("batch_create.create_offer") as span:
            existing_urls = set(Offer.objects.filter(url__in=urls, target=target).values_list("url", flat=True))

            new_offers = [
                Offer(url=url, target=target, **data)
                for url, data in zip(urls, all_offer_data, strict=True)
                if url not in existing_urls
            ]
            if new_offers:
                Offer.objects.bulk_create(new_offers, ignore_conflicts=False)

            all_instances = Offer.objects.filter(url__in=urls, target=target)
            url_to_offer = {o.url: o for o in all_instances}

            results: list[tuple[Offer, bool]] = []
            for url in urls:
                offer = url_to_offer[url]
                created = url not in existing_urls
                results.append((offer, created))

            span.set_attribute("offers.total", len(results))
            span.set_attribute("offers.created", sum(1 for _, c in results if c))

        return results

    @staticmethod
    def _record_checkins(offers_data: list, created_offers: list[tuple[Offer, bool]], target: ScrappingTarget):
        """
        Record checkins for scraping URLs based on the list_url field of offers.
        """
        offers_count = Counter(offer.get("list_url") for offer in offers_data if offer.get("list_url"))
        new_offers_count = Counter([offer.list_url for offer, created in created_offers if created and offer.list_url])

        for list_url, count in offers_count.items():
            if not (
                scraping_url := ScrapingUrl.objects.filter(url=list_url, scraping_target=target)
                .order_by("pk")
                .first()  # it's first instead of get because we don't care if user has duplicated urls
            ):
                logger.warning("Scraping URL %s does not exist for target %s", list_url, target)
                continue
            record_checkin(
                scraping_url_id=scraping_url.id,
                offers_count=count,
                new_offers_count=new_offers_count.get(list_url, 0),
            )

    def _notify(self, snapshot_result: FilterSnapshotResult, scrapping_target: ScrappingTarget):
        if not snapshot_result.passed:
            return

        if not (scrapping_target.notification_config and scrapping_target.enable_notifications):
            logger.debug(
                "Skipping notifications for target %s (config=%s, enabled=%s)",
                scrapping_target.id,
                scrapping_target.notification_config_id,
                scrapping_target.enable_notifications,
            )
            return

        # Group passing ExtractedOffers by list_url
        by_list_url: dict[str, list[ExtractedOffer]] = {}
        for ext in snapshot_result.passed:
            by_list_url.setdefault(ext._offer.list_url or "", []).append(ext)

        message_contexts: list[NotificationMessageContext] = []
        for list_url, ext_offers in by_list_url.items():
            scraping_url = snapshot_result.scraping_url_by_list_url.get(list_url)
            contexts = self._build_contexts(ext_offers, scraping_url)
            message_contexts.extend(contexts)

        span = trace.get_current_span()
        span.set_attribute("notifications.offers_in", len(snapshot_result.passed))
        span.set_attribute("notifications.offers_after_filters", len(snapshot_result.passed))
        span.set_attribute("notifications.messages", len(message_contexts))

        if not message_contexts:
            return

        notification_title = self._get_notification_title(
            list(snapshot_result.scraping_url_by_list_url.values()),
            scrapping_target,
            list(by_list_url.keys()),
        )
        self.notification_service_class(message_contexts, scrapping_target, notification_title=notification_title).run()

    @staticmethod
    def _build_contexts(extracted_offers, scraping_url):
        selected = set()
        if scraping_url and scraping_url.notification_fields:
            selected = set(scraping_url.notification_fields.fields)

        show_location = scraping_url.show_location_map_in_notifications if scraping_url else False
        send_map = scraping_url.send_map_in_notifications if scraping_url else True
        waypoints = scraping_url.waypoints if scraping_url else None

        contexts = []
        for extracted in extracted_offers:
            map_url, location_name, is_exact, coords = None, None, False, None
            distances = []
            if show_location:
                # TODO: Move domain/metadata to ExtractedOffer.fields when plugins extract them
                parser = LocationParserFactory.get_parser(extracted.domain, extracted.metadata)
                map_center = Coordinates(lat=waypoints[0]["lat"], lon=waypoints[0]["lon"]) if waypoints else None
                map_url = parser.get_map_url(map_center=map_center)
                location_name = parser.get_location_name()
                is_exact = parser.is_location_exact()
                coords = parser.get_coordinates()
                if coords and waypoints:
                    distances = [
                        (str(wp["name"]), haversine(coords.lat, coords.lon, wp["lat"], wp["lon"])) for wp in waypoints
                    ]

            contexts.append(
                NotificationMessageContext(
                    offer=extracted._offer,
                    map_url=map_url,
                    location_name=location_name,
                    is_exact_location=is_exact,
                    distances=distances,
                    coordinates=coords,
                    send_map=send_map,
                    extracted_fields=[
                        ExtractedFieldEntry(name=k, value=v) for k, v in extracted.fields.items() if k in selected
                    ],
                )
            )
        return contexts

    @staticmethod
    def _get_notification_title(scraping_urls, scrapping_target, list_urls):
        url_map = {sc.url: sc for sc in scraping_urls}
        if list_urls and list_urls[0] in url_map and url_map[list_urls[0]].name:
            return url_map[list_urls[0]].name
        return scrapping_target.name
