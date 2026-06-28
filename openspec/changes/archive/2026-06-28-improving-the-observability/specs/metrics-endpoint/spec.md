## ADDED Requirements

### Requirement: Metrics endpoint exposes RED metrics per Django view
The system SHALL expose a `/metrics/` HTTP endpoint returning Prometheus-formatted metrics. The metrics SHALL include per-view request rate, error count, and latency histogram (p50/p95/p99) labeled by view name, HTTP method, and status code.

#### Scenario: Metrics endpoint returns 200 with prometheus content type
- **WHEN** a GET request is sent to `/metrics/`
- **THEN** the response SHALL have status 200 and content type `text/plain; version=0.0.4; charset=utf-8`

#### Scenario: Request latency histogram is populated after an API call
- **WHEN** a request is made to any Django view
- **THEN** the `django_http_request_latency_seconds` histogram SHALL contain a new observation with labels for the view, method, and status code

#### Scenario: Request counter is incremented after each request
- **WHEN** a request completes with any status code
- **THEN** the `django_http_requests_total` counter SHALL be incremented with labels for view, method, and status

### Requirement: DB query timing metrics are collected
The system SHALL expose `django_db_query_duration_seconds` histogram and `django_db_queries_total` counter tracking all database queries executed during a request.

#### Scenario: DB query duration histogram is populated after a view executes a query
- **WHEN** a view executes a database query
- **THEN** the `django_db_query_duration_seconds` histogram SHALL contain an observation for that query

### Requirement: Model CRUD operations are counted
The system SHALL expose `django_model_inserts_total`, `django_model_updates_total`, and `django_model_deletes_total` counters per model class.

#### Scenario: Model create increments insert counter
- **WHEN** a new model instance is saved
- **THEN** the `django_model_inserts_total` counter SHALL be incremented with a label for the model name

### Requirement: django-prometheus middleware is applied to all requests
`PrometheusBeforeMiddleware` SHALL be the first middleware and `PrometheusAfterMiddleware` SHALL be the last middleware in the MIDDLEWARE list.

#### Scenario: Middleware order is correct
- **WHEN** the MIDDLEWARE setting is inspected
- **THEN** `django_prometheus.middleware.PrometheusBeforeMiddleware` SHALL be at index 0 and `django_prometheus.middleware.PrometheusAfterMiddleware` SHALL be at the last index
