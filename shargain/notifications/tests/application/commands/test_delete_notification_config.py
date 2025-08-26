import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.notifications.application.commands.delete_notification_config import (
    delete_notification_config,
)
from shargain.notifications.application.exceptions import NotificationConfigDoesNotExist
from shargain.notifications.application.queries.get_notification_config import (
    get_notification_config,
)
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig


class TestDeleteNotificationConfig:
    """Test cases for the delete_notification_config command."""

    def test_delete_notification_config_success(self, actor: Actor, user: CustomUser):
        """Test successfully deleting a notification config."""
        config = NotificationConfig.objects.create(
            name="Test Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="12345",
            owner=user,
        )

        delete_notification_config(actor, config.id)

        with pytest.raises(NotificationConfigDoesNotExist):
            get_notification_config(actor, config.id)

    @pytest.mark.django_db
    def test_delete_notification_config_not_found(self, actor: Actor):
        """Test deleting a notification config that doesn't exist."""
        # When / Then
        with pytest.raises(NotificationConfigDoesNotExist):
            delete_notification_config(actor, 999999)

    @pytest.mark.django_db
    def test_delete_notification_config_wrong_owner(self, actor: Actor, user: CustomUser):
        """Test deleting a notification config that belongs to another user."""
        other_user = UserFactory.create(username="otheruser", password="testpass")
        config = NotificationConfig.objects.create(
            name="Other User Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="67890",
            owner=other_user,
        )

        with pytest.raises(NotificationConfigDoesNotExist):
            delete_notification_config(actor, config.id)

        other_actor = Actor(user_id=other_user.id)
        fetched_config = get_notification_config(other_actor, config.id)
        assert fetched_config.id == config.id
