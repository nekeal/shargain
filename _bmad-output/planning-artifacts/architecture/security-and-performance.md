# Security and Performance

## Security Requirements

-   **Frontend Security:**
    -   **CSP Headers:** A strict Content Security Policy (CSP) must be implemented to prevent Cross-Site Scripting (XSS) attacks. It should only allow scripts, styles, and images from trusted, specified domains.
    -   **XSS Prevention:** React inherently mitigates many XSS risks by escaping JSX content. Developers must avoid using `dangerouslySetInnerHTML` without proper sanitization.
    -   **Secure Storage:** The application uses secure, `HttpOnly` session cookies for authentication, which are not accessible to JavaScript. This is the primary defense against token-stealing XSS attacks.

-   **Backend Security:**
    -   **Input Validation:** All incoming API data is automatically validated by Django Ninja against the Pydantic schemas. This prevents malformed data from being processed.
    -   **Rate Limiting:** Sensitive endpoints, especially login and password reset, must be rate-limited to prevent brute-force attacks.
    -   **CORS Policy:** The backend's Cross-Origin Resource Sharing (CORS) policy must be configured to only allow requests from the production frontend domain.

-   **Authentication Security:**
    -   **Token Storage:** Handled by Django's secure, server-side session framework using `HttpOnly` cookies.
    -   **Password Policy:** The application must enforce strong password policies using Django's built-in password validators (e.g., minimum length, complexity).
    -   **Secrets Management:** All secrets (e.g., `SECRET_KEY`, database passwords, API tokens) must be loaded from environment variables and never hard-coded.

## Performance Optimization

-   **Frontend Performance:**
    -   **Bundle Size Target:** The initial JavaScript bundle size should be kept under 250KB. Use code-splitting by route (handled by Vite) and lazy-load heavy components.
    -   **Loading Strategy:** Leverage TanStack Query's caching to avoid re-fetching data unnecessarily. Static assets should have long-lived browser cache headers.
    -   **Image Optimization:** All images should be served in modern formats (like WebP) and appropriately sized for their container.

-   **Backend Performance:**
    -   **Response Time Target:** API endpoints should have a 95th percentile (p95) response time of under 200ms.
    -   **Database Optimization:** Ensure all foreign keys and frequently filtered columns have database indexes. Use tools like `django-debug-toolbar` during development to identify and eliminate slow or duplicate queries.
    -   **Asynchronous Operations:** Continue to use the `Async Job Service (Celery)` for any operation that is not instantaneous, ensuring the API remains fast.
