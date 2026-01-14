# Shargain Brownfield Architecture Document

## Introduction

This document captures the CURRENT STATE of the Shargain codebase, including its architecture, patterns, and technology stack. It is based on an analysis of the existing code and is intended to serve as a reference for AI agents and senior developers working on the project.

### Document Scope
This is a comprehensive documentation of the entire system, prepared to formalize the project for its public launch and future monetization.

### Change Log

| Date | Version | Description | Author |
| --- | --- | --- | --- |
| 2025-09-20 | 1.0 | Initial brownfield analysis | Winston (Architect) |

## Quick Reference - Key Files and Entry Points

### Critical Files for Understanding the System

*   **Main Backend Application**: `shargain/`
*   **Core Business Logic**: `shargain/offers/application/` (Contains the command/query handlers)
*   **API Layer**: `shargain/public_api/api.py` (Exposes the business logic to the web)
*   **Authentication**: `shargain/public_api/auth.py` (Handles user login/signup)
*   **Database Models**: `shargain/*/models.py` (Standard Django models)
*   **Frontend Application**: `frontend/`
*   **Main Frontend Entrypoint**: `frontend/src/main.tsx`

## High Level Architecture

### Technical Summary
The project is a web application with a decoupled frontend and backend. The backend is a monolithic Django application that exposes a REST API. It has a separate, out-of-repository scraping service that pushes data to it. The frontend is a modern single-page application (SPA). The entire system is designed to be containerized for deployment.

### Actual Tech Stack

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

### Repository Structure Reality Check

*   **Type**: Monorepo (Backend and Frontend in the same repository).
*   **Package Manager**: `pnpm` for the frontend, `uv`/`poetry` for the backend.
*   **Notable**: A separate, out-of-repository project exists for the scrapers.

## Source Tree and Module Organization

### Project Structure (Actual)
```text
shargain/
├── frontend/            # React SPA
│   ├── src/
│   │   ├── routes/      # File-based routing with TanStack Router
│   │   └── ...
│   ├── package.json     # Frontend dependencies (pnpm)
│   └── vite.config.ts   # Vite build configuration
├── shargain/            # Django Project
│   ├── offers/          # Core "offers" Django App
│   │   ├── application/ # Core business logic (Commands/Queries)
│   │   ├── models.py    # Database models
│   │   └── ...
│   ├── public_api/      # Django Ninja API Layer
│   │   ├── api.py
│   │   └── auth.py
│   ├── settings/        # Django settings
│   └── manage.py        # Django management script
├── docs/                # Project documentation
├── deployment/          # Deployment scripts and configs
├── pyproject.toml       # Backend dependencies (poetry/uv)
└── compose.yml          # Docker Compose configuration
```

### Key Modules and Their Purpose

*   **`shargain/offers/application/`**: The heart of the backend. It contains the core business logic, cleanly separated into commands (write operations) and queries (read operations). This is the most important module to understand for backend development.
*   **`shargain/offers/services/`**: Contains specialized service classes that act as facades for specific business domains. Includes the `QuotaService` which is the official internal API and facade for managing offer quotas. The service supports overlapping quota periods with precedence given to the quota with the latest `period_start`.
*   **`shargain/public_api/`**: The presentation layer. It uses Django Ninja to expose the application services as a secure, session-authenticated REST API for the frontend.
*   **`frontend/src/routes/`**: The core of the frontend application, using file-based routing. Each file here represents a page or view in the application.

## Data Models and APIs

### Data Models
The source of truth for data models are the Django model files (e.g., `shargain/offers/models.py`, `shargain/accounts/models.py`). These define the schema for the PostgreSQL database.

#### New Subscription/Billing Models
With the introduction of subscription tiers, a new `OfferQuota` model was added to `shargain/offers/models.py` to track offer limits per user and target. The `QuotaService` allows overlapping quota periods, with the quota having the latest `period_start` taking precedence when multiple quotas are active for the same target. This provides a scalable foundation for the future subscription and billing system.

### API Specifications
The backend exposes an OpenAPI-compliant REST API. The frontend uses `openapi-ts` to generate a typed client from this specification, ensuring type safety between the frontend and backend. The main API definition can be found in `shargain/public_api/api.py`.

## Development and Deployment

### Local Development Setup
The project can be run locally using Docker Compose (`docker compose up`) or natively using `uv` for the backend and `pnpm` for the frontend, as detailed in the root `README.md`.

### Build and Deployment Process
*   **Build Commands**: `pnpm build` for the frontend; the backend is not compiled.
*   **Deployment**: The presence of `docker-compose-assets.yml` and a `deployment` directory suggests a container-based deployment strategy.

## Testing Reality

### Current Test Coverage
*   **Backend**: `pytest` is configured. The exact coverage is unknown without running the tests, but the configuration is robust.
*   **Frontend**: `vitest` is configured for testing.

### Running Tests
```bash
# Backend
pytest shargain

# Frontend
pnpm test
```
