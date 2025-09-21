# Source Tree and Module Organization

## Project Structure (Actual)
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

## Key Modules and Their Purpose

*   **`shargain/offers/application/`**: The heart of the backend. It contains the core business logic, cleanly separated into commands (write operations) and queries (read operations). This is the most important module to understand for backend development.
*   **`shargain/public_api/`**: The presentation layer. It uses Django Ninja to expose the application services as a secure, session-authenticated REST API for the frontend.
*   **`frontend/src/routes/`**: The core of the frontend application, using file-based routing. Each file here represents a page or view in the application.
