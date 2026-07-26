"""Tests for URL-aware filter validation."""

import pytest

from shargain.offers.schemas.offer_filter import validate_filters_for_url


class TestValidateFiltersForUrl:
    def test_validates_field_exists(self):
        filters = {
            "ruleGroups": [
                {
                    "logic": "and",
                    "rules": [{"field": "title", "operator": "contains", "value": "test"}],
                }
            ],
        }
        validate_filters_for_url(filters, "https://example.com/")

    def test_rejects_nonexistent_field(self):
        filters = {
            "ruleGroups": [
                {
                    "logic": "and",
                    "rules": [{"field": "nonexistent", "operator": "contains", "value": "test"}],
                }
            ],
        }
        with pytest.raises(ValueError, match="nonexistent"):
            validate_filters_for_url(filters, "https://example.com/")

    def test_rejects_invalid_operator_for_field_type(self):
        filters = {
            "ruleGroups": [
                {
                    "logic": "and",
                    "rules": [{"field": "price", "operator": "contains", "value": "test"}],
                }
            ],
        }
        with pytest.raises(ValueError, match="contains"):
            validate_filters_for_url(filters, "https://example.com/")
