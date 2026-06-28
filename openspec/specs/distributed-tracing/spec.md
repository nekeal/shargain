# Distributed Tracing

## Purpose

Enable observability of request flows across service boundaries by exporting OpenTelemetry spans to Jaeger. This allows developers to trace requests end-to-end, including database queries, outbound HTTP calls, and business-logic operations.

## Requirements

### Requirement: Traces are exported to Jaeger via OTLP HTTP
The system SHALL export OpenTelemetry spans to a Jaeger endpoint via OTLP HTTP/protobuf. The exporter endpoint SHALL be configurable via the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable, defaulting to `http://jaeger:4318/v1/traces`. The Jaeger service SHALL use the `jaegertracing/jaeger:2.x` image.

#### Scenario: Traces appear in Jaeger after a request
- **WHEN** a Django view processes an HTTP request
- **THEN** a trace SHALL appear in Jaeger for service `shargain-django` containing spans for the request

### Requirement: Django requests produce traces
Every HTTP request to a Django view SHALL produce a trace with spans for the request lifecycle, including database queries and outbound HTTP calls.

#### Scenario: Trace is created for each request
- **WHEN** a request is made to any Django view
- **THEN** a trace SHALL be created containing spans for the request, its database queries, and its downstream HTTP calls

### Requirement: Traces are visible per-fork
Each server worker SHALL produce traces independently without leaking state between workers.

#### Scenario: Worker restart does not break tracing
- **WHEN** a worker process restarts
- **THEN** new traces SHALL still be produced from the new worker

### Requirement: Health-check and metrics traffic are excluded from tracing
Tracing SHALL exclude Prometheus scraping and health-check traffic to avoid noise.

### Requirement: Log records are enriched with trace context
Every Python log record emitted during an active trace SHALL contain the trace and span IDs for correlation.

### Requirement: Jaeger service is available for trace collection
The development Docker Compose file SHALL include a `jaeger` service using image `jaegertracing/jaeger:2.19.0` with OTLP HTTP receiver enabled on port 4318.

#### Scenario: Jaeger container starts successfully
- **WHEN** `docker compose -f compose.dev.yml up -d` is run
- **THEN** the Jaeger container SHALL start and listen on port 4318 for OTLP HTTP traces

### Requirement: Business-logic spans are created manually in key services
`offers.services.batch_create` SHALL contain explicit OpenTelemetry spans to capture business-logic timing (overall batch processing, per-offer creation).

#### Scenario: Batch create appears as a named span in the trace
- **WHEN** `offers.services.batch_create` is invoked
- **THEN** a named span for the batch processing SHALL appear in the trace, wrapping the DB query and HTTP call spans within it
