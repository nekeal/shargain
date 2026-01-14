# Story 1.10: Frontend Usage/Tier Display

**Status**: Draft

## Story

**As an** authenticated user,
**I want** to see my current monthly notification usage on the dashboard,
**so that** I understand my limits.

## Acceptance Criteria

*   **AC1**: The dashboard displays the user's current notification count for the month (e.g., "Monthly Usage: 75/100 notifications").
*   **AC2**: When the user reaches the limit, the dashboard clearly indicates that notifications are paused until the next billing period.
*   **AC3**: On the dashboard the user sees the button to upgrade to a higher tier when he's close (90%) to the limit of notifications.
*   **AC4**: On the dashboard the user sees the button to upgrade to a higher tier when he reaches limit of links added for scraping.

## Tasks / Subtasks

*   **Task 1: Add API endpoint for user quota/usage data** (AC: #1, #2, #3, #4)
    *   Create a new endpoint in `shargain/public_api/api.py` to expose user quota/usage information
    *   The endpoint should return the user's current tier, notification usage count, and limits
    *   The endpoint should also return information about URL/scrapping target limits
    *   Add the endpoint to the OpenAPI schema

*   **Task 2: Update the auto-generated API client** (AC: #1, #2, #3, #4)
    *   Run `pnpm generate:api-client` to update the frontend API client with the new endpoint
    *   Verify the new endpoint is available in `frontend/src/lib/api/`

*   **Task 3: Create or update dashboard component to display usage** (AC: #1, #2)
    *   Modify the dashboard component in `frontend/src/routes/dashboard.tsx` or create a new component
    *   Display the user's current usage in the format "Monthly Usage: X/Y notifications"
    *   Show visual indicators when limits are reached or nearly reached

*   **Task 4: Add upgrade buttons to dashboard** (AC: #3, #4)
    *   Add a prominent "Upgrade" button that appears when usage reaches 90% of the limit
    *   Add a prominent "Upgrade" button that appears when URL/scrapping target limit is reached
    *   Ensure buttons are styled consistently with the design system

*   **Task 5: Add unit tests for the dashboard component** (AC: #1, #2, #3, #4)
    *   Write Vitest unit tests for the dashboard component with different usage scenarios
    *   Test different states: normal usage, 90% usage, limit reached, etc.

*   **Task 6: Add integration tests for API endpoint** (AC: #1, #2, #3, #4)
    *   Write Pytest integration tests for the new API endpoint
    *   Test different user tiers and quota states

## Dev Notes

#### Previous Story Insights
*   **Story 1.9**: The `OfferQuota` model and `QuotaService` were implemented to provide a scalable foundation for subscription and billing. The service supports overlapping quota periods with precedence given to the latest `period_start`. This provides the backend infrastructure needed for tracking usage that this story will display on the frontend.

#### Data Models
*   **OfferQuota Model**: Located in `shargain/offers/models.py`, this model tracks `max_offers_per_period`, `used_offers_count`, `period_start`, and `period_end` for each target. [Source: data-models.md]
*   **CustomUser Model**: Located in `shargain/accounts/models.py`, this model has a `tier` field that determines the user's subscription level. [Source: data-models.md]

#### API Specifications
*   **New Endpoint**: A new endpoint `/me/usage` or similar needs to be added to the public API to expose user quota and usage information to the frontend. This should return the user's current tier, usage counts, and limits.
*   **Authentication**: The endpoint should require authentication using the existing Django session authentication. [Source: api-specification.md]

#### Component Specifications
*   **Dashboard Component**: The dashboard component is located in `frontend/src/routes/dashboard.tsx`. This component should be enhanced to display usage information. [Source: frontend-architecture.md]
*   **UI Components**: All UI elements should be built using shadcn/ui primitives located in `frontend/src/components/ui/`. [Source: frontend-architecture.md]

#### File Locations
*   **Backend API**: New endpoint should be added to `shargain/public_api/api.py`
*   **Frontend API Client**: Auto-generated in `frontend/src/lib/api/` (updated via `pnpm generate:api-client`)
*   **Dashboard Component**: `frontend/src/routes/dashboard.tsx`
*   **Component Tests**: `frontend/src/routes/dashboard.test.tsx`
*   **API Tests**: `shargain/public_api/tests/test_usage_api.py`

#### Testing Requirements
*   **Frontend Tests**: Use Vitest and React Testing Library for component tests. Co-locate test files with components. [Source: testing-strategy.md]
*   **Backend Tests**: Use Pytest for API endpoint tests. Place tests in app-specific test directories. [Source: testing-strategy.md]
*   **API Testing**: Ensure the new endpoint is properly authenticated and returns correct data based on user tier and quotas. [Source: testing-strategy.md]

#### Technical Constraints
*   **Type Safety**: All API communication must go through the auto-generated TanStack Query hooks to maintain type safety. [Source: frontend-architecture.md]
*   **Server State Management**: Use TanStack Query exclusively for server state management, not Redux or other state management libraries. [Source: frontend-architecture.md]
*   **API Client**: The auto-generated API client in `src/lib/api/` is the source of truth for backend communication. [Source: frontend-architecture.md]

## Change Log

| Date       | Version | Description                            | Author             |
| :--------- | :------ | :------------------------------------- | :----------------- |
| 2025-10-20 | 1.0     | Initial Draft                          | Bob (Scrum Master) |

## QA Results

**Quality Gate Decision**: PENDING - Implementation required before QA review

**Review Summary**: N/A - Story draft pending implementation

**Verification Results:**
- AC1: N/A
- AC2: N/A
- AC3: N/A
- AC4: N/A

**Testing Coverage:** N/A - Implementation required first

**Code Quality:** N/A - Implementation required first

**Risk Assessment:** N/A - Implementation required first
