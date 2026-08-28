from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from shargain.notifications.models import NotificationChannelChoices
from shargain.notifications.senders import TelegramNotificationSender
from shargain.offers.field_extraction import ExtractedFieldEntry, RichValue
from shargain.offers.models import Offer, ScrappingTarget

if TYPE_CHECKING:
    from shargain.offers.services.location_parsers import Coordinates


@dataclass
class NotificationMessageContext:
    offer: Offer
    map_url: str | None = None
    location_name: str | None = None
    is_exact_location: bool = False
    distances: list[tuple[str, float]] = field(default_factory=list)  # (waypoint_name, distance_km)
    extracted_fields: list[ExtractedFieldEntry] = field(default_factory=list)
    coordinates: Coordinates | None = None

    def get_distances(self) -> str:
        result = ""
        for name, km in self.distances:
            if km < 1:
                result += f"\n📏 {int(km * 1000)} m from {name}"
            else:
                result += f"\n📏 {km:.1f} km from {name}"
        return result

    def get_extracted_fields_block(self) -> str:
        if not self.extracted_fields:
            return ""
        lines = []
        for entry in self.extracted_fields:
            if entry.value is None:
                continue
            if isinstance(entry.value, RichValue):
                if entry.value.display is not None:
                    display = entry.value.display
                else:
                    display = "Yes" if entry.value.get_value() else "No"
            elif isinstance(entry.value, bool):
                display = "Yes" if entry.value else "No"
            else:
                display = str(entry.value)
            lines.append(f"\n🏷️ {entry.name.replace('_', ' ').title()}: {display}")
        return "".join(lines)


class NewOfferNotificationService:
    def __init__(
        self,
        message_contexts: list[NotificationMessageContext],
        scrapping_target: ScrappingTarget,
        notification_title: str,
    ):
        assert scrapping_target.notification_config_id, "Scrapping target has no notification_config"  # noqa: S101
        self.message_contexts = message_contexts
        self._scrapping_target = scrapping_target
        self.notification_title = notification_title

    def run(self):
        header = self.get_message_header()
        message = header
        for context in self.message_contexts:
            if context.coordinates:
                self._send_single_with_pin(context)
                continue
            offer_message = self.get_message_for_offer(context)
            if len(message + offer_message) > self.get_maximum_message_length(
                self._scrapping_target.notification_config.channel  # type: ignore
            ):
                if len(message) > len(header):
                    self._send(message)
                message = header + offer_message
            else:
                message += offer_message
        if len(message) > len(header):
            self._send(message)

    def _send_single_with_pin(self, context: NotificationMessageContext):
        notification_sender = self._get_notification_sender_class()(self._scrapping_target.notification_config)
        coordinates = context.coordinates
        assert coordinates is not None  # noqa: S101
        card = self.get_message_for_offer(context, include_map_url=False)
        notification_sender.send_with_pin(
            card,
            coordinates.lat,
            coordinates.lon,
            horizontal_accuracy=1500.0,
        )

    def _send(self, message):
        notification_sender = self._get_notification_sender_class()(self._scrapping_target.notification_config)
        notification_sender.send(message)

    def _get_notification_sender_class(self):
        return self.get_notification_sender_class(
            self._scrapping_target.notification_config.channel  # type: ignore
        )

    @staticmethod
    def get_maximum_message_length(notification_channel):
        return {NotificationChannelChoices.TELEGRAM: 4096}[notification_channel]

    @staticmethod
    def get_notification_sender_class(notification_channel):
        return {NotificationChannelChoices.TELEGRAM: TelegramNotificationSender}[notification_channel]

    def get_message_for_offer(self, context: NotificationMessageContext, *, include_map_url: bool = True) -> str:
        base_msg = (
            f"{context.offer.title} ({context.offer.published_at and context.offer.published_at.time()})\n"
            f"za {context.offer.price}zł\n{context.offer.url}"
        )

        if context.map_url and include_map_url:
            icon = "📍" if context.is_exact_location else "🗺️"
            base_msg += f"\n{icon} {context.map_url}"
        if context.location_name:
            base_msg += f"\n🏙️ {context.location_name}"

        base_msg += context.get_distances()
        base_msg += context.get_extracted_fields_block()

        return base_msg + "\n\n"

    def get_message_header(self):
        return f"{self.notification_title.upper()}\n\n"
