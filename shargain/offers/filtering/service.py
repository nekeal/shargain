"""Service for filtering offers based on configured rules before sending notifications."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, NotRequired, TypedDict

from shargain.offers.field_extraction.plugin import ExtractedOffer, Operator, RichValue


class FilterRuleData(TypedDict):
    field: str
    operator: Operator
    value: str
    case_sensitive: NotRequired[bool]


class RuleGroupData(TypedDict):
    rules: list[FilterRuleData]
    logic: NotRequired[str]
    logicWithNext: NotRequired[str]


class FiltersData(TypedDict, total=False):
    ruleGroups: list[RuleGroupData]


class OfferFilterService:
    """Service to filter offers based on rule groups with configurable logic.

    Operates on ExtractedOffer fields only — does not access the Offer model.
    """

    def __init__(self, filters: FiltersData | None):
        self.filters = filters or {}

    def apply(self, offers: list[ExtractedOffer]) -> list[ExtractedOffer]:
        if not self.filters or not self.filters.get("ruleGroups"):
            return offers

        filtered = []
        for offer in offers:
            if self._evaluate_offer(offer):
                filtered.append(offer)
        return filtered

    def _evaluate_offer(self, offer: ExtractedOffer) -> bool:
        rule_groups = self.filters.get("ruleGroups", [])
        if not rule_groups:
            return True

        result = self._evaluate_group(offer, rule_groups[0])
        for i in range(len(rule_groups) - 1):
            current_group = rule_groups[i]
            next_group = rule_groups[i + 1]
            logic_operator = current_group.get("logicWithNext", "or")
            next_result = self._evaluate_group(offer, next_group)
            if logic_operator == "and":
                result = result and next_result
            else:
                result = result or next_result
        return result

    def _evaluate_group(self, offer: ExtractedOffer, group: RuleGroupData) -> bool:
        rules = group.get("rules", [])
        group_logic = group.get("logic", "and")
        if group_logic == "and":
            return all(self._evaluate_rule(offer, rule) for rule in rules)
        else:
            return any(self._evaluate_rule(offer, rule) for rule in rules)

    def _evaluate_rule(self, offer: ExtractedOffer, rule: FilterRuleData) -> bool:
        field_name = rule["field"]
        operator = rule["operator"]
        filter_value = rule["value"]

        field_value = offer.fields.get(field_name)
        if isinstance(field_value, RichValue):
            field_value = field_value.get_value()
        if field_value is None:
            return False

        if not rule.get("case_sensitive", False):
            if isinstance(field_value, str) and isinstance(filter_value, str):
                field_value = field_value.lower()
                filter_value = filter_value.lower()

        handler = self._get_operator_handler(operator)
        return handler(field_value, filter_value)

    def _get_operator_handler(self, operator: Operator) -> Callable:
        if operator == Operator.CONTAINS:
            return _op_contains
        elif operator == Operator.NOT_CONTAINS:
            return _op_not_contains
        elif operator == Operator.EQUALS:
            return _op_equals
        elif operator == Operator.NOT_EQUALS:
            return _op_not_equals
        elif operator == Operator.GREATER_THAN:
            return lambda fv, fv2: _compare_numeric(fv, fv2, lambda a, b: a > b)
        elif operator == Operator.LESS_THAN:
            return lambda fv, fv2: _compare_numeric(fv, fv2, lambda a, b: a < b)
        elif operator == Operator.GTE:
            return lambda fv, fv2: _compare_numeric(fv, fv2, lambda a, b: a >= b)
        elif operator == Operator.LTE:
            return lambda fv, fv2: _compare_numeric(fv, fv2, lambda a, b: a <= b)
        else:
            raise ValueError(f"Unknown operator: {operator}")


def _op_contains(field_value: Any, filter_value: str) -> bool:
    return isinstance(field_value, str) and filter_value in field_value


def _op_not_contains(field_value: Any, filter_value: str) -> bool:
    return isinstance(field_value, str) and filter_value not in field_value


def _op_equals(field_value: Any, filter_value: str) -> bool:
    if isinstance(field_value, str) and isinstance(filter_value, str):
        return field_value == filter_value
    try:
        return float(field_value) == float(filter_value)
    except (TypeError, ValueError):
        return str(field_value) == str(filter_value)


def _op_not_equals(field_value: Any, filter_value: str) -> bool:
    if isinstance(field_value, str) and isinstance(filter_value, str):
        return field_value != filter_value
    try:
        return float(field_value) != float(filter_value)
    except (TypeError, ValueError):
        return str(field_value) != str(filter_value)


def _compare_numeric(field_value, filter_value, comparator) -> bool:
    try:
        return comparator(float(field_value), float(filter_value))
    except (TypeError, ValueError):
        return False
