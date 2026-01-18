"""Tests for offer filter validation schemas."""

import pytest
from pydantic import ValidationError

from shargain.offers.schemas.offer_filter import (
    FilterField,
    FilterOperator,
    FilterRule,
    FiltersConfig,
    RuleGroup,
    validate_filters,
)


class TestFilterRule:
    """Tests for FilterRule validation."""

    def test_valid_contains_rule(self):
        """Test creating a valid 'contains' filter rule."""
        rule = FilterRule(
            field=FilterField.TITLE,
            operator=FilterOperator.CONTAINS,
            value="apartment",
            case_sensitive=False,
        )
        assert rule.field == FilterField.TITLE
        assert rule.operator == FilterOperator.CONTAINS
        assert rule.value == "apartment"
        assert rule.case_sensitive is False

    def test_valid_not_contains_rule(self):
        """Test creating a valid 'not_contains' filter rule."""
        rule = FilterRule(
            field=FilterField.TITLE,
            operator=FilterOperator.NOT_CONTAINS,
            value="studio",
        )
        assert rule.operator == FilterOperator.NOT_CONTAINS
        assert rule.value == "studio"

    def test_rule_strips_whitespace_from_value(self):
        """Test that whitespace is stripped from filter values."""
        rule = FilterRule(
            field=FilterField.TITLE,
            operator=FilterOperator.CONTAINS,
            value="  apartment  ",
        )
        assert rule.value == "apartment"

    def test_rule_rejects_empty_value(self):
        """Test that empty values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            FilterRule(
                field=FilterField.TITLE,
                operator=FilterOperator.CONTAINS,
                value="",
            )
        # Pydantic's min_length=1 catches empty strings
        assert "at least 1 character" in str(exc_info.value).lower()

    def test_rule_rejects_whitespace_only_value(self):
        """Test that whitespace-only values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            FilterRule(
                field=FilterField.TITLE,
                operator=FilterOperator.CONTAINS,
                value="   ",
            )
        assert "Filter value cannot be blank" in str(exc_info.value)

    def test_rule_rejects_value_too_long(self):
        """Test that values exceeding max length are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            FilterRule(
                field=FilterField.TITLE,
                operator=FilterOperator.CONTAINS,
                value="a" * 201,  # Max is 200
            )
        assert "String should have at most 200 characters" in str(exc_info.value)

    def test_rule_rejects_invalid_operator(self):
        """Test that invalid operators are rejected."""
        with pytest.raises(ValidationError):
            FilterRule(
                field=FilterField.TITLE,
                operator="invalid_op",  # type: ignore
                value="test",
            )

    def test_rule_rejects_invalid_field(self):
        """Test that invalid fields are rejected."""
        with pytest.raises(ValidationError):
            FilterRule(
                field="invalid_field",  # type: ignore
                operator=FilterOperator.CONTAINS,
                value="test",
            )


class TestRuleGroup:
    """Tests for RuleGroup validation."""

    def test_valid_single_rule_group(self):
        """Test creating a group with a single rule."""
        rule = FilterRule(
            field=FilterField.TITLE,
            operator=FilterOperator.CONTAINS,
            value="apartment",
        )
        group = RuleGroup(rules=[rule])
        assert len(group.rules) == 1

    def test_valid_multiple_rules_group(self):
        """Test creating a group with multiple rules."""
        rules = [
            FilterRule(
                field=FilterField.TITLE,
                operator=FilterOperator.CONTAINS,
                value="apartment",
            ),
            FilterRule(
                field=FilterField.TITLE,
                operator=FilterOperator.NOT_CONTAINS,
                value="studio",
            ),
        ]
        group = RuleGroup(rules=rules)
        assert len(group.rules) == 2

    def test_group_rejects_empty_rules_list(self):
        """Test that groups with no rules are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RuleGroup(rules=[])
        assert "at least 1 item" in str(exc_info.value).lower()

    def test_group_rejects_too_many_rules(self):
        """Test that groups with more than 10 rules are rejected."""
        rules = [
            FilterRule(
                field=FilterField.TITLE,
                operator=FilterOperator.CONTAINS,
                value=f"value{i}",
            )
            for i in range(11)
        ]
        with pytest.raises(ValidationError) as exc_info:
            RuleGroup(rules=rules)
        assert "at most 10 items" in str(exc_info.value).lower()


