import pytest

from shargain.notifications.application.actor import Actor
from shargain.notifications.application.commands.create_notification_config import (
    create_notification_config,
)
from shargain.notifications.application.dto import NotificationConfigDTO
from shargain.notifications.application.queries.get_notification_config import (
    get_notification_config,
)
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig


class TestCreateNotificationConfig:
    """Test cases for the create_notification_config command."""

    @pytest.mark.django_db
    def test_create_notification_config_success(self, actor: Actor):
        """Test successfully creating a notification config."""
        # Given
        name = "Test Config"
        chat_id = "12345"

        # When
        result = create_notification_config(actor, name, chat_id)

        # Then
        expected = NotificationConfigDTO(
            id=result.id,  # We need to use the actual ID from the result
            name=name,
            channel=NotificationChannelChoices.TELEGRAM,
            chat_id=chat_id,
        )
        assert result == expected

        # Verify it was saved to the database
        config = NotificationConfig.objects.get(id=result.id)
        assert config.name == name
        assert config.channel == NotificationChannelChoices.TELEGRAM
        assert config.chatid == chat_id
        assert config.owner_id == actor.user_id

    @pytest.mark.django_db
    def test_create_notification_config_with_none_name_is_converted_to_empty_string(self, actor: Actor):
        """Test creating a notification config with None name which should be converted to empty string."""

        result = create_notification_config(actor, name=None, chat_id="12345")
        expected = NotificationConfigDTO(
            id=result.id,  # We need to use the actual ID from the result
            name="",  # Should be converted to empty string
            channel=NotificationChannelChoices.TELEGRAM,
            chat_id="12345",
        )
        assert result == expected

        config = get_notification_config(actor, config_id=result.id)
        assert config.name == ""

    @pytest.mark.django_db
    def test_create_notification_config_with_explicit_channel(self, actor: Actor):
        """Test creating a notification config with an explicit channel."""
        # Given
        name = "Test Config"
        chat_id = "12345"
        channel = NotificationChannelChoices.DISCORD

        # When
        result = create_notification_config(actor, name, chat_id, channel)

        # Then
        expected = NotificationConfigDTO(
            id=result.id,  # We need to use the actual ID from the result
            name=name,
            channel=NotificationChannelChoices.DISCORD,
            chat_id=chat_id,
        )
        assert result == expected
