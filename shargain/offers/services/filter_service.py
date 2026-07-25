"""Service for filtering offers based on configured rules before sending notifications."""

from collections.abc import Callable
from typing import Any

from shargain.offers.schemas.field_plugin import ExtractedOffer


class OfferFilterService:
    """Service to filter offers based on rule groups with configurable logic.

    Operates on ExtractedOffer fields only — does not access the Offer model.
    """

    def __init__(self, filters: dict | None):
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

    def _evaluate_group(self, offer: ExtractedOffer, group: dict) -> bool:
        rules = group.get("rules", [])
        group_logic = group.get("logic", "and")
        if group_logic == "and":
            for rule in rules:
                if not self._evaluate_rule(offer, rule):
                    return False
            return True
        else:
            for rule in rules:
                if self._evaluate_rule(offer, rule):
                    return True
            return False

    def _evaluate_rule(self, offer: ExtractedOffer | Any, rule: dict) -> bool:
        field_name = rule["field"]
        operator = rule["operator"]
        filter_value = rule["value"]

        if isinstance(offer, ExtractedOffer):
            field_value = offer.fields.get(field_name)
        else:
            field_value = getattr(offer, field_name, "")
        if field_value is None:
            return False

        if not rule.get("case_sensitive", False):
            if isinstance(field_value, str) and isinstance(filter_value, str):
                field_value = field_value.lower()
                filter_value = filter_value.lower()

        handler = self._get_operator_handler(operator)
        return handler(field_value, filter_value)

    def _get_operator_handler(self, operator: str) -> Callable:
        if operator == "contains":
            return _op_contains
        elif operator == "not_contains":
            return _op_not_contains
        elif operator == "equals":
            return _op_equals
        elif operator == "not_equals":
            return _op_not_equals
        elif operator == "greater_than":
            return lambda fv, fv2: _compare_numeric(fv, fv2, lambda a, b: a > b)
        elif operator == "less_than":
            return lambda fv, fv2: _compare_numeric(fv, fv2, lambda a, b: a < b)
        elif operator == "gte":
            return lambda fv, fv2: _compare_numeric(fv, fv2, lambda a, b: a >= b)
        elif operator == "lte":
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
