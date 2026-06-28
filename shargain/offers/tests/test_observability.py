"""Tests for observability metrics and tracing instrumentation."""

from unittest.mock import patch

import pytest
from opentelemetry import trace

from shargain.offers.models import Offer
from shargain.offers.services.batch_create import OfferBatchCreateService
from shargain.offers.tests.conftest import InMemorySpanExporter
from shargain.offers.tests.factories import ScrappingTargetFactory


class TestBaseSettingsMiddleware:
    def test_prometheus_before_middleware_is_first(self):
        from shargain.settings import base

        first = base.MIDDLEWARE[0]
        assert "PrometheusBeforeMiddleware" in first
        last = base.MIDDLEWARE[-1]
        assert "PrometheusAfterMiddleware" in last

    def test_django_prometheus_in_installed_apps(self):
        from shargain.settings import base

        assert "django_prometheus" in base.INSTALLED_APPS

    def test_test_settings_strips_prometheus_middleware(self):
        from django.conf import settings

        middleware_str = " ".join(settings.MIDDLEWARE)
        assert "Prometheus" not in middleware_str

    def test_test_settings_strips_django_prometheus_app(self):
        from django.conf import settings

        assert "django_prometheus" not in settings.INSTALLED_APPS


class TestBatchCreateTracing:
    @pytest.mark.django_db
    def test_batch_create_creates_otel_spans(self, otel_test_provider):
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        exporter = InMemorySpanExporter()
        otel_test_provider.add_span_processor(SimpleSpanProcessor(exporter))

        tracer = trace.get_tracer("test")
        scraping_target = ScrappingTargetFactory()

        with tracer.start_as_current_span("test-batch"):
            offer_data = {
                "target": scraping_target.id,
                "offers": [
                    {
                        "url": "https://example.com/traced-offer-1",
                        "title": "Traced Offer 1",
                    },
                ],
            }

            with patch("shargain.offers.services.batch_create.NewOfferNotificationService") as mock_notif:
                mock_instance = mock_notif.return_value
                mock_instance.run.return_value = None
                service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})
                service.notification_service_class = mock_notif
                service.run()

        spans = exporter.get_finished_spans()
        span_names = [s.name for s in spans]

        assert any("batch_create" in name.lower() for name in span_names), (
            f"No batch_create span found in: {span_names}"
        )
        assert Offer.objects.filter(url="https://example.com/traced-offer-1").exists()
