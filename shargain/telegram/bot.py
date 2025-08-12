import logging
import re
from enum import Enum
from typing import Any

from django.conf import settings
from django.core.validators import URLValidator
from django.db import transaction
from django.utils.translation import activate, override
from django.utils.translation import gettext as _
from telebot import BaseMiddleware, TeleBot
from telebot.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telebot.types import (
    Message as TelebotMessage,
)

from shargain.notifications.models import NotificationConfig
from shargain.telegram.application import (
    AddScrapingLinkHandler,
    DeleteScrapingLinkHandler,
    ListScrapingLinksHandler,
    MessageProtocol,
    SetupScrapingTargetHandler,
)

logger = logging.getLogger(__name__)


class SetLanguageMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ["message", "callback_query"]

    def pre_process(self, message: TelebotMessage, data: dict[str, Any]):
        lang = message.from_user and message.from_user.language_code
        if lang in ["pl", "en"]:
            activate(lang)

    def post_process(self, message: TelebotMessage, data: dict[str, Any], exception: Exception | None) -> None:
        pass


class TelegramBot:
    _bot: TeleBot = None

    @classmethod
    def get_bot(cls):
        if not cls._bot:
            cls._bot = TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False, use_class_middlewares=True)
            cls._bot.setup_middleware(SetLanguageMiddleware())
            for lang in ["en", "pl"]:
                with override(lang):
                    cls._bot.set_my_commands(
                        [
                            BotCommand("menu", _("Show menu")),
                        ],
                        language_code=lang,
                    )
            if settings.TELEGRAM_WEBHOOK_URL:
                logger.info("Setting webhook to %s", settings.TELEGRAM_WEBHOOK_URL)
                cls._bot.set_webhook(url=settings.TELEGRAM_WEBHOOK_URL)
            else:
                logger.info("Starting polling")
                cls._bot.polling(none_stop=True)
            return cls._bot
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

    @classmethod
    def get_username(cls) -> str:
        return cls.get_bot().get_me().username  # type: ignore[union-attr]


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
            TelegramBot.get_bot().reply_to(message, _("This token is invalid"))
            return
        if notification_config.chatid:
            logger.info(
                "NotificationConfig is already registered for [chatid=%s]",
                notification_config.chatid,
            )
            TelegramBot.get_bot().reply_to(message, _("Channel for this token is already registered"))
            return
        notification_config.chatid = message.chat.id
        notification_config.save()
        logger.info("Channel registered successfully: %s", notification_config)
        TelegramBot.get_bot().reply_to(message, _("Channel registered successfully"))


@TelegramBot.get_bot().message_handler(commands=["start"])
def start_handler(message: Message) -> None:
    """Handle the /start command with optional parameter.

    Supports deep linking in the format: https://t.me/YourBot?start=TOKEN
    which sends: /start TOKEN
    """
    logger.info("Start command received: %s", message.text)

    command_parts = message.text.split()

    if len(command_parts) > 1:
        # Extract the token after /start
        token = command_parts[1]
        logger.warning("Start command with token: %s", token)

        handler = SetupScrapingTargetHandler()
        result = handler.handle(message.chat.id, token)

        if result.success:
            TelegramBot.get_bot().send_message(
                message.chat.id,
                _(
                    "✅ Configuration successful!\n\n"
                    "The bot is now ready to use. You can start adding links to monitor using the /add command."
                ),
            )
        else:
            TelegramBot.get_bot().reply_to(message, result.message)
            logger.info("Couldn't start configuration: %s, chat_id: %s", result.message, message.chat.id)
    else:
        TelegramBot.get_bot().send_message(
            message.chat.id,
            _(
                "Hello! I'm a Shargain bot. I can send you notifications about new offers. "
                "To start receiving notifications, please register your channel or this conversation using "
                "the following command: /configure <token>"
            ),
        )


@TelegramBot.get_bot().message_handler(commands=["configure"])
@transaction.atomic
def create_target_and_notifications_handler(message):
    logger.info("Creating scraping target and notifications")
    result = SetupScrapingTargetHandler().handle(message.chat.id, message.text.split()[1])
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
    TelegramBot.get_bot().send_message(
        message.chat.id,
        result.message,
        parse_mode="HTML",
    )


