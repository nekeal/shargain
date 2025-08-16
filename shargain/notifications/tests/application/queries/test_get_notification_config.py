import pytest
from django.contrib.auth import get_user_model

from shargain.commons.application.actor import Actor
from shargain.notifications.application.dto import NotificationConfigDTO
from shargain.notifications.application.exceptions import NotificationConfigDoesNotExist
from shargain.notifications.application.queries.get_notification_config import (
    get_notification_config,
)
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig

User = get_user_model()


class TestGetNotificationConfig:
    """Test cases for the get_notification_config query."""

    @pytest.mark.django_db
    def test_get_notification_config_success(self, actor: Actor, user: User):
        """Test successfully getting a notification config."""
        # Given
        config = NotificationConfig.objects.create(
            name="Test Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="12345",
            owner=user,
        )

        # When
        result = get_notification_config(actor, config.id)

        # Then
        expected = NotificationConfigDTO(
            id=config.id,
            name="Test Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chat_id="12345",
        )
        assert result == expected

    @pytest.mark.django_db
    def test_get_notification_config_not_found(self, actor: Actor):
        """Test getting a notification config that doesn't exist."""
        # Given
        non_existent_id = 999999

        # When / Then
        with pytest.raises(NotificationConfigDoesNotExist):
            get_notification_config(actor, non_existent_id)

    @pytest.mark.django_db
    def test_get_notification_config_wrong_owner(self, actor: Actor, user: User):
        """Test getting a notification config that belongs to another user."""
        # Given
        other_user = User.objects.create_user(username="otheruser", password="testpass")
        config = NotificationConfig.objects.create(
            name="Other User Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="67890",
            owner=other_user,
        )

        # When / Then
        with pytest.raises(NotificationConfigDoesNotExist):
            get_notification_config(actor, config.id)
