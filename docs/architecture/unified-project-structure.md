# Unified Project Structure

The project is organized as a monorepo, containing the frontend, backend, and all related configuration in a single Git repository. This co-location simplifies cross-stack development and ensures consistency.

```plaintext
shargain/ (Monorepo Root)
├── .github/                    # CI/CD workflows (GitHub Actions)
├── docs/                       # Project documentation
│   └── architecture.md         # This document
├── frontend/                   # React SPA (The Frontend Application)
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── routes/             # File-based routing
│   │   └── lib/
│   │       └── api/            # Auto-generated API client and hooks
│   ├── public/                 # Static assets
│   ├── openapi.json            # The API contract
│   └── package.json            # Frontend dependencies
├── shargain/                   # Django Project (The Backend API)
│   ├── accounts/               # User management app
│   ├── offers/                 # Offer and ScrappingTarget models
│   ├── notifications/          # Notification models and logic
│   ├── public_api/             # API endpoint definitions
│   ├── settings/               # Django settings
│   └── manage.py               # Django management script
├── .gitignore
├── compose.yml                 # Production Docker configuration
├── docker-compose.yml          # Local development Docker configuration
└── pyproject.toml              # Backend dependencies
```
