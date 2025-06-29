"""Handles the interactive add link flow in the Telegram bot."""

import logging
from enum import Enum

from django.core.validators import URLValidator
from django.utils.translation import gettext as _
from telebot import TeleBot, types
from telebot.types import Message as TelebotMessage

from shargain.telegram.application import AddScrapingLinkHandler, ListScrapingLinksHandler

logger = logging.getLogger(__name__)
url_validator = URLValidator()


class AddLinkCallback(str, Enum):
    SKIP_NAME = "CMD_SKIP_NAME"
    PROMPT_NAME_YES = "PROMPT_NAME_YES"
    PROMPT_NAME_NO = "PROMPT_NAME_NO"


def start_add_link_flow(bot, call: types.CallbackQuery) -> None:
    """Start the add link flow."""
    chat_id = call.message.chat.id
    msg = bot.send_message(
        chat_id,
        _("🔗 Please send me the URL you want to monitor:"),
        reply_markup=types.ForceReply(selective=True),
    )
    bot.register_for_reply(msg, lambda m: process_url(bot, m))


def process_url(bot: TeleBot, message: TelebotMessage) -> None:
    """Process the URL input and prompt for name."""
    chat_id = message.chat.id
    try:
        url = message.text.strip()
        url_validator(url)

        # Create inline keyboard with yes/no buttons
        markup = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton(
            text=_("✅ Yes"), callback_data=f"{AddLinkCallback.PROMPT_NAME_YES}:{url}"
        )
        no_button = types.InlineKeyboardButton(text=_("❌ No"), callback_data=f"{AddLinkCallback.PROMPT_NAME_NO}:{url}")
        markup.row(yes_button, no_button)

        # Ask if user wants to provide a name
        bot.send_message(chat_id, _("📝 Would you like to provide a name for this link?"), reply_markup=markup)

    except Exception:
        logger.exception("Error in process_url")
        msg = bot.send_message(
            chat_id,
            _("❌ Invalid URL. Please send a valid URL:"),
            reply_markup=types.ForceReply(selective=True),
        )
        # Register for reply to handle the retry
        bot.register_for_reply(msg, lambda m: process_url(bot, m))


def process_name(bot: TeleBot, message: TelebotMessage, url: str) -> None:
    """Process the name input and save the link."""
    chat_id = message.chat.id
    try:
        name = message.text.strip()
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
        )
    except Exception:
        logger.exception("Error saving link")
        bot.send_message(
            chat_id,
            _("❌ An error occurred while saving the link. Please try again."),
        )


def prompt_for_name(bot: TeleBot, call: types.CallbackQuery) -> None:
    """Prompt user to enter a name for the link."""
    chat_id = call.message.chat.id
    try:
        url = call.data.split(":", 1)[1]
        msg = bot.send_message(
            chat_id,
            _("📝 Please enter a name for this link:"),
            reply_markup=types.ForceReply(selective=True),
        )
        bot.register_for_reply(msg, lambda m, u=url: process_name(bot, m, u))
    except Exception:
        logger.exception("Error in prompt_for_name")
        bot.send_message(
            chat_id,
            _("❌ An error occurred. Please try again."),
        )


def handle_skip_name(bot: TeleBot, call: types.CallbackQuery) -> None:
    """Handle skip name button click."""
    chat_id = call.message.chat.id
    try:
        url = call.data.split(":", 1)[1]
        save_and_confirm_link(bot, chat_id, url, "")
    except Exception:
        logger.exception("Error handling skip name")
        bot.send_message(
            chat_id,
            _("❌ An error occurred while saving the link. Please try again."),
        )
        bot.answer_callback_query(call.id, _("Error skipping name"))
