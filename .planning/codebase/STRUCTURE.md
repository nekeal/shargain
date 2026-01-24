# Codebase Structure

**Analysis Date:** 2026-01-24

## Directory Layout

```
shargain/
├── shargain/                    # Main Django project package
│   ├── settings/                # Django settings (dev/prod/test)
│   │   ├── base.py              # Shared settings
│   │   ├── local.py             # Development override
│   │   ├── production.py         # Production override
│   │   ├── tests.py             # Test settings
│   │   └── conf/                # Modular settings
│   │       ├── celery_settings.py
│   │       └── theme.py
│   ├── accounts/                # User authentication & profiles
│   │   ├── models.py            # CustomUser, RegisterToken
│   │   ├── views.py             # Auth viewsets
│   │   ├── serializers.py       # Auth serializers
│   │   ├── urls.py              # Router registration
│   │   ├── applications/        # Application layer (commands/queries)
│   │   └── tests/               # Auth tests
│   ├── offers/                  # Core offers management
│   │   ├── models.py            # Offer, ScrappingTarget, ScrapingUrl, ScrapingCheckin
│   │   ├── views.py             # Offer viewsets
│   │   ├── serializers.py       # Serializers
│   │   ├── urls.py              # Router registration
│   │   ├── services/            # Business logic services
│   │   │   ├── batch_create.py  # OfferBatchCreateService
│   │   │   └── filter_service.py # Filter logic
│   │   ├── schemas/             # Ninja schema definitions
│   │   ├── application/         # Application layer
│   │   │   ├── commands/        # Write operations
│   │   │   ├── queries/         # Read operations
│   │   │   ├── dto.py           # Data transfer objects
│   │   │   ├── actor.py         # User context
│   │   │   └── exceptions.py    # Domain exceptions
│   │   ├── admin/               # Django admin config
│   │   ├── tasks.py             # Celery tasks
│   │   ├── websites.py          # Supported website configs
│   │   └── tests/               # Offer tests
│   ├── notifications/           # Notification channels & configs
│   │   ├── models.py            # NotificationConfig
│   │   ├── views/               # API endpoints
│   │   ├── serializers.py       # Serializers
│   │   ├── urls.py              # Router registration
│   │   ├── senders.py           # Telegram/Discord senders
│   │   ├── services/            # Notification services
│   │   ├── application/         # Application layer (commands/queries)
│   │   ├── scripts/             # Utility scripts
│   │   └── tests/               # Notification tests
│   ├── telegram/                # Telegram bot integration
│   │   ├── models.py            # Telegram-specific data
│   │   ├── application/         # Commands/queries for Telegram
│   │   └── tests/               # Telegram tests
│   ├── commons/                 # Shared utilities
│   │   ├── models.py            # TimeStampedModel base class
│   │   ├── application/         # Shared Actor class
│   │   └── views.py             # Common view mixins
│   ├── scrapper/                # Web scraping orchestration
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── scrap.py     # Main scraping command
│   │   └── parsers/             # Site-specific parsers
│   ├── parsers/                 # Parser utilities
│   ├── public_api/              # Ninja API endpoints
│   │   ├── api.py               # All Ninja routes
│   │   └── auth.py              # API authentication
│   ├── urls.py                  # Root URL routing
│   ├── wsgi.py                  # WSGI entry point
│   ├── asgi.py                  # ASGI entry point
│   └── celery.py                # Celery app config
│
├── frontend/                    # React SPA
│   ├── src/
│   │   ├── App.tsx              # Root component
│   │   ├── index.tsx            # Entry point
│   │   ├── main.tsx             # Vite entry
│   │   ├── routes/              # TanStack Router routes
│   │   │   ├── __root.tsx       # Root layout
│   │   │   ├── index.tsx        # Landing page
│   │   │   ├── dashboard.tsx    # Main dashboard
│   │   │   ├── notifications.tsx # Notifications page
│   │   │   └── auth/            # Auth routes (signin, signup)
│   │   ├── components/          # React components
│   │   │   ├── ui/              # Generic UI components
│   │   │   ├── dashboard/       # Dashboard-specific
│   │   │   ├── auth/            # Auth components
│   │   │   └── notifications/   # Notification components
│   │   ├── context/             # React Context (auth, etc)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── api/                 # OpenAPI generated client
│   │   ├── lib/                 # Utilities & helpers
│   │   ├── types/               # TypeScript types
│   │   ├── styles.css           # Global styles (Tailwind)
│   │   ├── i18n/                # i18n configuration
│   │   ├── locales/             # Translation files
│   │   └── test/                # Test utilities
│   ├── public/                  # Static assets
│   ├── dist/                    # Build output
│   ├── vite.config.ts           # Vite bundler config
│   ├── tsconfig.json            # TypeScript config
│   ├── eslint.config.js         # ESLint config
│   ├── vitest.config.ts         # Test runner config
│   ├── tailwind.config.ts        # Tailwind CSS config
│   ├── package.json             # Dependencies
│   └── Dockerfile               # Container image
│
├── templates/                   # Django templates (mostly unused, API-first)
├── docs/                        # Project documentation
├── fixtures/                    # Test data
├── deployment/                  # Deployment configuration
│   └── ansible-play-shargain/   # Ansible roles
├── manage.py                    # Django CLI
├── Makefile                     # Build/dev commands
├── docker-compose.yml           # Local docker setup
├── Dockerfile                   # Backend container
├── .env                         # Environment variables
├── .env.example                 # Env template
├── .pre-commit-config.yaml      # Git hooks
└── mypy.ini                     # Type checking config
```

## Directory Purposes

**`shargain/`:**
- Purpose: Main Django project package
- Contains: App modules, settings, URL routing, entry points
- Key files: `urls.py` (root routing), `celery.py` (async config)

