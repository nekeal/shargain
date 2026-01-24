# Technology Stack

**Analysis Date:** 2026-01-24

## Languages

**Primary:**
- Python 3.13 - Backend server, tasks, scrapers
- TypeScript/JavaScript - Frontend web application
- HTML/CSS - Frontend templates

**Secondary:**
- SQL (PostgreSQL) - Data persistence

## Runtime

**Environment:**
- Python 3.13-bookworm (backend)
- Node.js (frontend, version unspecified)

**Package Manager:**
- Backend: `uv` (Python package manager) - Lockfile: `uv.lock` present
- Frontend: npm - Lockfile: `package-lock.json` (inferred from Node projects)

## Frameworks

**Core Backend:**
- Django 4.x - Web framework for REST API and admin
- Django REST Framework (DRF) - RESTful API construction
- Django Ninja - API specification and generation

**Frontend:**
- React 19.0.0 - UI framework
- TanStack Router 1.130.2 - Client-side routing
- TanStack React Query 5.84.1 - Server state management

**Build/Dev:**
- Vite 6.3.5 - Frontend dev server and bundler
- TypeScript <5.9.0 - Type safety for frontend
- Tailwind CSS 4.1.11 - Utility-first CSS framework

**Testing:**
- pytest - Python test framework
- pytest-django - Django testing utilities
- pytest-sugar - Enhanced pytest output
- pytest-xdist - Parallel test execution
- pytest-cov - Coverage reports
- vitest 3.0.5 - Frontend test runner
- @testing-library/react 16.2.0 - React component testing

**Code Quality:**
- ruff >=0.11.10 - Python linter and formatter
- mypy - Python type checker
- pyright >=1.1.403 - Alternative Python type checker
- eslint 9.32.0 - JavaScript/TypeScript linting
- TypeScript compiler (tsc) - Type checking

**Admin & Tools:**
- django-jazzmin - Enhanced Django admin UI
- django-extensions - Django management command extensions
- django-debug-toolbar - Development debugging
- IPython - Interactive Python shell

## Key Dependencies

**Critical Backend:**
- psycopg2-binary - PostgreSQL database adapter
- celery - Distributed task queue
- requests - HTTP client library for web scraping and API calls
- BeautifulSoup4 (bs4) - HTML/XML parsing for web scraping

**Messaging & Bots:**
- pytelegrambotapi - Telegram bot integration
- discord.py (listed as "discord") - Discord API integration (may not be actively used)

**API Documentation & Schema:**
- drf-yasg - Swagger/OpenAPI documentation for DRF
- django-ninja - Modern API framework with automatic schema generation

**Data Management:**
- django-dbbackup - Database backup utility
- django-filter - Filtering for querysets
- django-better-admin-arrayfield - PostgreSQL array field admin support
- django-cors-headers - Cross-Origin Resource Sharing support

**Environment & Config:**
- environs - Environment variable management
- yarl >=1.9.2 - URL handling library

**Error Tracking & Monitoring:**
- sentry-sdk - Error tracking and performance monitoring (production)

**Deployment:**
- gunicorn - WSGI HTTP server
- ansible >=10.7.0 - Infrastructure automation (dev dependency)
- mitogen >=0.3.23 - Ansible acceleration (dev dependency)

**Frontend UI Components:**
- @radix-ui/* (various) - Accessible React component primitives
- lucide-react 0.476.0 - Icon library
- class-variance-authority 0.7.1 - CSS class composition

**Frontend Internationalization:**
- i18next 25.4.1 - i18n framework
- react-i18next 15.7.2 - React i18n binding
- i18next-browser-languagedetector 8.2.0 - Language detection
- i18next-http-backend 3.0.2 - i18n backend loading

**Frontend API Client Generation:**
- @hey-api/openapi-ts 0.80.5 - OpenAPI TypeScript code generation
- form-data 4.0.4 - FormData handling

**Frontend Utilities:**
- zod 4.0.17 - TypeScript schema validation
- clsx 2.1.1 - Conditional className utility
- tailwind-merge 3.0.2 - Tailwind CSS class merging

## Configuration

**Environment:**
- `.env` files for environment-specific configuration
- Django settings module selection via `DJANGO_SETTINGS_MODULE` environment variable
- Separate settings files: `base.py`, `local.py`, `production.py`, `tests.py`

**Key Configuration Files:**
- `pyproject.toml` - Python project config with ruff, mypy, pytest, coverage
- `shargain/settings/base.py` - Base Django settings
- `shargain/settings/local.py` - Local development overrides
- `shargain/settings/production.py` - Production settings with Sentry
- `shargain/settings/conf/celery_settings.py` - Celery configuration
- `frontend/vite.config.ts` - Vite build configuration
- `frontend/tsconfig.json` - TypeScript compilation settings
- `frontend/vitest.config.ts` - Test configuration
- `frontend/tailwind.config.ts` - Tailwind CSS customization
- `frontend/.eslintrc.js` - ESLint configuration
- `frontend/openapi-ts.config.ts` - OpenAPI code generation config

**Key Environment Variables:**
- `DJANGO_SETTINGS_MODULE` - Django settings to use (tests/local/production)
- `POSTGRES_DB` - PostgreSQL database name
- `POSTGRES_USER` - PostgreSQL user
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_HOST` - PostgreSQL host
- `TELEGRAM_BOT_TOKEN` - Telegram bot authentication token
- `TELEGRAM_WEBHOOK_URL` - Telegram webhook endpoint
- `TELEGRAM_SETUP_BOT` - Enable/disable bot setup
- `CELERY_BROKER_URL` - Celery message broker connection string
- `VITE_API_URL` - Frontend API base URL (e.g., http://localhost:8000)
- `DJANGO_ALLOWED_HOSTS` - Comma-separated allowed hostnames
- `DJANGO_SECRET_KEY` - Django secret key (production only)
- `SENTRY_RELEASE` - Sentry release version (production)

## Platform Requirements

**Development:**
- Python 3.13
- PostgreSQL 13+ (via Docker)
- Node.js (version not specified, recommend 18.x+)
- Docker & Docker Compose (for local dev infrastructure)

**Production:**
- Python 3.13-slim-bookworm (Docker image)
- PostgreSQL 13+
- Celery broker (Redis/RabbitMQ/other AMQP)
- Sentry account (error tracking)
- Telegram Bot API (for bot integration)
- Discord Webhook URL (optional, if Discord notifications enabled)

**Static/Media Storage:**
- Local filesystem or S3-compatible service
- Production uses S3: https://s3c.bcode.app/shargain/

---

*Stack analysis: 2026-01-24*
