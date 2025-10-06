# Backend Architecture

This section describes the architecture of the backend system, which is a modular monolith Django application designed for clarity, security, and performance.

## Application Structure (Django Apps)

The backend is organized into several discrete Django applications, each with a single, well-defined responsibility. This modular approach simplifies development and maintenance.

-   `shargain/accounts/`: Manages user models, profiles, and authentication. It integrates with `django-allauth` to handle registration and login flows (including social auth if configured).
-   `shargain/offers/`: The core application containing the primary business models: `ScrappingTarget`, `ScrapingUrl`, and `Offer`. It holds the logic for managing these resources. The business logic mainly lives in `shargain/offers/application/` directory which contains commands and queries which are interface to the rest of the application.
-   `shargain/notifications/`: Manages `NotificationConfig` models and contains the business logic for preparing and dispatching notifications to the async task queue.
-   `shargain/public_api/`: This app serves as the primary entry point for the REST API. It initializes the `NinjaAPI` instance and includes modular `APIRouter` instances from the other applications to construct the complete `openapi.json` specification.

## API Design with Django Ninja

Our API design philosophy prioritizes type safety, automatic documentation, and developer efficiency.

-   **Contract-First via Code:** We use Django Ninja to automatically generate the `openapi.json` specification from our Python code. Type hints and Pydantic schemas define the API contract, ensuring the implementation and documentation are always synchronized.
-   **Schema Validation:** All incoming request data (bodies, query parameters) is automatically validated against Pydantic schemas. This provides robust data integrity at the edge of the application, preventing invalid data from reaching the business logic.
-   **Modular Routers:** To keep the API code organized, each Django app exposes its own `APIRouter`. These routers are then included in the main `NinjaAPI` instance in the `public_api` app. This allows API endpoints to live alongside the models and logic they relate to.

## Authentication and Authorization

Security is handled with a multi-layered approach.

-   **Frontend Authentication:** The primary mechanism is **session-based authentication**. After a user logs in, Django sets a secure, `HttpOnly` session cookie. This cookie is automatically sent by the browser on subsequent requests and is not accessible to JavaScript, mitigating the risk of XSS-based token theft.
-   **Internal API Authentication:** The endpoints for the `Scraping Microservice` will be secured using a simple **API Key**. The scraper will include a pre-shared secret in an HTTP header, which will be validated by a custom Django Ninja authentication class.
-   **Authorization:** Permissions are enforced within each API view. For any action on a resource, the backend logic **MUST** first verify that the authenticated user (`request.user`) is the owner of that resource. This prevents one user from accessing or modifying another user's data.

## Asynchronous Task Processing (Celery)

To ensure the API remains fast and responsive, any operation that is not instantaneous is delegated to a background task.

-   **Flow:**
    1.  **Dispatch:** When a long-running action is triggered (e.g., sending a notification), the API view calls `.delay()` on a Celery task function (e.g., `send_telegram_notification.delay(offer_id)`).
    2.  **Queue:** This action places a message describing the job onto a **RabbitMQ** queue and the API returns an immediate response to the client.
    3.  **Execution:** An independent **Celery worker** process continually monitors the queue. It picks up the job message and executes the task function in the background, without blocking the web server.

## Database Access

-   **Django ORM:** All database interactions are performed exclusively through the Django Object-Relational Mapper (ORM). Direct SQL queries are forbidden. This provides a secure, abstract interface for database operations, preventing SQL injection vulnerabilities and making the code more portable and readable.
-   **Migrations:** The database schema is managed declaratively via Django models. Schema changes are version-controlled and applied using Django's built-in migration system (`makemigrations` and `migrate`).
