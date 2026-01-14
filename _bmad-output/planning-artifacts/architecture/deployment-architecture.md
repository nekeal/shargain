# Deployment Architecture

## Deployment Strategy

The entire application is deployed as a set of Docker containers, orchestrated by Docker Compose on a single server.

-   **Frontend Deployment:**
    -   **Platform:** The frontend is built into a static bundle and placed into a lightweight Nginx Docker container.
    -   **Build Command:** `pnpm build`
    -   **Output Directory:** `dist`
    -   **CDN/Edge:** Traefik serves the static files directly. For higher performance, a CDN like Cloudflare could be placed in front of the entire application.

-   **Backend Deployment:**
    -   **Platform:** The Django application is deployed as a Docker container using Gunicorn as the WSGI server.
    -   **Build Command:** `docker compose -f compose.yml build backend`
    -   **Deployment Method:** The production `compose.yml` file is run on the server, which starts the `backend` API container, runs database `migrations`, and collects static files.

## CI/CD Pipeline

We use a system called GitHub Actions to create an automated assembly line for our code. Whenever a developer merges new code into the `main` branch, this assembly line kicks off automatically to ensure the code is tested and safely deployed to our live server.

The process works in three main stages:

1.  **Stage 1: Run All Tests**
    -   First, the system acts as a quality checker. It automatically runs every single test for both the frontend and the backend.
    -   **Goal:** To catch bugs early. If even one test fails, the process stops immediately, and the team is notified. This prevents a bad update from ever leaving the starting gate.

2.  **Stage 2: Build the Application "Boxes"
    -   Once all tests pass, the system builds the application. It packages the backend code and the frontend code into separate, standardized containers called "Docker images".
    -   **Goal:** To create self-contained, ready-to-run versions of our application. Think of them as perfectly packed, sealed boxes that will run identically anywhere. These boxes are then uploaded to a secure storage library (a container registry).

3.  **Stage 3: Deploy to the Live Server
    -   After the "boxes" are built and stored, the system automatically connects to our production server.
    -   It tells the server to pull down the new application boxes and start them up, seamlessly replacing the old ones.
    -   **Goal:** To update the live application with the new code, with zero manual work and zero downtime.

## Environments

| Environment | Frontend URL | Backend URL | Purpose |
| :--- | :--- | :--- | :--- |
| Development | `http://localhost:3000` | `http://localhost:8000` | Local development |
| Staging | `https://staging.yourdomain.com` | `https://staging.yourdomain.com` | Pre-production testing |
| Production | `https://yourdomain.com` | `https://yourdomain.com` | Live environment |
