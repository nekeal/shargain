import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
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
        config = NotificationConfig.objects.create(
            name="Original Name",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="12345",
            owner=user,
        )
        new_name = "Updated Name"

        result = update_notification_config(actor, config.id, new_name)

        expected = NotificationConfigDTO(
            id=config.id,
            name=new_name,
            channel=NotificationChannelChoices.TELEGRAM,
            chat_id="12345",
        )
        assert result == expected

        fetched_config = get_notification_config(actor, config.id)
        assert fetched_config == expected

    def test_update_notification_config_with_none_name_is_converted_to_empty_string(
        self, actor: Actor, user: CustomUser
    ):
        """Test updating a notification config with None name which should be converted to empty string."""
        config = NotificationConfig.objects.create(
            name="Original Name",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="12345",
            owner=user,
        )

        result = update_notification_config(actor, config.id, None)

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
        with pytest.raises(NotificationConfigDoesNotExist):
            update_notification_config(actor, 999999, "New Name")

    def test_update_notification_config_wrong_owner(self, actor: Actor, user: CustomUser):
        """Test updating a notification config that belongs to another user."""
        other_user = UserFactory.create(username="otheruser", password="testpass")
        config = NotificationConfig.objects.create(
            name="Other User Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="67890",
            owner=other_user,
        )

        with pytest.raises(NotificationConfigDoesNotExist):
            update_notification_config(actor, config.id, "Updated Name")
