## Context

The backend (`shargain`) is a Django application running in Docker containers. The server already runs a separate monitoring compose stack with Prometheus, Grafana, and Loki, but no application metrics or traces are emitted. Sentry is configured in `production.py` for error tracking only — there is no per-endpoint latency data, DB query timing, or request-level trace visibility. Celery tasks exist in code but are not running in production.

The codebase has a dead Grafana integration (admin iframes pointing to a defunct `jessdefiance.art/grafana/`) and no Prometheus or OpenTelemetry infrastructure.

## Goals / Non-Goals

**Goals:**
- Expose Prometheus RED metrics (Rate, Errors, Duration) per Django view at `/metrics/`
- Add DB query timing histograms and model CRUD counters via django-prometheus
- Add distributed tracing across Django requests, psycopg2 queries, and outbound HTTP calls via OpenTelemetry
- Add manual OpenTelemetry spans in `offers.services.batch_create` for business-logic visibility
- Ship traces to Jaeger (in-memory, no persistent storage) via OTLP HTTP/protobuf
- Add Jaeger to the shared monitoring compose stack, reachable via the `traefik` Docker network
- Configure OTEL environment variables on the web container
- Ensure all metrics/tracing code is omitted from test settings

**Non-Goals:**
- OpenTelemetry Collector (Jaeger accepts OTLP directly; collector adds ops burden at this scale)
- Exemplars (trace IDs embedded in Prometheus metrics) — requires forking or monkey-patching django-prometheus
- Tempo / other trace backends (Jaeger can be swapped later by changing one env var)
- Grafana "Trace to Logs" or "Metrics to Traces" linking (requires Loki or exemplars)
- Application-level custom metrics beyond what django-prometheus auto-exposes

## Decisions

### 1. django-prometheus over custom prometheus_client integration
**Chosen:** django-prometheus wraps `prometheus_client` with Django-specific middleware that auto-latches view names, methods, and status codes into metric labels. Provides histogram bucketing, DB query tracking via psycopg2 wrapper, and model CRUD counters out of the box.
**Rejected:** Manual `prometheus_client` instrumentation per view — higher maintenance, inconsistent labels, no auto-DB tracking.

### 2. OpenTelemetry over Prometheus-only approach
**Chosen:** OTel provides distributed tracing which Prometheus cannot. Traces show the full request lifecycle including DB queries and downstream HTTP calls. The OTel Django/psycopg2/requests auto-instrumentation packages capture spans with minimal application code changes. Manual spans are added for key business-logic boundaries (`offers.services.batch_create`).
**Rejected:** Prometheus-only — no trace context, no way to correlate a slow endpoint with its DB queries.

### 3. OTLP HTTP/protobuf (port 4318) over gRPC (port 4317)
**Chosen:** HTTP/protobuf avoids the `grpcio` C extension build dependency, is trivially debuggable with `curl`, and Jaeger's all-in-one receiver supports it natively.
**Rejected:** gRPC — adds native compilation dependency, harder to debug.

### 4. BatchSpanProcessor over SimpleSpanProcessor
**Chosen:** BatchSpanProcessor exports spans asynchronously in batches, eliminating per-span HTTP latency overhead.
**Rejected:** SimpleSpanProcessor — makes a synchronous HTTP request per span, destroying request latency.

### 5. Jaeger in dev compose over monitoring compose
**Chosen:** Jaeger lives in the development compose (`compose.dev.yml`) alongside Prometheus and Postgres. This keeps the dev environment self-contained with a single `docker compose -f compose.dev.yml up` command. The production compose (`compose.yml`) relies on OTEL env vars to point to an externally managed trace backend.
**Alternative considered:** Jaeger in a separate monitoring compose — requires `docker compose -f compose.dev.yml -f monitoring.yml up`, harder to discover, doesn't match the dev workflow.

### 6. Jaeger v2 over Tempo
**Chosen:** Jaeger v2 (`jaegertracing/jaeger:2.x`) runs the unified all-in-one binary in ~200MB RAM with in-memory storage — no object store dependency. Replaces the legacy `jaegertracing/all-in-one` image. Can be swapped for Tempo later by changing the OTLP endpoint.
**Rejected:** Tempo — requires object storage (S3/GCS), overkill at current scale.

