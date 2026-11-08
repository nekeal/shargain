import logging
from collections.abc import Sequence
from dataclasses import dataclass

from shargain.offers.field_extraction import ExtractedOffer, ListUrl, OfferFieldResolver
from shargain.offers.filtering import OfferFilterService
from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FilterSnapshotResult:
    passed: list[ExtractedOffer]
    scraping_url_by_list_url: dict[str, ScrapingUrl]


class OfferFilterSnapshotService:
    def apply(self, offers: Sequence[Offer], target: ScrappingTarget) -> FilterSnapshotResult:
        if not offers:
            return FilterSnapshotResult(passed=[], scraping_url_by_list_url={})

        offers_by_url: dict[str, list[Offer]] = {}
        for offer in offers:
            offers_by_url.setdefault(offer.list_url or "", []).append(offer)

        scraping_url_by_list_url = self._fetch_scraping_urls_by_list_url(offers_by_url, target)

        passed_extracted: list[ExtractedOffer] = []
        updates_true: list[int] = []
        updates_false: list[int] = []

        for list_url, group_offers in offers_by_url.items():
            scraping_url = scraping_url_by_list_url.get(list_url)
            group_passed, ids_true, ids_false = self._process_group(group_offers, list_url, scraping_url, target)
            passed_extracted.extend(group_passed)
            updates_true.extend(ids_true)
            updates_false.extend(ids_false)

        self._persist_and_update_instances(offers, updates_true, updates_false)

        return FilterSnapshotResult(
            passed=passed_extracted,
            scraping_url_by_list_url=scraping_url_by_list_url,
        )

    @staticmethod
    def _fetch_scraping_urls_by_list_url(
        offers_by_url: dict[str, list[Offer]], target: ScrappingTarget
    ) -> dict[str, ScrapingUrl]:
        raw_scraping_urls = ScrapingUrl.objects.filter(
            url__in=list(offers_by_url.keys()), scraping_target=target
        ).order_by("pk")
        mapping: dict[str, ScrapingUrl] = {}
        for sc in raw_scraping_urls:
            if sc.url not in mapping:
                mapping[sc.url] = sc
        return mapping

    def _process_group(
        self,
        group_offers: list[Offer],
        list_url: str,
        scraping_url: ScrapingUrl | None,
        target: ScrappingTarget,
    ) -> tuple[list[ExtractedOffer], list[int], list[int]]:
        extracted_group = self._extract_group(group_offers, list_url)

        if not scraping_url or not scraping_url.filters:
            passed = [ext for _, ext in extracted_group]
            ids_true = [offer.id for offer, _ in extracted_group]
            return passed, ids_true, []

        return self._evaluate_filters(extracted_group, scraping_url, list_url, target)

    @staticmethod
    def _extract_group(group_offers: list[Offer], list_url: str) -> list[tuple[Offer, ExtractedOffer]]:
        extracted: list[tuple[Offer, ExtractedOffer]] = []
        for offer in group_offers:
            try:
                fields = OfferFieldResolver.extract(offer, ListUrl(list_url))
                extracted.append((offer, ExtractedOffer(_offer=offer, fields=fields)))
            except Exception:
                logger.exception(
                    "Field extraction failed for offer %s (list_url=%s); leaving passed_filters NULL",
                    offer.id,
                    list_url,
                )
        return extracted

    @staticmethod
    def _evaluate_filters(
        extracted_group: list[tuple[Offer, ExtractedOffer]],
        scraping_url: ScrapingUrl,
        list_url: str,
        target: ScrappingTarget,
    ) -> tuple[list[ExtractedOffer], list[int], list[int]]:
        try:
            filter_service = OfferFilterService(scraping_url.filters)
            filtered_passed_ext = filter_service.apply([ext for _, ext in extracted_group])
            passed_offer_ids = {ext._offer.id for ext in filtered_passed_ext}
            passed: list[ExtractedOffer] = []
            ids_true: list[int] = []
            ids_false: list[int] = []
            for offer, ext in extracted_group:
                if offer.id in passed_offer_ids:
                    ids_true.append(offer.id)
                    passed.append(ext)
                else:
                    ids_false.append(offer.id)
            return passed, ids_true, ids_false
        except Exception:
            logger.exception(
                "Filter evaluation failed for list_url %s (target %s); leaving passed_filters NULL",
                list_url,
                target.id,
            )
            return [], [], []

    @staticmethod
    def _persist_and_update_instances(
        offers: Sequence[Offer], updates_true: list[int], updates_false: list[int]
    ) -> None:
        if updates_true:
            Offer.objects.filter(id__in=updates_true).update(passed_filters=True)
        if updates_false:
            Offer.objects.filter(id__in=updates_false).update(passed_filters=False)

        set_true = set(updates_true)
        set_false = set(updates_false)
        for offer in offers:
            if offer.id in set_true:
                offer.passed_filters = True
            elif offer.id in set_false:
                offer.passed_filters = False
