"""Tests for core field plugin types."""

from shargain.offers.field_extraction import ExtractedOffer, FieldDefinition, FieldType, Operator
from shargain.offers.tests.factories import OfferFactory


class TestOperator:
    def test_all_operators_have_labels(self):
        for op in Operator:
            label = str(op.label)
            assert len(label) > 0, f"Operator {op.value!r} has empty label"
            assert label != op.value, f"Operator {op.value!r} label equals its value"


class TestFieldDefinition:
    def test_custom_allowed_operators(self):
        fd = FieldDefinition(
            name="phone",
            label="Phone",
            field_type=FieldType.STRING,
            allowed_operators=[Operator.EQUALS],
        )
        assert fd.allowed_operators == [Operator.EQUALS]


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
