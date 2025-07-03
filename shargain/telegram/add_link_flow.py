"""Handles the interactive add link flow in the Telegram bot."""

import logging
from enum import Enum

from django.utils.translation import gettext as _
from telebot import TeleBot, types
from telebot.types import CallbackQuery
from telebot.types import Message as TelebotMessage

from shargain.offers.websites import OlxWebsiteValidator
from shargain.telegram.application import AddScrapingLinkHandler, ListScrapingLinksHandler
from shargain.telegram.bot import MenuCallback, TelegramBot

logger = logging.getLogger(__name__)
olx_validator = OlxWebsiteValidator()

bot = TelegramBot.get_bot()


class AddLinkCallback(str, Enum):
    SKIP_NAME = "CMD_SKIP_NAME"
    PROMPT_NAME_YES = "PROMPT_NAME_YES"
    PROMPT_NAME_NO = "PROMPT_NAME_NO"


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data == MenuCallback.ADD_LINK)
def callback_add_link(call: CallbackQuery) -> None:
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
    url = message.text.strip()
    try:
        if not olx_validator.validate_list_url(url):
            raise ValueError(_("Invalid URL format. Please provide a valid URL."))

        markup = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton(
            text=_("✅ Yes"), callback_data=f"{AddLinkCallback.PROMPT_NAME_YES}:{url}"
        )
        no_button = types.InlineKeyboardButton(text=_("❌ No"), callback_data=f"{AddLinkCallback.PROMPT_NAME_NO}:{url}")
        markup.row(yes_button, no_button)

        bot.send_message(chat_id, _("📝 Would you like to provide a name for this link?"), reply_markup=markup)

    except Exception:
        logger.warning("Error in process_url")
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
            reply_markup=types.ForceReply(selective=False),
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


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data.startswith(AddLinkCallback.PROMPT_NAME_YES))
def handle_prompt_name_yes(call: CallbackQuery) -> None:
    """Handle the 'Yes' button click for providing a name."""
    try:
        prompt_for_name(TelegramBot.get_bot(), call)
    finally:
        TelegramBot.get_bot().answer_callback_query(call.id)


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data.startswith(AddLinkCallback.PROMPT_NAME_NO))
def handle_prompt_name_no(call: CallbackQuery) -> None:
    """Handle the 'No' button click for skipping name."""
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
