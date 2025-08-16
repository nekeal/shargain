import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.notifications.application.actor import Actor
from shargain.notifications.application.commands.update_notification_config import (
    update_notification_config,
)
from shargain.notifications.application.dto import NotificationConfigDTO
from shargain.notifications.application.exceptions import NotificationConfigDoesNotExist
from shargain.notifications.application.queries.get_notification_config import (
    get_notification_config,
)
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig


class TestUpdateNotificationConfig:
    """Test cases for the update_notification_config command."""

    @pytest.mark.django_db
    def test_update_notification_config_success(self, actor: Actor, user: CustomUser):
        """Test successfully updating a notification config."""
        # Given
        config = NotificationConfig.objects.create(
            name="Original Name",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="12345",
            owner=user,
        )
        new_name = "Updated Name"

        # When
        result = update_notification_config(actor, config.id, new_name)

        # Then
        expected = NotificationConfigDTO(
            id=config.id,
            name=new_name,
            channel=NotificationChannelChoices.TELEGRAM,
            chat_id="12345",
        )
        assert result == expected

        # Verify it was updated in the database
        config.refresh_from_db()
        assert config.name == new_name

    def test_update_notification_config_with_none_name_is_converted_to_empty_string(
        self, actor: Actor, user: CustomUser
    ):
        """Test updating a notification config with None name which should be converted to empty string."""
        # Given
        config = NotificationConfig.objects.create(
            name="Original Name",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="12345",
            owner=user,
        )

        # When
        result = update_notification_config(actor, config.id, None)

        # Then
        expected = NotificationConfigDTO(
            id=config.id,
            name="",
            channel=NotificationChannelChoices.TELEGRAM,
            chat_id="12345",
        )
        assert result == expected

        fetched_config = get_notification_config(actor, config.id)
        assert fetched_config.name == ""

    @pytest.mark.django_db
    def test_update_notification_config_not_found(self, actor: Actor):
        """Test updating a notification config that doesn't exist."""
        # Given
        non_existent_id = 999999

        # When / Then
        with pytest.raises(NotificationConfigDoesNotExist):
            update_notification_config(actor, non_existent_id, "New Name")

    def test_update_notification_config_wrong_owner(self, actor: Actor, user: CustomUser):
        """Test updating a notification config that belongs to another user."""
        # Given
        other_user = UserFactory.create(username="otheruser", password="testpass")
        config = NotificationConfig.objects.create(
            name="Other User Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="67890",
            owner=other_user,
        )
        # When / Then
        with pytest.raises(NotificationConfigDoesNotExist):
            update_notification_config(actor, config.id, "Updated Name")
