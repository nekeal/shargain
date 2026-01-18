"""Filter validation schemas for offer notifications.

This module provides Pydantic models for validating filter configurations
that determine which scraped offers trigger notifications.
"""

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class FilterOperator(StrEnum):
    """Supported filter operators for matching offer fields.

    Future operators (not yet implemented):
    - equals: Exact match
    - not_equals: Not an exact match
    - regex: Regular expression match
    """

    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"


class LogicOperator(StrEnum):
    """Logical operators for combining filter rules or groups."""

    AND = "and"
    OR = "or"


class FilterField(StrEnum):
    """Supported fields for filtering offers.

    Future fields (not yet implemented):
    - description: Filter on offer description
    - price: Filter on numeric price values
    """

    TITLE = "title"


class FilterRule(BaseModel):
    """A single filter rule for matching offer attributes.

    Args:
        field: The offer field to filter on (e.g., "title")
        operator: The comparison operator (e.g., "contains")
        value: The value to match against
        case_sensitive: Whether matching should be case-sensitive (default: False)
    """

    field: FilterField
    operator: FilterOperator
    value: str = Field(..., min_length=1, max_length=200)
    case_sensitive: bool = False

    @field_validator("value")
    @classmethod
    def value_not_blank(cls, v: str) -> str:
        """Validate that filter value is not empty or whitespace only."""
        if not v.strip():
            raise ValueError("Filter value cannot be blank or whitespace only")
        return v.strip()


class RuleGroup(BaseModel):
    """A group of filter rules combined with configurable logic.

    Args:
        rules: List of filter rules to evaluate
        logic: How to combine rules ("and" or "or", default: "and")
        logic_with_next: How this group connects to the next one ("and" or "or")
    """

    rules: list[FilterRule] = Field(..., min_length=1, max_length=10)
    logic: LogicOperator = LogicOperator.AND
    logic_with_next: LogicOperator | None = Field(None, alias="logicWithNext")


class FiltersConfig(BaseModel):
    """Complete filter configuration with rule groups.

    Example with mixed logic between groups:
        {
            "ruleGroups": [
                {
                    "logic": "and",
                    "logicWithNext": "or",
                    "rules": [
                        {"field": "title", "operator": "contains", "value": "apartment"},
                        {"field": "title", "operator": "not_contains", "value": "studio"}
                    ]
                },
                {
                    "logic": "and",
                    "rules": [
                        {"field": "title", "operator": "contains", "value": "flat"}
                    ]
                }
            ]
        }

    This represents: (title contains "apartment" AND NOT "studio") OR (title contains "flat")
    """

    rule_groups: list[RuleGroup] = Field(..., min_length=1, max_length=5, alias="ruleGroups")

    class Config:
        populate_by_name = True


def validate_filters(filters_data: dict | None) -> dict | None:
    """Validate filter JSON and return normalized structure.

    Args:
        filters_data: Raw filter JSON from API request

    Returns:
        Validated and normalized filter dict, or None if no filters

    Raises:
        ValueError: If filter structure is invalid
    """
    if filters_data is None:
        return None

    if not filters_data:  # Empty dict
        return None

    try:
        validated = FiltersConfig.model_validate(filters_data)
        return validated.model_dump(by_alias=True)
    except Exception as e:
        raise ValueError(f"Invalid filter configuration: {e}") from e
