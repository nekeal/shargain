"""Handles the interactive add link flow in the Telegram bot."""

import logging
from enum import Enum

from django.utils.translation import gettext as _
from telebot import TeleBot
from telebot.types import CallbackQuery, ForceReply, ReplyKeyboardMarkup
from telebot.types import Message as TelebotMessage

from shargain.offers.websites import OlxWebsiteValidator
from shargain.telegram.application import AddScrapingLinkHandler, ListScrapingLinksHandler
from shargain.telegram.bot import MenuCallback, TelegramBot

logger = logging.getLogger(__name__)
olx_validator = OlxWebsiteValidator()

bot = TelegramBot.get_bot()


class AddLinkCallback(str, Enum):
    SKIP_NAME = "CMD_SKIP_NAME"


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data == MenuCallback.ADD_LINK)
def callback_add_link(call: CallbackQuery) -> None:
    """Start the add link flow."""
    chat_id = call.message.chat.id
    msg = bot.send_message(chat_id, _("🔗 Please send me the URL you want to monitor:"), reply_markup=ForceReply())

    bot.register_for_reply_by_message_id(msg.id, lambda m: process_url(bot, m))


def process_url(bot: TeleBot, message: TelebotMessage) -> None:
    """Process the URL input and prompt for name."""
    chat_id = message.chat.id
    url = message.text.strip()
    try:
        if not olx_validator.validate_list_url(url):
            raise ValueError(_("Invalid URL format. Please provide a valid URL."))

        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(_("Skip"))
        msg = bot.send_message(
            chat_id,
            _("📝 Please enter a name for this link or type '%(skip_word)s' or 'x' to add without a name.")
            % {"skip_word": _("Skip")},
            reply_markup=markup,
            reply_to_message_id=message.message_id,
        )
        bot.register_next_step_handler(msg, lambda m: process_name(bot, m, url))

    except Exception:
        logger.warning("Error in process_url url=%s", url, exc_info=True)
        msg = bot.send_message(
            chat_id,
            _("❌ Invalid URL. Please send a valid URL:"),
            reply_markup=ForceReply(),
        )
        bot.register_for_reply(msg, lambda m: process_url(bot, m))


def process_name(bot: TeleBot, message: TelebotMessage, url: str) -> None:
    """Process the name input and save the link."""
    chat_id = message.chat.id
    try:
        name = message.text.strip()
        if name == _("Skip") or name.lower() == "x":
            name = ""
        save_and_confirm_link(bot, chat_id, url, name)
    except Exception:
        bot.send_message(
            chat_id,
            _("❌ An error occurred. Please try again."),
        )


def save_and_confirm_link(bot: TeleBot, chat_id: int, url: str, name: str = "") -> None:
    """Save the link and show confirmation."""
    try:
        AddScrapingLinkHandler().handle(chat_id, url, name)
        result = ListScrapingLinksHandler().handle(chat_id=chat_id)
        bot.send_message(
            chat_id,
            result.message,
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Error saving link")
        bot.send_message(
            chat_id,
            _("❌ An error occurred while saving the link. Please try again."),
        )
