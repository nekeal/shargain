from unittest import mock

import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.telegram.bot import TelegramBot


@pytest.fixture
def m_telegram_bot() -> TelegramBot:
    m_telegram_bot = mock.Mock(spec=TelegramBot)
    m_telegram_bot.get_username.return_value = "shargain_bot"
    return m_telegram_bot


@pytest.fixture
def user() -> CustomUser:
    return UserFactory.create()
