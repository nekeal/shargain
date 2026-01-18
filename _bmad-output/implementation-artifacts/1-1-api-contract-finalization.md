# Story 1.1: Configurable Offer Filters

Status: review

## Story

As a user tracking offers,
I want to configure filters to exclude irrelevant results after scraping,
so that I only receive notifications for offers that truly match my criteria.

## Acceptance Criteria

**AC1: Title Contains Filter** - User can create a filter rule with "title contains [text]"
o only notify on offers where the title contains the specified text (case-insensitive).
`
**AC2: Title Does Not Contain Filter** - User can create a filter rule with "title does not contain [text]" to exclude offers where the title contains the specified text (case-insensitive)`.

**AC3: Configurable Logic Within Groups** - User can create multiple filter rules within a group and choose whether to combine them with AND logic (all must pass) or OR logic (any can pass). For example: "title contains X AND title contains Y" or "title contains X OR title contains Y".

**AC4: Configurable Logic Between Groups** - User can create multiple rule groups and choose how each group connects to the next using AND or OR logic. This enables complex expressions like "(Group1 AND Group2) OR Group3" or "(Group1) AND (Group2 OR Group3)". Each group-to-group connection is independently configurable for maximum flexibility.

**AC5: Filters are Optional** - Filters are completely optional. If no filters are configured, all scraped offers trigger notifications (current behavior is preserved).

**AC6: Frontend Filter UI** - The dashboard provides an intuitive, non-overwhelming interface for adding, editing, and removing filter rules per scraping URL. The UI clearly shows AND/OR logic between rules and rule groups. The filter section feels optional and doesn't clutter the main URL management flow.

**AC7: Extensible Design** - The filter system is designed to support future field types (like "description contains") without requiring major refactoring.

## Tasks / Subtasks

