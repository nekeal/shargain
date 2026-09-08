"""Tests for OlxPlugin."""

import pytest

from shargain.offers.field_extraction import FieldType, ListUrl
from shargain.offers.field_extraction.plugins.olx import olx
from shargain.offers.tests.factories import OfferFactory

OLX_URL = "https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/krakow/"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.olx.pl/d/oferta/abc.html",
        "https://sub.olx.pl/foo",
    ],
)
def test_matches_olx(url):
    assert olx.matches(ListUrl(url)) is True


@pytest.mark.parametrize(
    "url",
    [
        "https://olx.pl/oferty/",
        "https://notolx.pl/foo",
        "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie",
        "https://example.com/",
    ],
)
def test_does_not_match_other(url):
    assert olx.matches(ListUrl(url)) is False


def test_fields_declare_address_string():
    assert [f.name for f in olx.fields] == ["address"]
    field = olx.fields[0]
    assert field.field_type == FieldType.STRING
    assert str(field.label) == "Address"


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        ({"cityName": "Warsaw", "districtName": "Centrum"}, "Warsaw, Centrum"),
        ({"cityName": "Warsaw"}, "Warsaw"),
        ({"districtName": "Centrum"}, "Centrum"),
    ],
)
def test_extract_address(location, expected):
    offer = OfferFactory.build(url=OLX_URL, metadata={"extra": {"location": location}})
    assert olx.extract(offer, ListUrl(OLX_URL))["address"] == expected


def test_extract_without_location_returns_none():
    offer = OfferFactory.build(url=OLX_URL, metadata={"extra": {}})
    assert olx.extract(offer, ListUrl(OLX_URL))["address"] is None
