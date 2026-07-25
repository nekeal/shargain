"""Tests for the notification service."""

import pytest

from shargain.notifications.services.notifications import (
    NewOfferNotificationService,
    NotificationMessageContext,
)
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory


@pytest.mark.django_db
class TestGetMessageForOffer:
    @staticmethod
    def _make_service():
        config = NotificationConfigFactory()
        target = ScrappingTargetFactory(notification_config=config)
        return NewOfferNotificationService([], target, "NOTIFICATION TITLE")

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


@pytest.mark.django_db
class TestGetMessageHeader:
    @staticmethod
    def _make_service(notification_title="TEST TARGET"):
        config = NotificationConfigFactory()
        target = ScrappingTargetFactory(notification_config=config)
        return NewOfferNotificationService([], target, notification_title)

    def test_message_header_uses_provided_title(self):
        service = self._make_service("MY CUSTOM TITLE")
        header = service.get_message_header()

        assert "MY CUSTOM TITLE" in header
        assert header == "MY CUSTOM TITLE\n\n"


@pytest.mark.django_db
class TestExtractedFieldsInMessage:
    @staticmethod
    def _make_service():
        config = NotificationConfigFactory()
        target = ScrappingTargetFactory(notification_config=config)
        return NewOfferNotificationService([], target, "NOTIFICATION TITLE")

    def test_extracted_fields_appended_as_key_value(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(
            offer=offer,
            extracted_fields={"price_per_m2": 42, "rooms": 3},
        )
        service = self._make_service()
        msg = service.get_message_for_offer(context)
        assert "Price Per M2: 42" in msg
        assert "Rooms: 3" in msg

    def test_boolean_fields_rendered_as_yes_no(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(
            offer=offer,
            extracted_fields={"has_balcony": True},
        )
        service = self._make_service()
        msg = service.get_message_for_offer(context)
        assert "Yes" in msg

    def test_no_extracted_fields_does_not_add_section(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(offer=offer)
        service = self._make_service()
        msg = service.get_message_for_offer(context)
        assert "\U0001f3f7\ufe0f" not in msg

    def test_mixed_types_rendered_correctly(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(
            offer=offer,
            extracted_fields={
                "price_per_m2": 42.5,
                "floor": 4,
                "has_elevator": False,
                "notes": "Great location",
            },
        )
        service = self._make_service()
        msg = service.get_message_for_offer(context)
        assert "42.5" in msg
        assert "4" in msg
        assert "No" in msg
        assert "Great location" in msg
