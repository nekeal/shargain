"""Tests for OfferFieldResolver."""

from unittest.mock import Mock, PropertyMock

import pytest

from shargain.offers.models import Offer
from shargain.offers.schemas.field_plugin import (
    BaseFieldPlugin,
    FieldDefinition,
    FieldType,
    ListUrl,
)
from shargain.offers.services.offer_field_resolver import OfferFieldResolver


@pytest.fixture(autouse=True)
def reset_plugins():
    OfferFieldResolver._plugins = []


@pytest.fixture
def plugin_alpha():
    plugin = Mock(spec=BaseFieldPlugin)
    plugin.matches.return_value = True
    type(plugin).fields = PropertyMock(
        return_value=[
            FieldDefinition("title", "Title", FieldType.STRING),
            FieldDefinition("price", "Price", FieldType.NUMBER),
        ]
    )
    plugin.extract.return_value = {"title": "Test", "price": 100}
    return plugin


@pytest.fixture
def plugin_beta():
    def matches(url):
        return "olx.pl" in url

    plugin = Mock(spec=BaseFieldPlugin)
    plugin.matches.side_effect = matches
    type(plugin).fields = PropertyMock(
        return_value=[
            FieldDefinition("price_per_m2", "Price per m\u00b2", FieldType.NUMBER),
            FieldDefinition("rooms", "Rooms", FieldType.NUMBER),
        ]
    )
    plugin.extract.return_value = {"price_per_m2": 5000, "rooms": 3}
    return plugin


class TestOfferFieldResolver:
    def test_register_adds_plugin(self):
        plugin = Mock(spec=BaseFieldPlugin)
        OfferFieldResolver.register(plugin)
        assert plugin in OfferFieldResolver._plugins

    def test_get_fields_returns_matching_plugins_fields(self, plugin_alpha, plugin_beta):
        OfferFieldResolver._plugins = [plugin_alpha, plugin_beta]
        url = ListUrl("https://olx.pl/oferty/mieszkania/")
        fields = OfferFieldResolver.get_fields(url)
        names = [f.name for f in fields]
        assert "title" in names
        assert "price" in names
        assert "price_per_m2" in names
        assert "rooms" in names

    def test_get_fields_first_plugin_wins_on_conflict(self, plugin_alpha):
        plugin_dup = Mock(spec=BaseFieldPlugin)
        plugin_dup.matches.return_value = True
        type(plugin_dup).fields = PropertyMock(
            return_value=[
                FieldDefinition("title", "Overridden", FieldType.STRING),
            ]
        )
        OfferFieldResolver._plugins = [plugin_alpha, plugin_dup]
        url = ListUrl("https://example.com/")
        fields = OfferFieldResolver.get_fields(url)
        title_field = [f for f in fields if f.name == "title"][0]
        assert title_field.label == "Title"

    def test_get_fields_non_matching_plugin_excluded(self, plugin_alpha, plugin_beta):
        OfferFieldResolver._plugins = [plugin_alpha, plugin_beta]
        url = ListUrl("https://otomoto.pl/cars/")
        fields = OfferFieldResolver.get_fields(url)
        names = [f.name for f in fields]
        assert "title" in names
        assert "price_per_m2" not in names

    def test_extract_merges_from_matching_plugins(self, plugin_alpha, plugin_beta):
        OfferFieldResolver._plugins = [plugin_alpha, plugin_beta]
        url = ListUrl("https://olx.pl/oferty/mieszkania/")
        offer_mock = Mock()
        result = OfferFieldResolver.extract(offer_mock, url)
        assert result["title"] == "Test"
        assert result["price"] == 100
        assert result["price_per_m2"] == 5000

    def test_extract_no_matching_plugins_returns_empty(self):
        plugin = Mock(spec=BaseFieldPlugin)
        plugin.matches.return_value = False
        OfferFieldResolver._plugins = [plugin]
        url = ListUrl("https://unknown.com/")
        offer_mock = Mock()
        result = OfferFieldResolver.extract(offer_mock, url)
        assert result == {}


class TestConcretePlugin:
    def test_concrete_plugin_round_trip_via_resolver(self):
        class TestPlugin(BaseFieldPlugin):
            def matches(self, url: ListUrl) -> bool:
                return True

            @property
            def fields(self) -> list[FieldDefinition]:
                return [FieldDefinition("test_field", "Test", FieldType.STRING)]

            def extract(self, offer: Offer, url: ListUrl) -> dict:
                return {"test_field": "hello"}

        OfferFieldResolver.register(TestPlugin())

        fields = OfferFieldResolver.get_fields(ListUrl("https://example.com/"))
        assert len(fields) == 1
        assert fields[0].name == "test_field"

        offer_mock = Mock(spec=Offer)
        result = OfferFieldResolver.extract(offer_mock, ListUrl("https://example.com/"))
        assert result == {"test_field": "hello"}
