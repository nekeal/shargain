from django.utils.translation import gettext as _
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from shargain.offers.websites import OlxWebsiteValidator
from shargain.telegram.add_link_flow import process_url
from shargain.telegram.bot import TelegramBot, logger


def detect_olx_offer_list(message: Message) -> bool:
    """Check if a message contains an OLX offer list URL."""
    if not message.text or message.reply_to_message:  # if message is reply to another do not process
        return False
    if not (url := extract_url(message.text.strip())):
        return False

    return OlxWebsiteValidator().validate_list_url(url)


def extract_url(text: str) -> str:
    """Extract the first URL from the given text."""
    url_start = text.find("http")
    if url_start == -1:
        return ""
    # Find the end of the URL (first whitespace or end of string)
    space_pos = text.find(" ", url_start)
    return text[url_start:space_pos] if space_pos != -1 else text[url_start:]


@TelegramBot.get_bot().message_handler(func=detect_olx_offer_list, content_types=["text"])
def handle_olx_offer_list(message: Message) -> None:
    """Handle detection of OLX offer list URL."""
    bot = TelegramBot.get_bot()

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(_("✅ Yes"), callback_data="OLX_ADD"),
        InlineKeyboardButton(_("❌ No"), callback_data="OLX_IGNORE"),
    )

    bot.send_message(
        message.chat.id,
        _("🔍 I noticed an OLX offer list. Would you like to add it to monitoring?"),
        reply_to_message_id=message.message_id,
        reply_markup=markup,
    )


@TelegramBot.get_bot().callback_query_handler(func=lambda call: call.data.startswith(("OLX_ADD", "OLX_IGNORE")))
def handle_olx_confirmation(call: CallbackQuery) -> None:
    """Handle OLX URL confirmation response."""

    bot = TelegramBot.get_bot()
    message: Message = call.message

    if call.data == "OLX_IGNORE":
        bot.delete_message(message.chat.id, message.message_id)
        return

    try:
        if not (message_with_url := message.reply_to_message):
            logger.warning("No reply to message found in callback")
            return
        if not (url := extract_url(message_with_url.text)):
            logger.warning("No URL found in reply message")
            return

        message_with_url.text = url
        process_url(bot, message_with_url)

        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            logger.warning("Could not delete message: %s", e)

    except (IndexError, ValueError, AttributeError) as e:
        logger.error("Error processing OLX confirmation: %s", e)
        bot.send_message(message.chat.id, _("❌ An error occurred while processing your request. Please try again."))
    except Exception as e:
        logger.error("Error processing URL from callback: %s", e)
        bot.send_message(message.chat.id, _("❌ An error occurred while processing the URL. Please try again."))
        return
    print("HANDLED confirmation")
