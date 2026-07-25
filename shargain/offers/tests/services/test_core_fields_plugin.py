"""Tests for CoreFieldsPlugin."""

from shargain.offers.schemas.field_plugin import FieldType, ListUrl
from shargain.offers.services.source_plugins.core_fields import core_fields
from shargain.offers.tests.factories import OfferFactory


class TestCoreFieldsPlugin:
    def test_matches_all_urls(self):
        assert core_fields.matches(ListUrl("https://olx.pl/any")) is True
        assert core_fields.matches(ListUrl("https://unknown.com/foo")) is True

    def test_fields_provides_title_and_price(self):
        fields = core_fields.fields
        names = [f.name for f in fields]
        assert "title" in names
        assert "price" in names

    def test_title_is_string_type(self):
        title = [f for f in core_fields.fields if f.name == "title"][0]
        assert title.field_type == FieldType.STRING

    def test_price_is_number_type(self):
        price = [f for f in core_fields.fields if f.name == "price"][0]
        assert price.field_type == FieldType.NUMBER
        assert price.unit == "z\u0142"

    def test_extract_returns_from_offer_attributes(self):
        offer = OfferFactory.build(title="Test Flat", price=2500)
        result = core_fields.extract(offer, ListUrl("https://example.com/"))
        assert result["title"] == "Test Flat"
        assert result["price"] == 2500
