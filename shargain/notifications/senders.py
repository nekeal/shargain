import abc
import logging

import telebot
from django.conf import settings
from telebot.apihelper import ApiTelegramException
from telebot.types import ReplyParameters

from shargain.notifications.models import NotificationConfig

logger = logging.getLogger(__name__)


class BaseNotificationSender(abc.ABC):
    def __init__(self, notification_config: NotificationConfig):
        self._notification_config = notification_config

    @abc.abstractmethod
    def send(self, message: str):
        pass

    @abc.abstractmethod
    def send_with_pin(
        self,
        message: str,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
    ):
        pass


class TelegramNotificationSender(BaseNotificationSender):
    def __init__(self, notification_config: NotificationConfig, bot_token: str = ""):
        """
        :param notification_config: user's notification config
        :param bot_token: Telegram bot token. By default, it's taken from settings
        """
        self._bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        assert self._bot_token, "Telegram bot token is not set"  # noqa: S101
        self._bot: telebot.TeleBot | None = None
        super().__init__(notification_config)

    def _get_bot(self) -> telebot.TeleBot:
        if self._bot is None:
            self._bot = telebot.TeleBot(self._bot_token, parse_mode=None)
        return self._bot

    def send(self, message: str):
        self._get_bot().send_message(self._notification_config.chatid, message)

    def send_with_pin(
        self,
        message: str,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
    ):
        bot = self._get_bot()
        sent_message = bot.send_message(self._notification_config.chatid, message)
        try:
            bot.send_location(
                self._notification_config.chatid,
                latitude=latitude,
                longitude=longitude,
                horizontal_accuracy=horizontal_accuracy,
                reply_parameters=ReplyParameters(message_id=sent_message.message_id),
            )
        except ApiTelegramException as exc:
            logger.warning(
                "Failed to send location pin for chat %s: %s",
                self._notification_config.chatid,
                exc,
            )
