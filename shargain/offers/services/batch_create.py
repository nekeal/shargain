import logging
from collections import Counter

from opentelemetry import trace

from shargain.notifications.services.notifications import NewOfferNotificationService, NotificationMessageContext
from shargain.offers.application.commands.record_checkin import record_checkin
from shargain.offers.field_extraction import ExtractedFieldEntry, ExtractedOffer, ListUrl, OfferFieldResolver
from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget
from shargain.offers.serializers import OfferBatchCreateSerializer
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
        target = validated_data["target"]
        offers_data_list = validated_data["offers"]

        urls: list[str] = []
        all_offer_data: list[dict] = []
        for offer_data in offers_data_list:
            url = offer_data.pop("url")
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

        offers_by_url = self._group_by_url(new_offers)
        scraping_urls = self._fetch_scraping_urls(offers_by_url.keys(), scrapping_target)
        url_to_config_map = {sc.url: sc for sc in scraping_urls}

        message_contexts: list[NotificationMessageContext] = []
        for list_url, url_offers in offers_by_url.items():
            scraping_url = url_to_config_map.get(list_url)

            extracted = self._extract_offers(url_offers, list_url)
            filtered = self._filter_offers(extracted, scraping_url)
            if not filtered:
                continue

            contexts = self._build_contexts(filtered, scraping_url)
            message_contexts.extend(contexts)

        if not message_contexts:
            return

        notification_title = self._get_notification_title(scraping_urls, scrapping_target, list(offers_by_url.keys()))
        self.notification_service_class(message_contexts, scrapping_target, notification_title=notification_title).run()

    @staticmethod
    def _group_by_url(offers):
        offers_by_url: dict[str, list[Offer]] = {}
        for offer in offers:
            offers_by_url.setdefault(offer.list_url, []).append(offer)
        return offers_by_url

    @staticmethod
    def _fetch_scraping_urls(list_urls, scrapping_target):
        return list(ScrapingUrl.objects.filter(url__in=list(list_urls), scraping_target=scrapping_target))

    @staticmethod
    def _extract_offers(offers, list_url):
        return [
            ExtractedOffer(
                _offer=offer,
                fields=OfferFieldResolver.extract(offer, ListUrl(list_url)),
            )
            for offer in offers
        ]

    @staticmethod
    def _filter_offers(extracted_offers, scraping_url):
        if not scraping_url or not scraping_url.filters:
            return extracted_offers
        from shargain.offers.filtering import OfferFilterService

        return OfferFilterService(scraping_url.filters).apply(extracted_offers)

    @staticmethod
    def _build_contexts(extracted_offers, scraping_url):
        from shargain.offers.services.location_parsers import LocationParserFactory

        selected = set()
        if scraping_url and scraping_url.notification_fields:
            selected = set(scraping_url.notification_fields.fields)

        show_location = scraping_url.show_location_map_in_notifications if scraping_url else False
        waypoints = scraping_url.waypoints if scraping_url else None

        contexts = []
        for extracted in extracted_offers:
            map_url, location_name, is_exact = None, None, False
            distances = []
            if show_location:
                # TODO: Move domain/metadata to ExtractedOffer.fields when plugins extract them
                parser = LocationParserFactory.get_parser(extracted.domain, extracted.metadata)
                map_url = parser.get_map_url()
                location_name = parser.get_location_name()
                is_exact = parser.is_location_exact()
                coords = parser.get_coordinates()
                if coords and waypoints:
                    from shargain.offers.services.geo_utils import haversine

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
