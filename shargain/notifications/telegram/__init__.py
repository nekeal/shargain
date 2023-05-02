import logging

from django.conf import settings
from django.db import transaction
from telebot import TeleBot
from telebot.types import Message

from shargain.notifications.models import NotificationConfig

logger = logging.getLogger(__name__)


class TelegramBot:
    _bot: TeleBot = None

    @classmethod
    def get_bot(cls):
        if not cls._bot:
            cls._bot = TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False)
            cls._configure_bot()
        return cls._bot

    @classmethod
    def _configure_bot(cls):
        if settings.TELEGRAM_WEBHOOK_URL:
            cls._bot.set_webhook(url=settings.TELEGRAM_WEBHOOK_URL)


@TelegramBot.get_bot().message_handler(commands=["register"])
def register_channel_handler(message: Message) -> None:
    """
    The purpose of this method is to configure NotificationConfig using
    the unique token. Basing on it the chat_id is extracted and
    put into NotificationConfig.
    :param message: Message with register command
    :return: None
    """
    logger.info("Registering channel")
    token = message.text.split()[1]
    with transaction.atomic():
        if not (
            notification_config := NotificationConfig.objects.select_for_update()
            .filter(register_token=token)
            .first()
        ):
            logger.info(
                "Channel not found for token [username=%s] [token=%s] [chatid=%s]",
                message.from_user.username,
                token,
                message.chat.id,
            )
            TelegramBot.get_bot().reply_to(message, "This token is invalid")
            return
        if notification_config.chatid:
            logger.info(
                "NotificationConfig is already registered for [chatid=%s]",
                notification_config.chatid,
            )
            TelegramBot.get_bot().reply_to(
                message, "Channel for this token is already registered"
            )
            return
        notification_config.chatid = message.chat.id
        notification_config.save()
        logger.info(f"Channel registered successfully: {notification_config}")
        TelegramBot.get_bot().reply_to(message, "Channel registered successfully")
