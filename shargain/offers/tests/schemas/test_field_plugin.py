"""Tests for core field plugin types."""

import pytest

from shargain.offers.field_extraction import ExtractedOffer, FieldDefinition, FieldType, ListUrl, Operator
from shargain.offers.tests.factories import OfferFactory


class TestFieldType:
    def test_enum_values(self):
        assert FieldType.STRING.value == "string"
        assert FieldType.NUMBER.value == "number"
        assert FieldType.BOOLEAN.value == "boolean"


class TestOperator:
    def test_enum_values(self):
        assert Operator.CONTAINS.value == "contains"
        assert Operator.NOT_CONTAINS.value == "not_contains"
        assert Operator.EQUALS.value == "equals"
        assert Operator.NOT_EQUALS.value == "not_equals"
        assert Operator.GREATER_THAN.value == "greater_than"
        assert Operator.LESS_THAN.value == "less_than"
        assert Operator.GTE.value == "gte"
        assert Operator.LTE.value == "lte"


class TestFieldDefinition:
    def test_frozen_dataclass(self):
        fd = FieldDefinition(
            name="price_per_m2",
            label="Price per m\u00b2",
            field_type=FieldType.NUMBER,
            unit="z\u0142/m\u00b2",
        )
        assert fd.name == "price_per_m2"
        assert fd.label == "Price per m\u00b2"
        assert fd.field_type == FieldType.NUMBER
        assert fd.unit == "z\u0142/m\u00b2"
        assert fd.allowed_operators is None

    def test_custom_allowed_operators(self):
        fd = FieldDefinition(
            name="phone",
            label="Phone",
            field_type=FieldType.STRING,
            allowed_operators=[Operator.EQUALS],
        )
        assert fd.allowed_operators == [Operator.EQUALS]

    def test_is_frozen(self):
        fd = FieldDefinition(name="x", label="X", field_type=FieldType.STRING)
        with pytest.raises(AttributeError):
            fd.name = "y"


class TestListUrl:
    def test_is_newtype_of_str(self):
        url = ListUrl("https://olx.pl/oferty/mieszkania/")
        assert isinstance(url, str)
        assert url == "https://olx.pl/oferty/mieszkania/"


class TestExtractedOffer:
    def test_holds_offer_and_fields(self):
        offer = OfferFactory.build()
        extracted = ExtractedOffer(
            _offer=offer,
            fields={"price_per_m2": 8500, "rooms": 3},
        )
        assert extracted._offer is offer
        assert extracted.fields["price_per_m2"] == 8500
        assert extracted.fields["rooms"] == 3

    def test_fields_can_be_empty(self):
        offer = OfferFactory.build()
        extracted = ExtractedOffer(_offer=offer, fields={})
        assert extracted.fields == {}
