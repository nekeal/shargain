import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig
from shargain.offers.application.actor import Actor
from shargain.offers.application.queries.get_target import get_target_by_user
from shargain.offers.models import ScrappingTarget
from shargain.telegram.application.setup_scraping_target_handler import SetupScrapingTargetHandler
from shargain.telegram.models import TelegramRegisterToken, TelegramUser


@pytest.fixture
def user(db) -> CustomUser:
    return UserFactory.create()


@pytest.fixture
def handler() -> SetupScrapingTargetHandler:
    return SetupScrapingTargetHandler()


class TestSetupScrapingTargetHandlerForNewScrapingTarget:
    """
    Test cases for the SetupScrapingTargetHandler when a registration token is used to create a new scraping target,
    notification config, and link them.
    """

    @pytest.fixture
    def register_token(self, user) -> TelegramRegisterToken:
        return TelegramRegisterToken.objects.create(
            user=user, register_token="test-token-123", name="Test Target", is_used=False
        )

    def test_creates_new_scraping_target_and_notification_config(self, user, register_token, handler):
        result = handler.handle(chat_id="12345", token_str=register_token.register_token)

        assert result.success is True
        assert "configured successfully" in result.message.lower()

        # Verify notification config was created
        notification_config = NotificationConfig.objects.get(
            owner=user, chatid="12345", channel=NotificationChannelChoices.TELEGRAM
        )
        assert notification_config.name == register_token.name

        # Verify scraping target was created
        assert ScrappingTarget.objects.filter(owner=user, notification_config=notification_config).first()

        # Verify token was marked as used
        register_token.refresh_from_db()
        assert register_token.is_used is True

        # Verify Telegram user was created
        assert TelegramUser.objects.filter(user=user, telegram_id="12345", is_active=True).exists()

    def test_fails_when_token_already_used(self, user, handler):
        used_token = TelegramRegisterToken.objects.create(
            user=user, register_token="test-token-1234", name="Test Target", is_used=True
        )

        result = handler.handle(chat_id="12345", token_str=used_token.register_token)

        assert result.success is False
        assert "invalid or already used" in result.message.lower()

    def test_scraping_target_is_configured_when_notification_config_exists_for_chat(
        self, user, register_token, handler
    ):
        # Create existing notification config for this chat
        notification_config = NotificationConfig.objects.create(
            owner=user, chatid="12345", channel=NotificationChannelChoices.TELEGRAM, name="Existing Config"
        )

        result = handler.handle(chat_id="12345", token_str=register_token.register_token)

        assert result.success is True

        assert get_target_by_user(Actor(user_id=user.id)).notification_config_id == notification_config.id


class TestSetupScrapingTargetHandlerForSettingNotificationConfig:
    """
    Test cases for the SetupScrapingTargetHandler when a registration token is used
     to set a notification config for an existing scraping target.
    """

    @pytest.fixture
    def scraping_target(self, user) -> ScrappingTarget:
        return ScrappingTarget.objects.create(name="Test Target", owner=user, notification_config=None)

    @pytest.fixture
    def register_token(self, user, scraping_target) -> TelegramRegisterToken:
        return TelegramRegisterToken.objects.create(
            user=user,
            register_token="test-token-456",
            name="Test Target",
            is_used=False,
        )

    def test_links_existing_target_to_new_notification_config(self, user, register_token, scraping_target, handler):
        result = handler.handle(chat_id="12345", token_str=register_token.register_token)

        assert result.success is True
        assert "configured successfully" in result.message.lower()

        notification_config = NotificationConfig.objects.filter(
            owner=user, chatid="12345", channel=NotificationChannelChoices.TELEGRAM
        ).first()
        assert notification_config

        scraping_target_dto = get_target_by_user(Actor(user_id=user.id))

        assert scraping_target_dto.notification_config_id == notification_config.pk

        # Verify token was marked as used
        register_token.refresh_from_db()
        assert register_token.is_used is True

    def test_handles_invalid_token(self, user):
        # Given
        handler = SetupScrapingTargetHandler()
        chat_id = "67890"
        invalid_token = "nonexistent-token"

        # When
        result = handler.handle(chat_id=chat_id, token_str=invalid_token)

        # Then
        assert result.success is False
        assert "invalid or already used" in result.message.lower()

    def test_creates_new_scraping_target_when_user_has_multiple_scraping_targets(
        self, handler, user, register_token, scraping_target
    ):
        """
        When user has multiple scraping targets, it's not possible to tell which one
         to configure for the new notification config. Therefore a new scraping target is created.
         It also covers the case when admin can create a register token for an external user.
        """
        _ = ScrappingTarget.objects.create(name="Test Target 2", owner=user, notification_config=None)
        assert ScrappingTarget.objects.filter(owner=user, notification_config=None).count() == 2

        result = handler.handle(chat_id="12345", token_str=register_token.register_token)

        assert result.success is True
        assert "configured successfully" in result.message.lower()

        assert ScrappingTarget.objects.filter(owner=user).count() == 3
        assert ScrappingTarget.objects.filter(owner=user, notification_config__isnull=False).count() == 1
