"""Tests for OfferBatchCreateService."""

from unittest.mock import patch

import pytest

from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.models import Offer
from shargain.offers.services.batch_create import OfferBatchCreateService
from shargain.offers.tests.factories import ScrapingUrlFactory, ScrappingTargetFactory
from shargain.quotas.tests.factories import OfferQuotaFactory


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
        # Don't create offers beforehand - let the service create them as "new"
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

        with patch(
            "shargain.offers.services.batch_create.NewOfferNotificationService"
        ) as mock_notification_service_class:
            # Mock the instance and its run method
            mock_instance = mock_notification_service_class.return_value
            mock_instance.run.return_value = None

            # Create service and inject mock
            service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})
            service.notification_service_class = mock_notification_service_class
            service.run()

            # Verify the notification service was instantiated with filtered offers
            mock_notification_service_class.assert_called_once()
            filtered_offers = mock_notification_service_class.call_args[0][0]
            assert len(filtered_offers) == 1
            assert filtered_offers[0].title == "Beautiful apartment in city center"

            # Verify run() was called on the instance
            mock_instance.run.assert_called_once()

    def test_offer_batch_create_without_filters(self):
        """Test that offers are not filtered if no filters are configured."""
        notification_config = NotificationConfigFactory()
        scraping_target = ScrappingTargetFactory(
            notification_config=notification_config,
            enable_notifications=True,
        )
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, filters=None)
        # Don't create offers beforehand - let the service create them as "new"
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

        with patch(
            "shargain.offers.services.batch_create.NewOfferNotificationService"
        ) as mock_notification_service_class:
            # Mock the instance and its run method
            mock_instance = mock_notification_service_class.return_value
            mock_instance.run.return_value = None

            # Create service and inject mock
            service = OfferBatchCreateService(serializer_kwargs={"data": offer_data})
            service.notification_service_class = mock_notification_service_class
            service.run()

            # Verify the notification service was instantiated with all offers (no filtering)
            mock_notification_service_class.assert_called_once()
            filtered_offers = mock_notification_service_class.call_args[0][0]
            assert len(filtered_offers) == 2

            # Verify run() was called on the instance
            mock_instance.run.assert_called_once()

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
