# High Level Architecture

## Technical Summary
The project is a web application with a decoupled frontend and backend. The backend is a monolithic Django application that exposes a REST API. It has a separate, out-of-repository scraping service that pushes data to it. The frontend is a modern single-page application (SPA). The entire system is designed to be containerized for deployment.

## Actual Tech Stack

| Category | Technology | Version/Details |
| --- | --- | --- |
| **Backend** | | |
| Language | Python | ~3.13 |
| Framework | Django, Django Ninja | |
| Async Tasks | Celery | |
| Database | PostgreSQL | |
| Scraping Libs | requests, beautifulsoup4 | |
| **Frontend** | | |
| Framework | React | ~19 |
| Build Tool | Vite | ~6.3 |
| Language | TypeScript | |
| Routing | TanStack Router | ~1.130 |
| State/Cache | TanStack Query | ~5.84 |
| Styling | Tailwind CSS, shadcn/ui | |
| **Deployment** | | |
| Containerization | Docker, Docker Compose | |
| **Tooling** | | |
| BE Package/Env | uv, poetry | |
| FE Package | pnpm | |
| Lint/Format | ruff, eslint | |
| Type Checking | mypy | |

## Repository Structure Reality Check

*   **Type**: Monorepo (Backend and Frontend in the same repository).
*   **Package Manager**: `pnpm` for the frontend, `uv`/`poetry` for the backend.
*   **Notable**: A separate, out-of-repository project exists for the scrapers.
