from dataclasses import dataclass, field

from shargain.notifications.models import NotificationChannelChoices
from shargain.notifications.senders import TelegramNotificationSender
from shargain.offers.models import Offer, ScrappingTarget


@dataclass
class NotificationMessageContext:
    offer: Offer
    map_url: str | None = None
    location_name: str | None = None
    is_exact_location: bool = False
    distances: list[tuple[str, float]] = field(default_factory=list)  # (waypoint_name, distance_km)
    extra_lines: list[str] = field(default_factory=list)

    def get_distances(self) -> str:
        result = ""
        for name, km in self.distances:
            if km < 1:
                result += f"\n📏 {int(km * 1000)} m from {name}"
            else:
                result += f"\n📏 {km:.1f} km from {name}"
        return result


class NewOfferNotificationService:
    def __init__(self, message_contexts: list[NotificationMessageContext], scrapping_target: ScrappingTarget):
        assert scrapping_target.notification_config_id, "Scrapping target has no notification_config"  # noqa: S101
        self.message_contexts = message_contexts
        self._scrapping_target = scrapping_target

    def run(self):
        message = self.get_message_header()
        for context in self.message_contexts:
            offer_message = self.get_message_for_offer(context)
            if len(message + offer_message) > self.get_maximum_message_length(
                self._scrapping_target.notification_config.channel  # type: ignore
            ):
                self._send(message)
                message = self.get_message_header() + offer_message
            else:
                message += offer_message
        self._send(message)

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

    def get_message_for_offer(self, context: NotificationMessageContext) -> str:
        base_msg = (
            f"{context.offer.title} ({context.offer.published_at and context.offer.published_at.time()})\n"
            f"za {context.offer.price}zł\n{context.offer.url}"
        )

        if context.extra_lines:
            for line in context.extra_lines:
                base_msg += f"\n{line}"
        else:
            if context.map_url:
                icon = "📍" if context.is_exact_location else "🗺️"
                base_msg += f"\n{icon} {context.map_url}"
            if context.location_name:
                base_msg += f"\n🏙️ {context.location_name}"
            base_msg += context.get_distances()

        return base_msg + "\n\n"

    def get_message_header(self):
        return f"{self._scrapping_target.name.upper()}\n\n"
