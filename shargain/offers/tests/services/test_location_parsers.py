"""Tests for location parsers."""

import pytest

from shargain.offers.geo import Coordinates
from shargain.offers.location_parsers import (
    BaseLocationParser,
    DummyLocationParser,
    OlxLocationParser,
    OtodomLocationParser,
)


class TestBaseLocationParser:
    def test_abstract_get_coordinates_raises(self):
        """BaseLocationParser cannot be instantiated without implementing get_coordinates."""
        with pytest.raises(TypeError):
            BaseLocationParser({})


class TestOlxLocationParser:
    def test_get_coordinates_returns_coordinates_for_valid_map_data(self):
        parser = OlxLocationParser({"extra": {"map": {"lat": 52.23, "lon": 21.01}}})
        coords = parser.get_coordinates()
        assert coords == Coordinates(lat=52.23, lon=21.01)

    def test_get_coordinates_returns_none_for_empty_metadata(self):
        parser = OlxLocationParser({})
        coords = parser.get_coordinates()
        assert coords is None

    def test_get_coordinates_returns_none_when_map_missing(self):
        parser = OlxLocationParser({"extra": {}})
        coords = parser.get_coordinates()
        assert coords is None

    def test_get_map_url_returns_coordinates_with_zoom(self):
        parser = OlxLocationParser({"extra": {"map": {"lat": 52.23, "lon": 21.01}}})
        url = parser.get_map_url()
        assert url == "https://maps.google.com/?q=52.23,21.01&ll=52.23,21.01&z=13"

    def test_get_map_url_returns_none_when_no_coordinates(self):
        parser = OlxLocationParser({})
        url = parser.get_map_url()
        assert url is None

    def test_get_map_url_ignores_map_center_uses_own_coordinates(self):
        parser = OlxLocationParser({"extra": {"map": {"lat": 52.23, "lon": 21.01}}})
        url = parser.get_map_url(map_center=Coordinates(lat=50.06, lon=19.94))
        assert url == "https://maps.google.com/?q=52.23,21.01&ll=52.23,21.01&z=13"


class TestDummyLocationParser:
    def test_get_coordinates_returns_none(self):
        parser = DummyLocationParser({})
        assert parser.get_coordinates() is None

    def test_get_map_url_returns_none_with_map_center(self):
        parser = DummyLocationParser({})
        assert parser.get_map_url(map_center=Coordinates(lat=50.06, lon=19.94)) is None


class TestOtodomLocationParser:
    def test_get_coordinates_returns_none(self):
        parser = OtodomLocationParser({"extra": {"location": {"address": {"city": {"name": "Kraków"}}}}})
        assert parser.get_coordinates() is None

    def test_get_map_url_returns_none_for_empty_metadata(self):
        parser = OtodomLocationParser({})
        assert parser.get_map_url() is None

    def test_get_map_url_returns_search_query_for_city_and_street(self):
        parser = OtodomLocationParser(
            {
                "extra": {
                    "location": {
                        "address": {
                            "city": {"name": "Kraków"},
                            "street": {"name": "ul. Jana Dekerta"},
                        }
                    }
                }
            }
        )
        assert parser.get_map_url() == "https://maps.google.com/?q=Krak%C3%B3w%2C%20ul.%20Jana%20Dekerta"

    def test_get_map_url_with_map_center_appends_zoom(self):
        parser = OtodomLocationParser(
            {
                "extra": {
                    "location": {
                        "address": {
                            "city": {"name": "Kraków"},
                            "street": {"name": "ul. Jana Dekerta"},
                        }
                    }
                }
            }
        )
        url = parser.get_map_url(map_center=Coordinates(lat=50.018166, lon=19.89713))
        assert url == "https://maps.google.com/?q=Krak%C3%B3w%2C%20ul.%20Jana%20Dekerta&ll=50.018166,19.89713&z=13"

    def test_is_location_exact_returns_false(self):
        parser = OtodomLocationParser({"extra": {"location": {"address": {"city": {"name": "Kraków"}}}}})
        assert parser.is_location_exact() is False

    def test_get_location_name_city_and_street(self):
        parser = OtodomLocationParser(
            {
                "extra": {
                    "location": {
                        "address": {
                            "city": {"name": "Kraków"},
                            "street": {"name": "ul. Jana Dekerta"},
                        }
                    }
                }
            }
        )
        assert parser.get_location_name() == "Kraków, ul. Jana Dekerta"

    def test_get_location_name_city_only_when_street_missing(self):
        parser = OtodomLocationParser(
            {
                "extra": {
                    "location": {
                        "address": {
                            "city": {"name": "Kraków"},
                        }
                    }
                }
            }
        )
        assert parser.get_location_name() == "Kraków"