class TestFiltersConfig:
    """Tests for FiltersConfig validation."""

    def test_valid_single_group_config(self):
        """Test creating a config with a single rule group."""
        config_data = {
            "ruleGroups": [
                {
                    "rules": [
                        {
                            "field": "title",
                            "operator": "contains",
                            "value": "apartment",
                            "case_sensitive": False,
                        }
                    ]
                }
            ]
        }
        config = FiltersConfig.model_validate(config_data)
        assert len(config.rule_groups) == 1
        assert len(config.rule_groups[0].rules) == 1

    def test_valid_multiple_groups_config(self):
        """Test creating a config with multiple rule groups (OR logic)."""
        config_data = {
            "ruleGroups": [
                {
                    "rules": [
                        {"field": "title", "operator": "contains", "value": "apartment"},
                        {"field": "title", "operator": "not_contains", "value": "studio"},
                    ]
                },
                {"rules": [{"field": "title", "operator": "contains", "value": "flat"}]},
            ]
        }
        config = FiltersConfig.model_validate(config_data)
        assert len(config.rule_groups) == 2
        assert len(config.rule_groups[0].rules) == 2
        assert len(config.rule_groups[1].rules) == 1

    def test_config_accepts_camelcase_alias(self):
        """Test that config accepts 'ruleGroups' (camelCase) field name."""
        config_data = {"ruleGroups": [{"rules": [{"field": "title", "operator": "contains", "value": "test"}]}]}
        config = FiltersConfig.model_validate(config_data)
        assert len(config.rule_groups) == 1

    def test_config_model_dump_uses_camelcase(self):
        """Test that dumping config uses camelCase field names."""
        config_data = {"ruleGroups": [{"rules": [{"field": "title", "operator": "contains", "value": "test"}]}]}
        config = FiltersConfig.model_validate(config_data)
        dumped = config.model_dump(by_alias=True)
        assert "ruleGroups" in dumped
        assert "rule_groups" not in dumped

    def test_config_rejects_empty_groups_list(self):
        """Test that configs with no rule groups are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            FiltersConfig.model_validate({"ruleGroups": []})
        assert "at least 1 item" in str(exc_info.value).lower()

    def test_config_rejects_too_many_groups(self):
        """Test that configs with more than 5 rule groups are rejected."""
        config_data = {
            "ruleGroups": [
                {"rules": [{"field": "title", "operator": "contains", "value": f"value{i}"}]} for i in range(6)
            ]
        }
        with pytest.raises(ValidationError) as exc_info:
            FiltersConfig.model_validate(config_data)
        assert "at most 5 items" in str(exc_info.value).lower()


class TestValidateFilters:
    """Tests for the validate_filters function."""

    def test_validate_filters_with_none(self):
        """Test that None returns None."""
        result = validate_filters(None)
        assert result is None

    def test_validate_filters_with_empty_dict(self):
        """Test that empty dict returns None."""
        result = validate_filters({})
        assert result is None

    def test_validate_filters_with_valid_config(self):
        """Test that valid config is validated and normalized."""
        config_data = {"ruleGroups": [{"rules": [{"field": "title", "operator": "contains", "value": "apartment"}]}]}
        result = validate_filters(config_data)
        assert result is not None
        assert "ruleGroups" in result
        assert len(result["ruleGroups"]) == 1

    def test_validate_filters_with_invalid_config(self):
        """Test that invalid config raises ValueError."""
        invalid_config = {"ruleGroups": [{"rules": [{"field": "invalid", "operator": "contains", "value": "test"}]}]}
        with pytest.raises(ValueError, match="Invalid filter configuration"):
            validate_filters(invalid_config)

    def test_validate_filters_preserves_structure(self):
        """Test that validated filters maintain the correct structure."""
        config_data = {
            "ruleGroups": [
                {
                    "rules": [
                        {"field": "title", "operator": "contains", "value": "apt"},
                        {"field": "title", "operator": "not_contains", "value": "studio"},
                    ]
                },
                {"rules": [{"field": "title", "operator": "contains", "value": "flat"}]},
            ]
        }
        result = validate_filters(config_data)
        assert len(result["ruleGroups"]) == 2
        assert len(result["ruleGroups"][0]["rules"]) == 2
        assert len(result["ruleGroups"][1]["rules"]) == 1
        assert result["ruleGroups"][0]["rules"][0]["value"] == "apt"
