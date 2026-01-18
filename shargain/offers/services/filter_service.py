"""Service for filtering offers based on configured rules before sending notifications."""

from shargain.offers.models import Offer


class OfferFilterService:
    """Service to filter offers based on rule groups with configurable logic.

    Rule evaluation logic:
    - Rules within a group are combined per group's logic operator (AND/OR)
    - Groups are combined per config's logic operator (AND/OR)
    - No filters configured = all offers pass through
    """

    def __init__(self, filters: dict | None):
        """Initialize filter service with filter configuration.

        Args:
            filters: The filter configuration dict (from JSONField)
        """
        self.filters = filters or {}

    def apply_filters(self, offers: list[Offer]) -> list[Offer]:
        """Filter offers based on configured rule groups.

        Args:
            offers: List of offers to filter

        Returns:
            List of offers that pass the filters. If no filters configured,
            all offers pass through.
        """
        if not self.filters or not self.filters.get("ruleGroups"):
            return offers  # No filters = pass all through

        filtered = []
        for offer in offers:
            if self._evaluate_offer(offer):
                filtered.append(offer)
        return filtered

    def _evaluate_offer(self, offer: Offer) -> bool:
        """Evaluate offer against groups using granular logic operators.

        Args:
            offer: The offer to evaluate

        Returns:
            True if offer passes per configured logic, False otherwise
        """
        rule_groups = self.filters.get("ruleGroups", [])

        if not rule_groups:
            return True  # No groups = pass through

        # Evaluate first group
        result = self._evaluate_group(offer, rule_groups[0])

        # Combine remaining groups using their logicWithNext operators
        for i in range(len(rule_groups) - 1):
            current_group = rule_groups[i]
            next_group = rule_groups[i + 1]
            logic_operator = current_group.get("logicWithNext", "or")  # Default: OR

            next_result = self._evaluate_group(offer, next_group)

            if logic_operator == "and":
                result = result and next_result
            else:  # 'or'
                result = result or next_result

        return result

    def _evaluate_group(self, offer: Offer, group: dict) -> bool:
        """Check if offer passes rules in group using configured logic operator.

        Args:
            offer: The offer to evaluate
            group: Dictionary containing list of rules and logic operator

        Returns:
            True if rules pass per configured logic, False otherwise
        """
        rules = group.get("rules", [])
        group_logic = group.get("logic", "and")  # Default: AND

        if group_logic == "and":
            # AND logic: ALL rules must pass
            for rule in rules:
                if not self._evaluate_rule(offer, rule):
                    return False
            return True  # All rules passed
        else:  # OR logic
            # OR logic: ANY rule can pass
            for rule in rules:
                if self._evaluate_rule(offer, rule):
                    return True
            return False  # No rules passed

    def _evaluate_rule(self, offer: Offer, rule: dict) -> bool:
        """Evaluate a single filter rule against an offer.

        Args:
            offer: The offer to evaluate
            rule: Dictionary with field, operator, value, and case_sensitive

        Returns:
            True if rule passes, False if it fails

        Raises:
            ValueError: If operator is not supported
        """
        field_value = getattr(offer, rule["field"], "")
        operator = rule["operator"]
        filter_value = rule["value"]

        # Case-insensitive by default
        if not rule.get("case_sensitive", False):
            # Treat None as empty string before lowercasing
            field_value = str(field_value or "").lower()
            filter_value = str(filter_value).lower()

        if operator == "contains":
            return filter_value in field_value
        elif operator == "not_contains":
            return filter_value not in field_value
        else:
            raise ValueError(f"Unknown operator: {operator}")
