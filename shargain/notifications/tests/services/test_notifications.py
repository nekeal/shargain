"""Tests for the notification service."""

import pytest

from shargain.notifications.services.notifications import (
    NewOfferNotificationService,
    NotificationMessageContext,
)
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.field_extraction import ExtractedFieldEntry, RichValue
from shargain.offers.tests.factories import ScrappingTargetFactory


@pytest.mark.django_db
class TestGetMessageForOffer:
    def test_message_includes_distances_when_provided(self, notification_service, offer):
        context = NotificationMessageContext(
            offer=offer,
            distances=[
                ("Metro Centrum", 1.2),
                ("Office", 3.5),
            ],
        )
        msg = notification_service.get_message_for_offer(context)

        assert "1.2 km from Metro Centrum" in msg
        assert "3.5 km from Office" in msg

    def test_message_includes_distance_under_one_km_in_meters(self, notification_service, offer):
        context = NotificationMessageContext(
            offer=offer,
            distances=[
                ("Office", 0.85),
            ],
        )
        msg = notification_service.get_message_for_offer(context)

        assert "850 m from Office" in msg

    def test_message_does_not_include_distances_when_none(self, notification_service, offer):
        context = NotificationMessageContext(
            offer=offer,
        )
        msg = notification_service.get_message_for_offer(context)

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
    def _make_context(fields: list[ExtractedFieldEntry] | None = None, offer=None):
        return NotificationMessageContext(
            offer=offer,
            extracted_fields=fields or [],
        )

    @pytest.mark.parametrize(
        ("fields", "assertions"),
        [
            (
                [ExtractedFieldEntry(name="price_per_m2", value=42), ExtractedFieldEntry(name="rooms", value=3)],
                ["Price Per M2: 42", "Rooms: 3"],
            ),
            ([ExtractedFieldEntry(name="has_balcony", value=True)], ["Yes"]),
            ([ExtractedFieldEntry(name="has_elevator", value=False)], ["No"]),
            (
                [
                    ExtractedFieldEntry(name="price_per_m2", value=42.5),
                    ExtractedFieldEntry(name="floor", value=4),
                    ExtractedFieldEntry(name="has_elevator", value=False),
                    ExtractedFieldEntry(name="notes", value="Great location"),
                ],
                ["42.5", "4", "No", "Great location"],
            ),
            (
                [ExtractedFieldEntry(name="parking", value=RichValue(True, "przynależne na ulicy, w garażu"))],
                ["przynależne na ulicy, w garażu"],
            ),
            ([ExtractedFieldEntry(name="parking", value=RichValue(True))], ["Yes"]),
            ([ExtractedFieldEntry(name="parking", value=RichValue(False))], ["No"]),
        ],
    )
    def test_extracted_fields_rendered(self, fields, assertions, notification_service, offer):
        context = self._make_context(fields, offer=offer)
        msg = notification_service.get_message_for_offer(context)
        for expected in assertions:
            assert expected in msg

    def test_no_extracted_fields_does_not_add_section(self, notification_service, offer):
        context = self._make_context(offer=offer)
        msg = notification_service.get_message_for_offer(context)
        assert "\U0001f3f7\ufe0f" not in msg
