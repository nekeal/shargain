# Architecture

**Analysis Date:** 2026-01-24

## Pattern Overview

**Overall:** Modular Monolith with Domain-Driven Design (DDD) principles

**Key Characteristics:**
- Backend: Django REST Framework with Ninja API for modern endpoints
- Frontend: React 19 with TanStack Router for client-side routing
- Separated application layer (commands/queries) following CQRS patterns
- Feature-oriented modular structure with explicit domain boundaries
- Service layer for cross-cutting business logic
- Celery for async task processing

## Layers

**Presentation Layer:**
- Purpose: HTTP request/response handling, routing, serialization
- Location: `shargain/accounts/views.py`, `shargain/offers/views.py`, `shargain/notifications/views/`, `shargain/public_api/api.py`
- Contains: ViewSets (DRF), Serializers, Ninja API handlers
- Depends on: Application layer (commands/queries), Models
- Used by: HTTP clients, REST API consumers

**Application Layer:**
- Purpose: Business logic orchestration, command execution, query handling
- Location: `shargain/*/application/` (offers, notifications, commons, telegram)
- Contains:
  - `commands/`: State-changing operations (add_scraping_url.py, create_target.py, etc.)
  - `queries/`: Read operations (get_target.py, list_targets.py, etc.)
  - `dto.py`: Data transfer objects
  - `actor.py`: User/request context
  - `exceptions.py`: Domain exceptions
- Depends on: Models (data access), Commons (shared actors)
- Used by: Views, API handlers, Celery tasks

**Domain Layer:**
- Purpose: Core domain models and business rules
- Location: `shargain/*/models.py` (offers, notifications, accounts, commons, telegram)
- Contains: Django models with QuerySets and custom managers
- Key models:
  - `Offer`: Core entity representing marketplace offers
  - `ScrappingTarget`: Monitoring target with notification config
  - `ScrapingUrl`: Individual URL to scrape
  - `ScrapingCheckin`: Checkin history/audit trail
  - `NotificationConfig`: Notification channel (Telegram/Discord)
  - `CustomUser`: Extended auth model

**Infrastructure/Services Layer:**
- Purpose: External integrations, task scheduling, notification delivery
- Location: `shargain/offers/services/`, `shargain/notifications/senders.py`, `shargain/scrapper/`
- Contains:
  - Batch operations (OfferBatchCreateService in `offers/services/batch_create.py`)
  - Filter logic (FilterService in `offers/services/filter_service.py`)
  - Notification senders (Telegram, Discord hooks)
  - Web scraping parsers
  - Celery task definitions (`offers/tasks.py`, `scrapper/management/commands/`)

**Frontend Presentation:**
- Purpose: React components, routing, user interaction
- Location: `frontend/src/`
- Contains:
  - Routes: `routes/` (dashboard, notifications, auth)
  - Components: UI components, feature components
  - Context: Auth context for state management
  - Hooks: Custom React hooks
  - API: Generated OpenAPI client

## Data Flow

**Scraping & Offer Creation Flow:**
1. Scheduled Celery task triggers scraping (`celery.py` beat schedule)
2. `shargain/scrapper/management/commands/scrap.py` executes parser
3. New offers create via `OfferBatchCreateService` (`offers/services/batch_create.py`)
4. Service applies filters via `FilterService` (`offers/services/filter_service.py`)
5. Notifications sent via appropriate channel (Telegram/Discord)
6. `ScrapingCheckin` records audit trail

**User Interaction Flow:**
1. Frontend makes authenticated request to Ninja API (`public_api/api.py`)
2. API calls application command/query (e.g., `offers/application/commands/add_scraping_url.py`)
3. Command validates actor permissions via `Actor` context
4. Domain model updated via ORM
5. Response serialized to DTO and returned

**Notification Configuration Flow:**
1. User creates NotificationConfig via `public_api/api.py`
2. Command handler (`notifications/application/commands/`) validates and persists
3. Config linked to ScrappingTarget
4. When offers discovered, NotificationSender dispatches to webhook/Telegram

**State Management:**
- Backend: Django ORM manages all state in PostgreSQL
- Frontend: React Query (`@tanstack/react-query`) handles server state caching
- Auth: Django session-based with token support via Ninja
- Async: Celery Beat scheduler coordinates periodic scraping tasks

## Key Abstractions

**Actor:**
- Purpose: Encapsulate user/request context
- Examples: `shargain/commons/application/actor.py`, `shargain/offers/application/actor.py`
- Pattern: Simple dataclass holding `user_id` for permission checks

**Service:**
- Purpose: Orchestrate multi-step operations
- Examples: `OfferBatchCreateService`, `FilterService`
- Pattern: Callable class with `run()` method, accepts config dict

**DTO (Data Transfer Object):**
- Purpose: Decouple external API from internal models
- Examples: `ScrapingUrlDTO`, `TargetDTO` in application layers
- Pattern: Pydantic models with `from_orm()` conversion

**QuerySet Customization:**
- Purpose: Encapsulate domain queries in reusable methods
- Examples: `OfferQueryset` (opened(), closed(), olx(), otomoto())
- Pattern: Extend `QuerySet`, attach via `Manager.from_queryset()`

**Command/Query Pattern:**
- Purpose: Explicit separation of writes (commands) vs. reads (queries)
- Examples: `add_scraping_url()` (command), `get_target()` (query)
- Pattern: Functions in `application/commands/` and `application/queries/` modules

## Entry Points

**Backend API:**
- Location: `shargain/urls.py`
- Triggers: HTTP requests
- Responsibilities: Route to DRF ViewSets or Ninja API, serve API docs

**Ninja API Endpoint:**
- Location: `shargain/public_api/api.py`
- Triggers: Frontend requests to `/api/public/`
- Responsibilities: Modern API with application layer integration

**Celery Task Scheduler:**
- Location: `shargain/celery.py`
- Triggers: Beat schedule (5-second polling for checkins)
- Responsibilities: Trigger periodic scraping, coordinate background work

**Django Admin:**
- Location: Django default admin at `/admin/`
- Triggers: Admin user access
- Responsibilities: Manage entities via Jazzmin admin interface

**Frontend SPA:**
- Location: `frontend/src/index.tsx` → `App.tsx`
- Triggers: Browser navigation
- Responsibilities: Route to pages, manage auth state, render components

## Error Handling

**Strategy:** Explicit exception hierarchy with domain-specific exceptions

**Patterns:**
- Domain exceptions inherit from base (e.g., `TargetDoesNotExist`, `NotificationConfigDoesNotExist`)
- Application layer raises domain exceptions
- API handlers catch exceptions and map to HTTP status codes
- Frontend handles error responses and displays user feedback

**Key Exception Types:**
- `ApplicationException`: Base for domain errors
- `TargetDoesNotExist`: When scraping target not found
- `ScrapingUrlDoesNotExist`: When URL not found in target
- `NotificationConfigDoesNotExist`: When notification config not found

## Cross-Cutting Concerns

**Logging:** Django logging configured in `settings/base.py` and environment-specific settings

**Validation:**
- Model-level: Django ORM validators on fields
- Serializer-level: DRF serializers validate input
- Command-level: Application commands validate business rules (e.g., owner check)

**Authentication:**
- Session-based via Django auth
- Custom user model: `shargain/accounts/models.py::CustomUser`
- Permission enforcement in views: `IsAuthenticated` permission checks
- Actor context passed through application layer

**CORS:** Enabled via `corsheaders` middleware (all origins in dev, configurable in prod)

**Internationalization:** Django i18n with Polish and English support. Locale files in `shargain/locale/`

---

*Architecture analysis: 2026-01-24*
