from collections.abc import Generator

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.offers.models import ScrappingTarget
from shargain.offers.tests.factories import ScrappingTargetFactory


class InMemorySpanExporter(SpanExporter):
    def __init__(self):
        self.spans = []

    def export(self, spans, timeout_millis=30000):
        self.spans.extend(spans)
        return 0

    def shutdown(self):
        self.spans.clear()

    def get_finished_spans(self):
        spans = list(self.spans)
        self.spans.clear()
        return spans


@pytest.fixture
def otel_test_provider() -> Generator[TracerProvider]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    original = trace.get_tracer_provider()
    trace.set_tracer_provider(provider)
    yield provider
    trace.set_tracer_provider(original)


@pytest.fixture
def user(db) -> CustomUser:
    return UserFactory.create()


@pytest.fixture
def scraping_target(user) -> ScrappingTarget:
    return ScrappingTargetFactory(owner=user)
