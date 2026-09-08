"""Tests for OtodomPlugin."""

from shargain.offers.field_extraction import FieldType, ListUrl
from shargain.offers.field_extraction.plugins.otodom import otodom
from shargain.offers.tests.factories import OfferFactory

OTODOM_URL = ListUrl("https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie")
OTODOM_KRAKOW_URL = ListUrl("https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/malopolskie/krakow/krakow/krakow")


def _extra(**kwargs):
    return {"extra": kwargs}


class TestOtodomPluginMatches:
    def test_matches_otodom_apartment_url(self):
        assert otodom.matches(OTODOM_URL) is True

    def test_matches_otodom_krakow_url(self):
        assert otodom.matches(OTODOM_KRAKOW_URL) is True

    def test_not_matches_lookalike_domains(self):
        assert otodom.matches(ListUrl("https://nototodom.pl/foo")) is False
        assert otodom.matches(ListUrl("https://otodom.pl.evil.com/foo")) is False

    def test_not_matches_other_domains(self):
        assert otodom.matches(ListUrl("https://www.olx.pl/nieruchomosci/mieszkania/")) is False
        assert otodom.matches(ListUrl("https://example.com/")) is False


class TestOtodomPluginFields:
    def test_fields_listed(self):
        names = [f.name for f in otodom.fields]
        assert names == ["address"]

    def test_field_is_string_with_label(self):
        field = otodom.fields[0]
        assert field.field_type == FieldType.STRING
        assert str(field.label) == "Address"
        assert field.unit is None


class TestOtodomPluginExtract:
    def test_city_and_street(self):
        offer = OfferFactory.build(
            url="https://www.otodom.pl/pl/oferta/abc.html",
            metadata=_extra(location={"address": {"city": {"name": "Kraków"}, "street": {"name": "ul. Jana Dekerta"}}}),
        )
        assert otodom.extract(offer, OTODOM_URL)["address"] == "Kraków, ul. Jana Dekerta"

    def test_city_only(self):
        offer = OfferFactory.build(
            url="https://www.otodom.pl/pl/oferta/abc.html",
            metadata=_extra(location={"address": {"city": {"name": "Kraków"}}}),
        )
        assert otodom.extract(offer, OTODOM_URL)["address"] == "Kraków"

    def test_no_location_data_returns_none(self):
        offer = OfferFactory.build(url="https://www.otodom.pl/pl/oferta/abc.html", metadata=_extra())
        assert otodom.extract(offer, OTODOM_URL)["address"] is None

    def test_missing_extra_returns_none(self):
        offer = OfferFactory.build(url="https://www.otodom.pl/pl/oferta/abc.html", metadata={})
        assert otodom.extract(offer, OTODOM_URL)["address"] is None
