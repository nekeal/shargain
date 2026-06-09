"""Tests for the notification service."""

import pytest

from shargain.notifications.services.notifications import (
    NewOfferNotificationService,
    NotificationMessageContext,
)
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory


@pytest.mark.django_db
class TestGetMessageForOfferExtraLines:
    @staticmethod
    def _make_service():
        config = NotificationConfigFactory()
        target = ScrappingTargetFactory(notification_config=config)
        return NewOfferNotificationService([], target)

    def test_extra_lines_rendered_below_shared_header(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(
            offer=offer,
            extra_lines=[
                "📍 https://maps.google.com/?q=52.0,21.0",
                "🏙️ Warsaw, Śródmieście",
                "📏 1.2 km from Home",
            ],
        )
        service = self._make_service()
        msg = service.get_message_for_offer(context)

        assert offer.title in msg
        assert f"za {offer.price}zł" in msg
        assert "📍 https://maps.google.com/?q=52.0,21.0" in msg
        assert "🏙️ Warsaw, Śródmieście" in msg
        assert "📏 1.2 km from Home" in msg

    def test_no_extra_lines_still_renders_header(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(offer=offer)
        service = self._make_service()
        msg = service.get_message_for_offer(context)

        assert offer.title in msg
        assert f"za {offer.price}zł" in msg
        assert offer.url in msg


@pytest.mark.django_db
class TestGetMessageForOffer:
    @staticmethod
    def _make_service():
        config = NotificationConfigFactory()
        target = ScrappingTargetFactory(notification_config=config)
        return NewOfferNotificationService([], target)

    def test_message_includes_distances_when_provided(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(
            offer=offer,
            distances=[
                ("Metro Centrum", 1.2),
                ("Office", 3.5),
            ],
        )
        service = self._make_service()
        msg = service.get_message_for_offer(context)

        assert "1.2 km from Metro Centrum" in msg
        assert "3.5 km from Office" in msg

    def test_message_includes_distance_under_one_km_in_meters(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(
            offer=offer,
            distances=[
                ("Office", 0.85),
            ],
        )
        service = self._make_service()
        msg = service.get_message_for_offer(context)

        assert "850 m from Office" in msg

    def test_message_does_not_include_distances_when_none(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(
            offer=offer,
        )
        service = self._make_service()
        msg = service.get_message_for_offer(context)

        assert "km from" not in msg
        assert "m from" not in msg