def _ask_for_link_to_delete(message: Message):
    bot = TelegramBot.get_bot()
    chat_id = message.chat.id
    urls = ListScrapingLinksHandler().get_urls_by_chat_id(chat_id=chat_id)

    if not urls:
        bot.send_message(chat_id, _("You have no links to delete."))
        return

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i, url_data in enumerate(urls):
        button_text = f"{i + 1}: {url_data.name or url_data.url}"
        markup.add(button_text)

    bot.send_message(
        chat_id,
        ListScrapingLinksHandler().handle(chat_id=chat_id).message,
        parse_mode="HTML",
    )

    bot.send_message(chat_id, text=_("Select a link to delete:"), reply_markup=markup)
    bot.register_next_step_handler(message, handle_delete_selection)


def handle_delete_selection(message: Message):
    bot = TelegramBot.get_bot()
    chat_id = message.chat.id

    try:
        index_str = message.text.split(":")[0]
        index = int(index_str) - 1
    except (ValueError, IndexError):
        bot.send_message(
            chat_id,
            _("Invalid selection. Please use the buttons provided."),
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    result = DeleteScrapingLinkHandler().handle(chat_id=chat_id, index=index)

    bot.send_message(
        chat_id,
        result.message,
        reply_markup=ReplyKeyboardRemove(),
    )


@TelegramBot.get_bot().message_handler(commands=["delete"])
def delete_link_handler(message: Message) -> None:
    logger.info("Deleting link")
    chat_id = message.chat.id

    command_regex = re.compile(r"^/delete (?P<index>\d+)$")
    match = command_regex.match(message.text)

    if match:
        index = int(match.group("index")) - 1
        result = DeleteScrapingLinkHandler().handle(chat_id=chat_id, index=index)
        response = result.message
        TelegramBot.get_bot().send_message(chat_id, response)
    else:
        _ask_for_link_to_delete(message)


class MenuCallback(str, Enum):
    """Callback data for menu actions."""

    ADD_LINK = "CMD_ADD_LINK"
    LIST_LINKS = "CMD_LIST_LINKS"
    DELETE_LINK = "CMD_DELETE_LINK"


@TelegramBot.get_bot().message_handler(commands=["menu"])
def menu_handler(message: Message) -> None:
    """Display the main menu with inline keyboard options."""
    keyboard = [
        [
            InlineKeyboardButton(_("➕ Add Link"), callback_data=MenuCallback.ADD_LINK),
        ],
        [
            InlineKeyboardButton(_("📋 List Links"), callback_data=MenuCallback.LIST_LINKS),
            InlineKeyboardButton(_("🗑️ Delete Link"), callback_data=MenuCallback.DELETE_LINK),
        ],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    TelegramBot.get_bot().send_message(message.chat.id, _("Select an action:"), reply_markup=markup)


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data == MenuCallback.LIST_LINKS)
def callback_list_links(call):
    """Handle listing links from inline keyboard."""
    chat_id = call.message.chat.id
    logger.info("Listing links via inline keyboard [chat_id=%s]", chat_id)
    result = ListScrapingLinksHandler().handle(chat_id=chat_id)
    TelegramBot.get_bot().answer_callback_query(call.id)
    TelegramBot.get_bot().send_message(chat_id, result.message, parse_mode="HTML")


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data == MenuCallback.DELETE_LINK)
def callback_delete_link(call):
    """Prompt user with an interactive menu to delete a link."""
    logger.info("Initiating delete link via inline keyboard [chat_id=%s]", call.message.chat.id)
    TelegramBot.get_bot().answer_callback_query(call.id)
    _ask_for_link_to_delete(call.message)


def get_token_for_webhook_url():
    """
    Used for configuring urlpatterns
    """
    if not settings.TELEGRAM_WEBHOOK_URL:
        return "token"
    else:
        return settings.TELEGRAM_WEBHOOK_URL.rstrip("/").split("/")[-1]
