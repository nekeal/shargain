import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor, Span
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def _response_hook(span: Span, request, response):
    if not span.is_recording():
        return
    resolver_match = getattr(request, "resolver_match", None)
    view_name = resolver_match.view_name if resolver_match else "unknown"
    span.set_attribute("django.view", view_name)


def post_fork(server, worker):
    if trace.get_tracer_provider().__class__.__name__ != "ProxyTracerProvider":
        return

    os.environ.setdefault("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf")
    os.environ.setdefault("OTEL_TRACES_EXPORTER", "otlp")
    os.environ.setdefault("OTEL_PYTHON_DJANGO_EXCLUDED_URLS", "/metrics,/health.*,/readiness.*,/static/.*")
    os.environ.setdefault("OTEL_BSP_SCHEDULE_DELAY", "5000")

    resource = Resource.create({"service.name": "shargain"})

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    DjangoInstrumentor().instrument(is_sql_commenter_enabled=False, response_hook=_response_hook)
    Psycopg2Instrumentor().instrument()
    RequestsInstrumentor().instrument()
    LoggingInstrumentor().instrument()
