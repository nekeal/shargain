"""Tests for TelegramNotificationSender."""

from unittest.mock import patch

import pytest
from telebot.apihelper import ApiTelegramException

from shargain.notifications.senders import TelegramNotificationSender
from shargain.notifications.tests.factories import NotificationConfigFactory


@pytest.fixture
def sender(db):
    return TelegramNotificationSender(NotificationConfigFactory(), bot_token="test-token")


@pytest.fixture
def mock_telebot():
    with patch("shargain.notifications.senders.telebot.TeleBot") as telebot_class:
        yield telebot_class


def test_send_with_pin_sends_text_then_location_reusing_one_bot(sender, mock_telebot):
    bot = mock_telebot.return_value

    sender.send_with_pin("Apartment card", latitude=52.22, longitude=21.01, horizontal_accuracy=300.0)

    bot.send_message.assert_called_once_with("1234567890", "Apartment card")
    bot.send_location.assert_called_once()
    call_kwargs = bot.send_location.call_args.kwargs
    assert call_kwargs["latitude"] == 52.22
    assert call_kwargs["longitude"] == 21.01
    assert call_kwargs["horizontal_accuracy"] == 300.0
    assert call_kwargs["reply_parameters"].message_id is bot.send_message.return_value.message_id


def test_send_uses_same_bot_instance(sender, mock_telebot):
    sender.send("first")
    sender.send("second")

    mock_telebot.assert_called_once()
    mock_telebot.return_value.send_message.assert_called_with("1234567890", "second")


def test_send_with_pin_swallows_location_errors_but_keeps_card(sender, mock_telebot):
    bot = mock_telebot.return_value
    bot.send_location.side_effect = ApiTelegramException(
        "send_location",
        "error",
        {"error_code": 429, "description": "Too Many Requests", "parameters": {"retry_after": 1}},
    )

    sender.send_with_pin("Apartment card", latitude=52.22, longitude=21.01, horizontal_accuracy=300.0)

    bot.send_message.assert_called_once_with("1234567890", "Apartment card")
