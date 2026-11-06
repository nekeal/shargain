"""Tests for the notification service."""

from unittest.mock import patch

import pytest

from shargain.jobs.models import Job
from shargain.notifications.services.notifications import (
    NewOfferNotificationService,
    NotificationMessageContext,
)
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.field_extraction import ExtractedFieldEntry, RichValue
from shargain.offers.geo import Coordinates
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

    def test_message_includes_map_url_by_default(self):
        offer = OfferFactory.build()
        context = NotificationMessageContext(offer=offer, map_url="https://maps.google.com/?q=52.22,21.01")
        service = self._make_service()
        msg = service.get_message_for_offer(context)

        assert "maps.google.com" in msg


@pytest.mark.django_db
class TestRunPinSplitting:
    """run() must enqueue pinned offers as their own card+pin job and batch the rest."""

    def _make_context(self, *, coordinates=None, map_url=None, send_map=True):
        return NotificationMessageContext(
            offer=OfferFactory.build(),
            map_url=map_url,
            coordinates=coordinates,
            send_map=send_map,
        )

    def _make_service(self, contexts):
        config = NotificationConfigFactory()
        target = ScrappingTargetFactory(notification_config=config)
        return NewOfferNotificationService(contexts, target, "NOTIFICATION TITLE"), config

    def test_pinned_offer_gets_own_card_and_pin(self):
        service, config = self._make_service(
            [
                self._make_context(
                    coordinates=Coordinates(lat=52.22, lon=21.01), map_url="https://maps.google.com/?q=52.22,21.01"
                )
            ]
        )

        service.run()

        jobs = list(Job.objects.filter(payload__config_id=config.id))
        assert len(jobs) == 1
        job = jobs[0]
        assert job.payload["kind"] == "location"
        assert (job.payload["lat"], job.payload["lon"]) == (52.22, 21.01)
        assert job.payload["horizontal_accuracy"] == 1500.0
        assert "maps.google.com" in job.payload["message"]

    def test_unpinned_offers_stay_batched(self):
        pinned = self._make_context(
            coordinates=Coordinates(lat=52.22, lon=21.01),
            map_url="https://maps.google.com/?q=52.22,21.01",
        )
        unpinned = self._make_context(map_url="https://maps.google.com/?q=Krak%C3%B3w")
        service, config = self._make_service([unpinned, pinned])

        service.run()

        jobs = list(Job.objects.filter(payload__config_id=config.id))
        assert len(jobs) == 2
        kinds = {j.payload["kind"] for j in jobs}
        assert "location" in kinds
        assert "text" in kinds
        text_job = next(j for j in jobs if j.payload["kind"] == "text")
        assert unpinned.offer.title in text_job.payload["message"]
        assert pinned.offer.title not in text_job.payload["message"]

    def test_pin_order_matches_offer_order(self):
        first = self._make_context(coordinates=Coordinates(lat=52.1, lon=21.1))
        second = self._make_context(coordinates=Coordinates(lat=52.2, lon=21.2))
        service, config = self._make_service([first, second])

        service.run()

        jobs = list(Job.objects.filter(payload__config_id=config.id).order_by("created_at"))
        assert len(jobs) == 2
        assert all(j.payload["kind"] == "location" for j in jobs)
        assert (jobs[0].payload["lat"], jobs[0].payload["lon"]) == (52.1, 21.1)
        assert (jobs[1].payload["lat"], jobs[1].payload["lon"]) == (52.2, 21.2)

    def test_batch_with_no_offers_left_is_not_sent(self):
        context = self._make_context(coordinates=Coordinates(lat=52.22, lon=21.01))
        service, config = self._make_service([context])

        service.run()

        jobs = list(Job.objects.filter(payload__config_id=config.id))
        assert len(jobs) == 1
        assert jobs[0].payload["kind"] == "location"

    def test_send_map_disabled_batches_offers_with_coordinates(self):
        first = NotificationMessageContext(
            offer=OfferFactory.build(),
            coordinates=Coordinates(lat=52.1, lon=21.1),
            map_url="https://maps.google.com/?q=52.1,21.1",
            distances=[("Metro Centrum", 1.2)],
            send_map=False,
        )
        second = NotificationMessageContext(
            offer=OfferFactory.build(),
            coordinates=Coordinates(lat=52.2, lon=21.2),
            map_url="https://maps.google.com/?q=52.2,21.2",
            send_map=False,
        )
        service, config = self._make_service([first, second])

        service.run()

        jobs = list(Job.objects.filter(payload__config_id=config.id))
        assert len(jobs) == 1
        job = jobs[0]
        assert job.payload["kind"] == "text"
        message = job.payload["message"]
        assert first.offer.title in message
        assert second.offer.title in message
        assert "maps.google.com" in message
        assert "1.2 km from Metro Centrum" in message