### 7. Tracer init in gunicorn post_fork hook (not wsgi.py)
**Chosen:** Place OTel initialization in a `gunicorn.conf.py` `post_fork` hook, not in `wsgi.py`. Production runs `gunicorn -w 4` — gunicorn's pre-fork model loads the WSGI module in the parent process, and `fork()` does not copy `BatchSpanProcessor`'s background thread. Each worker initialises its own tracer provider via `post_fork`, avoiding orphaned threads and broken export sockets. The dev server (`runserver`) uses `wsgi.py` directly and runs single-process, so a guard condition checks whether `trace.get_tracer_provider()` is already configured.

**`service.instance.id`:** Not set manually — the SDK's `ServiceInstanceIdResourceDetector` (enabled by default since opentelemetry-sdk 1.41.1 / PR #5259) auto-generates a random UUID v4 on every `Resource.create()` call and regenerates it after `fork()` when PID changes, which is exactly the gunicorn worker scenario.
**Rejected:** 
  - **wsgi.py init** — breaks silently with gunicorn multi-worker (forked workers inherit dead exporter threads)
  - **Django AppConfig.ready()** — runs too early, before gunicorn forks, same problem
  - **Shared module imported from both places** — unnecessary without Celery in production

### 8. psycopg2 instrumentation (current stack uses psycopg2-binary)
**Chosen:** Install `opentelemetry-instrumentation-psycopg2`. Verify the project uses `psycopg2-binary` (check `pyproject.toml`) — if v3 (`psycopg`), use `opentelemetry-instrumentation-psycopg` instead. Set `is_sql_commenter_enabled=False` in `DjangoInstrumentor().instrument()` to avoid double-commenting SQL queries (django-prometheus wraps DB at the engine level while OTel wraps psycopg2; leaving SQLCommenter on would append duplicate trace comments).
**Rejected:** N/A — must match the installed psycopg variant exactly.

### 9. Exclude noisy URLs from tracing
**Chosen:** Set `OTEL_PYTHON_DJANGO_EXCLUDED_URLS=/metrics,/health.*,/readiness.*,/static/.*` to avoid polluting traces with Prometheus scraping and health-check noise.
**Rejected:** Tracing everything — wastes bandwidth and storage on non-business-relevant paths.

### 10. Manual instrumentation for business-logic boundaries
**Chosen:** Add explicit spans in `offers.services.batch_create` to capture business-logic timing (processing batches, individual offer creation). Auto-instrumentation covers DB queries and HTTP calls within these spans.
**Rejected:** Manual instrumentation in every view — too much overhead for the value at this stage.

### 11. Sentry DjangoIntegration + OTel coexistence
**Chosen:** Keep Sentry's error-only config (`DjangoIntegration` without `traces_sample_rate`) and run OTel for distributed tracing. Sentry's `DjangoIntegration` patches the same Django signals as `DjangoInstrumentor`, but the conflict is limited because Sentry is error-only (no performance/tracing). If Sentry tracing is ever needed in the future, replace `DjangoIntegration()` with Sentry's `OTLPIntegration` from `sentry-sdk[opentelemetry-otlp]`, which reads from OTel directly.
**Rejected:** 
  - **Disabling Sentry entirely** — would lose error tracking, which is stable and valuable
  - **Using Sentry's OTLPIntegration now** — Sentry pipeline is error-only; switching to OTLPIntegration adds risk for zero gain at this stage

### 12. Direct package pinning over opentelemetry-bootstrap
**Chosen:** Pin instrumentation packages directly in `pyproject.toml` without using `opentelemetry-bootstrap -a install`. The project uses `uv` for package management — OTel's own docs warn that `opentelemetry-bootstrap` can produce "errored or unexpected dependency setups" with `uv`. Direct pinning (`opentelemetry-instrumentation-django`, `-psycopg2`, `-requests`) is CI-safe, deterministic, and avoids an entire fragile build step. `opentelemetry-distro` is not needed — it's only required for zero-code instrumentation (the CLI launcher), not for programmatic `.instrument()` calls.
**Rejected:** 
  - **opentelemetry-bootstrap** — fragile with `uv`, installs ALL matching instrumentation packages (not just the three needed), adds non-determinism to Docker builds
  - **opentelemetry-distro** — only useful for the `opentelemetry-instrument` command-line launcher; unnecessary bloat for programmatic instrumentation

