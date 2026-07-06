# Repository Guidelines

## Project Structure & Module Organization
- `shargain/`: Django backend (apps like `accounts`, `offers`, `notifications`, `telegram`, plus `settings/`).
- `shargain/*/tests/`: backend tests, usually split by `application/`, `services/`, and model/view test files.
- `frontend/`: React + Vite TypeScript app (`src/components`, `src/routes`, `src/lib`).
- `deployment/`: Docker and Ansible deployment assets.
- `docs/`: architecture, PRD, and implementation notes.
- `fixtures/`: seed data loaded during bootstrap.

## Build, Test, and Development Commands
- `uv sync`: install backend dependencies.
- `just bootstrap`: run migrations and load fixtures for local backend setup.
- `uv run python manage.py runserver`: start Django locally.
- `just test`: run backend tests (`pytest shargain`).
- `just quality-check`: run Ruff lint/format checks and mypy.
- `just coverage`: run backend coverage report.
- `docker compose up`: run local stack in containers.
- `pnpm -C frontend dev`: start frontend on port `3000`.
- `pnpm -C frontend test`: run frontend Vitest suite.
- `pnpm -C frontend lint`: run TypeScript + ESLint checks.

## Coding Style & Naming Conventions
- Python: 4-space indentation, max line length 120, `snake_case` for modules/functions.
- TypeScript/React: `camelCase` for variables/hooks, `PascalCase` for components.
- API routes use `kebab-case`; keep public (`/api/public/...`) and internal API boundaries separate.
- Format/lint with Ruff (`uv run ruff format`, `uv run ruff check`) and frontend ESLint.
- Install hooks once per clone: `uv run pre-commit install --install-hooks`.

## Testing Guidelines
- Backend: Pytest with Django settings `shargain.settings.tests`; test files match `test_*.py`.
- Add tests near changed code (for example `shargain/offers/tests/services/`).
- Frontend: Vitest + Testing Library (`*.test.tsx`).
- Before PR, run backend and frontend checks locally.
- Prefer assertions on observable behavior (API responses, persisted state, emitted event objects), not internal call order or private implementation details.
- Keep test setup and test assertions at the same abstraction level (API-level setup with API-level assertions; service-level setup with service-level assertions).
- When creating model objects in tests, use factories instead of direct `Model.objects.create(...)` unless there is a strong reason not to.

## Integration Rules (Non-Obvious)
- For Django signals crossing module boundaries, use typed dataclass payloads (single `event` object) instead of unstructured kwargs.
- Keep cross-context contracts explicit and stable. For subscriptions -> quotas integration, `SubscriptionChangedEvent` + `PlanLimitsDTO` is the contract surface.
- On subscription upgrades, quota period bounds should come from subscription period when available; only fall back to `QUOTA_PERIOD_DAYS` for open-ended subscriptions.

## Commit & Pull Request Guidelines
- Use concise conventional prefixes seen in history: `fix: ...`, `docs: ...`, `chore: ...`.
- Keep commits focused and atomic; include regenerated artifacts only when required.
- PRs should include: clear summary, linked issue/story, test evidence (commands run), and UI screenshots for frontend changes.
- Ensure CI passes backend tests and quality jobs before merge.

## Security & Configuration Tips
- Keep secrets in `.env`; never commit real credentials.
- Local PostgreSQL defaults are documented in `README.md`; production values must come from environment/secrets.
