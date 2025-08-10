from unittest.mock import patch

import pytest

from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.application.actor import Actor
from shargain.offers.application.commands.send_test_notification import send_test_notification
from shargain.offers.application.exceptions import (
    NotificationConfigDoesNotExist,
    TargetDoesNotExist,
)


@pytest.mark.django_db
class TestSendTestNotification:
    def test_send_test_notification_succeeds(self, scraping_target):
        notification_config = NotificationConfigFactory(owner=scraping_target.owner)
        scraping_target.notification_config = notification_config
        scraping_target.save()
        actor = Actor(user_id=scraping_target.owner_id)

        with patch(
            "shargain.offers.application.commands.send_test_notification.TelegramNotificationSender"
        ) as mock_sender:
            send_test_notification(actor=actor, target_id=scraping_target.id)
            mock_sender.assert_called_once_with(notification_config)
            mock_sender.return_value.send.assert_called_once_with("This is a test notification from Shargain.")

    def test_send_test_notification_target_does_not_exist(self):
        actor = Actor(user_id=1)
        with pytest.raises(TargetDoesNotExist):
            send_test_notification(actor=actor, target_id=999)

    def test_send_test_notification_target_belongs_to_other_user(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id + 1)
        with pytest.raises(TargetDoesNotExist):
            send_test_notification(actor=actor, target_id=scraping_target.id)

    def test_send_test_notification_no_notification_config(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id)
        with pytest.raises(NotificationConfigDoesNotExist):
            send_test_notification(actor=actor, target_id=scraping_target.id)
