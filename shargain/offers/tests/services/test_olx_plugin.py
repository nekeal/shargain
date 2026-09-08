"""Tests for OlxPlugin."""

from shargain.offers.field_extraction import FieldType, ListUrl
from shargain.offers.field_extraction.plugins.olx import olx
from shargain.offers.tests.factories import OfferFactory

OLX_URL = ListUrl("https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/krakow/")


def _extra(**kwargs):
    return {"extra": kwargs}


class TestOlxPluginMatches:
    def test_matches_olx_apartment_url(self):
        assert olx.matches(OLX_URL) is True

    def test_matches_olx_listing_url(self):
        assert olx.matches(ListUrl("https://www.olx.pl/d/oferta/msi-rtx-4060ti-CID99-ID1bISYm.html")) is True

    def test_matches_olx_subdomain(self):
        assert olx.matches(ListUrl("https://sub.olx.pl/foo")) is True

    def test_not_matches_bare_olx_domain(self):
        assert olx.matches(ListUrl("https://olx.pl/oferty/")) is False

    def test_not_matches_lookalike_domains(self):
        assert olx.matches(ListUrl("https://notolx.pl/foo")) is False
        assert olx.matches(ListUrl("https://olx.pl.evil.com/foo")) is False

    def test_not_matches_other_domains(self):
        assert olx.matches(ListUrl("https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie")) is False
        assert olx.matches(ListUrl("https://example.com/")) is False


class TestOlxPluginFields:
    def test_fields_listed(self):
        names = [f.name for f in olx.fields]
        assert names == ["address"]

    def test_field_is_string_with_label(self):
        field = olx.fields[0]
        assert field.field_type == FieldType.STRING
        assert str(field.label) == "Address"
        assert field.unit is None


class TestOlxPluginExtract:
    def test_city_and_district(self):
        offer = OfferFactory.build(
            url="https://www.olx.pl/d/oferta/abc.html",
            metadata=_extra(location={"cityName": "Warsaw", "districtName": "Centrum"}),
        )
        assert olx.extract(offer, OLX_URL)["address"] == "Warsaw, Centrum"

    def test_city_only(self):
        offer = OfferFactory.build(
            url="https://www.olx.pl/d/oferta/abc.html",
            metadata=_extra(location={"cityName": "Warsaw"}),
        )
        assert olx.extract(offer, OLX_URL)["address"] == "Warsaw"

    def test_district_only(self):
        offer = OfferFactory.build(
            url="https://www.olx.pl/d/oferta/abc.html",
            metadata=_extra(location={"districtName": "Centrum"}),
        )
        assert olx.extract(offer, OLX_URL)["address"] == "Centrum"

    def test_no_location_data_returns_none(self):
        offer = OfferFactory.build(url="https://www.olx.pl/d/oferta/abc.html", metadata=_extra())
        assert olx.extract(offer, OLX_URL)["address"] is None

    def test_missing_extra_returns_none(self):
        offer = OfferFactory.build(url="https://www.olx.pl/d/oferta/abc.html", metadata={})
        assert olx.extract(offer, OLX_URL)["address"] is None
