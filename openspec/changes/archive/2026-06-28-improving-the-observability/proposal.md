## Why

The backend currently has no per-endpoint latency visibility, no DB query timing, and no distributed tracing. Sentry provides error tracking but lacks the granular metrics needed to diagnose performance regressions and understand system behavior under load. Adding Prometheus metrics and OpenTelemetry traces will enable data-driven capacity planning, faster debugging of slow endpoints, and observability into the full request lifecycle.

## What Changes

- Add `django-prometheus` to expose standard RED metrics (Rate, Errors, Duration) per endpoint, scraped by the existing Prometheus + Grafana stack on the server
- Add OpenTelemetry instrumentation for Django, psycopg2, requests, and logging to produce distributed traces with trace-log correlation, shipped to Jaeger (in-memory, OTLP HTTP)
- Add Jaeger to the shared monitoring compose stack (alongside existing Prometheus + Grafana + Loki), reachable via a shared Docker network
- Add manual OpenTelemetry instrumentation in `offers.services.batch_create` to capture business-logic spans
- Add `gunicorn.conf.py` with OTel initialization in a `post_fork` hook (replaces `wsgi.py` init)
- Add environment variables for OTEL configuration on the web container

## Capabilities

### New Capabilities
- `metrics-endpoint`: Prometheus metrics export at `/metrics/` with RED metrics (rate, errors, duration) per Django view, DB query timing histogram, and model CRUD counters — scraped by Prometheus and visualized in Grafana
- `distributed-tracing`: OpenTelemetry-based distributed tracing across Django requests, DB queries, outbound HTTP calls, and key business-logic services, exported to Jaeger via OTLP HTTP/protobuf and browsable in Grafana via the Jaeger datasource

### Modified Capabilities
- None — no existing specs with requirement changes

## Impact

- **New dependencies**: `django-prometheus`, `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp`, `opentelemetry-instrumentation-django`, `opentelemetry-instrumentation-psycopg2`, `opentelemetry-instrumentation-requests`, `opentelemetry-instrumentation-logging`
- **Settings changes**: `INSTALLED_APPS` and `MIDDLEWARE` in `base.py` will include django-prometheus entries
- **URLs**: `/metrics/` endpoint added to `shargain/urls.py`
- **Docker compose**: Jaeger service added to the monitoring compose (alongside existing Prometheus, Grafana, Loki), connected to the `traefik` shared network for cross-stack reachability
- **Gunicorn config**: `gunicorn.conf.py` created with `post_fork` hook for per-worker OTel initialization; compose command updated to `-c gunicorn.conf.py`
- **Env vars**: `OTEL_*` variables needed on the web container
- **Manual instrumentation**: Custom spans added in `offers.services.batch_create` for business-logic visibility
- **Logging**: Trace IDs injected into every log record via `LoggingInstrumentor` — no application code changes needed
- **Sentry**: Documented coexistence decision — Sentry remains error-only with `DjangoIntegration`; no changes to `production.py`
- **No breaking changes** to existing APIs or data models
