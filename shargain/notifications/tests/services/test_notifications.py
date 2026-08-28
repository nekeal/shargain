"""Tests for the notification service."""

from unittest.mock import patch

import pytest

from shargain.notifications.services.notifications import (
    NewOfferNotificationService,
    NotificationMessageContext,
)
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.field_extraction import ExtractedFieldEntry, RichValue
from shargain.offers.services.location_parsers import Coordinates
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory


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


@pytest.mark.django_db
class TestGetMessageForOfferMapUrl:
    @staticmethod
    def _make_service():
        config = NotificationConfigFactory()
        target = ScrappingTargetFactory(notification_config=config)
        return NewOfferNotificationService([], target, "NOTIFICATION TITLE")

    def test_context_stores_coordinates(self):
        coords = Coordinates(lat=52.22, lon=21.01)
        context = NotificationMessageContext(offer=OfferFactory.build(), coordinates=coords)

        assert context.coordinates == coords

    def test_message_includes_map_url_by_default(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(offer=offer, map_url="https://maps.google.com/?q=52.22,21.01")
        service = self._make_service()
        msg = service.get_message_for_offer(context)

        assert "maps.google.com" in msg

    def test_message_can_omit_map_url_for_pinned_cards(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(
            offer=offer,
            map_url="https://maps.google.com/?q=52.22,21.01",
            location_name="Warsaw, Centrum",
            distances=[("Office", 1.2)],
        )
        service = self._make_service()
        msg = service.get_message_for_offer(context, include_map_url=False)

        assert "maps.google.com" not in msg
        assert "Warsaw, Centrum" in msg
        assert "1.2 km from Office" in msg


@pytest.mark.django_db
class TestRunPinSplitting:
    """run() must send pinned offers as their own card+pin and batch the rest."""

    @pytest.fixture(autouse=True)
    def _patched_sender(self):
        with patch("shargain.notifications.services.notifications.TelegramNotificationSender") as sender_class:
            self.sender_instance = sender_class.return_value
            yield sender_class

    def _make_context(self, *, coordinates=None, map_url=None, is_exact_location=False):
        return NotificationMessageContext(
            offer=OfferFactory.build(),
            map_url=map_url,
            is_exact_location=is_exact_location,
            coordinates=coordinates,
        )

    def _make_service(self, contexts):
        config = NotificationConfigFactory()
        target = ScrappingTargetFactory(notification_config=config)
        return NewOfferNotificationService(contexts, target, "NOTIFICATION TITLE")

    def test_pinned_offer_gets_own_card_and_pin(self):
        service = self._make_service([self._make_context(coordinates=Coordinates(lat=52.22, lon=21.01))])

        service.run()

        self.sender_instance.send_with_pin.assert_called_once()
        self.sender_instance.send.assert_not_called()
        card, lat, lon = self.sender_instance.send_with_pin.call_args.args[:3]
        assert (lat, lon) == (52.22, 21.01)
        assert self.sender_instance.send_with_pin.call_args.kwargs["horizontal_accuracy"] == 1500.0
        assert "maps.google.com" not in card

    def test_exact_location_uses_wide_city_radius(self):
        context = self._make_context(coordinates=Coordinates(lat=52.22, lon=21.01), is_exact_location=True)
        service = self._make_service([context])

        service.run()

        assert self.sender_instance.send_with_pin.call_args.kwargs["horizontal_accuracy"] == 1500.0

    def test_unpinned_offers_stay_batched(self):
        pinned = self._make_context(coordinates=Coordinates(lat=52.22, lon=21.01))
        unpinned = self._make_context(map_url="https://maps.google.com/?q=Krak%C3%B3w")
        service = self._make_service([unpinned, pinned])

        service.run()

        self.sender_instance.send_with_pin.assert_called_once()
        self.sender_instance.send.assert_called_once()
        card = self.sender_instance.send_with_pin.call_args.args[0]
        batch_text = self.sender_instance.send.call_args.args[0]
        assert unpinned.offer.title in batch_text
        assert pinned.offer.title not in batch_text
        assert "maps.google.com" not in card
        assert "maps.google.com" in batch_text

    def test_pin_order_matches_offer_order(self):
        first = self._make_context(coordinates=Coordinates(lat=52.1, lon=21.1))
        second = self._make_context(coordinates=Coordinates(lat=52.2, lon=21.2))
        service = self._make_service([first, second])

        service.run()

        assert self.sender_instance.send_with_pin.call_count == 2
        calls = self.sender_instance.send_with_pin.call_args_list
        assert (calls[0].args[1], calls[0].args[2]) == (52.1, 21.1)
        assert (calls[1].args[1], calls[1].args[2]) == (52.2, 21.2)

    def test_batch_with_no_offers_left_is_not_sent(self):
        context = self._make_context(coordinates=Coordinates(lat=52.22, lon=21.01))
        service = self._make_service([context])

        service.run()

        self.sender_instance.send.assert_not_called()
