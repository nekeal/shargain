import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.application.actor import Actor
from shargain.offers.application.commands.change_notification_config import (
    TargetDTO,
    change_notification_config,
)
from shargain.offers.models import ScrappingTarget


@pytest.mark.django_db
class TestChangeNotificationConfig:
    @pytest.fixture
    def notification_config(self, scraping_target):
        return NotificationConfigFactory(owner=scraping_target.owner)

    def test_change_notification_config_success(self, scraping_target, notification_config):
        """Test successfully changing the notification config for a target"""
        actor = Actor(user_id=scraping_target.owner_id)

        result = change_notification_config(actor, scraping_target.id, notification_config_id=notification_config.id)

        assert result.notification_config_id == notification_config.id

        updated_target = ScrappingTarget.objects.get(id=scraping_target.id)
        assert updated_target.notification_config_id == notification_config.id

    def test_remove_notification_config_success(self, scraping_target, notification_config):
        """Test successfully removing the notification config from a target"""
        scraping_target.notification_config = notification_config
        scraping_target.save()
        actor = Actor(user_id=scraping_target.owner_id)

        result = change_notification_config(actor, scraping_target.id, None)

        assert result.notification_config_id is None
        updated_target = ScrappingTarget.objects.get(id=scraping_target.id)
        assert updated_target.notification_config_id is None

    def test_target_not_found_raises_error(self, db):
        """Test that changing config for non-existent target raises error"""
        actor = Actor(user_id=1)

        with pytest.raises(ValueError, match="Target not found or access denied"):
            change_notification_config(actor, 999, 1)

    def test_notification_config_not_found_raises_error(self, scraping_target):
        """Test that using non-existent notification config ID raises error"""
        actor = Actor(user_id=scraping_target.owner_id)

        with pytest.raises(ValueError, match="Notification config not found or access denied"):
            change_notification_config(actor, scraping_target.id, 999)

    def test_notification_config_belongs_to_different_user_raises_error(self, scraping_target):
        """Test that using notification config from another user raises error"""
        other_user = UserFactory()
        other_config = NotificationConfigFactory(owner=other_user)
        actor = Actor(user_id=scraping_target.owner_id)

        with pytest.raises(ValueError, match="Notification config not found or access denied"):
            change_notification_config(actor, scraping_target.id, other_config.id)

    def test_returns_correct_dto(self, scraping_target, notification_config):
        """Test that the returned DTO contains correct data"""
        actor = Actor(user_id=scraping_target.owner_id)

        result = change_notification_config(actor, scraping_target.id, notification_config.id)

        assert result == TargetDTO(
            id=scraping_target.id,
            name=scraping_target.name,
            is_active=scraping_target.is_active,
            enable_notifications=scraping_target.enable_notifications,
            notification_config_id=notification_config.id,
        )
