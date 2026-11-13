"""
Send a test notification to the configured channel for a ScrapingTarget.
"""

from shargain.commons.application.actor import Actor
from shargain.jobs.service import Jobs
from shargain.offers.application.exceptions import (
    NotificationConfigDoesNotExist,
    TargetDoesNotExist,
)
from shargain.offers.models import ScrappingTarget


def send_test_notification(actor: Actor, target_id: int) -> None:
    """
    Enqueues a test notification to the configured channel for a ScrapingTarget.

    Args:
        actor: The user performing the action.
        target_id: ID of the target to send the notification to.

    Raises:
        TargetDoesNotExist: If the target doesn't exist or doesn't belong to the user.
        NotificationConfigDoesNotExist: If the target does not have a notification channel configured.
    """
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as exc:
        raise TargetDoesNotExist() from exc

    if not target.notification_config:
        raise NotificationConfigDoesNotExist()

    config = target.notification_config
    Jobs.enqueue(
        "notification.telegram",
        stream_key=f"telegram:{config.chatid}",
        payload={
            "config_id": config.id,
            "kind": "text",
            "message": "This is a test notification from Shargain.",
            "rate_limit_scope": "notification:telegram",
        },
    )
