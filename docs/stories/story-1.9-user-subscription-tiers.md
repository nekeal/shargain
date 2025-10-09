# Story 1.9: Refactor to Offer Quota Model

**Status**: Approved

## Story

**As a** developer,
**I want** to refactor the offer limiting mechanism to use a dedicated `OfferQuota` model,
**so that** we establish a scalable foundation for a future subscription and billing system.

## Acceptance Criteria

*   **AC1**: A new `OfferQuota` model exists in the `offers` application. It contains fields for `user`, `target`, `max_offers_per_period`, `used_offers_count`, `period_start`, and `period_end`.
*   **AC2**: A new `QuotaService` exists in `offers.services` and acts as a facade for all quota-related operations. It is the sole public interface for the quota system.
*   **AC3**: The `QuotaService` has a `get_active_quota(user, target)` method that returns the single currently active quota object for a given user and target, or `None`.
*   **AC4**: The `QuotaService` has a `set_new_quota(...)` method that idempotently creates or updates an `OfferQuota` record.
*   **AC5**: The offer creation logic is refactored to use `QuotaService.get_active_quota()` to check if a user can create an offer.
*   **AC6**: If an active quota exists and the limit has been reached, the offer is discarded. Otherwise, the `used_offers_count` is incremented upon successful creation.
*   **AC7**: If no active quota is found, the check passes by default, allowing offer creation to proceed.

## Tasks / Subtasks

*   **[ ] Task 1: Implement `OfferQuota` Model** (AC: #1)
    *   [ ] Create the `OfferQuota` model in `shargain/offers/models.py`.
    *   [ ] Generate and apply the database migration.
*   **[ ] Task 2: Implement `QuotaService` Facade** (AC: #2, #3, #4)
    *   [ ] Create a new file `shargain/offers/services/quota.py`.
    *   [ ] Implement the `QuotaService` class.
    *   [ ] Add the `get_active_quota` method with the required query logic.
    *   [ ] Add the `set_new_quota` method with the create/update logic.
*   **[ ] Task 3: Refactor Offer Creation Logic** (AC: #5, #6, #7)
    *   [ ] Locate the existing service responsible for saving new offers.
    *   [ ] Modify it to use the new `QuotaService` for checking limits and incrementing usage.
*   **[ ] Task 4: Update Architecture Document**
    *   [ ] Modify `docs/architecture.md` to include the new `OfferQuota` data model.
    *   [ ] Document the `QuotaService` as the official internal API and facade for managing quotas.
*   **[ ] Task 5: Add Tests**
    *   [ ] Write unit tests for the `QuotaService` methods, covering all scenarios (no quota, active quota, limit reached, etc.).
    *   [ ] Write integration tests for the offer creation flow to verify the facade is used correctly.

## Dev Notes

#### Relevant Architecture
*   **Backend:** Django, Celery, PostgreSQL
*   **Models:** A new `offers.OfferQuota` model will be created.
*   **Logic:** A new `offers.services.QuotaService` will be created to act as a facade for all quota management. This service encapsulates the business logic for checking, setting, and enforcing offer limits, providing a clean API for the rest of the application.

#### Relevant Source Tree
*   `shargain/offers/models.py` (To add the new `OfferQuota` model)
*   `shargain/offers/services/quota.py` (New file for the `QuotaService` facade)
*   `shargain/offers/services/offer_creation.py` (Or similar existing service to be refactored)
*   `docs/architecture.md` (To be updated with the new service)

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
