# Story 1.9: Refactor to Offer Quota Model

**Status**: Approved

## Story

**As a** developer,
**I want** to refactor the offer limiting mechanism to use a dedicated `OfferQuota` model,
**so that** we establish a scalable foundation for a future subscription and billing system.

## Acceptance Criteria

*   **AC1**: A new `OfferQuota` model exists in the `offers` application. It contains fields for `target`, `max_offers_per_period` (nullable for unlimited offers), `used_offers_count`, `period_start`, and `period_end` (nullable for indefinite periods).
*   **AC2**: A new `QuotaService` exists in `offers.services` and acts as a facade for all quota-related operations. It is the sole public interface for the quota system.
*   **AC3**: The `QuotaService` has a `get_active_quota(target)` method that returns the single currently active quota object for a given target, or `None`.
*   **AC4**: The `QuotaService` has a `set_new_quota(...)` method that idempotently creates or updates an `OfferQuota` record.
*   **AC5**: The offer creation logic is refactored to use `QuotaService.get_active_quota()` to check if a target can have new offers created.
*   **AC6**: If an active quota exists and the limit has been reached, the offer is discarded. Otherwise, the `used_offers_count` is incremented upon successful creation.
*   **AC7**: If no active quota is found, the check passes by default, allowing offer creation to proceed.
*   **AC8**: New quotas can be created even if periods overlap with existing quotas for a given target. When multiple quotas are active for a target, the one with the latest `period_start` takes precedence.

## Tasks / Subtasks

*   **[x] Task 1: Implement `OfferQuota` Model** (AC: #1)
    *   [x] Create the `OfferQuota` model in `shargain/offers/models.py`.
    *   [x] Generate and apply the database migration.
*   **[x] Task 2: Implement `QuotaService` Facade** (AC: #2, #3, #4)
    *   [x] Create a new file `shargain/offers/services/quota.py`.
    *   [x] Implement the `QuotaService` class.
    *   [x] Add the `get_active_quota` method with the required query logic.
    *   [x] Add the `set_new_quota` method with the create/update logic.
*   **[x] Task 3: Refactor Offer Creation Logic** (AC: #5, #6, #7)
    *   [x] Locate the existing service responsible for saving new offers.
    *   [x] Modify it to use the new `QuotaService` for checking limits and incrementing usage.
*   **[x] Task 4: Update Architecture Document**
    *   [x] Modify `docs/project-architecture.md` to include the new `OfferQuota` data model.
    *   [x] Document the `QuotaService` as the official internal API and facade for managing quotas.
*   **[x] Task 5: Add Tests**
    *   [x] Write unit tests for the `QuotaService` methods, covering all scenarios (no quota, active quota, limit reached, etc.).
    *   [x] Write integration tests for the offer creation flow to verify the facade is used correctly.

## Dev Notes

#### Relevant Architecture
*   **Backend:** Django, Celery, PostgreSQL
*   **Models:** A new `offers.OfferQuota` model will be created.
*   **Logic:** A new `offers.services.QuotaService` will be created to act as a facade for all quota management. This service encapsulates the business logic for checking, setting, and enforcing offer limits, providing a clean API for the rest of the application. The service supports overlapping quota periods with precedence given to the quota with the latest `period_start`. The service handles nullable `period_end` for indefinite periods and nullable `max_offers_per_period` for unlimited offers.
*   **Data classes:** A new `QuotaInfo` data class will be created to represent quota information. This isolates the database model from the rest of the application.

#### Relevant Source Tree
*   `shargain/offers/models.py` (To add the new `OfferQuota` model)
*   `shargain/offers/services/quota.py` (New file for the `QuotaService` facade)
*   `shargain/offers/services/offer_creation.py` (Or similar existing service to be refactored)
*   `docs/architecture/` (To be updated with the new service)

#### Testing
*   **Test file location**: `shargain/offers/tests/`
*   **Test standards**: Use `pytest` and `pytest-django`.
*   **Test data requirements**: Test the `QuotaService` thoroughly by creating `User` and `OfferQuota` instances to simulate various states.

## Change Log

| Date       | Version | Description                            | Author             |
| :--------- | :------ | :------------------------------------- | :----------------- |
| 2025-10-06 | 1.0     | Initial Draft                          | Bob (Scrum Master) |
| 2025-10-06 | 1.1     | Revised to use per-target offer limits | Bob (Scrum Master) |
| 2025-10-09 | 2.0     | Refactored to use `OfferQuota` model   | Bob (Scrum Master) |
| 2025-10-09 | 3.0     | Redesigned to use `QuotaService` facade| Bob (Scrum Master) |
| 2025-10-20 | 3.1     | Updated to allow overlapping periods with latest period_start precedence | John (Product Manager) |
| 2025-10-21 | 3.2     | Proposed nullable period_end and max_offers_per_period for indefinite periods and unlimited offers | John (Product Manager) |

## Proposed Changes Requiring SM Team Confirmation

The following changes are proposed to enhance the flexibility of the offer quota system:

1. **Nullable `period_end`**: Allow `period_end` field to be nullable to support indefinite subscription periods
2. **Nullable `max_offers_per_period`**: Allow `max_offers_per_period` to be nullable to indicate unlimited offers

### Business Justification
- Enables promotional periods with no fixed end date
- Allows unlimited offer subscriptions (e.g., enterprise plans)
- Provides flexibility for special customer arrangements

### Technical Considerations
- Updated business logic in `QuotaService` to handle nullable fields
- Updated validation and query logic to account for null values
- Proper handling of "unlimited" state in the UI

**Next Steps**: Awaiting confirmation from Scrum Master team before implementing these changes.
