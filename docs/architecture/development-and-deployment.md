# Development and Deployment

## Local Development Setup
The project can be run locally using Docker Compose (`docker compose up`) or natively using `uv` for the backend and `pnpm` for the frontend, as detailed in the root `README.md`.

## Build and Deployment Process
*   **Build Commands**: `pnpm build` for the frontend; the backend is not compiled.
*   **Deployment**: The presence of `docker-compose-assets.yml` and a `deployment` directory suggests a container-based deployment strategy.
