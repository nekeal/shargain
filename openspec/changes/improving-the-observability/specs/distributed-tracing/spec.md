## ADDED Requirements

### Requirement: Traces are exported to Jaeger via OTLP HTTP
The system SHALL export OpenTelemetry spans to a Jaeger endpoint via OTLP HTTP/protobuf. The exporter endpoint SHALL be configurable via the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable, defaulting to `http://jaeger:4318/v1/traces`.

#### Scenario: Traces appear in Jaeger after a request
- **WHEN** a Django view processes an HTTP request
- **THEN** a trace SHALL appear in Jaeger for service `shargain-django` containing spans for the request

### Requirement: Django requests are instrumented
Django request handling SHALL be instrumented via `DjangoInstrumentor().instrument()`, producing spans for each HTTP request with the URL route, HTTP method, and status code as span attributes.

#### Scenario: Django span is created for each request
- **WHEN** a request is made to any Django view
- **THEN** a span named with the URL pattern SHALL be created under service `shargain-django`

### Requirement: Database queries are instrumented
psycopg2 database queries SHALL be instrumented via `Psycopg2Instrumentor().instrument()`, producing child spans under the Django request span for each SQL query.

#### Scenario: DB query spans appear under request span
- **WHEN** a Django view executes a SQL query
- **THEN** a child span for that query SHALL appear in the trace, showing the SQL statement and duration

### Requirement: Outbound HTTP calls are instrumented
Requests library HTTP calls SHALL be instrumented via `RequestsInstrumentor().instrument()`, producing child spans for each outbound HTTP request.

#### Scenario: HTTP client span appears under request span
- **WHEN** a Django view makes an outbound HTTP request via the `requests` library
- **THEN** a child span SHALL appear in the trace showing the HTTP method, URL, and duration

### Requirement: OTel initialization runs in gunicorn post_fork hook
TracerProvider and instrumentor setup SHALL run in a `gunicorn.conf.py` `post_fork` hook to ensure each forked worker initialises its own tracer provider, span processor, and exporter connections.

#### Scenario: Gunicorn worker has active tracer
- **WHEN** a Gunicorn worker process forks
- **THEN** a TracerProvider SHALL be configured as the global trace provider within that worker, separate from the parent process

#### Scenario: Dev server falls back to wsgi.py init
- **WHEN** the Django dev server (`manage.py runserver`) starts via `wsgi.py`
- **THEN** the TracerProvider SHALL be configured with a guard check to avoid double-instrumentation on reload

### Requirement: Noisy URLs are excluded from tracing
The `OTEL_PYTHON_DJANGO_EXCLUDED_URLS` env var SHALL contain `/metrics`, `/health.*`, `/readiness.*`, and `/static/.*` to avoid tracing Prometheus scraping and health-check traffic.

### Requirement: Log records are enriched with trace context
`LoggingInstrumentor` SHALL be initialised alongside other OTel instrumentations to inject `trace_id`, `span_id`, and `trace_flags` into every Python log record emitted during an active trace.

#### Scenario: Log record contains trace ID during a request
- **WHEN** a Django view processes a request and emits a log message
- **THEN** the log record SHALL contain `otelTraceID` and `otelSpanID` attributes matching the current trace

### Requirement: Jaeger service is defined in the monitoring compose
The shared monitoring Docker Compose file SHALL include a `jaeger` service using image `jaegertracing/all-in-one:1.76` with OTLP HTTP receiver enabled on port 4318, connected to the `traefik` external network so the application can reach it across stacks.

#### Scenario: Jaeger container starts successfully
- **WHEN** `docker compose up -d` is run with the monitoring compose file
- **THEN** the Jaeger container SHALL start and listen on port 4318 for OTLP HTTP traces

### Requirement: Business-logic spans are created manually in key services
`offers.services.batch_create` SHALL contain explicit OpenTelemetry spans to capture business-logic timing (overall batch processing, per-offer creation).

#### Scenario: Batch create appears as a named span in the trace
- **WHEN** `offers.services.batch_create` is invoked
- **THEN** a named span for the batch processing SHALL appear in the trace, wrapping the DB query and HTTP call spans within it
