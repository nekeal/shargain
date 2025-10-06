# Monitoring and Observability

## Monitoring Stack

We will use **Sentry** as our primary, unified monitoring platform. It provides a comprehensive solution covering error tracking, performance monitoring, and session replay for both the frontend and backend.

-   **Frontend Monitoring:** Sentry Performance Monitoring will be used to track Core Web Vitals and custom performance metrics. Sentry Session Replay will help diagnose user-facing issues.
-   **Backend Monitoring:** Sentry Performance Monitoring will trace transactions, identify slow API endpoints, and find database query bottlenecks.
-   **Error Tracking:** Sentry Error Tracking will be used across both the frontend and backend to capture, aggregate, and alert on all application errors in real-time.
-   **Logging:** The application will log to `stdout`/`stderr` within the Docker containers. In production, the Docker host can be configured to forward these logs to a log aggregation service (e.g., Datadog, Logstash) for long-term storage and analysis.

## Key Metrics

-   **Frontend Metrics:**
    -   Core Web Vitals (LCP, FID, CLS): To measure the user's perceived loading experience.
    -   JavaScript Errors: The rate of unhandled exceptions in the browser.
    -   API Latency: The time it takes for API requests to complete, as measured from the client-side.
    -   User Interactions: Key conversion funnels, such as the number of users who successfully create a scraping target.

-   **Backend Metrics:**
    -   Request Rate (Throughput): The number of requests per minute the API is handling.
    -   Error Rate: The percentage of 5xx server errors.
    -   API Latency (p95/p99): The 95th and 99th percentile response times for API endpoints.
    -   Database Query Performance: The execution time of the slowest and most frequent database queries.
