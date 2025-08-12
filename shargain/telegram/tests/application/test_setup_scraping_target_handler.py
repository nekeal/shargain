import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.notifications.models import NotificationConfig
from shargain.offers.application.actor import Actor
from shargain.offers.models import ScrappingTarget
from shargain.telegram.application.commands.generate_telegram_token import generate_telegram_token
from shargain.telegram.application.setup_scraping_target_handler import (
    SetupScrapingTargetHandler,
)
from shargain.telegram.models import TelegramRegisterToken, TelegramUser


@pytest.mark.django_db
class TestSetupScrapingTargetHandler:
    @pytest.fixture
    def user(self) -> CustomUser:
        return UserFactory.create()

    def test_handle_registers_user_and_config_with_valid_token(self, user, m_telegram_bot):
        token = generate_telegram_token(bot=m_telegram_bot, actor=Actor(user_id=user.id))
        handler = SetupScrapingTargetHandler()
        result = handler.handle(chat_id="12345", token_str=token.token)

        assert result.success is True
        assert TelegramRegisterToken.objects.get(register_token=token.token).is_used is True
        assert TelegramUser.objects.filter(user=user, telegram_id="12345", is_active=True).exists()
        assert NotificationConfig.objects.filter(owner=user, chatid="12345").exists()
        assert ScrappingTarget.objects.filter(owner=user).exists()

    def test_handle_returns_failure_for_invalid_token(self):
        handler = SetupScrapingTargetHandler()
        result = handler.handle(chat_id="12345", token_str="invalid_token")

        assert result.success is False
        assert "token is invalid or already used" in result.message

    def test_handle_returns_failure_for_already_used_token(self, user):
        TelegramRegisterToken.objects.create(user=user, register_token="used_token", is_used=True)
        handler = SetupScrapingTargetHandler()
        result = handler.handle(chat_id="12345", token_str="used_token")

        assert result.success is False
        assert "token is invalid or already used" in result.message

    def test_handle_returns_failure_when_notification_config_exists(self, user):
        TelegramRegisterToken.objects.create(user=user, register_token="token_exists", is_used=False)
        NotificationConfig.objects.create(owner=user, chatid="12345", name="test-user")
        handler = SetupScrapingTargetHandler()
        result = handler.handle(chat_id="12345", token_str="token_exists")

        assert result.success is False
        assert "already taken or notifications are already configured" in result.message

    def test_handle_returns_failure_when_scraping_target_exists(self, user):
        TelegramRegisterToken.objects.create(user=user, register_token="token_exists_target", is_used=False)
        ScrappingTarget.objects.create(owner=user, name="test-user")
        handler = SetupScrapingTargetHandler()
        result = handler.handle(chat_id="12345", token_str="token_exists_target")

        assert result.success is False
        assert "already taken or notifications are already configured" in result.message
