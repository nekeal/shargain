import html
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

from shargain.commons.application.actor import Actor
from shargain.notifications.models import NotificationConfig
from shargain.offers.application.exceptions import OfferDoesNotExist
from shargain.offers.application.offer_state import get_offer_states, like_offers, unlike_offers
from shargain.offers.models import Offer, ScrappingTarget, UserOfferState
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
            cls._bot.set_webhook(url=settings.TELEGRAM_WEBHOOK_URL, allowed_updates=["message", "callback_query"])

    @classmethod
    def _set_logging_level(cls, logging_level: int):
        telebot.logger.setLevel(logging_level)

    @classmethod
    def run(cls, verbose: bool = False):
        if verbose:
            cls._set_logging_level(logging.DEBUG)
        cls.get_bot().polling(allowed_updates=["message", "callback_query"])

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


def resolve_user_for_offer_chat(offer: Offer, chat_id: int | str) -> int | None:
    target = getattr(offer, "target", None)
    config = getattr(target, "notification_config", None) if target else None
    if (
        target
        and config
        and config.owner_id
        and str(config.chatid) == str(chat_id)
        and target.owner_id == config.owner_id
    ):
        return config.owner_id
    return None


def resolve_user_for_chat(chat_id: int | str) -> int | None:
    owners = list(
        ScrappingTarget.objects.filter(
            notification_config__chatid=str(chat_id),
            notification_config__owner__isnull=False,
        )
        .values_list("notification_config__owner_id", flat=True)
        .distinct()
    )
    if len(owners) == 1:
        return owners[0]
    return None


def resolve_offers_from_message(message: telebot.types.Message) -> list[Offer]:
    if not message or not message.text or not getattr(message, "chat", None):
        return []

    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', message.text)
    if not urls:
        return []

    return list(
        Offer.objects.filter(
            url__in=urls,
            target__notification_config__chatid=str(message.chat.id),
            target__notification_config__owner__isnull=False,
        ).select_related("target__notification_config")
    )


def is_like_reply(message: telebot.types.Message) -> bool:
    if not message.reply_to_message or not message.text:
        return False
    text = message.text.strip().lower()
    return text in ["like", "/like", "❤️", "❤", "👍", "unlike", "/unlike", "💔", "👎"]


@TelegramBot.get_bot().message_handler(func=is_like_reply)
def handle_like_reply(message: telebot.types.Message) -> None:
    logger.info("Received like reply: %s", message.text)
    offers = resolve_offers_from_message(message.reply_to_message)
    if not offers:
        logger.warning("No offers found in the replied message.")
        TelegramBot.get_bot().reply_to(message, _("No offers found in the message you replied to."))
        return

    user_ids = {resolve_user_for_offer_chat(o, message.chat.id) for o in offers}
    if None in user_ids or len(user_ids) != 1:
        logger.warning("Could not attribute like in chat %s for offers %s", message.chat.id, [o.id for o in offers])
        TelegramBot.get_bot().reply_to(message, _("Could not attribute like to an authorized account."))
        return
    user_id = next(iter(user_ids))
    if user_id is None:
        return
    actor = Actor(user_id=user_id)

    text = message.text.strip().lower()
    is_unlike_action = text in ["unlike", "/unlike", "💔", "👎"]
    states = get_offer_states(actor, [o.id for o in offers])
    all_liked = all(s.is_liked for s in states.values())
    try:
        if is_unlike_action or (all_liked and text in ["like", "/like", "❤️", "❤", "👍"]):
            unlike_offers(actor, [o.id for o in offers])
            TelegramBot.get_bot().reply_to(message, _("💔 Unliked {count} offer(s).").format(count=len(offers)))
        else:
            like_offers(actor, [o.id for o in offers])
            TelegramBot.get_bot().reply_to(message, _("❤️ Liked {count} offer(s)!").format(count=len(offers)))
    except OfferDoesNotExist:
        logger.warning("Target owner mismatch or offer does not exist in chat %s", message.chat.id)
        TelegramBot.get_bot().reply_to(message, _("Could not attribute like to an authorized account."))


@TelegramBot.get_bot().message_handler(commands=["liked", "likes"])
def handle_liked_command(message: telebot.types.Message) -> None:
    user_id = resolve_user_for_chat(message.chat.id)
    if not user_id:
        TelegramBot.get_bot().reply_to(message, _("Could not find registered targets for this chat."))
        return

    states = list(
        UserOfferState.objects.filter(
            user_id=user_id,
            liked_at__isnull=False,
            offer__target__notification_config__chatid=str(message.chat.id),
        )
        .select_related("offer")
        .order_by("-liked_at")[:50]
    )
    if not states:
        TelegramBot.get_bot().reply_to(message, _("No offers have been liked in this chat yet!"))
        return

    header = _("Latest liked offers in this chat:")
    lines = [header]
    for state in states:
        raw_title = state.offer.title if state.offer.title else _("Offer")
        escaped_title = html.escape(str(raw_title))
        escaped_url = html.escape(state.offer.url)
        lines.append(f"• <a href='{escaped_url}'>{escaped_title}</a> — /unlike_{state.offer.id}")

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_len = 0
    for line in lines:
        line_len = len(line) + 1
        if current_chunk and current_len + line_len > 4000:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_len = line_len
        else:
            current_chunk.append(line)
            current_len += line_len
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    for chunk in chunks:
        TelegramBot.get_bot().reply_to(message, chunk, parse_mode="HTML")


@TelegramBot.get_bot().message_handler(regexp=r"^/unlike_(\d+)(?:@\w+)?$")
def handle_unlike_by_id_command(message: telebot.types.Message) -> None:
    match = re.match(r"^/unlike_(\d+)(?:@\w+)?$", message.text.strip() if message.text else "")
    if not match:
        return
    offer_id = int(match.group(1))
    offer = (
        Offer.objects.filter(
            pk=offer_id,
            target__notification_config__chatid=str(message.chat.id),
            target__notification_config__owner__isnull=False,
        )
        .select_related("target__notification_config", "target")
        .first()
    )
    if not offer:
        TelegramBot.get_bot().reply_to(message, _("Offer not found or not accessible in this chat."))
        return

    user_id = resolve_user_for_offer_chat(offer, message.chat.id)
    if not user_id:
        TelegramBot.get_bot().reply_to(message, _("Could not attribute action to an authorized account."))
        return

    actor = Actor(user_id=user_id)
    try:
        unlike_offers(actor, [offer.id])
    except OfferDoesNotExist:
        TelegramBot.get_bot().reply_to(message, _("Could not attribute action to an authorized account."))
        return
    title = offer.title if offer.title else _("Offer")
    TelegramBot.get_bot().reply_to(message, _("💔 Unliked offer: {title}").format(title=title))
