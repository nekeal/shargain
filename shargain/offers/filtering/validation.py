"""URL-aware filter validation service."""

from shargain.offers.field_extraction.plugin import ListUrl
from shargain.offers.field_extraction.resolver import OfferFieldResolver
from shargain.offers.filtering.schemas import validate_filters


def validate_filters_for_url(filters_data: dict | None, url: str) -> dict | None:
    """Validate filters against available fields for the given URL.

    Args:
        filters_data: Raw filter JSON from API request
        url: The listing URL to validate against

    Returns:
        Validated and normalized filter dict, or None if no filters

    Raises:
        ValueError: If filter structure is invalid or references unavailable fields/operators
    """
    validated = validate_filters(filters_data)
    if validated is None:
        return None

    available = OfferFieldResolver.get_fields(ListUrl(url))
    available_map = {f.name: f for f in available}

    for group in validated.get("ruleGroups", []):
        for rule in group.get("rules", []):
            field_name = rule["field"]
            operator = rule["operator"]
            field_def = available_map.get(field_name)
            if field_def is None:
                raise ValueError(f"Field '{field_name}' is not available for this URL")
            if field_def.allowed_operators:
                allowed_op_values = {op.value for op in field_def.allowed_operators}
                if operator not in allowed_op_values:
                    raise ValueError(
                        f"Operator '{operator}' is not valid for field '{field_name}'. "
                        f"Allowed: {', '.join(sorted(allowed_op_values))}"
                    )
    return validated
