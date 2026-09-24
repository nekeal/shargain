import logging
import re
from enum import StrEnum
from typing import Any

import telebot
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
    MessageReactionUpdated,
)
from telebot.types import (
    Message as TelebotMessage,
)

from shargain.notifications.models import NotificationConfig
from shargain.offers.likes import AnonymousLiker, like_offers, unlike_offers
from shargain.offers.models import Offer
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


class MenuCallback(StrEnum):
    """Callback data for menu actions."""

    ADD_LINK = "CMD_ADD_LINK"
    LIST_LINKS = "CMD_LIST_LINKS"
    DELETE_LINK = "CMD_DELETE_LINK"
    DELETE_ITEM = "CMD_DEL_ITEM"


class TelegramHandlers:
    def __init__(self, bot: TeleBot):
        self.bot = bot

    def register_channel_handler(self, message: Message) -> None:
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
                self.bot.reply_to(message, _("This token is invalid"))
                return
            if notification_config.chatid:
                logger.info(
                    "NotificationConfig is already registered for [chatid=%s]",
                    notification_config.chatid,
                )
                self.bot.reply_to(message, _("Channel for this token is already registered"))
                return
            notification_config.chatid = message.chat.id
            notification_config.save()
            logger.info("Channel registered successfully: %s", notification_config)
            self.bot.reply_to(message, _("Channel registered successfully"))

    def start_handler(self, message: Message) -> None:
        logger.info("Start command received: %s", message.text)

        args = telebot.util.extract_arguments(message.text)
        if args:
            token = args.strip()
            logger.warning("Start command with token: %s", token)

            handler = SetupScrapingTargetHandler()
            result = handler.handle(str(message.chat.id), token)

            if result.success:
                self.bot.send_message(
                    message.chat.id,
                    _(
                        "✅ Configuration successful!\n\n"
                        "The bot is now ready to use. You can start adding links to monitor using the /add command."
                    ),
                )
            else:
                self.bot.reply_to(message, result.message)
                logger.info("Couldn't start configuration: %s, chat_id: %s", result.message, message.chat.id)
        else:
            self.bot.send_message(
                message.chat.id,
                _(
                    "Hello! I'm a Shargain bot. I can send you notifications about new offers. "
                    "To start receiving notifications, please register your channel or this conversation using "
                    "the following command: /configure <token>"
                ),
            )

    def create_target_and_notifications_handler(self, message: Message):
        logger.info("Creating scraping target and notifications")
        args = telebot.util.extract_arguments(message.text)
        if args:
            token = args.strip()
            result = SetupScrapingTargetHandler().handle(str(message.chat.id), token)
            self.bot.send_message(message.chat.id, result.message)
        else:
            self.bot.send_message(message.chat.id, _("Please provide a token: /configure <token>"))

    def add_link_handler(self, message: Message):
        logger.info("Adding link")
        chat_id = message.chat.id

        args = telebot.util.extract_arguments(message.text)
        if not args:
            self.bot.send_message(chat_id, _("Invalid format of message. Please use /add <url> [name] format."))
            return

        parts = args.split(maxsplit=1)
        url = parts[0]
        name = parts[1].strip() if len(parts) > 1 else ""

        if URLValidator.regex.match(url):  # type: ignore[union-attr]
            response = AddScrapingLinkHandler().handle(chat_id, url, name).message
        else:
            response = _("Invalid format of message. Please use /add <url> [name] format.")

        self.bot.send_message(chat_id, response)

    def list_links_handler(self, message: Message) -> None:
        logger.info("Listing links")
        chat_id = message.chat.id
        result = ListScrapingLinksHandler().handle(chat_id=chat_id)
        self.bot.send_message(
            chat_id,
            result.message,
            parse_mode="HTML",
        )

    def _ask_for_link_to_delete(self, chat_id: int):
        urls = ListScrapingLinksHandler().get_urls_by_chat_id(chat_id=chat_id)
        if not urls:
            self.bot.send_message(chat_id, _("You have no links to delete."))
            return

        markup = InlineKeyboardMarkup()
        for i, url_data in enumerate(urls):
            button_text = f"{i + 1}: {url_data.name or url_data.url}"
            markup.add(InlineKeyboardButton(button_text, callback_data=f"{MenuCallback.DELETE_ITEM}:{i}"))

        self.bot.send_message(
            chat_id,
            ListScrapingLinksHandler().handle(chat_id=chat_id).message,
            parse_mode="HTML",
        )
        self.bot.send_message(chat_id, text=_("Select a link to delete:"), reply_markup=markup)

    def delete_link_handler(self, message: Message) -> None:
        logger.info("Deleting link")
        chat_id = message.chat.id
        args = telebot.util.extract_arguments(message.text)

        if args and args.isdigit():
            index = int(args) - 1
            result = DeleteScrapingLinkHandler().handle(chat_id=chat_id, index=index)
            self.bot.send_message(chat_id, result.message)
        else:
            self._ask_for_link_to_delete(chat_id)

    def callback_delete_item(self, call):
        chat_id = call.message.chat.id
        try:
            index = int(call.data.split(":")[1])
        except (ValueError, IndexError):
            self.bot.answer_callback_query(call.id, _("Invalid selection."))
            return

        result = DeleteScrapingLinkHandler().handle(chat_id=chat_id, index=index)
        self.bot.answer_callback_query(call.id, _("Link deleted"))
        self.bot.send_message(chat_id, result.message)
        self.bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)

    def menu_handler(self, message: Message) -> None:
        keyboard = [
            [InlineKeyboardButton(_("➕ Add Link"), callback_data=MenuCallback.ADD_LINK)],
            [
                InlineKeyboardButton(_("📋 List Links"), callback_data=MenuCallback.LIST_LINKS),
                InlineKeyboardButton(_("🗑️ Delete Link"), callback_data=MenuCallback.DELETE_LINK),
            ],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        self.bot.send_message(message.chat.id, _("Select an action:"), reply_markup=markup)

    def callback_list_links(self, call):
        chat_id = call.message.chat.id
        logger.info("Listing links via inline keyboard [chat_id=%s]", chat_id)
        result = ListScrapingLinksHandler().handle(chat_id=chat_id)
        self.bot.answer_callback_query(call.id)
        self.bot.send_message(chat_id, result.message, parse_mode="HTML")

    def callback_delete_link(self, call):
        logger.info("Initiating delete link via inline keyboard [chat_id=%s]", call.message.chat.id)
        self.bot.answer_callback_query(call.id)
        self._ask_for_link_to_delete(call.message.chat.id)

    def setup(self):
        self.bot.register_message_handler(
            self.register_channel_handler, commands=["register"], regexp=r"^/register \w{32}$"
        )
        self.bot.register_message_handler(self.start_handler, commands=["start"])
        self.bot.register_message_handler(self.create_target_and_notifications_handler, commands=["configure"])
        self.bot.register_message_handler(self.add_link_handler, commands=["add"])
        self.bot.register_message_handler(self.list_links_handler, commands=["list"])
        self.bot.register_message_handler(self.delete_link_handler, commands=["delete"])
        self.bot.register_message_handler(self.menu_handler, commands=["menu"])

        self.bot.register_callback_query_handler(
            self.callback_delete_item, func=lambda call: call.data.startswith(MenuCallback.DELETE_ITEM)
        )
        self.bot.register_callback_query_handler(
            self.callback_list_links, func=lambda call: call.data == MenuCallback.LIST_LINKS
        )
        self.bot.register_callback_query_handler(
            self.callback_delete_link, func=lambda call: call.data == MenuCallback.DELETE_LINK
        )


class TelegramBot:
    _bot: TeleBot = None

    @classmethod
    def get_bot(cls):
        if not cls._bot:
            cls._bot = TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False, use_class_middlewares=True)
            cls._bot.setup_middleware(SetLanguageMiddleware())
            cls._configure_bot()
            TelegramHandlers(cls._bot).setup()
            return cls._bot
        return cls._bot

    @classmethod
    def _configure_bot(cls):
        if not settings.TELEGRAM_SETUP_BOT:
            return
        for lang in ["en", "pl"]:
            with override(lang):
                cls._bot.set_my_commands(
                    [
                        BotCommand("menu", _("Show menu")),
                    ],
                    language_code=lang,
                )
        if settings.TELEGRAM_WEBHOOK_URL:
            cls._bot.set_webhook(
                url=settings.TELEGRAM_WEBHOOK_URL, allowed_updates=["message", "callback_query", "message_reaction"]
            )

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


