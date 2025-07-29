"""
Change the notification configuration for a ScrapingTarget.

This command updates the notification configuration for an existing scraping target.
"""

from shargain.notifications.models import NotificationConfig
from shargain.offers.application.actor import Actor
from shargain.offers.application.dto import TargetDTO
from shargain.offers.application.exceptions import (
    NotificationConfigDoesNotExist,
    TargetDoesNotExist,
)
from shargain.offers.models import ScrappingTarget


def change_notification_config(
    actor: Actor,
    target_id: int,
    notification_config_id: int | None = None,
) -> TargetDTO:
    """Update the notification configuration for a target.

    Args:
        actor: The user performing the action.
        target_id: ID of the target to update.
        notification_config_id: Optional ID of the new notification configuration.
                             Set to None to remove the notification configuration.

    Returns:
        TargetDTO: Updated target data.

    Raises:
        TargetDoesNotExist: If the target doesn't exist or doesn't belong to the user.
        NotificationConfigDoesNotExist: If the notification config doesn't exist.
    """
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as exc:
        raise TargetDoesNotExist() from exc

    # If a new notification config ID is provided, verify it exists
    if notification_config_id is not None:
        try:
            NotificationConfig.objects.get(id=notification_config_id, owner_id=actor.user_id)
        except NotificationConfig.DoesNotExist as exc:
            raise NotificationConfigDoesNotExist() from exc

    # Update the target's notification configuration
    target.notification_config_id = notification_config_id
    target.save(update_fields=["notification_config_id"])

    return TargetDTO.from_orm(target)
