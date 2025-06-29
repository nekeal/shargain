import logging
import re
from enum import Enum

from django.conf import settings
from django.core.validators import URLValidator
from django.db import transaction
from django.utils.translation import gettext as _
from telebot import TeleBot
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from telebot.types import (
    Message as TelebotMessage,
)

from shargain.notifications.models import NotificationConfig
from shargain.telegram.add_link_flow import handle_skip_name, prompt_for_name, start_add_link_flow
from shargain.telegram.application import (
    AddScrapingLinkHandler,
    DeleteScrapingLinkHandler,
    ListScrapingLinksHandler,
    MessageProtocol,
    SetupScrapingTargetHandler,
)

from .add_link_flow import AddLinkCallback

logger = logging.getLogger(__name__)


class TelegramBot:
    _bot: TeleBot = None

    @classmethod
    def get_bot(cls):
        if not cls._bot:
            cls._bot = TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False)
            bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)
            if settings.TELEGRAM_WEBHOOK_URL:
                logger.info("Setting webhook to %s", settings.TELEGRAM_WEBHOOK_URL)
                bot.set_webhook(url=settings.TELEGRAM_WEBHOOK_URL)
            else:
                logger.info("Starting polling")
                bot.polling(none_stop=True)
            return bot
        return cls._bot

    @classmethod
    def _configure_bot(cls):
        if settings.TELEGRAM_WEBHOOK_URL:
            cls._bot.set_webhook(url=settings.TELEGRAM_WEBHOOK_URL)

    @classmethod
    def _set_logging_level(cls, logging_level: int):
        TeleBot.logger.setLevel(logging_level)

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
    def text(self) -> str:
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
    result = SetupScrapingTargetHandler(TelebotMessageAdapter(message)).dispatch()
    TelegramBot.get_bot().send_message(message.chat.id, result.message)


@TelegramBot.get_bot().message_handler(commands=["add"])
def add_link_handler(message):
    logger.error("Adding link")
    chat_id = message.chat.id

    command_regex: re.Pattern[str] = re.compile(r"^/add (?P<url>\S+)\s?(?P<name>[\w+\-_\s]+)?$")
    match = command_regex.match(message.text)

    if match and URLValidator.regex.match(match.group("url")):  # type: ignore[union-attr]
        url = match.group("url")
        name = (match.group("name") or "").strip()
        response = AddScrapingLinkHandler().handle(chat_id, url, name).message
    else:
        response = _("Invalid format of message. Please use /add <url> [name] format.")

    TelegramBot.get_bot().send_message(message.chat.id, response)


@TelegramBot.get_bot().message_handler(commands=["list"])
def list_links_handler(message: Message) -> None:
    logger.info("Listing links")
    chat_id = message.chat.id
    result = ListScrapingLinksHandler().handle(chat_id=chat_id)
    TelegramBot.get_bot().send_message(message.chat.id, result.message)


@TelegramBot.get_bot().message_handler(commands=["delete"])
def delete_link_handler(message: Message) -> None:
    logger.error("Deleting link")
    chat_id = message.chat.id

    command_regex = re.compile(r"^/delete (?P<index>\d+)$")
    match = command_regex.match(message.text)

    if match:
        index = int(match.group("index")) - 1  # Index of scraping url to delete (convert to 0-based index)
        response = DeleteScrapingLinkHandler.handle(chat_id, index).message
    else:
        logger.info(
            "Invalid format of message [chat_id=%s] [message=%s]",
            chat_id,
            message.text,
        )
        response = _(
            "Invalid format of message. Please use /delete <number> format."
            " Where number is a number of link from /list command"
        )

    TelegramBot.get_bot().send_message(message.chat.id, response)


class MenuCallback(str, Enum):
    """Callback data for menu actions."""

    ADD_LINK = "CMD_ADD_LINK"
    LIST_LINKS = "CMD_LIST_LINKS"
    DELETE_LINK = "CMD_DELETE_LINK"


@TelegramBot.get_bot().message_handler(commands=["menu"])
def menu_handler(message: Message) -> None:
    """Display main menu with inline keyboard options."""
    markup = InlineKeyboardMarkup(row_width=2)  # Changed to allow 2 buttons per row

    markup.add(
        InlineKeyboardButton(
            text="Add new link",
            callback_data=MenuCallback.ADD_LINK,
        )
    )
    markup.row(
        InlineKeyboardButton(
            text="List all links",
            callback_data=MenuCallback.LIST_LINKS,
        ),
        InlineKeyboardButton(
            text="Delete a link",
            callback_data=MenuCallback.DELETE_LINK,
        ),
    )

    TelegramBot.get_bot().send_message(message.chat.id, "Select an action:", reply_markup=markup)


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data == MenuCallback.LIST_LINKS)
def callback_list_links(call):
    """Handle listing links from inline keyboard."""
    chat_id = call.message.chat.id
    logger.info("Listing links via inline keyboard [chat_id=%s]", chat_id)
    result = ListScrapingLinksHandler().handle(chat_id=chat_id)
    TelegramBot.get_bot().answer_callback_query(call.id)
    TelegramBot.get_bot().send_message(chat_id, result.message)


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data == MenuCallback.ADD_LINK)
def callback_add_link(call: CallbackQuery) -> None:
    """Start the add link flow."""
    start_add_link_flow(TelegramBot.get_bot(), call)


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data == MenuCallback.DELETE_LINK)
def callback_delete_link(call):
    """Prompt user how to delete a link when selected from menu."""
    chat_id = call.message.chat.id
    logger.info("Prompting delete link via inline keyboard [chat_id=%s]", chat_id)
    TelegramBot.get_bot().answer_callback_query(call.id)
    TelegramBot.get_bot().send_message(
        chat_id,
        _("To delete a link first list them with /list and then send: /delete <number>"),
    )


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data.startswith(AddLinkCallback.PROMPT_NAME_YES))
def handle_prompt_name_yes(call: CallbackQuery) -> None:
    """Handle 'Yes' button click for providing a name."""
    try:
        prompt_for_name(TelegramBot.get_bot(), call)
    finally:
        TelegramBot.get_bot().answer_callback_query(call.id)


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data.startswith(AddLinkCallback.PROMPT_NAME_NO))
def handle_prompt_name_no(call: CallbackQuery) -> None:
    """Handle 'No' button click for skipping name."""
    try:
        handle_skip_name(TelegramBot.get_bot(), call)
    finally:
        TelegramBot.get_bot().answer_callback_query(call.id)


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data.startswith(AddLinkCallback.SKIP_NAME))
def handle_skip_name_callback(call: CallbackQuery) -> None:
    """Handle skip name button click from the add link flow."""
    try:
        handle_skip_name(TelegramBot.get_bot(), call)
    finally:
        TelegramBot.get_bot().answer_callback_query(call.id)


def get_token_for_webhook_url():
    """
    Used for configuring urlpatterns
    """
    if not settings.TELEGRAM_WEBHOOK_URL:
        return "token"
    else:
        return settings.TELEGRAM_WEBHOOK_URL.rstrip("/").split("/")[-1]
