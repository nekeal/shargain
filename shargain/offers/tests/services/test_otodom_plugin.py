"""Tests for OtodomPlugin."""

import pytest

from shargain.offers.field_extraction import FieldType, ListUrl
from shargain.offers.field_extraction.plugins.otodom import otodom
from shargain.offers.tests.factories import OfferFactory

OTODOM_URL = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie"


@pytest.mark.parametrize(
    "url",
    [
        OTODOM_URL,
        "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/malopolskie/krakow/krakow/krakow",
    ],
)
def test_matches_otodom(url):
    assert otodom.matches(ListUrl(url)) is True


@pytest.mark.parametrize(
    "url",
    [
        "https://otodom.pl/foo",
        "https://nototodom.pl/foo",
        "https://www.olx.pl/nieruchomosci/mieszkania/",
        "https://example.com/",
    ],
)
def test_does_not_match_other(url):
    assert otodom.matches(ListUrl(url)) is False


def test_fields_declare_address_string():
    assert [f.name for f in otodom.fields] == ["address"]
    field = otodom.fields[0]
    assert field.field_type == FieldType.STRING
    assert str(field.label) == "Address"


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        (
            {"address": {"city": {"name": "Kraków"}, "street": {"name": "ul. Jana Dekerta"}}},
            "Kraków, ul. Jana Dekerta",
        ),
        ({"address": {"city": {"name": "Kraków"}}}, "Kraków"),
    ],
)
def test_extract_address(location, expected):
    offer = OfferFactory.build(url=OTODOM_URL, metadata={"extra": {"location": location}})
    assert otodom.extract(offer, ListUrl(OTODOM_URL))["address"] == expected


def test_extract_without_location_returns_none():
    offer = OfferFactory.build(url=OTODOM_URL, metadata={"extra": {}})
    assert otodom.extract(offer, ListUrl(OTODOM_URL))["address"] is None