- [x] Design filter data model and schema (AC: #7, #3, #4)
  - [x] Design JSON schema for filter rules with rule groups
  - [x] Support user-configurable logic operators (AND/OR) at both levels
  - [x] Add `logic` field to RuleGroup for combining rules within group
  - [x] Add `logicWithNext` field to RuleGroup for connecting to next group
  - [x] Add JSONField to ScrapingUrl model for filters
  - [x] Create Django migration
  - [x] Define filter operators enum (contains, not_contains, future: equals, regex)
  - [x] Define logic operators enum (and, or)
  - [x] Create Pydantic validation schemas (FilterRule, RuleGroup, FiltersConfig)
  - [x] Implement validate_filters() function with constraint checking
- [x] Implement backend filter evaluation logic (AC: #1, #2, #3, #4, #5)
  - [x] Create OfferFilterService with rule evaluation
  - [x] Implement "contains" operator logic (case-insensitive)
  - [x] Implement "not_contains" operator logic (case-insensitive)
  - [x] Implement configurable AND/OR logic evaluation within rule groups
  - [x] Implement granular AND/OR logic evaluation between rule groups using logicWithNext
  - [x] Integrate filter service into OfferBatchCreateService.\_notify()
  - [x] Ensure filters only apply when configured (preserve current behavior)
- [x] Add filter API endpoints (AC: #1, #2, #3, #4)
  - [x] Add filter field to AddUrlRequest schema
  - [x] Add filter field to ScrapingUrlResponse schema
  - [x] Create endpoint to update filters for existing URL
  - [x] Integrate filter validation in API endpoints (400 errors for invalid filters)
  - [x] Update OpenAPI spec with filter schemas and error responses
- [x] Build frontend filter UI (AC: #6)
  - [x] Design filter UI component (collapsible/expandable section)
  - [x] Implement add/remove filter rule interactions within groups
  - [x] Implement add/remove rule group interactions
  - [x] Display AND/OR logic clearly between rules and groups
  - [x] Display active filters clearly
  - [x] Integrate into URL add/edit forms
- [x] Testing and validation (AC: #1, #2, #3, #4, #5)
  - [x] Write unit tests for filter evaluation logic (both AND and OR)
  - [x] Write integration tests for filtered notifications
  - [x] Test AND logic within groups
  - [x] Test OR logic between groups
  - [x] Test complex combinations (multiple groups with multiple rules)
  - [x] Test edge cases (empty filters, special characters, unicode)
  - [x] Verify no regression for URLs without filters

### Review Follow-ups (AI)

- [x] [AI-Review][HIGH] Add integration test for filter→notification flow - verify filtered offers don't trigger notifications [shargain/offers/tests/test_services.py] - Tests exist in test_batch_create.py and pass
- [x] [AI-Review][MEDIUM] Add `logicWithNext` field to RuleGroupSchema in API layer [shargain/public_api/api.py:122]
- [x] [AI-Review][MEDIUM] Remove incorrect top-level `logic` field from FiltersConfigSchema [shargain/public_api/api.py:133]
- [x] [AI-Review][MEDIUM] Call validate_filters() in add_url_to_target endpoint for consistent validation [shargain/public_api/api.py:245]
- [x] [AI-Review][LOW] Replace `as any` type casts with proper types in OfferFilters integration [frontend/src/components/dashboard/monitored-websites/index.tsx:272]
- [x] [AI-Review][LOW] Simplify FiltersConfig type inference or use generated API types [frontend/src/components/dashboard/monitored-websites/filterValidation.ts:66]

### Review Follow-ups (AI - Second Review 2026-01-18)

- [x] [AI-Review][MEDIUM] Remove `as any` type cast in useUpdateFiltersMutation - breaks type safety and defeats TypeScript validation [frontend/src/components/dashboard/monitored-websites/useMonitors.ts:65]
- [x] [AI-Review][MEDIUM] Add aria-label attributes to icon-only buttons for screen reader accessibility (Filter, ChevronDown, Plus, X, Save icons) [frontend/src/components/dashboard/monitored-websites/OfferFilters.tsx]
- [x] [AI-Review][MEDIUM] Replace console.error with proper error handling - remove/sanitize error logging that may expose user filter configs [frontend/src/components/dashboard/monitored-websites/useMonitors.ts:23,36,54,72]
- [x] [AI-Review][MEDIUM] Add frontend component tests for OfferFilters using Vitest/React Testing Library - verify rendering, validation, mobile behavior, and accessibility [frontend/src/components/dashboard/monitored-websites/OfferFilters.test.tsx]

### UX Improvements (Post-Review)

- [x] Auto-create first empty group when filters section opens (convenience, not forced)
- [x] Accordion-style trigger with chevron icon instead of button
- [x] Logic divider between groups (─── OR ───) for clarity
- [x] Reduced whitespace in rule cards and group containers
- [x] Wider field/operator selects to prevent truncation
- [x] Segmented toggle button for ALL/ANY logic (more discoverable than dropdown)
- [x] Responsive layout - rules stack vertically on mobile
- [x] Empty rules don't count as "configured" - badge only shows actual filters
- [x] Saving empty filters sends null (no false configuration state)
- [x] Added translations for new UI labels (EN + PL)

## Dev Notes

### Critical Context

**This is a BROWNFIELD story** - The scraping and notification system already works. You're adding an optional filtering layer to refine notifications.

**Current Flow:**

```
Scraper → OfferBatchCreateService.run()
  ↓
  create() - Creates Offer objects, returns (offer, created) tuples
  ↓
  _notify() - Sends notifications for new_offers
  ↓
  NewOfferNotificationService.run() - Formats and sends via Telegram/Discord
```

**Where Filters Fit:**
Filters should be applied in `_notify()` BEFORE calling `NewOfferNotificationService`:

```python
# File: shargain/offers/services.py:76-78
def _notify(self, new_offers, scrapping_target):
    if new_offers and scrapping_target.notification_config and scrapping_target.enable_notifications:
        # ADD FILTER LOGIC HERE
        filtered_offers = apply_filters(new_offers, scrapping_target)
        self.notification_service_class(filtered_offers, scrapping_target).run()
```

### Current Offer Model Structure

```python
# File: shargain/offers/models.py:108-140
class Offer(TimeStampedModel):
    url = models.URLField(max_length=1024)
    title = models.CharField(max_length=200)  # PRIMARY FILTER FIELD
    price = models.IntegerField(blank=True, null=True)
    main_image_url = models.URLField(blank=True, max_length=1024)
    source_html = models.FileField(upload_to=get_offer_source_html_path, blank=True)
    list_url = models.URLField(max_length=1024, blank=True)  # The scraping URL
    target = models.ForeignKey("ScrappingTarget", on_delete=models.PROTECT)
    published_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
```

**NOTE:** Currently only `title` field is populated consistently. There is NO `description` field yet, but the design should accommodate it for the future.

### Proposed Filter Data Model

Store filters as JSON on ScrapingUrl model:

```python
# File: shargain/offers/models.py:44-69
class ScrapingUrl(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    url = models.URLField(_("Target URL"), max_length=1024)
    is_active = models.BooleanField(_("Is active"), default=True)
    scraping_target = models.ForeignKey(ScrappingTarget, on_delete=models.CASCADE)

    # ADD THIS:
    filters = models.JSONField(
        verbose_name=_("Notification filters"),
        help_text=_("Filter rules to apply before sending notifications"),
        blank=True,
        null=True,
        default=None  # None = no filters, send all notifications
    )
```

**Filter JSON Schema (with granular logic operators):**

```json
{
  "ruleGroups": [
    {
      "logic": "and",
      "logicWithNext": "or",
      "rules": [
        {
          "field": "title",
          "operator": "contains",
          "value": "apartment",
          "case_sensitive": false
        },
        {
          "field": "title",
          "operator": "not_contains",
          "value": "studio",
          "case_sensitive": false
        }
      ]
    },
    {
      "logic": "and",
      "rules": [
        {
          "field": "title",
          "operator": "contains",
          "value": "flat",
          "case_sensitive": false
        }
      ]
    }
  ]
}
```

**Logic Explanation:**

- `logic`: Controls how rules WITHIN a group are combined ("and" or "or")
- `logicWithNext`: Controls how THIS group connects to the NEXT group ("and" or "or")
  - Last group has no `logicWithNext` (nothing to connect to)
- Example above: `(apartment AND NOT studio) OR (flat)`

**Complex Example:**

```json
{
  "ruleGroups": [
    { "logic": "and", "logicWithNext": "and", "rules": [...] },  // Group1 AND
    { "logic": "or", "logicWithNext": "or", "rules": [...] },    // Group2 OR
    { "logic": "and", "rules": [...] }                            // Group3
  ]
}
```

Evaluates as: `(Group1) AND (Group2) OR (Group3)`

**Simple Filter (single group):**

```json
{
  "ruleGroups": [
    {
      "logic": "and",
      "rules": [
        {
          "field": "title",
          "operator": "contains",
          "value": "apartment",
          "case_sensitive": false
        }
      ]
    }
  ]
}
```

Note: Single group doesn't need `logicWithNext` since there's no next group.

**Supported Operators (MVP):**

- `contains` - Field contains the value (case-insensitive by default)
- `not_contains` - Field does NOT contain the value (case-insensitive by default)

**Future Operators (design for but don't implement):**

- `equals` - Exact match
- `not_equals` - Not an exact match
- `regex` - Regular expression match
- `greater_than`, `less_than` - For numeric fields like price

### Architectural Guardrails

**Django Best Practices:**

- Use JSONField for flexible schema (supported in Django 3.1+, already using Postgres)
- Keep filter logic in a separate service class for testability
- Don't modify the Offer model - filters are configuration, not data

**Filter Service Pattern (with OR logic):**

```python
# File: shargain/offers/services/filter_service.py (NEW FILE)
from shargain.offers.models import Offer, ScrapingUrl

class OfferFilterService:
    def __init__(self, scraping_url: ScrapingUrl):
        self.scraping_url = scraping_url
        self.filters = scraping_url.filters or {}

    def apply_filters(self, offers: list[Offer]) -> list[Offer]:
        """Filter offers based on configured rule groups."""
        if not self.filters or not self.filters.get('ruleGroups'):
            return offers  # No filters = pass all through

        filtered = []
        for offer in offers:
            if self._evaluate_offer(offer):
                filtered.append(offer)
        return filtered

    def _evaluate_offer(self, offer: Offer) -> bool:
        """Evaluate offer against groups using granular logic operators."""
        rule_groups = self.filters.get('ruleGroups', [])

        if not rule_groups:
            return True  # No groups = pass through

        # Evaluate first group
        result = self._evaluate_group(offer, rule_groups[0])

        # Combine remaining groups using their logicWithNext operators
        for i in range(len(rule_groups) - 1):
            current_group = rule_groups[i]
            next_group = rule_groups[i + 1]
            logic_operator = current_group.get('logicWithNext', 'or')  # Default: OR

            next_result = self._evaluate_group(offer, next_group)

            if logic_operator == 'and':
                result = result and next_result
            else:  # 'or'
                result = result or next_result

        return result

    def _evaluate_group(self, offer: Offer, group: dict) -> bool:
        """Check if offer passes rules in group using group's logic operator."""
        rules = group.get('rules', [])
        group_logic = group.get('logic', 'and')  # Default: AND

        if group_logic == 'and':
            # AND logic: ALL rules must pass
            for rule in rules:
                if not self._evaluate_rule(offer, rule):
                    return False
            return True
        else:  # 'or'
            # OR logic: ANY rule can pass
            for rule in rules:
                if self._evaluate_rule(offer, rule):
                    return True
            return False

    def _evaluate_rule(self, offer: Offer, rule: dict) -> bool:
        """Evaluate a single filter rule against an offer."""
        field_value = getattr(offer, rule['field'], '')
        operator = rule['operator']
        filter_value = rule['value']

        # Case-insensitive by default
        if not rule.get('case_sensitive', False):
            field_value = str(field_value).lower()
            filter_value = str(filter_value).lower()

        if operator == 'contains':
            return filter_value in field_value
        elif operator == 'not_contains':
            return filter_value not in field_value
        else:
            raise ValueError(f"Unknown operator: {operator}")
```

**Integration Point:**

```python
# File: shargain/offers/services.py:76-78 (MODIFY)
def _notify(self, new_offers, scrapping_target):
    if new_offers and scrapping_target.notification_config and scrapping_target.enable_notifications:
        # Apply filters per scraping URL
        filtered_offers = self._apply_filters_by_url(new_offers)

        if filtered_offers:
            self.notification_service_class(filtered_offers, scrapping_target).run()

def _apply_filters_by_url(self, offers: list[Offer]) -> list[Offer]:
    """Apply filters grouped by scraping URL."""
    from shargain.offers.services.filter_service import OfferFilterService

    # Group offers by their list_url (the scraping URL)
    offers_by_url = {}
    for offer in offers:
        if offer.list_url not in offers_by_url:
            offers_by_url[offer.list_url] = []
        offers_by_url[offer.list_url].append(offer)

    # Apply filters per URL
    filtered_offers = []
    for list_url, url_offers in offers_by_url.items():
        scraping_url = ScrapingUrl.objects.filter(
            url=list_url,
            scraping_target=self._scrapping_target
        ).first()

        if scraping_url and scraping_url.filters:
            filter_service = OfferFilterService(scraping_url)
            filtered_offers.extend(filter_service.apply_filters(url_offers))
        else:
            # No filters configured = include all offers
            filtered_offers.extend(url_offers)

    return filtered_offers
```

### API Changes Required

**Update ScrapingUrlResponse Schema:**

```python
# File: shargain/public_api/api.py:111-117 (MODIFY)
class ScrapingUrlResponse(BaseSchema):
    id: int
    url: str
    name: str
    is_active: bool
    last_checked_at: str | None = None
    filters: dict | None = None  # ADD THIS
```

**Update AddUrlRequest Schema:**

```python
# File: shargain/public_api/api.py:201-204 (MODIFY)
class AddUrlRequest(BaseSchema):
    url: HttpUrl
    name: str | None = None
    filters: dict | None = None  # ADD THIS
```

**New Endpoint for Updating Filters:**

```python
# File: shargain/public_api/api.py (ADD NEW ENDPOINT)
class UpdateFiltersRequest(BaseSchema):
    filters: dict | None = None

@router.patch(
    "/targets/{target_id}/urls/{url_id}/filters",
    operation_id="update_scraping_url_filters",
    by_alias=True,
    response={200: ScrapingUrlResponse, 404: ErrorSchema},
)
def update_scraping_url_filters(
    request: HttpRequest,
    target_id: int,
    url_id: int,
    payload: UpdateFiltersRequest
):
    actor = get_actor(request)
    try:
        scraping_url = ScrapingUrl.objects.get(
            id=url_id,
            scraping_target_id=target_id,
            scraping_target__owner_id=actor.user_id
        )
        scraping_url.filters = payload.filters
        scraping_url.save()
        return scraping_url
    except ScrapingUrl.DoesNotExist:
        raise HttpError(404, "Scraping URL not found")
```

### Frontend UI/UX Design

**Location:** Within the URL management card/form on the dashboard

**UI Structure:**

```
┌─ Scraping URL Card ─────────────────────────┐
│ Name: Apartments in Warsaw                  │
│ URL: https://olx.pl/...                     │
│ Status: ● Active                            │
│                                             │
│ ┌─ Filters (Optional) ──────┐ ◄─ Collapsed by default
│ │ + Add Filter               │
│ └───────────────────────────┘
│                                             │
│ [Disable] [Delete]                          │
└─────────────────────────────────────────────┘

When expanded with granular logic operators:
┌─ Filters ──────────────────────────────────┐
│ Match offers where:                        │
│                                            │
│ ┌─ Group 1 ──────────────────────────┐    │
│ │ Rules logic: [AND ▼] [OR ▼]        │ ✕  │
│ │ ┌─ Rule 1.1 ───────────────────┐   │    │
│ │ │ Title [contains ▼] "apt"      │ ✕ │    │
│ │ └───────────────────────────────┘   │    │
│ │                                     │    │
│ │ AND  ◄─ Determined by group logic  │    │
│ │                                     │    │
│ │ ┌─ Rule 1.2 ───────────────────┐   │    │
│ │ │ Title [not contains ▼] "studio"│ ✕│   │
│ │ └───────────────────────────────┘   │    │
│ │                                     │    │
│ │ + Add rule to this group            │    │
│ └─────────────────────────────────────┘    │
│                                            │
│ ────── [OR ▼] ────── ◄─ User chooses!     │
│                                            │
│ ┌─ Group 2 ──────────────────────────┐    │
│ │ Rules logic: [AND ▼] [OR ▼]        │ ✕  │
│ │ ┌─ Rule 2.1 ───────────────────┐   │    │
│ │ │ Title [contains ▼] "flat"     │ ✕ │    │
│ │ └───────────────────────────────┘   │    │
│ │                                     │    │
│ │ + Add rule to this group            │    │
│ └─────────────────────────────────────┘    │
│                                            │
│ + Add another group                        │
└────────────────────────────────────────────┘

Logic: (apt AND NOT studio) OR (flat)

User can change to: (apt AND NOT studio) AND (flat)
by changing the dropdown between groups from OR to AND.
```

**Component Structure:**

```tsx
// frontend/src/components/features/url-filters/FilterBuilder.tsx
interface FilterRule {
  field: "title" | "description"; // Extensible
  operator: "contains" | "not_contains" | "equals" | "not_equals";
  value: string;
  caseSensitive?: boolean;
}

interface RuleGroup {
  logic: "and" | "or"; // How to combine rules within this group
  logicWithNext?: "and" | "or"; // How this group connects to next group
  rules: FilterRule[];
}

interface FiltersConfig {
  ruleGroups: RuleGroup[];
}

export function FilterBuilder({
  value,
  onChange,
}: {
  value: FiltersConfig | null;
  onChange: (filters: FiltersConfig | null) => void;
}) {
  // Collapsible section
  // Add/remove rule groups (OR logic between groups)
  // Add/remove rules within groups (AND logic within group)
  // Field selector (only 'title' for MVP)
  // Operator dropdown
  // Value text input
  // Visual indicators for AND/OR logic
}
```

### Testing Requirements

**Backend Tests:**

```python
# File: shargain/offers/tests/services/test_filter_service.py (NEW)
def test_filter_title_contains():
    """Test that 'contains' operator filters correctly."""

def test_filter_title_not_contains():
    """Test that 'not_contains' operator filters correctly."""

def test_multiple_and_rules_in_single_group():
    """Test multiple rules with AND logic within a group."""

def test_or_logic_between_groups():
    """Test that ANY passing group allows the offer through."""

def test_complex_filter_and_or_combination():
    """Test (A AND B) OR (C AND D) logic combinations."""

def test_single_rule_single_group():
    """Test simple filter with one rule in one group."""

def test_no_filters_passes_all():
    """Test that missing filters passes all offers."""

def test_empty_rule_groups_passes_all():
    """Test that empty ruleGroups array passes all offers."""

def test_case_insensitive_matching():
    """Test case-insensitive matching by default."""

def test_unicode_and_special_chars():
    """Test filters with unicode and special characters."""
```

**Integration Tests:**

```python
# File: shargain/offers/tests/test_services.py (MODIFY)
def test_offer_batch_create_with_filters():
    """Test that filtered offers don't trigger notifications."""

def test_offer_batch_create_without_filters():
    """Test backward compatibility - no filters = all notifications."""
```

**Frontend Tests:**

```typescript
// frontend/src/components/features/url-filters/FilterBuilder.test.tsx
describe("FilterBuilder", () => {
  it("starts collapsed and optional");
  it("allows adding rule groups");
  it("allows removing rule groups");
  it("allows adding rules within a group");
  it("allows removing rules from a group");
  it("displays AND between rules in same group");
  it("displays OR between different groups");
  it("validates filter values");
  it("serializes to correct JSON structure");
});
```

### Database Migration

```python
# File: shargain/offers/migrations/000X_add_filters_to_scraping_url.py (NEW)
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('offers', '000X_previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapingurl',
            name='filters',
            field=models.JSONField(
                blank=True,
                default=None,
                help_text='Filter rules to apply before sending notifications',
                null=True,
                verbose_name='Notification filters'
            ),
        ),
    ]
```

### Library/Framework Requirements

**Django JSONField:**

- Already using PostgreSQL (supports native JSON)
- Built-in since Django 3.1 (check current version in pyproject.toml)
- No additional dependencies needed

**Frontend:**

- Use existing shadcn/ui components (Select, Input, Button)
- TanStack Query for API calls (already in use)
- Type-safe with generated API client

### Known Gotchas

⚠️ **Scraping URL vs List URL** - The `Offer.list_url` field stores the URL that was scraped. Match this to `ScrapingUrl.url` to find the right filters.

⚠️ **Multiple URLs per Target** - A user can have multiple scraping URLs in one target. Filters are per-URL, not per-target.

⚠️ **Empty Title Field** - Some scrapers might not populate title. Handle gracefully (empty string should work with contains/not_contains).

⚠️ **Filter Validation** - Validate filter JSON schema on the backend before saving. Invalid filters should return 400 error, not silent failure.

⚠️ **Notification Batching** - Filters are applied before batching messages. This is correct - don't notify about filtered-out offers.

⚠️ **Migration Safety** - Adding a nullable JSONField with default=None is safe. No data migration needed.

### Filter Validation Schema

**Backend Validation with Pydantic:**

Validate filter JSON structure before saving to database. Use Pydantic models for type-safe validation:

```python
# File: shargain/offers/schemas/filter_schemas.py (NEW FILE)
from enum import StrEnum
from pydantic import BaseModel, Field, field_validator


class FilterOperator(StrEnum):
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    # Future operators (validate but don't implement evaluation yet)
    # EQUALS = "equals"
    # NOT_EQUALS = "not_equals"
    # REGEX = "regex"


class FilterField(StrEnum):
    TITLE = "title"
    # Future fields
    # DESCRIPTION = "description"
    # PRICE = "price"


class FilterRule(BaseModel):
    field: FilterField
    operator: FilterOperator
    value: str = Field(..., min_length=1, max_length=200)
    case_sensitive: bool = False

    @field_validator("value")
    @classmethod
    def value_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Filter value cannot be blank or whitespace only")
        return v.strip()


class LogicOperator(StrEnum):
    AND = "and"
    OR = "or"


class RuleGroup(BaseModel):
    logic: LogicOperator = LogicOperator.AND  # How to combine rules within this group
    logic_with_next: LogicOperator | None = Field(None, alias="logicWithNext")  # How this group connects to next group
    rules: list[FilterRule] = Field(..., min_length=1, max_length=10)


class FiltersConfig(BaseModel):
    rule_groups: list[RuleGroup] = Field(
        ...,
        min_length=1,
        max_length=5,
        alias="ruleGroups"
    )

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
```

**Validation Constraints:**

| Constraint              | Value                      | Reason                            |
| ----------------------- | -------------------------- | --------------------------------- |
| Max rule groups         | 5                          | Prevent overly complex filters    |
| Max rules per group     | 10                         | Keep filters manageable           |
| Max value length        | 200 chars                  | Match title field max length      |
| Min value length        | 1 char                     | Prevent empty filter values       |
| Allowed fields (MVP)    | `title` only               | Only consistently populated field |
| Allowed operators (MVP) | `contains`, `not_contains` | Core filtering needs              |

**Integration in API Endpoint:**

```python
# File: shargain/public_api/api.py (MODIFY update_scraping_url_filters)
from shargain.offers.schemas.filter_schemas import validate_filters

@router.patch(
    "/targets/{target_id}/urls/{url_id}/filters",
    operation_id="update_scraping_url_filters",
    by_alias=True,
    response={200: ScrapingUrlResponse, 400: ErrorSchema, 404: ErrorSchema},
)
def update_scraping_url_filters(
    request: HttpRequest,
    target_id: int,
    url_id: int,
    payload: UpdateFiltersRequest
):
    actor = get_actor(request)

    # Validate filter structure before saving
    try:
        validated_filters = validate_filters(payload.filters)
    except ValueError as e:
        raise HttpError(400, str(e))

    try:
        scraping_url = ScrapingUrl.objects.get(
            id=url_id,
            scraping_target_id=target_id,
            scraping_target__owner_id=actor.user_id
        )
        scraping_url.filters = validated_filters
        scraping_url.save()
        return scraping_url
    except ScrapingUrl.DoesNotExist:
        raise HttpError(404, "Scraping URL not found")
```

### Validation Strategy: Frontend-First with Zod

**Architecture:**

| Layer                  | Validation                     | Purpose                              |
| ---------------------- | ------------------------------ | ------------------------------------ |
| **Frontend (Zod)**     | Full validation + translations | UX - immediate feedback, type safety |
| **Backend (Pydantic)** | Basic structure validation     | Security - prevent bad data          |

**Why Frontend-First:**

- ✅ **Type-safe** - Zod infers TypeScript types automatically
- ✅ **Instant feedback** - Errors shown as user types (no API round-trip)
- ✅ **Translatable** - Pass `t()` directly in schema definitions
- ✅ **Single source of truth** - One schema for validation + TypeScript types
- ✅ **Better DX** - Autocomplete, IntelliSense for error handling

**Backend keeps simple errors** - Just returns basic 400 with message string for security fallback.

---

### Frontend Validation with Zod

**Validation Schemas:**

```typescript
// frontend/src/components/dashboard/monitored-websites/filterValidation.ts
import { z } from "zod";
import type { TFunction } from "i18next";

// Constants matching backend constraints
export const FILTER_CONSTRAINTS = {
  MAX_RULE_GROUPS: 5,
  MAX_RULES_PER_GROUP: 10,
  MAX_VALUE_LENGTH: 200,
  ALLOWED_FIELDS: ["title"] as const,
  ALLOWED_OPERATORS: ["contains", "not_contains"] as const,
  ALLOWED_LOGIC: ["and", "or"] as const,
} as const;

// Schema factory - accepts translation function for localized messages
export const createFilterSchemas = (t: TFunction) => {
  const filterRuleSchema = z.object({
    field: z.enum(FILTER_CONSTRAINTS.ALLOWED_FIELDS, {
      errorMap: () => ({ message: t("filters.errors.invalidField") }),
    }),
    operator: z.enum(FILTER_CONSTRAINTS.ALLOWED_OPERATORS, {
      errorMap: () => ({ message: t("filters.errors.invalidOperator") }),
    }),
    value: z
      .string()
      .min(1, { message: t("filters.errors.valueEmpty") })
      .max(FILTER_CONSTRAINTS.MAX_VALUE_LENGTH, {
        message: t("filters.errors.valueTooLong", {
          maxLength: FILTER_CONSTRAINTS.MAX_VALUE_LENGTH,
        }),
      })
      .transform((v) => v.trim())
      .refine((v) => v.length > 0, {
        message: t("filters.errors.valueOnlyWhitespace"),
      }),
    caseSensitive: z.boolean().default(false),
  });

  const ruleGroupSchema = z.object({
    logic: z
      .enum(FILTER_CONSTRAINTS.ALLOWED_LOGIC, {
        errorMap: () => ({ message: t("filters.errors.invalidLogic") }),
      })
      .default("and"),
    logicWithNext: z.enum(FILTER_CONSTRAINTS.ALLOWED_LOGIC).optional(),
    rules: z
      .array(filterRuleSchema)
      .min(1, { message: t("filters.errors.groupMustHaveRules") })
      .max(FILTER_CONSTRAINTS.MAX_RULES_PER_GROUP, {
        message: t("filters.errors.tooManyRules", {
          maxRules: FILTER_CONSTRAINTS.MAX_RULES_PER_GROUP,
        }),
      }),
  });

  const filtersConfigSchema = z.object({
    ruleGroups: z
      .array(ruleGroupSchema)
      .min(1, { message: t("filters.errors.noGroups") })
      .max(FILTER_CONSTRAINTS.MAX_RULE_GROUPS, {
        message: t("filters.errors.tooManyGroups", {
          maxGroups: FILTER_CONSTRAINTS.MAX_RULE_GROUPS,
        }),
      }),
  });

  return {
    filterRuleSchema,
    ruleGroupSchema,
    filtersConfigSchema,
  };
};

// Type inference from schema
export type FilterRule = z.infer<
  ReturnType<typeof createFilterSchemas>["filterRuleSchema"]
>;
export type RuleGroup = z.infer<
  ReturnType<typeof createFilterSchemas>["ruleGroupSchema"]
>;
export type FiltersConfig = z.infer<
  ReturnType<typeof createFilterSchemas>["filtersConfigSchema"]
>;
```

**Using Validation in Component:**

```tsx
// frontend/src/components/dashboard/monitored-websites/OfferFilters.tsx
import { useTranslation } from "react-i18next";
import { createFilterSchemas, type FiltersConfig } from "./filterValidation";

export function OfferFilters({
  targetId,
  urlId,
  initialFilters,
}: OfferFiltersProps) {
  const { t } = useTranslation();
  const [validationErrors, setValidationErrors] = useState<z.ZodError | null>(
    null,
  );

  // Create schemas with current translation function
  const { filtersConfigSchema } = useMemo(() => createFilterSchemas(t), [t]);

  // Validate on change (debounced) or before save
  const validateFilters = (filters: FiltersConfig | null): boolean => {
    if (!filters) {
      setValidationErrors(null);
      return true; // No filters is valid
    }

    const result = filtersConfigSchema.safeParse(filters);

    if (!result.success) {
      setValidationErrors(result.error);
      return false;
    }

    setValidationErrors(null);
    return true;
  };

  // Get error for specific field path
  const getFieldError = (path: string): string | undefined => {
    if (!validationErrors) return undefined;

    const error = validationErrors.errors.find(
      (e) => e.path.join(".") === path || e.path.join(".").startsWith(path),
    );

    return error?.message;
  };

  // Example: Get error for rule value input
  // getFieldError(`ruleGroups.${groupIndex}.rules.${ruleIndex}.value`)

  const handleSave = () => {
    if (!validateFilters(filters)) {
      return; // Don't save if validation fails
    }
    saveMutation.mutate();
  };

  // ... rest of component
}
```

**Inline Error Display:**

```tsx
{
  /* Value Input with inline error */
}
<div className="flex-1">
  <Label className="text-xs text-gray-600 mb-1">{t("filters.value")}</Label>
  <Input
    value={rule.value}
    onChange={(e) =>
      updateRule(groupIndex, ruleIndex, { value: e.target.value })
    }
    className={cn(
      "bg-white border-gray-300",
      getFieldError(`ruleGroups.${groupIndex}.rules.${ruleIndex}.value`)
        ? "border-red-500 focus:border-red-500 focus:ring-red-500"
        : "focus:border-violet-500 focus:ring-violet-500",
    )}
  />
  {getFieldError(`ruleGroups.${groupIndex}.rules.${ruleIndex}.value`) && (
    <p className="text-xs text-red-600 mt-1">
      {getFieldError(`ruleGroups.${groupIndex}.rules.${ruleIndex}.value`)}
    </p>
  )}
</div>;
```

---

### Translation Files

```json
// frontend/public/locales/en/translation.json
{
  "filters": {
    "title": "Smart Filters",
    "noFilters": "All offers will notify",
    "rulesCount": "{{count}} active rule(s)",
    "errors": {
      "valueEmpty": "Filter value cannot be empty",
      "valueOnlyWhitespace": "Filter value cannot be only whitespace",
      "valueTooLong": "Filter value too long (max {{maxLength}} characters)",
      "tooManyGroups": "Maximum {{maxGroups}} rule groups allowed",
      "tooManyRules": "Maximum {{maxRules}} rules per group allowed",
      "groupMustHaveRules": "Each group must have at least one rule",
      "invalidOperator": "Invalid filter operator",
      "invalidField": "Invalid filter field",
      "invalidLogic": "Invalid logic operator",
      "noGroups": "At least one rule group is required",
      "saveFailed": "Failed to save filters. Please try again."
    }
  }
}
```

```json
// frontend/public/locales/pl/translation.json
{
  "filters": {
    "title": "Inteligentne filtry",
    "noFilters": "Wszystkie oferty będą powiadamiać",
    "rulesCount": "{{count}} aktywna reguła/reguł",
    "errors": {
      "valueEmpty": "Wartość filtra nie może być pusta",
      "valueOnlyWhitespace": "Wartość filtra nie może składać się tylko z białych znaków",
      "valueTooLong": "Wartość filtra zbyt długa (max {{maxLength}} znaków)",
      "tooManyGroups": "Maksymalnie {{maxGroups}} grup reguł dozwolone",
      "tooManyRules": "Maksymalnie {{maxRules}} reguł na grupę dozwolone",
      "groupMustHaveRules": "Każda grupa musi mieć przynajmniej jedną regułę",
      "invalidOperator": "Nieprawidłowy operator filtra",
      "invalidField": "Nieprawidłowe pole filtra",
      "invalidLogic": "Nieprawidłowy operator logiczny",
      "noGroups": "Wymagana jest przynajmniej jedna grupa reguł",
      "saveFailed": "Nie udało się zapisać filtrów. Spróbuj ponownie."
    }
  }
}
```

---

### Backend Error Handling (Simplified)

Backend keeps simple error messages - just for security fallback:

```python
# File: shargain/public_api/api.py

@router.patch("/targets/{target_id}/urls/{url_id}/filters", ...)
def update_scraping_url_filters(...):
    # Pydantic validation happens automatically via payload type
    # If it fails, Django Ninja returns 422 with validation details

    # For business logic errors, return simple messages
    try:
        scraping_url = ScrapingUrl.objects.get(...)
    except ScrapingUrl.DoesNotExist:
        raise HttpError(404, "Scraping URL not found")

    # Save filters (already validated by Pydantic schema)
    scraping_url.filters = filters_dict
    scraping_url.save()

    return ScrapingUrlDTO.from_orm(scraping_url)
```

**Backend Error Response Format (simple):**

```json
{
  "detail": "Scraping URL not found"
}
```

Or for Pydantic validation errors (422):

```json
{
  "detail": [
    {
      "loc": ["body", "filters", "ruleGroups", 0, "rules", 0, "value"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

**Frontend handles 422 as generic error** - since frontend validation should catch these first:

```tsx
const handleSaveError = (error: unknown) => {
  // If backend returns 422, show generic message
  // (Frontend validation should have caught this)
  toast.error(t("filters.errors.saveFailed"));
};
```

**Client-Side Validation (prevent most errors before API call):**

```tsx
// frontend/src/components/features/url-filters/validation.ts
import { z } from "zod";

export const filterRuleSchema = z.object({
  field: z.enum(["title"]),
  operator: z.enum(["contains", "not_contains"]),
  value: z
    .string()
    .min(1, "Filter value is required")
    .max(200, "Filter value is too long (max 200 characters)")
    .transform((v) => v.trim())
    .refine((v) => v.length > 0, "Filter value cannot be only whitespace"),
  caseSensitive: z.boolean().default(false),
});

export const ruleGroupSchema = z.object({
  rules: z
    .array(filterRuleSchema)
    .min(1, "Each group must have at least one rule")
    .max(10, "Maximum 10 rules per group"),
});

export const filtersConfigSchema = z.object({
  ruleGroups: z
    .array(ruleGroupSchema)
    .min(1, "At least one filter group is required")
    .max(5, "Maximum 5 filter groups allowed"),
});

export type FiltersConfig = z.infer<typeof filtersConfigSchema>;
```

### Implementation Approach

**Recommended Order:**

1. **Backend Foundation (3-4 hours):**
   - Add filters JSONField to ScrapingUrl model
   - Create and run migration
   - Create OfferFilterService with filter evaluation logic
   - Implement AND logic within groups
   - Implement OR logic between groups
   - Write unit tests for both AND and OR logic

2. **Integration (1-2 hours):**
   - Modify OfferBatchCreateService.\_notify() to use filters
   - Write integration tests
   - Verify backward compatibility (no regressions)

3. **API Layer (1 hour):**
   - Update ScrapingUrlResponse and AddUrlRequest schemas
   - Add PATCH endpoint for updating filters
   - Regenerate OpenAPI spec and frontend client

4. **Frontend UI (3-4 hours):**
   - Build FilterBuilder component with rule groups
   - Implement add/remove group functionality
   - Implement add/remove rule within group functionality
   - Display AND/OR visual indicators clearly
   - Integrate into URL add/edit forms
   - Style with shadcn/ui components
   - Add client-side validation

5. **Testing & Polish (1-2 hours):**
   - End-to-end testing with real scraping
   - Test complex OR logic scenarios
   - Edge case testing
   - UI/UX polish
   - Documentation updates

**Total Estimated Effort:** 8-12 hours (includes OR logic implementation)

### Future Enhancements (Out of Scope)

- Nested AND/OR logic (groups within groups)
- Price range filters (greater_than, less_than)
- Regular expression matching
- Description field filters (when description scraping is added)
- Filter templates/presets
- Filter statistics (how many offers filtered out)
- Filter preview/testing (show which recent offers would match)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

No debug logs required - all tests passed successfully.

### Completion Notes List

**Backend Implementation Completed:**

- ✅ Implemented filter data model with Pydantic validation (FilterRule, RuleGroup, FiltersConfig)
- ✅ Created OfferFilterService with AND/OR logic evaluation (rules within groups use AND, groups use OR)
- ✅ Integrated filter service into OfferBatchCreateService.\_notify() for automatic filtering before notifications
- ✅ Added JSONField to ScrapingUrl model with Django migration
- ✅ Created comprehensive unit tests (34 tests covering all filter scenarios including edge cases)
- ✅ All 92 offers app tests passing with zero regressions

**API Endpoints Completed:**

- ✅ Created strongly-typed API schemas (FilterRuleSchema, RuleGroupSchema, FiltersConfigSchema)
- ✅ Added typed filters field to ScrapingUrlResponse and AddUrlRequest schemas (no generic dict!)
- ✅ Implemented filter validation in add_url_to_target endpoint with 400 error handling
- ✅ Created new PATCH /targets/{target_id}/urls/{url_id}/filters endpoint for updating filters
- ✅ Updated add_scraping_url command and ScrapingUrlDTO to handle filters
- ✅ Integrated validate_filters() function across all endpoints
- ✅ Full type safety with automatic OpenAPI/Swagger documentation generation

**Frontend Implementation Completed:**

- ✅ Implemented responsive OfferFilters component with collapsible UI
- ✅ Created Zod validation schemas with i18n support for localized error messages
- ✅ Integrated with TanStack Query for state management
- ✅ Added translations for English and Polish
- ✅ Implemented UX improvements (auto-create first group, accordion trigger, logic dividers, segmented toggles)

**Post-Review Fixes Completed (2026-01-18 - First Review):**

- ✅ Added `logic_with_next` field to RuleGroupSchema in API layer for granular group-to-group logic control
- ✅ Removed incorrect top-level `logic` field from FiltersConfigSchema (logic is per-group, not global)
- ✅ Added validate_filters() call in add_url_to_target endpoint with proper error handling (400 on invalid filters)
- ✅ Fixed integration tests in test_batch_create.py - tests now properly verify filter→notification flow
- ✅ Replaced `as any` type cast with proper `FiltersConfigSchema` type from generated API types
- ✅ Simplified FiltersConfig type inference using base Zod schemas (separated from i18n validation schemas)

**Post-Review Fixes Completed (2026-01-18 - Second Review):**

- ✅ Removed `as any` type cast in useUpdateFiltersMutation - now uses generated API type `FiltersConfigSchema` for full type safety
- ✅ Added aria-label attributes to all icon-only buttons (expand/collapse, toggle logic, delete group, delete rule) for screen reader accessibility
- ✅ Replaced console.error calls with proper error handling - removed redundant logging that exposed filter configs in console
- ✅ Added comprehensive frontend component tests (13 tests) using Vitest and React Testing Library covering rendering, user interactions, validation, and accessibility
- ✅ All frontend tests passing (13/13)
- ✅ All backend tests passing (95/95)

### File List

**New Files:**

- shargain/offers/schemas/**init**.py
- shargain/offers/schemas/offer_filter.py
- shargain/offers/services/**init**.py
- shargain/offers/services/filter_service.py
- shargain/offers/tests/services/**init**.py
- shargain/offers/tests/services/test_filter_service.py
- shargain/offers/tests/services/test_batch_create.py (post-review)
- shargain/offers/tests/test_filter_schemas.py
- shargain/offers/migrations/0018_add_filters_to_scraping_url.py

**Modified Files:**

- shargain/offers/models.py (added filters JSONField to ScrapingUrl)
- shargain/offers/services.py → shargain/offers/services/batch_create.py (reorganized into package, added filter integration)
- shargain/offers/application/commands/add_scraping_url.py (added filters parameter)
- shargain/offers/application/dto.py (added filters to ScrapingUrlDTO)
- shargain/public_api/api.py (added filter endpoints and validation)

**New Files (Frontend):**

- frontend/src/components/dashboard/monitored-websites/filterValidation.ts
- frontend/src/components/dashboard/monitored-websites/OfferFilters.tsx
- frontend/src/components/dashboard/monitored-websites/OfferFilters.test.tsx
- frontend/src/components/ui/alert.tsx
- frontend/src/test/setup.ts
- frontend/vitest.config.ts

**Modified Files (Frontend):**

- frontend/src/components/dashboard/monitored-websites/useMonitors.ts
- frontend/src/components/dashboard/monitored-websites/index.tsx
- frontend/src/locales/en/translation.json
- frontend/src/locales/pl/translation.json
- frontend/vite.config.ts
