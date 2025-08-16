import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.notifications.application.commands.delete_notification_config import (
    delete_notification_config,
)
from shargain.notifications.application.exceptions import NotificationConfigDoesNotExist
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig


class TestDeleteNotificationConfig:
    """Test cases for the delete_notification_config command."""

    def test_delete_notification_config_success(self, actor: Actor, user: CustomUser):
        """Test successfully deleting a notification config."""
        # Given
        config = NotificationConfig.objects.create(
            name="Test Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="12345",
            owner=user,
        )
        # When
        delete_notification_config(actor, config.id)

        # Then
        with pytest.raises(NotificationConfig.DoesNotExist):
            NotificationConfig.objects.get(id=config.id)

    @pytest.mark.django_db
    def test_delete_notification_config_not_found(self, actor: Actor):
        """Test deleting a notification config that doesn't exist."""
        # When / Then
        with pytest.raises(NotificationConfigDoesNotExist):
            delete_notification_config(actor, 999999)

    @pytest.mark.django_db
    def test_delete_notification_config_wrong_owner(self, actor: Actor, user: CustomUser):
        """Test deleting a notification config that belongs to another user."""
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
            delete_notification_config(actor, config.id)

        # Verify it still exists in the database
        assert NotificationConfig.objects.filter(id=config.id).exists()
