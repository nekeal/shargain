import pytest
from django.conf import settings

from shargain.accounts.models import CustomUser
from shargain.commons.application.actor import Actor
from shargain.telegram.application.commands.generate_telegram_token import (
    UserDoesNotExist,
    generate_telegram_token,
)
from shargain.telegram.bot import TelegramBot
from shargain.telegram.models import TelegramRegisterToken
from shargain.telegram.tests.factories import TelegramRegisterTokenFactory, UserFactory

# Set default bot username for tests
settings.TELEGRAM_BOT_USERNAME = "your_bot_username"


@pytest.mark.django_db
class TestGenerateTelegramToken:
    @pytest.fixture
    def user(self) -> CustomUser:
        return UserFactory.create()

    def test_generate_telegram_token_creates_new_token(self, user: CustomUser, m_telegram_bot: TelegramBot):
        """Test that a new token is created when none exists for the user."""
        actor = Actor(user_id=user.id)

        result = generate_telegram_token(bot=m_telegram_bot, actor=actor)

        token_obj = TelegramRegisterToken.objects.get(user=user)
        assert token_obj.is_used is False

        assert f"https://t.me/{m_telegram_bot.get_username()}?start={result.token}" == result.telegram_bot_url

    def test_generate_telegram_token_returns_existing_active_token(self, user: CustomUser, m_telegram_bot: TelegramBot):
        """Test that an existing active token is returned if one exists."""
        existing_token = TelegramRegisterTokenFactory(user=user, is_used=False)
        actor = Actor(user_id=user.id)

        result = generate_telegram_token(bot=m_telegram_bot, actor=actor)

        assert result.token == existing_token.register_token

        assert TelegramRegisterToken.objects.filter(user=user).count() == 1

    def test_generate_telegram_token_creates_new_if_all_used(self, m_telegram_bot: TelegramBot, user: CustomUser):
        """Test that a new token is created if all existing ones are used."""
        # Create multiple used tokens
        used_token = TelegramRegisterTokenFactory(user=user, is_used=True)

        actor = Actor(user_id=user.id)

        result = generate_telegram_token(bot=m_telegram_bot, actor=actor)

        tokens = list(TelegramRegisterToken.objects.filter(user=user).order_by("-created_at"))
        assert len(tokens) == 2

        new_token = tokens[0]
        assert new_token.register_token == result.token
        assert new_token.is_used is False
        assert used_token.is_used is True

    def test_generate_telegram_token_nonexistent_user(self, m_telegram_bot: TelegramBot):
        """Test that UserDoesNotExist is raised for non-existent users."""
        actor = Actor(user_id=1)

        with pytest.raises(UserDoesNotExist):
            generate_telegram_token(bot=m_telegram_bot, actor=actor)
