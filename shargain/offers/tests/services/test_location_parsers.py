"""Tests for location parsers."""

import pytest

from shargain.offers.services.location_parsers import (
    BaseLocationParser,
    Coordinates,
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

    def test_get_map_url_delegates_to_get_coordinates(self):
        parser = OlxLocationParser({"extra": {"map": {"lat": 52.23, "lon": 21.01}}})
        url = parser.get_map_url()
        assert url == "https://maps.google.com/?q=52.23,21.01"

    def test_get_map_url_returns_none_when_no_coordinates(self):
        parser = OlxLocationParser({})
        url = parser.get_map_url()
        assert url is None


class TestDummyLocationParser:
    def test_get_coordinates_returns_none(self):
        parser = DummyLocationParser({})
        assert parser.get_coordinates() is None


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
