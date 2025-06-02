import logging

import telebot
from django.conf import settings
from django.db import transaction
from telebot import TeleBot
from telebot.types import Message
from telebot.types import Message as TelebotMessage

from shargain.notifications.models import NotificationConfig
from shargain.notifications.services.telegram import (
    AddScrapingLinkHandler,
    DeleteScrapingLinkHandler,
    ListScrapingLinksHandler,
    MessageProtocol,
    SetupScrapingTargetHandler,
)

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

    @classmethod
    def _set_logging_level(cls, logging_level: int):
        telebot.logger.setLevel(logging_level)

    @classmethod
    def run(cls, verbose: bool = False):
        if verbose:
            cls._set_logging_level(logging.DEBUG)
        cls.get_bot().polling()


class TelebotMessageAdapter(MessageProtocol):
    """Adapts telebot's Message to our MessageProtocol."""

    def __init__(self, message: TelebotMessage):
        self._message = message

    @property
    def text(self) -> str | None:
        return self._message.text

    @property
    def chat_id(self) -> int:
        return self._message.chat.id

    @property
    def from_user(self) -> int:
        return self._message.from_user


@TelegramBot.get_bot().message_handler(commands=["register"], regexp=r"^/register \w{32}$")
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
            notification_config := NotificationConfig.objects.select_for_update().filter(register_token=token).first()
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
            TelegramBot.get_bot().reply_to(message, "Channel for this token is already registered")
            return
        notification_config.chatid = message.chat.id
        notification_config.save()
        logger.info("Channel registered successfully: %s", notification_config)
        TelegramBot.get_bot().reply_to(message, "Channel registered successfully")


@TelegramBot.get_bot().message_handler(commands=["start"])
def start_handler(message: Message) -> None:
    logger.info("Starting bot")
    TelegramBot.get_bot().send_message(
        message.chat.id,
        "Hello! I'm a Shargain bot. I can send you notifications about new offers. "
        "To start receiving notifications, please register your channel or this conversation using "
        "the following command: /configure <token>",
    )


@TelegramBot.get_bot().message_handler(commands=["configure"])
@transaction.atomic
def create_target_and_notifications_handler(message):
    logger.info("Creating scraping target and notifications")
    response = SetupScrapingTargetHandler(TelebotMessageAdapter(message)).dispatch()
    TelegramBot.get_bot().send_message(message.chat.id, response)


@TelegramBot.get_bot().message_handler(commands=["add"])
def add_link_handler(message):
    logger.info("Adding link")
    response = AddScrapingLinkHandler(TelebotMessageAdapter(message)).dispatch()
    TelegramBot.get_bot().send_message(message.chat.id, response)


@TelegramBot.get_bot().message_handler(commands=["list"])
def list_links_handler(message):
    logger.info("Listing links")
    response = ListScrapingLinksHandler(TelebotMessageAdapter(message)).dispatch()
    TelegramBot.get_bot().send_message(message.chat.id, response)


@TelegramBot.get_bot().message_handler(commands=["delete"])
def delete_link_handler(message):
    logger.info("Deleting link")
    response = DeleteScrapingLinkHandler(TelebotMessageAdapter(message)).dispatch()
    TelegramBot.get_bot().send_message(message.chat.id, response)
