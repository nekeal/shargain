# External Integrations

**Analysis Date:** 2026-01-24

## APIs & External Services

**Telegram Bot:**
- Service: Telegram Bot API
- What it's used for: User notifications, link tracking, offer management via chatbot interface
- SDK/Client: `pytelegrambotapi` (TeleBot)
- Auth: `TELEGRAM_BOT_TOKEN` environment variable
- Configuration: `shargain/telegram/bot.py`
- Webhook support: Webhook URL configurable via `TELEGRAM_WEBHOOK_URL`
- Features:
  - User registration via deep linking with token: `https://t.me/BotUsername?start=TOKEN`
  - Inline keyboards for callback queries (Add Link, List Links, Delete Link)
  - Multi-language support (English/Polish)
  - Message processing via `TelegramBot.get_bot().process_new_updates()`

**Discord Webhooks (Optional):**
- Service: Discord Webhook API
- What it's used for: Notifications to Discord channels
- Implementation: Discord webhook URLs stored in `NotificationConfig.webhook_url`
- Status: Code structure exists but integration may not be fully implemented
- Model: `shargain/notifications/models.py` - `NotificationChannelChoices.DISCORD`

**Web Scraping APIs:**
- OLX.pl - Polish classifieds platform
  - Method: HTTP requests + BeautifulSoup parsing
  - Used for: Extracting offer data, checking offer status
  - Implementation: `shargain/parsers/olx.py` - `OlxOffer` class
  - Details: Parses prerendered state from HTML script tags

- Otomoto.pl - Polish automotive classifieds
  - Method: HTTP requests + HTTP status codes
  - Used for: Offer status monitoring (404 = closed)
  - Implementation: `shargain/offers/tasks.py`

**Sentry (Error Tracking & Monitoring):**
- Service: Sentry.io
- What it's used for: Error tracking and performance monitoring (production only)
- SDK: `sentry-sdk` with Django integration
- DSN: `https://50ee8bdc6e1c4fb9ab3be75c0ee46a71@o288820.ingest.sentry.io/5728106`
- Configuration: `shargain/settings/production.py`
- Integration: DjangoIntegration
- Env var for release: `SENTRY_RELEASE`

## Data Storage

**Databases:**
- Primary: PostgreSQL 13+
  - Connection env vars: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`
  - Client: psycopg2-binary (Python) + Django ORM
  - Dev default: `shargain` database on localhost:5432
  - Production: Configurable via environment

**File Storage:**
- Local filesystem by default
- Production: S3-compatible storage at `https://s3c.bcode.app/shargain/`
- Models: Django FileField on `Offer.source_html`
- Paths:
  - Media root: `{BASE_DIR}/media/`
  - Static root: `{BASE_DIR}/public/` (local) or S3 (production)

**Database Backup:**
- Tool: django-dbbackup
- Purpose: Backup/restore PostgreSQL databases
- Configuration: Available but details not fully configured in provided files

**Caching:**
- None detected in base configuration
- Celery task result backend: Configured via `CELERY_BROKER_URL`

## Authentication & Identity

**Auth Provider:**
- Custom Django authentication
- Custom user model: `shargain.accounts.models.CustomUser`
- Password hashers: PBKDF2 (default), Argon2, BCrypt
- Session-based authentication via Django sessions

**Telegram User Registration:**
- Registration flow: User starts Telegram bot with registration token
- Token generation: UUID-based tokens
- User linking: `TelegramUser` model maps Telegram ID to system users
- Token validation: Used in deep linking for user registration

**API Token/Key Management:**
- Telegram tokens stored in environment variables
- User-specific registration tokens in `NotificationConfig.register_token`
- Per-channel tokens in `NotificationConfig._token` (deprecated)

## Monitoring & Observability

**Error Tracking:**
- Sentry.io (production)
  - Configuration: `shargain/settings/production.py`
  - Integration: Django integration enabled
  - Release tracking: Via `SENTRY_RELEASE` env var

**Logs:**
- Django logging to stdout (production)
- Logger configuration: `shargain/settings/production.py`
- Log levels: ERROR and above to console
- Format: `[{server_time}] {message}`
- Application logging via `logging.getLogger(__name__)`

## CI/CD & Deployment

**Hosting:**
- Docker containers
- Backend image: `python:3.13-slim-bookworm`
- Frontend built with Vite, served separately
- Production database: PostgreSQL (external or containerized)

**Docker Configuration:**
- Dockerfile (multi-stage): builder → development → ci → production
- docker-compose.yml for local development
- Services: web (Django), postgres (PostgreSQL)
- Dev entrypoint: `python manage.py runserver 0:8000`

**Deployment Method:**
- Docker images with version tag from git branch
- Image registry: Docker Hub or GitHub Container Registry (ghcr.io reference in Dockerfile)
- Build script: `frontend/package.json` includes docker build command
- Ansible playbooks available (dev dependency) at `deployment/` directory

## Environment Configuration

**Required env vars:**
- Backend: `TELEGRAM_BOT_TOKEN`, `POSTGRES_*` (host, user, password, db)
- Frontend: `VITE_API_URL`
- Production: `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `SENTRY_RELEASE`
- Celery: `CELERY_BROKER_URL` (required for task queue)

**Secrets location:**
- `.env` file in project root (not committed to git)
- Environment variables injected at deployment time
- Sensitive values: Database credentials, API tokens, Sentry DSN

## Webhooks & Callbacks

**Incoming (Telegram):**
- Endpoint: `/api/webhooks/telegram/{token}/`
- Location: `shargain/notifications/urls.py`
- Handler: `TelegramWebhookViewSet.create()`
- Processing: Converts webhook JSON to `telebot.types.Update` and processes via bot
- Format: Telegram Update object (JSON)
- Response: `{"ok": True}`

**Incoming (User-defined):**
- Discord webhooks: Configurable URL in `NotificationConfig.webhook_url`
- Purpose: Custom notification destinations

**Outgoing:**
- No external webhook calls detected
- Notifications sent via Telegram API (polling or webhook mode)
- Discord integration via webhook URLs provided by users

## API Specification

**OpenAPI/Swagger:**
- Schema generation: drf-yasg (Swagger for Django REST Framework)
- Swagger UI: `/api/swagger/`
- ReDoc UI: `/api/doc/`
- Schema endpoint: Auto-generated from DRF viewsets
- Frontend API client: Auto-generated from `openapi.json` via @hey-api/openapi-ts

**API Documentation:**
- Frontend OpenAPI config: `frontend/openapi-ts.config.ts`
- Input: `frontend/openapi.json` (generated from backend)
- Output: TypeScript client code in `frontend/src/lib/api/`
- Code generation: `npm run generate:api-client`

## Rate Limiting & Quotas

**Not detected:**
- No explicit rate limiting middleware configured
- No API quota management visible
- No throttling classes in DRF settings

## Cross-Origin (CORS)

**Configuration:**
- Dev: `CORS_ALLOW_ALL_ORIGINS = True` in local settings
- Production: `CORS_ALLOW_ALL_ORIGINS = True` in base settings
- Middleware: `corsheaders.middleware.CorsMiddleware` installed
- Frontend proxy: Vite dev server proxies `/api` requests to backend

---

*Integration audit: 2026-01-24*
