"""Tests for OfferBatchCreateService."""

import pytest

from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.models import Offer
from shargain.offers.services.batch_create import OfferBatchCreateService
from shargain.offers.tests.factories import ScrapingUrlFactory, ScrappingTargetFactory
from shargain.quotas.tests.factories import OfferQuotaFactory


class NotificationServiceSpy:
    """Captures contexts passed to NewOfferNotificationService without sending notifications."""

    def __init__(self, contexts, target):
        self.contexts = contexts
        self.target = target

    def run(self):
        pass


@pytest.mark.django_db
class TestOfferBatchCreateService:
    """Tests for the OfferBatchCreateService class."""

    def test_offer_batch_create_with_filters(self):
        """Test that filtered offers don't trigger notifications."""
        notification_config = NotificationConfigFactory()
        scraping_target = ScrappingTargetFactory(
            notification_config=notification_config,
            enable_notifications=True,
        )
        scraping_url = ScrapingUrlFactory(
            scraping_target=scraping_target,
            filters={
                "ruleGroups": [
                    {"logic": "and", "rules": [{"field": "title", "operator": "contains", "value": "apartment"}]}
                ]
            },
        )
        offer_data = {
            "target": scraping_url.scraping_target.id,
            "offers": [
                {
                    "url": "https://example.com/offer-1-apartment",
                    "title": "Beautiful apartment in city center",
                    "list_url": scraping_url.url,
                },
                {
                    "url": "https://example.com/offer-2-studio",
                    "title": "Cozy studio for rent",
                    "list_url": scraping_url.url,
                },
            ],
        }

        captured = []

        class Spy(NotificationServiceSpy):
            def __init__(self, contexts, target):
                super().__init__(contexts, target)
                captured.append(self)

        service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})
        service.notification_service_class = Spy
        service.run()

        assert len(captured) == 1
        contexts = captured[0].contexts
        assert len(contexts) == 1
        assert contexts[0].offer.title == "Beautiful apartment in city center"

    def test_offer_batch_create_without_filters(self):
        """Test that offers are not filtered if no filters are configured."""
        notification_config = NotificationConfigFactory()
        scraping_target = ScrappingTargetFactory(
            notification_config=notification_config,
            enable_notifications=True,
        )
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, filters=None)
        offer_data = {
            "target": scraping_url.scraping_target.id,
            "offers": [
                {
                    "url": "https://example.com/no-filter-offer-1",
                    "title": "Beautiful apartment in city center",
                    "list_url": scraping_url.url,
                },
                {
                    "url": "https://example.com/no-filter-offer-2",
                    "title": "Cozy studio for rent",
                    "list_url": scraping_url.url,
                },
            ],
        }

        captured = []

        class Spy(NotificationServiceSpy):
            def __init__(self, contexts, target):
                super().__init__(contexts, target)
                captured.append(self)

        service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})
        service.notification_service_class = Spy
        service.run()

        assert len(captured) == 1
        contexts = captured[0].contexts
        assert len(contexts) == 2

    def test_offer_batch_create_returns_empty_when_quota_is_reached(self):
        scraping_target = ScrappingTargetFactory()
        OfferQuotaFactory(
            user=scraping_target.owner,
            target=scraping_target,
            max_offers_per_period=1,
            used_offers_count=1,
        )

        offer_data = {
            "target": scraping_target.id,
            "offers": [
                {
                    "url": "https://example.com/quota-limit-offer",
                    "title": "Will not be created",
                }
            ],
        }
        service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})

        created_urls = service.run()

        assert created_urls == []
        assert Offer.objects.filter(target=scraping_target).count() == 0

    def test_offer_batch_create_records_usage_via_signal_receiver(self):
        scraping_target = ScrappingTargetFactory()
        quota = OfferQuotaFactory(
            user=scraping_target.owner,
            target=scraping_target,
            max_offers_per_period=10,
            used_offers_count=0,
        )
        offer_data = {
            "target": scraping_target.id,
            "offers": [
                {
                    "url": "https://example.com/new-offer-1",
                    "title": "new offer 1",
                },
                {
                    "url": "https://example.com/new-offer-2",
                    "title": "new offer 2",
                },
            ],
        }
        service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})

        service.run()

        quota.refresh_from_db()
        assert quota.used_offers_count == 2

    def test_offer_batch_create_saves_metadata(self):
        scraping_target = ScrappingTargetFactory()
        offer_data = {
            "target": scraping_target.id,
            "offers": [
                {
                    "url": "https://example.com/metadata-offer",
                    "title": "Offer with metadata",
                    "metadata": {"extra": {"foo": "bar"}},
                }
            ],
        }
        service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})

        service.run()

        offer = Offer.objects.get(url="https://example.com/metadata-offer")
        assert offer.metadata == {"extra": {"foo": "bar"}}

    def test_offer_batch_create_with_waypoints(self):
        """Test that distances to waypoints are computed and passed to the notification service."""
        notification_config = NotificationConfigFactory()
        scraping_target = ScrappingTargetFactory(
            notification_config=notification_config,
            enable_notifications=True,
        )
        scraping_url = ScrapingUrlFactory(
            scraping_target=scraping_target,
            show_location_map_in_notifications=True,
            waypoints=[
                {"name": "Metro Centrum", "lat": 52.23, "lon": 21.00},
                {"name": "Office", "lat": 52.19, "lon": 21.04},
            ],
        )
        offer_data = {
            "target": scraping_url.scraping_target.id,
            "offers": [
                {
                    "url": "https://olx.pl/offer-with-coords",
                    "title": "Apartment near metro",
                    "list_url": scraping_url.url,
                    "metadata": {
                        "extra": {
                            "map": {"lat": 52.22, "lon": 21.01, "show_detailed": True},
                            "location": {"cityName": "Warsaw", "districtName": "Centrum"},
                        }
                    },
                },
            ],
        }

        captured = []

        class Spy(NotificationServiceSpy):
            def __init__(self, contexts, target):
                super().__init__(contexts, target)
                captured.append(self)

        service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})
        service.notification_service_class = Spy
        service.run()

        assert len(captured) == 1
        contexts = captured[0].contexts
        assert len(contexts) == 1
        ctx = contexts[0]
        assert ctx.extra_lines is not None
        assert any("Metro Centrum" in line for line in ctx.extra_lines)
        assert any("Office" in line for line in ctx.extra_lines)
        assert any("📍" in line for line in ctx.extra_lines)
        assert any("🏙️ Warsaw" in line for line in ctx.extra_lines)
