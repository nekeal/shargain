from unittest.mock import patch

import pytest

from shargain.offers.field_extraction import OfferFieldResolver
from shargain.offers.services.filter_snapshot import OfferFilterSnapshotService
from shargain.offers.tests.factories import OfferFactory, ScrapingUrlFactory, ScrappingTargetFactory


@pytest.mark.django_db
class TestOfferFilterSnapshotService:
    def test_offers_matching_filters_get_passed_true(self):
        target = ScrappingTargetFactory()
        scraping_url = ScrapingUrlFactory(
            scraping_target=target,
            url="https://www.olx.pl/d/nieruchomosci/mieszkania/",
            filters={
                "ruleGroups": [
                    {
                        "rules": [
                            {"field": "price", "operator": "gte", "value": "1000"},
                            {"field": "price", "operator": "lte", "value": "3000"},
                        ]
                    }
                ]
            },
        )
        offer_pass = OfferFactory(
            target=target,
            list_url=scraping_url.url,
            price=2000,
            title="Apartment in budget",
        )
        offer_fail = OfferFactory(
            target=target,
            list_url=scraping_url.url,
            price=5000,
            title="Apartment too expensive",
        )

        service = OfferFilterSnapshotService()
        result = service.apply([offer_pass, offer_fail], target)

        assert offer_pass.passed_filters is True
        assert offer_fail.passed_filters is False

        offer_pass.refresh_from_db()
        offer_fail.refresh_from_db()

        assert offer_pass.passed_filters is True
        assert offer_fail.passed_filters is False
        assert [eo._offer.id for eo in result.passed] == [offer_pass.id]
        assert result.scraping_url_by_list_url[scraping_url.url].id == scraping_url.id

    def test_offer_without_matching_scraping_url_passes(self):
        target = ScrappingTargetFactory()
        offer = OfferFactory(target=target, list_url="https://unknown-url.com/feed", price=100)

        service = OfferFilterSnapshotService()
        result = service.apply([offer], target)

        assert offer.passed_filters is True
        offer.refresh_from_db()
        assert offer.passed_filters is True
        assert len(result.passed) == 1
        assert result.passed[0]._offer.id == offer.id

    def test_offer_with_scraping_url_having_no_filters_passes(self):
        target = ScrappingTargetFactory()
        scraping_url = ScrapingUrlFactory(
            scraping_target=target,
            url="https://www.olx.pl/d/nieruchomosci/mieszkania/",
            filters=None,
        )
        offer = OfferFactory(target=target, list_url=scraping_url.url, price=100)

        service = OfferFilterSnapshotService()
        result = service.apply([offer], target)

        assert offer.passed_filters is True
        offer.refresh_from_db()
        assert offer.passed_filters is True
        assert len(result.passed) == 1

    def test_duplicate_scraping_urls_selects_lowest_pk(self):
        target = ScrappingTargetFactory()
        url = "https://www.olx.pl/d/nieruchomosci/mieszkania/"
        sc_first = ScrapingUrlFactory(
            scraping_target=target,
            url=url,
            filters={
                "ruleGroups": [{"rules": [{"field": "price", "operator": "gte", "value": "500"}]}],
            },
        )
        sc_second = ScrapingUrlFactory(
            scraping_target=target,
            url=url,
            filters={
                "ruleGroups": [{"rules": [{"field": "price", "operator": "gte", "value": "9999"}]}],
            },
        )

        offer = OfferFactory(target=target, list_url=url, price=1000)

        service = OfferFilterSnapshotService()
        result = service.apply([offer], target)

        lowest_pk = min(sc_first.id, sc_second.id)
        assert result.scraping_url_by_list_url[url].id == lowest_pk
        assert offer.passed_filters is True
        offer.refresh_from_db()
        assert offer.passed_filters is True

    def test_extraction_error_leaves_null_and_omits_from_passed(self):
        target = ScrappingTargetFactory()
        url = "https://www.olx.pl/d/nieruchomosci/mieszkania/"
        ScrapingUrlFactory(scraping_target=target, url=url, filters=None)
        offer_ok = OfferFactory(target=target, list_url=url, price=1000)
        offer_err = OfferFactory(target=target, list_url=url, price=2000)

        original_extract = OfferFieldResolver.extract

        def side_effect(offer, list_url):
            if offer.id == offer_err.id:
                raise RuntimeError("Extraction boom")
            return original_extract(offer, list_url)

        with patch.object(OfferFieldResolver, "extract", side_effect=side_effect):
            service = OfferFilterSnapshotService()
            result = service.apply([offer_ok, offer_err], target)

        assert offer_ok.passed_filters is True
        assert offer_err.passed_filters is None

        offer_ok.refresh_from_db()
        offer_err.refresh_from_db()

        assert offer_ok.passed_filters is True
        assert offer_err.passed_filters is None
        assert [eo._offer.id for eo in result.passed] == [offer_ok.id]

    def test_filter_error_leaves_null_and_omits_from_passed(self):
        target = ScrappingTargetFactory()
        url = "https://www.olx.pl/d/nieruchomosci/mieszkania/"
        ScrapingUrlFactory(
            scraping_target=target,
            url=url,
            filters={
                "ruleGroups": [
                    {
                        "rules": [
                            {"field": "price", "operator": "unknown_op", "value": "100"},
                        ]
                    }
                ]
            },
        )
        offer = OfferFactory(target=target, list_url=url, price=1000)

        service = OfferFilterSnapshotService()
        result = service.apply([offer], target)

        assert offer.passed_filters is None
        offer.refresh_from_db()
        assert offer.passed_filters is None
        assert result.passed == []

    def test_empty_offers_returns_empty_result(self):
        target = ScrappingTargetFactory()
        service = OfferFilterSnapshotService()
        result = service.apply([], target)

        assert result.passed == []
        assert result.scraping_url_by_list_url == {}