def get_token_for_webhook_url():
    """
    Used for configuring urlpatterns
    """
    if not settings.TELEGRAM_WEBHOOK_URL:
        return "token"
    else:
        return settings.TELEGRAM_WEBHOOK_URL.rstrip("/").split("/")[-1]


def is_heart_reaction_added(reaction_update: MessageReactionUpdated) -> bool:
    old_has_heart = any(r.emoji == "❤️" for r in reaction_update.old_reaction if getattr(r, "emoji", None))
    new_has_heart = any(r.emoji == "❤️" for r in reaction_update.new_reaction if getattr(r, "emoji", None))
    return new_has_heart and not old_has_heart


def resolve_offers_from_reaction(reaction_update: MessageReactionUpdated) -> list[Offer]:
    # As per spec, we should fetch message via bot.get_message.
    # Note: telebot might lack this natively depending on version/plugins,
    # but we follow the spec's assumption that bot has get_message or we catch error.
    bot = TelegramBot.get_bot()
    try:
        # Some versions/extensions of telebot might support get_message
        message = getattr(bot, "get_message", lambda c, m: None)(reaction_update.chat.id, reaction_update.message_id)
    except Exception as e:
        logger.warning("Failed to fetch message for reaction: %s", e)
        return []

    if not message or not message.text:
        return []

    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', message.text)
    if not urls:
        return []

    return list(Offer.objects.filter(url__in=urls))


@TelegramBot.get_bot().message_reaction_handler(func=lambda u: True)
def handle_like_reaction(reaction_update: MessageReactionUpdated) -> None:
    old_has_heart = any(r.emoji == "❤️" for r in reaction_update.old_reaction if getattr(r, "emoji", None))
    new_has_heart = any(r.emoji == "❤️" for r in reaction_update.new_reaction if getattr(r, "emoji", None))

    if old_has_heart == new_has_heart:
        return

    heart_added = new_has_heart
    offers = resolve_offers_from_reaction(reaction_update)
    if not offers:
        return

    liker_label = str(reaction_update.user.id) if reaction_update.user else str(reaction_update.chat.id)
    liker = AnonymousLiker(label=liker_label)

    if heart_added:
        like_offers(offers, liker)
    else:
        unlike_offers(offers, liker)
