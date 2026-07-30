"""Tests for OfferFilterService."""

import pytest

from shargain.offers.field_extraction import ExtractedOffer
from shargain.offers.filtering import FilterOperator, OfferFilterService


class TestOfferFilterService:
    """Tests for the OfferFilterService class."""

    @pytest.fixture
    def offer_apartment(self):
        return ExtractedOffer(_offer=None, fields={"title": "Beautiful apartment in city center"})

    @pytest.fixture
    def offer_studio(self):
        return ExtractedOffer(_offer=None, fields={"title": "Cozy studio apartment for rent"})

    @pytest.fixture
    def offer_flat(self):
        return ExtractedOffer(_offer=None, fields={"title": "Modern flat with great view"})

    @pytest.fixture
    def offer_house(self):
        return ExtractedOffer(_offer=None, fields={"title": "Spacious house with garden"})

    def test_no_filters_passes_all(self, offer_apartment, offer_studio, offer_flat, offer_house):
        service = OfferFilterService(None)
        offers = [offer_apartment, offer_studio, offer_flat, offer_house]
        filtered = service.apply(offers)
        assert len(filtered) == 4

    def test_empty_filters_passes_all(self, offer_apartment, offer_studio, offer_flat):
        service = OfferFilterService({})
        offers = [offer_apartment, offer_studio, offer_flat]
        filtered = service.apply(offers)
        assert len(filtered) == 3

    def test_empty_rule_groups_passes_all(self, offer_apartment, offer_studio, offer_flat):
        service = OfferFilterService({"ruleGroups": []})
        offers = [offer_apartment, offer_studio, offer_flat]
        filtered = service.apply(offers)
        assert len(filtered) == 3

    def test_filter_title_contains(self, offer_apartment, offer_studio, offer_house):
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {"rules": [{"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "apartment"}]}
                ]
            }
        )
        offers = [offer_apartment, offer_studio, offer_house]
        filtered = service.apply(offers)

        assert len(filtered) == 2
        assert offer_apartment in filtered
        assert offer_studio in filtered
        assert offer_house not in filtered

    def test_filter_title_not_contains(self, offer_apartment, offer_studio, offer_house):
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {"rules": [{"field": "title", "operator": FilterOperator.NOT_CONTAINS.value, "value": "studio"}]}
                ]
            }
        )
        offers = [offer_apartment, offer_studio, offer_house]
        filtered = service.apply(offers)

        assert len(filtered) == 2
        assert offer_apartment in filtered
        assert offer_studio not in filtered
        assert offer_house in filtered

    def test_multiple_and_rules_in_single_group(self, offer_apartment, offer_studio, offer_house):
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "rules": [
                            {"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "apartment"},
                            {"field": "title", "operator": FilterOperator.NOT_CONTAINS.value, "value": "studio"},
                        ]
                    }
                ]
            }
        )
        offers = [offer_apartment, offer_studio, offer_house]
        filtered = service.apply(offers)

        assert len(filtered) == 1
        assert offer_apartment in filtered
        assert offer_studio not in filtered
        assert offer_house not in filtered

    def test_or_logic_between_groups(self, offer_apartment, offer_studio, offer_flat, offer_house):
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "logic": "and",
                        "logicWithNext": "or",
                        "rules": [
                            {"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "apartment"},
                            {"field": "title", "operator": FilterOperator.NOT_CONTAINS.value, "value": "studio"},
                        ],
                    },
                    {"rules": [{"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "flat"}]},
                ]
            }
        )
        offers = [offer_apartment, offer_studio, offer_flat, offer_house]
        filtered = service.apply(offers)

        assert len(filtered) == 2
        assert offer_apartment in filtered
        assert offer_flat in filtered
        assert offer_studio not in filtered
        assert offer_house not in filtered

    def test_and_logic_between_groups(self, offer_apartment, offer_studio, offer_flat):
        offer_apartment_with_flat = ExtractedOffer(_offer=None, fields={"title": "Modern apartment flat"})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "logic": "and",
                        "logicWithNext": "and",
                        "rules": [{"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "apartment"}],
                    },
                    {"rules": [{"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "flat"}]},
                ]
            }
        )
        offers = [offer_apartment, offer_studio, offer_flat, offer_apartment_with_flat]
        filtered = service.apply(offers)

        assert len(filtered) == 1
        assert offer_apartment_with_flat in filtered

    def test_complex_filter_and_or_combination(self, offer_apartment, offer_studio, offer_flat, offer_house):
        offer_house_with_garden = ExtractedOffer(_offer=None, fields={"title": "A beautiful house with a garden"})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "logic": "and",
                        "logicWithNext": "and",
                        "rules": [
                            {"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "apartment"},
                        ],
                    },
                    {
                        "logic": "and",
                        "logicWithNext": "or",
                        "rules": [
                            {"field": "title", "operator": FilterOperator.NOT_CONTAINS.value, "value": "studio"},
                        ],
                    },
                    {
                        "logic": "and",
                        "rules": [
                            {"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "house"},
                            {"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "garden"},
                        ],
                    },
                ]
            }
        )
        offers = [offer_apartment, offer_studio, offer_flat, offer_house, offer_house_with_garden]
        filtered = service.apply(offers)

        assert len(filtered) == 3
        assert offer_apartment in filtered
        assert offer_house_with_garden in filtered
        assert offer_house in filtered
        assert offer_studio not in filtered
        assert offer_flat not in filtered

    def test_single_rule_single_group(self, offer_apartment, offer_house):
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {"rules": [{"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "apartment"}]}
                ]
            }
        )
        offers = [offer_apartment, offer_house]
        filtered = service.apply(offers)

        assert len(filtered) == 1
        assert offer_apartment in filtered

    def test_case_insensitive_matching(self):
        offer_upper = ExtractedOffer(_offer=None, fields={"title": "LUXURY APARTMENT"})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {"rules": [{"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "apartment"}]}
                ]
            }
        )
        filtered = service.apply([offer_upper])

        assert len(filtered) == 1
        assert offer_upper in filtered

    def test_case_sensitive_matching(self):
        offer_upper = ExtractedOffer(_offer=None, fields={"title": "LUXURY APARTMENT"})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "rules": [
                            {
                                "field": "title",
                                "operator": FilterOperator.CONTAINS.value,
                                "value": "apartment",
                                "case_sensitive": True,
                            }
                        ]
                    }
                ]
            }
        )
        filtered = service.apply([offer_upper])

        assert len(filtered) == 0

    def test_unicode_and_special_chars(self):
        offer_unicode = ExtractedOffer(_offer=None, fields={"title": "Apartament w Krakowie - świetna lokalizacja!"})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {"rules": [{"field": "title", "operator": FilterOperator.CONTAINS.value, "value": "świetna"}]}
                ]
            }
        )
        filtered = service.apply([offer_unicode])

        assert len(filtered) == 1
        assert offer_unicode in filtered

    def test_unknown_operator_raises_error(self, offer_apartment):
        service = OfferFilterService(
            {"ruleGroups": [{"rules": [{"field": "title", "operator": "regex", "value": "test"}]}]}
        )
        with pytest.raises(ValueError, match="Unknown operator"):
            service.apply([offer_apartment])

    def test_field_not_in_extracted_returns_false(self):
        offer = ExtractedOffer(_offer=None, fields={"title": "Some offer"})
        service = OfferFilterService(
            {"ruleGroups": [{"rules": [{"field": "price", "operator": FilterOperator.EQUALS.value, "value": "100"}]}]}
        )
        filtered = service.apply([offer])

        assert len(filtered) == 0

    def test_filter_title_equals(self, offer_apartment, offer_studio):
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "rules": [
                            {
                                "field": "title",
                                "operator": FilterOperator.EQUALS.value,
                                "value": "beautiful apartment in city center",
                            }
                        ]
                    }
                ]
            }
        )
        offers = [offer_apartment, offer_studio]
        filtered = service.apply(offers)

        assert len(filtered) == 1
        assert offer_apartment in filtered

    def test_filter_title_not_equals(self, offer_apartment, offer_studio):
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "rules": [
                            {
                                "field": "title",
                                "operator": FilterOperator.NOT_EQUALS.value,
                                "value": "beautiful apartment in city center",
                            }
                        ]
                    }
                ]
            }
        )
        offers = [offer_apartment, offer_studio]
        filtered = service.apply(offers)

        assert len(filtered) == 1
        assert offer_studio in filtered

    def test_filter_price_greater_than(self):
        offer_cheap = ExtractedOffer(_offer=None, fields={"title": "Cheap", "price": 500})
        offer_expensive = ExtractedOffer(_offer=None, fields={"title": "Expensive", "price": 1500})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {"rules": [{"field": "price", "operator": FilterOperator.GREATER_THAN.value, "value": "1000"}]}
                ]
            }
        )
        filtered = service.apply([offer_cheap, offer_expensive])

        assert len(filtered) == 1
        assert offer_expensive in filtered

    def test_filter_price_less_than(self):
        offer_cheap = ExtractedOffer(_offer=None, fields={"title": "Cheap", "price": 500})
        offer_expensive = ExtractedOffer(_offer=None, fields={"title": "Expensive", "price": 1500})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {"rules": [{"field": "price", "operator": FilterOperator.LESS_THAN.value, "value": "1000"}]}
                ]
            }
        )
        filtered = service.apply([offer_cheap, offer_expensive])

        assert len(filtered) == 1
        assert offer_cheap in filtered

    def test_filter_price_gte(self):
        offer_cheap = ExtractedOffer(_offer=None, fields={"title": "Cheap", "price": 500})
        offer_exact = ExtractedOffer(_offer=None, fields={"title": "Exact", "price": 1000})
        offer_expensive = ExtractedOffer(_offer=None, fields={"title": "Expensive", "price": 1500})
        service = OfferFilterService(
            {"ruleGroups": [{"rules": [{"field": "price", "operator": FilterOperator.GTE.value, "value": "1000"}]}]}
        )
        filtered = service.apply([offer_cheap, offer_exact, offer_expensive])

        assert len(filtered) == 2
        assert offer_exact in filtered
        assert offer_expensive in filtered

    def test_filter_price_lte(self):
        offer_cheap = ExtractedOffer(_offer=None, fields={"title": "Cheap", "price": 500})
        offer_exact = ExtractedOffer(_offer=None, fields={"title": "Exact", "price": 1000})
        offer_expensive = ExtractedOffer(_offer=None, fields={"title": "Expensive", "price": 1500})
        service = OfferFilterService(
            {"ruleGroups": [{"rules": [{"field": "price", "operator": FilterOperator.LTE.value, "value": "1000"}]}]}
        )
        filtered = service.apply([offer_cheap, offer_exact, offer_expensive])

        assert len(filtered) == 2
        assert offer_cheap in filtered
        assert offer_exact in filtered

    def test_filter_rooms_equals(self):
        offer_2rooms = ExtractedOffer(_offer=None, fields={"title": "Two rooms", "rooms": 2})
        offer_3rooms = ExtractedOffer(_offer=None, fields={"title": "Three rooms", "rooms": 3})
        service = OfferFilterService(
            {"ruleGroups": [{"rules": [{"field": "rooms", "operator": FilterOperator.EQUALS.value, "value": "2"}]}]}
        )
        filtered = service.apply([offer_2rooms, offer_3rooms])

        assert len(filtered) == 1
        assert offer_2rooms in filtered

    def test_multiple_groups_with_and_logic(self):
        offer_pass = ExtractedOffer(_offer=None, fields={"title": "Nice flat", "price": 1500, "rooms": 2})
        offer_too_pricey = ExtractedOffer(_offer=None, fields={"title": "Expensive flat", "price": 500, "rooms": 2})
        offer_too_many_rooms = ExtractedOffer(_offer=None, fields={"title": "Big flat", "price": 1500, "rooms": 5})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "logicWithNext": "and",
                        "rules": [{"field": "price", "operator": FilterOperator.GREATER_THAN.value, "value": "1000"}],
                    },
                    {"rules": [{"field": "rooms", "operator": FilterOperator.LESS_THAN.value, "value": "4"}]},
                ]
            }
        )
        offers = [offer_pass, offer_too_pricey, offer_too_many_rooms]
        filtered = service.apply(offers)

        assert len(filtered) == 1
        assert offer_pass in filtered

    def test_multiple_groups_with_or_logic(self):
        offer_cheap = ExtractedOffer(_offer=None, fields={"title": "Cheap", "price": 100})
        offer_big = ExtractedOffer(_offer=None, fields={"title": "Big", "rooms": 10})
        offer_normal = ExtractedOffer(_offer=None, fields={"title": "Normal", "price": 500, "rooms": 3})
        service = OfferFilterService(
            {
                "ruleGroups": [
                    {
                        "logicWithNext": "or",
                        "rules": [{"field": "price", "operator": FilterOperator.LESS_THAN.value, "value": "200"}],
                    },
                    {"rules": [{"field": "rooms", "operator": FilterOperator.GREATER_THAN.value, "value": "5"}]},
                ]
            }
        )
        offers = [offer_cheap, offer_big, offer_normal]
        filtered = service.apply(offers)

        assert len(filtered) == 2
        assert offer_cheap in filtered
        assert offer_big in filtered
