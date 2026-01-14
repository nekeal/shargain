# Components

## Frontend Application (React SPA)

-   **Responsibility:** To provide the configuration interface for the Shargain platform. Its purpose is to allow users to manage their account, scraping targets, and notification channels. **It is explicitly out of scope for this component to display the offers discovered by the scraper.** Users receive offers only via their configured notification channels (e.g., Telegram, Discord).
-   **Key Interfaces:** Consumes the backend REST API for all data and business operations. It does not have any direct access to the database or other backend services.
-   **Dependencies:** Depends entirely on the **Backend API** to function.
-   **Technology Stack:** React 19, Vite, TypeScript, TanStack Router, TanStack Query, Tailwind CSS.

## Scraping Microservice (External)

-   **Responsibility:** To operate as a fully independent service that drives the scraping process. It periodically polls the main backend for jobs, executes the scraping, and pushes the results back.
-   **Key Interfaces:**
    -   Makes scheduled `GET` requests to the **Backend API** to fetch a list of active `ScrapingUrl`s.
    -   Makes `POST` or `PUT` requests to the **Backend API** to submit the discovered `Offer` data.
    -   Makes outbound HTTP requests to the external websites being scraped.
-   **Dependencies:**
    -   **Backend API:** Relies on the main application's API being available to fetch jobs and submit results.
    -   **External Websites:** Dependent on the availability and structure of the target websites.
-   **Technology Stack:** Independent of this project. The specific technologies are not relevant to this architecture, only its interfaces are.

## Backend API (Django)

-   **Responsibility:** To serve the frontend application, manage core data, and provide an interface for the external scraper. Its duties include:
    -   Handling user authentication and account management.
    -   Exposing a REST API for the **Frontend Application** to manage configurations.
    -   **Exposing a secure, internal API endpoint to provide active `ScrapingUrl` data to the external Scraping Microservice.**
    -   **Exposing a secure, internal API endpoint to receive `Offer` data from the Scraping Microservice.**
    -   Dispatching notification tasks to the **Async Job Service (Celery)** after new offers are received.
-   **Key Interfaces:**
    -   Exposes a public RESTful API for the **Frontend Application**.
    -   **Exposes an internal-facing RESTful API for the Scraping Microservice.** This should be secured via an API key or other non-session-based mechanism.
    -   Connects to the **Database** (PostgreSQL).
    -   Connects to the **Message Broker** (RabbitMQ).
-   **Dependencies:**
    -   **Database (PostgreSQL)**
    -   **Message Broker (RabbitMQ)**
    -   **Async Job Service (Celery)**
-   **Technology Stack:** Django, Django Ninja, Python, Gunicorn.

## Component Diagrams

```mermaid
graph TD
    subgraph "User"
        U[User's Browser]
    end

    subgraph "Shargain System (Hosted on IaaS)"
        T[Traefik Reverse Proxy]

        subgraph "Frontend"
            F[React SPA <br>(Nginx Container)]
        end

        subgraph "Backend"
            B[Backend API <br>(Django/Gunicorn Container)]
            C[Async Job Service <br>(Celery Container)]
            DB[(PostgreSQL Database)]
            MQ[(RabbitMQ Broker)]
        end
    end

    subgraph "External Services"
        S[Scraping Microservice]
        W[Target Websites]
        N[Notification Services <br>(e.g., Telegram API)]
    end

    U -- "Interacts with" --> F
    F -- "API Calls (HTTPS)" --> T
    T -- "Serves Static Files" --> F
    T -- "Forwards API Traffic" --> B

    B -- "Reads/Writes Data" --> DB
    B -- "Dispatches Jobs" --> MQ
    C -- "Consumes Jobs" --> MQ
    C -- "Reads/Writes Data" --> DB
    C -- "Sends Notifications" --> N

    S -- "Fetches Scraping Jobs (Internal API)" --> B
    S -- "Submits Found Offers (Internal API)" --> B
    S -- "Scrapes" --> W
```