### 13. Trace-log correlation via opentelemetry-instrumentation-logging
**Chosen:** Add `opentelemetry-instrumentation-logging` to inject `trace_id`, `span_id`, and `trace_flags` into every Python log record. This connects log output to trace context with zero application code changes — every `logger.info(...)` call carries the current trace identifiers, making it possible to find all logs for a given trace in the log aggregator.
**Rejected:** 
  - **structlog** — adds a new logging dependency and requires code changes across all modules; overkill for trace ID injection alone
  - **No log correlation** — logs are disconnected from traces, making debugging slower when you need to correlate a trace with its log lines

### 14. Local dev monitoring stack in compose.dev.yml
**Chosen:** Replace the runserver-based dev compose with a gunicorn-based stack that includes Jaeger and Prometheus. This makes all verification tasks (metrics endpoint, Jaeger traces, Sentry+OTel coexistence) reproducible with a single `docker compose -f compose.dev.yml up`. The dev compose (`compose.dev.yml`) gets:

  - **web**: runs gunicorn with `gunicorn.conf.py` so OTel init runs, 1 worker for simplicity, OTEL env vars applied
  - **postgres**: unchanged
  - **jaeger**: `jaegertracing/jaeger:2.19.0` with OTLP HTTP on 4318, UI on 16686, in-memory storage
  - **prometheus**: scrapes `web:8000/metrics`, stores data locally, no external dependencies

  Prometheus scrape config is a new file at `deployment/dev/prometheus.yml`. Jaeger is ephemeral (no volumes). This replaces the separate `deployment/docker/monitoring.yml` approach — one compose file for both app and monitoring in dev.

  **Rejected:**
  - **Adding to separate monitoring.yml** — requires two `docker compose -f` commands, harder to discover, doesn't match the dev workflow
  - **Prometheus-only in dev** — no trace verification without Jaeger; defeats the purpose of local testing
  - **Keep runserver** — OTel init is gated behind gunicorn.conf.py; runserver wouldn't exercise tracing

## Risks / Trade-offs

- **[Risk] Double instrumentation with Django auto-reloader** → Use `--noreload` with `runserver` or check for existing instrumentation before calling `instrument()`. Mitigation: `gunicorn.conf.py` only runs in gunicorn context; the dev server is single-process and the guard pattern prevents re-instrumentation.
- **[Risk] Sentry DjangoIntegration + OTel conflict** → Both patch Django request handling internals. Mitigation: Sentry is error-only (`traces_sample_rate` not set), so the conflict is limited to signal handler stacking, not trace corruption. Add a smoke test that both instrumentations load without crashing. If Sentry tracing is ever enabled, switch to `OTLPIntegration`.
- **[Risk] psycopg2 vs psycopg v3 mismatch** → Wrong instrumentation package silently fails to instrument queries. Mitigation: verify `pyproject.toml` before installing, add a smoke test that checks `django_db_query_duration_seconds` exists after startup.
- **[Risk] Prometheus endpoint accidentally public** → `/metrics/` could expose request volume patterns. Mitigation: ensure it's behind Traefik or nginx with internal-network-only access in production.
- **[Risk] Jaeger memory pressure** → All-in-one with in-memory storage loses traces on restart and can OOM under heavy trace volume. Mitigation: set `OTEL_BSP_SCHEDULE_DELAY=5000` (5s batch interval) to reduce throughput; acceptable for current scale (<100 req/min).
- **[Risk] Metric cardinality explosion** → django-prometheus labels by view/method/status. High-cardinality paths (user-specific URLs) could inflate Prometheus storage. Mitigation: monitor metric series count after deploy, exclude high-cardinality views via `prometheus_monitored_views` if needed.
- **[Risk] LoggingInstrumentor conflicting with existing logging config** → `LoggingInstrumentor().instrument()` patches Python's root `logging.Logger` factory. If the project uses custom logging handlers that depend on unpatched log records, trace ID injection could break them. Mitigation: order initialization so `LoggingInstrumentor` runs last; test with the existing `LOGGING` config in `local.py` and `production.py`.
- **[Risk] Dev compose diverges from production** → The dev compose runs 1 gunicorn worker with auto-reload off, while production runs 4 workers. OTel behavior (fork safety, BatchSpanProcessor threads) is identical. The scrape config differences (dev uses a static config, production uses Traefik/service discovery) are orthogonal to observability.