**`shargain/accounts/`:**
- Purpose: User authentication, registration, profiles
- Contains: Django auth models, user-related viewsets
- Key files: `models.py` (CustomUser), `views.py` (auth endpoints)

**`shargain/offers/`:**
- Purpose: Core business logic for monitoring offers/deals
- Contains: Models for offers and scraping targets, services for bulk operations
- Key files: `models.py`, `application/commands/`, `services/batch_create.py`

**`shargain/notifications/`:**
- Purpose: Notification configuration and delivery
- Contains: Notification channels, senders for Telegram/Discord/webhooks
- Key files: `models.py` (NotificationConfig), `senders.py` (delivery)

**`shargain/public_api/`:**
- Purpose: Modern Ninja API endpoints (preferred over DRF views)
- Contains: All `/api/public/` endpoints with application layer integration
- Key files: `api.py` (all routes), `auth.py` (API authentication)

**`shargain/commons/`:**
- Purpose: Shared utilities and base classes
- Contains: TimeStampedModel, Actor context, common exceptions
- Key files: `models.py` (base model), `application/actor.py`

**`frontend/src/`:**
- Purpose: React SPA source code
- Contains: Components, routes, state management, API client
- Key files: `App.tsx` (root), `routes/` (page components)

**`frontend/src/routes/`:**
- Purpose: TanStack Router page definitions
- Contains: One `.tsx` file per route
- Pattern: Each route is a page-level component

**`frontend/src/components/`:**
- Purpose: Reusable React components
- Contains: UI components (shadcn/ui), feature-specific components
- Subdirectories: `ui/`, `dashboard/`, `auth/`, `notifications/`

**`deployment/`:**
- Purpose: Infrastructure as code
- Contains: Ansible playbooks for server setup
- Managed separately from application code

## Key File Locations

**Entry Points:**
- `shargain/urls.py`: Root URL routing, combines DRF routers and Ninja API
- `shargain/public_api/api.py`: Primary API endpoint (Ninja)
- `shargain/celery.py`: Async task configuration
- `manage.py`: Django management CLI
- `frontend/src/index.tsx`: Frontend React entry point
- `frontend/src/App.tsx`: Frontend root component with routing

**Configuration:**
- `shargain/settings/base.py`: Shared Django settings
- `shargain/settings/local.py`: Development overrides
- `shargain/settings/production.py`: Production overrides
- `frontend/vite.config.ts`: Frontend build configuration
- `frontend/tsconfig.json`: TypeScript configuration

**Core Logic:**
- `shargain/offers/application/commands/`: State-changing operations
- `shargain/offers/application/queries/`: Read operations
- `shargain/offers/services/`: Multi-step business operations
- `shargain/notifications/senders.py`: Notification delivery

**Testing:**
- `shargain/*/tests/`: Per-app test modules
- `frontend/src/test/`: Frontend test utilities
- `frontend/src/**/*.test.tsx`: Component tests (co-located)

## Naming Conventions

**Files:**
- Models: `models.py` (always singular concept, plural data)
- Views: `views.py` (DRF ViewSets)
- Serializers: `serializers.py` (DRF Serializers)
- URL routing: `urls.py`
- Services: `services.py` or in `services/` directory
- Commands: `command_name.py` in `application/commands/`
- Queries: `query_name.py` in `application/queries/`
- Tests: `test_*.py` or `*_test.py`
- Frontend components: `ComponentName.tsx` (PascalCase)

**Directories:**
- App directories: `lowercase_singular` (e.g., `offers`, `notifications`)
- Component directories: `kebab-case` (e.g., `monitored-websites`)
- Utility directories: `lowercase_singular` (e.g., `services`, `hooks`)

## Where to Add New Code

**New Backend Feature:**
1. Create Django app if needed: `python manage.py startapp feature_name`
2. Model layer: Add to `shargain/feature_name/models.py`
3. Application layer:
   - Commands: `shargain/feature_name/application/commands/operation_name.py`
   - Queries: `shargain/feature_name/application/queries/operation_name.py`
4. API layer: Add routes to `shargain/public_api/api.py`
5. Tests: `shargain/feature_name/tests/test_operation.py`

**New Frontend Feature:**
1. Route: Add `.tsx` file in `frontend/src/routes/feature/page.tsx`
2. Components: Create in `frontend/src/components/feature/`
3. Hooks: Custom logic in `frontend/src/hooks/useFeature.ts`
4. Types: Shared types in `frontend/src/types/feature.ts`
5. Tests: Co-locate as `ComponentName.test.tsx`

**New Service/Business Logic:**
- Location: `shargain/app_name/services/service_name.py` or in `services/` directory
- Pattern: Callable class with `__init__()` and `run()` method
- Example: `OfferBatchCreateService` in `shargain/offers/services/batch_create.py`

**Shared Utilities:**
- Backend: `shargain/commons/` for application-wide code
- Frontend: `frontend/src/lib/` for utility functions, `frontend/src/hooks/` for custom hooks

## Special Directories

**`shargain/locale/`:**
- Purpose: Translation files for i18n
- Generated: By Django `makemessages`
- Committed: Yes (translation files are version controlled)

**`frontend/dist/`:**
- Purpose: Production build output
- Generated: Yes (by `npm run build`)
- Committed: No (generated, not version controlled)

**`shargain/migrations/`:**
- Purpose: Django database migration files
- Generated: By `python manage.py makemigrations`
- Committed: Yes (migrations are version controlled)

**`frontend/public/`:**
- Purpose: Static assets served directly
- Generated: No
- Committed: Yes (favicon, static images, etc)

**`docs/`:**
- Purpose: Project documentation (separate from code)
- Generated: No
- Committed: Yes (documentation is version controlled)

---

*Structure analysis: 2026-01-24*
