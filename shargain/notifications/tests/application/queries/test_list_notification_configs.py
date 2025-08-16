import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.notifications.application.dto import NotificationConfigDTO
from shargain.notifications.application.queries.list_notification_configs import (
    list_notification_configs,
)
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig


class TestListNotificationConfigs:
    """Test cases for the list_notification_configs query."""

    @pytest.mark.django_db
    def test_list_notification_configs_empty(self, actor: Actor):
        """Test listing notification configs when none exist."""
        # When
        result = list_notification_configs(actor)

        # Then
        assert result.configs == []

    @pytest.mark.django_db
    def test_list_notification_configs_with_data(self, actor: Actor, user: CustomUser):
        """Test listing notification configs when some exist."""
        config1 = NotificationConfig.objects.create(
            name="Test Config 1",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="12345",
            owner=user,
        )
        config2 = NotificationConfig.objects.create(
            name="Test Config 2",
            channel=NotificationChannelChoices.DISCORD,
            webhook_url="https://discord.com/webhook",
            owner=user,
        )
        # Create a config for another user to ensure it's not included
        other_user = UserFactory.create(username="otheruser", password="testpass")
        NotificationConfig.objects.create(
            name="Other User Config",
            channel=NotificationChannelChoices.TELEGRAM,
            chatid="67890",
            owner=other_user,
        )

        result = list_notification_configs(actor)

        # Check that we got the right configs (order may vary)
        config_dto1 = NotificationConfigDTO(
            id=config1.id,
            name="Test Config 1",
            channel=NotificationChannelChoices.TELEGRAM,
            chat_id="12345",
        )
        config_dto2 = NotificationConfigDTO(
            id=config2.id,
            name="Test Config 2",
            channel=NotificationChannelChoices.DISCORD,
            chat_id="",
        )

        assert len(result.configs) == 2
        assert config_dto1 in result.configs
        assert config_dto2 in result.configs
