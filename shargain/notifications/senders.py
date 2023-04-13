import abc

import telebot
from django.conf import settings

from shargain.notifications.models import NotificationConfig


class BaseNotificationSender(abc.ABC):
    def __init__(self, notification_config: NotificationConfig):
        self._notification_config = notification_config

    @abc.abstractmethod
    def send(self, message: str):
        pass


class TelegramNotificationSender(BaseNotificationSender):
    def __init__(self, notification_config: NotificationConfig, bot_token: str = ""):
        """
        :param notification_config: user's notification config
        :param bot_token: Telegram bot token. By default, it's taken from settings
        """
        self._bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        assert self._bot_token, "Telegram bot token is not set"
        super().__init__(notification_config)

    def send(self, message: str):
        bot = telebot.TeleBot(self._bot_token, parse_mode=None)
        bot.send_message(self._notification_config.chatid, message)
