from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def post_fork(server, worker):
    if trace.get_tracer_provider().__class__.__name__ != "ProxyTracerProvider":
        return

    resource = Resource.create({"service.name": "shargain"})

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    DjangoInstrumentor().instrument(is_sql_commenter_enabled=False)
    Psycopg2Instrumentor().instrument()
    RequestsInstrumentor().instrument()
    LoggingInstrumentor().instrument()
