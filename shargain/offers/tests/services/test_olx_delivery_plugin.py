"""Tests for OlxDeliveryPlugin."""

from shargain.offers.field_extraction import FieldType, ListUrl
from shargain.offers.field_extraction.plugins.olx_delivery import olx_delivery
from shargain.offers.tests.factories import OfferFactory

OLX_URL = ListUrl("https://www.olx.pl/d/oferta/msi-rtx-4060ti-16gb-gaming-slim-CID99-ID1bISYm.html")


def _extra(**kwargs):
    return {"extra": kwargs}


class TestOlxDeliveryPluginMatches:
    def test_matches_olx_detail_url(self):
        assert olx_delivery.matches(OLX_URL) is True

    def test_matches_olx_listing_url(self):
        assert olx_delivery.matches(ListUrl("https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/krakow/")) is True

    def test_matches_olx_subdomain(self):
        assert olx_delivery.matches(ListUrl("https://sub.olx.pl/foo")) is True

    def test_not_matches_bare_olx_domain(self):
        # OLX URLs always carry www in practice; the bare domain is not matched
        assert olx_delivery.matches(ListUrl("https://olx.pl/oferty/")) is False

    def test_not_matches_lookalike_domains(self):
        assert olx_delivery.matches(ListUrl("https://notolx.pl/foo")) is False
        assert olx_delivery.matches(ListUrl("https://olx.pl.evil.com/foo")) is False

    def test_not_matches_other_domains(self):
        assert olx_delivery.matches(ListUrl("https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie")) is False
        assert olx_delivery.matches(ListUrl("https://example.com/")) is False


class TestOlxDeliveryPluginFields:
    def test_fields_listed(self):
        names = [f.name for f in olx_delivery.fields]
        assert names == ["olx_delivery"]

    def test_field_is_boolean(self):
        field = olx_delivery.fields[0]
        assert field.field_type == FieldType.BOOLEAN


class TestOlxDeliveryPluginExtract:
    def test_delivery_available(self):
        offer = OfferFactory.build(
            metadata=_extra(delivery={"rock": {"mode": "BuyWithDelivery", "active": True, "offer_id": "abc"}})
        )
        assert olx_delivery.extract(offer, OLX_URL)["olx_delivery"] is True

    def test_delivery_not_eligible(self):
        offer = OfferFactory.build(
            metadata=_extra(delivery={"rock": {"mode": "NotEligible", "active": False, "offer_id": None}})
        )
        assert olx_delivery.extract(offer, OLX_URL)["olx_delivery"] is False

    def test_missing_delivery_returns_none(self):
        offer = OfferFactory.build(metadata=_extra())
        assert olx_delivery.extract(offer, OLX_URL)["olx_delivery"] is None

    def test_missing_extra_returns_none(self):
        offer = OfferFactory.build(metadata={})
        assert olx_delivery.extract(offer, OLX_URL)["olx_delivery"] is None

    def test_non_bool_active_returns_none(self):
        offer = OfferFactory.build(metadata=_extra(delivery={"rock": {"mode": "BuyWithDelivery", "active": "yes"}}))
        assert olx_delivery.extract(offer, OLX_URL)["olx_delivery"] is None
