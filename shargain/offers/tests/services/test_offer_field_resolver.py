"""Tests for OfferFieldResolver."""

from unittest.mock import Mock, PropertyMock

import pytest

from shargain.offers.field_extraction import (
    BaseFieldPlugin,
    FieldDefinition,
    FieldType,
    ListUrl,
    OfferFieldResolver,
    Operator,
)
from shargain.offers.models import Offer


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


class TestGetOperatorsForType:
    def test_string_type(self):
        from shargain.offers.field_extraction import get_operators_for_type

        ops = get_operators_for_type(FieldType.STRING)
        assert Operator.CONTAINS in ops
        assert Operator.NOT_CONTAINS in ops
        assert Operator.EQUALS in ops

    def test_number_type(self):
        from shargain.offers.field_extraction import get_operators_for_type

        ops = get_operators_for_type(FieldType.NUMBER)
        assert Operator.EQUALS in ops
        assert Operator.GREATER_THAN in ops
        assert Operator.LESS_THAN in ops
        assert Operator.GTE in ops
        assert Operator.LTE in ops

    def test_boolean_type(self):
        from shargain.offers.field_extraction import get_operators_for_type

        ops = get_operators_for_type(FieldType.BOOLEAN)
        assert Operator.EQUALS in ops
        assert len(ops) == 1

    def test_custom_operators_override_defaults(self):
        from shargain.offers.field_extraction import get_operators_for_type

        custom = [Operator.CONTAINS]
        result = get_operators_for_type(FieldType.NUMBER, custom)
        assert result == custom

    def test_get_fields_resolves_operators_from_type(self):
        OfferFieldResolver._plugins = []
        from shargain.offers.field_extraction.plugins.core_fields import core_fields

        OfferFieldResolver.register(core_fields)
        url = ListUrl("https://example.com/")
        fields = OfferFieldResolver.get_fields(url)
        for f in fields:
            assert f.allowed_operators is not None
        title_field = [f for f in fields if f.name == "title"][0]
        assert Operator.CONTAINS in title_field.allowed_operators
        price_field = [f for f in fields if f.name == "price"][0]
        assert Operator.GREATER_THAN in price_field.allowed_operators


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
