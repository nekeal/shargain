# Development Workflow

## Local Development Setup

### Prerequisites

Before you begin, ensure you have the following tools installed on your system:
-   Docker & Docker Compose
-   `pnpm` (for frontend package management)
-   `uv` (for backend Python package management)

### Initial Setup

To set up the project for the first time, follow these steps:

```bash
# 1. Clone the repository
git clone <repository_url>
cd shargain

# 2. Set up environment variables for the backend
cp .env.example .env
# (Then edit .env with your local secrets)

# 3. Install frontend dependencies
cd frontend
pnpm install

# 4. Generate the API client
pnpm generate:api-client
cd ..

# 5. Build and start the backend services (database, etc.)
docker-compose up --build -d
```

### Development Commands

Once the initial setup is complete, use these commands for daily development:

```bash
# Start all services (backend API, database, etc.)
docker-compose up

# Start only the frontend development server (in a separate terminal)
cd frontend && pnpm dev

# Run frontend tests
cd frontend && pnpm test

# Run backend tests
pytest shargain/
```

## Environment Configuration

### Required Environment Variables

-   **Backend (`.env`):**
    -   `SECRET_KEY`: Django's secret key for cryptographic signing.
    -   `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Credentials for the database.
    -   `TELEGRAM_BOT_TOKEN`: The secret token for the Telegram Bot API.

-   **Frontend (`frontend/.env.development`):**
    -   `VITE_API_URL`: The full URL to the local backend API (e.g., `http://localhost:8000`).
