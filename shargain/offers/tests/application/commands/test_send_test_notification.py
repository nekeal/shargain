import pytest

from shargain.commons.application.actor import Actor
from shargain.jobs.models import Job
from shargain.notifications.tests.factories import NotificationConfigFactory
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

        send_test_notification(actor=actor, target_id=scraping_target.id)

        job = Job.objects.get()
        assert job.type == "notification.telegram"
        assert job.payload["message"] == "This is a test notification from Shargain."
        assert job.payload["config_id"] == notification_config.id
        assert job.stream_key == f"telegram:{notification_config.chatid}"

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
