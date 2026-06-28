## 1. Dependencies and Settings (django-prometheus)

- [x] 1.1 Add `django-prometheus` to `pyproject.toml` dependencies and run `uv sync`
- [x] 1.2 Add `django_prometheus` to the top of `INSTALLED_APPS` in `shargain/settings/base.py`
- [x] 1.3 Add `PrometheusBeforeMiddleware` as first entry and `PrometheusAfterMiddleware` as last entry in `MIDDLEWARE` in `shargain/settings/base.py`
- [x] 1.4 Add `path("metrics/", include("django_prometheus.urls"))` to `shargain/urls.py`
- [x] 1.5 Strip django-prometheus apps and middleware from test settings in `shargain/settings/tests.py` (mirror the debug_toolbar pattern)

## 2. Dependencies and Setup (OpenTelemetry)

- [x] 2.1 Confirm the project uses `psycopg2-binary` (not `psycopg` v3) by inspecting `pyproject.toml`
- [x] 2.2 Add OTel dependencies to `pyproject.toml` with correct version constraints and run `uv sync`:
  - `opentelemetry-api>=1.41.0,<2`
  - `opentelemetry-sdk>=1.41.0,<2`
  - `opentelemetry-exporter-otlp>=1.41.0,<2`
  - `opentelemetry-instrumentation-django>=0.62b0,<0.63`
  - `opentelemetry-instrumentation-psycopg2>=0.62b0,<0.63`
  - `opentelemetry-instrumentation-requests>=0.62b0,<0.63`
  - `opentelemetry-instrumentation-logging>=0.62b0,<0.63`
- [x] 2.3 Verify all packages installed correctly with `uv run python -c "from opentelemetry.instrumentation.django import DjangoInstrumentor; print('OK')"`

## 3. OTel Initialization — Gunicorn post_fork Hook

- [x] 3.1 Create `gunicorn.conf.py` in project root with a `post_fork` hook that:
  - Creates a `TracerProvider` with `Resource` containing `SERVICE_NAME` and per-worker `SERVICE_INSTANCE_ID` (via `uuid4()`)
  - Adds `BatchSpanProcessor` pointed at `OTEL_EXPORTER_OTLP_ENDPOINT` (default: `http://jaeger:4318/v1/traces`)
  - Sets the global tracer provider via `trace.set_tracer_provider()`
  - Calls `DjangoInstrumentor().instrument(is_sql_commenter_enabled=False)`, `Psycopg2Instrumentor().instrument()`, `RequestsInstrumentor().instrument()`, and `LoggingInstrumentor().instrument()`
- [x] 3.2 Add an idempotency guard: check `trace.get_tracer_provider()` before instrumenting (catches the dev server single-process case)
- [x] 3.3 Update `deployment/docker/compose.yml` command from `gunicorn shargain.wsgi -w 4 -b 0.0.0.0:8010` to `gunicorn shargain.wsgi -c gunicorn.conf.py -w 4 -b 0.0.0.0:8010`
- [x] 3.4 Keep `shargain/wsgi.py` minimal — no OTel init code there (the single-process dev server case is handled by the guard pattern in gunicorn.conf.py)

## 4. Manual Instrumentation — business-logic spans

- [x] 4.1 Add OpenTelemetry tracing imports and manual span creation in `offers.services.batch_create`: a top-level span for the overall batch operation and child spans for individual offer creation steps
- [x] 4.2 Verify manual spans propagate trace context correctly (spans appear under the Django request span, not as orphaned traces)

## 5. Infrastructure — Dev Monitoring Stack

- [x] 5.1 Update `docker-compose.yml` web service from runserver to gunicorn with `-c gunicorn.conf.py -w 1 -b 0.0.0.0:8000`, add `OTEL_*` env vars
- [x] 5.2 Add `jaeger` service to `docker-compose.yml` using `jaegertracing/jaeger:2.19.0` with OTLP HTTP on port 4318, ports `4318:4318`, `16686:16686`
- [x] 5.3 Add `prometheus` service to `docker-compose.yml` with config mounted from `deployment/dev/prometheus.yml`, port `9090:9090`
- [x] 5.4 Create `deployment/dev/prometheus.yml` scrape config targeting `web:8000/metrics`

## 6. Test Settings and Isolation

- [x] 6.1 Ensure `shargain/settings/tests.py` strips django-prometheus apps and middleware (if they interfere with tests)
- [x] 6.2 Ensure tests that exercise views work correctly with the new middleware stack
- [x] 6.3 Verify that OTel instrumentation does not activate during tests (it's gated behind `gunicorn.conf.py`/`wsgi.py`, which tests don't load)
- [x] 6.4 If testing manual spans in `offers.services.batch_create`, use OTel's `InMemorySpanExporter` with a `@pytest.fixture` to assert span creation without needing Jaeger

## 7. Verification

- [x] 7.1 Run `just quality-check` (Ruff lint/format, mypy) to verify no issues
- [x] 7.2 Run `just test` (pytest) to confirm all existing tests pass
- [ ] 7.3 Start the dev stack with `docker compose up` and verify `/metrics/` returns 200 with Prometheus content
- [ ] 7.4 Hit a Django endpoint (e.g. `/api/public/targets/`) and confirm `django_http_request_latency_seconds` appears in `/metrics/` output
- [ ] 7.5 Verify Jaeger starts and traces appear by checking the Jaeger UI at `http://localhost:16686`
- [ ] 7.6 Verify log records emitted during a request contain `otelTraceID` and `otelSpanID` attributes
- [ ] 7.7 Verify Prometheus is scraping successfully at `http://localhost:9090/targets`
