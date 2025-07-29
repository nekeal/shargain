import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.application.actor import Actor
from shargain.offers.application.commands.change_notification_config import (
    change_notification_config,
)
from shargain.offers.application.queries.get_target import get_target


@pytest.mark.django_db
class TestChangeNotificationConfig:
    @pytest.fixture
    def notification_config(self, scraping_target):
        return NotificationConfigFactory(owner=scraping_target.owner)

    def test_change_notification_config_sets_new_config_id_succeeds(self, scraping_target, notification_config):
        actor = Actor(user_id=scraping_target.owner_id)

        change_notification_config(
            actor,
            scraping_target.id,
            notification_config_id=notification_config.id,
        )

        updated_target = get_target(actor, scraping_target.id)
        assert updated_target.notification_config_id == notification_config.id

    def test_change_notification_config_to_none_removes_config_succeeds(self, scraping_target, notification_config):
        scraping_target.notification_config = notification_config
        scraping_target.save()
        actor = Actor(user_id=scraping_target.owner_id)

        change_notification_config(actor, scraping_target.id, None)

        updated_target = get_target(actor, scraping_target.id)

        assert updated_target.notification_config_id is None

    def test_change_notification_config_for_non_existent_target_raises_error(
        self,
    ):
        actor = Actor(user_id=1)

        with pytest.raises(ValueError, match="Target not found or access denied"):
            change_notification_config(actor, 999, 1)

    def test_change_notification_config_with_non_existent_config_id_raises_error(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id)

        with pytest.raises(ValueError, match="Notification config not found or access denied"):
            change_notification_config(actor, scraping_target.id, 999)

    def test_change_notification_config_with_other_user_config_id_raises_error(self, scraping_target):
        other_user = UserFactory()
        other_config = NotificationConfigFactory(owner=other_user)
        actor = Actor(user_id=scraping_target.owner_id)

        with pytest.raises(ValueError, match="Notification config not found or access denied"):
            change_notification_config(actor, scraping_target.id, other_config.id)
