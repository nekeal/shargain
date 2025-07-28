"""
Change the notification configuration for a ScrapingTarget.

This command updates the notification configuration for an existing scraping target.
"""

from dataclasses import dataclass
from typing import Self

from shargain.notifications.models import NotificationConfig
from shargain.offers.application.actor import Actor
from shargain.offers.models import ScrappingTarget


@dataclass
class TargetDTO:
    """Data Transfer Object for ScrappingTarget with notification configuration."""

    id: int
    name: str
    is_active: bool
    enable_notifications: bool
    notification_config_id: int | None

    @classmethod
    def from_orm(cls, target: ScrappingTarget) -> Self:
        """Create a DTO from a ScrappingTarget model instance."""
        return cls(
            id=target.id,
            name=target.name,
            is_active=target.is_active,
            enable_notifications=target.enable_notifications,
            notification_config_id=target.notification_config_id,
        )


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
        ValueError: If the target doesn't exist or doesn't belong to the user.
        ValueError: If the notification config doesn't exist.
    """
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner=actor.user_id)
    except ScrappingTarget.DoesNotExist as exc:
        raise ValueError("Target not found or access denied") from exc

    # If a new notification config ID is provided, verify it exists
    if notification_config_id is not None:
        try:
            NotificationConfig.objects.get(id=notification_config_id, owner=actor.user_id)
        except NotificationConfig.DoesNotExist as exc:
            raise ValueError("Notification config not found or access denied") from exc

    # Update the target's notification configuration
    target.notification_config_id = notification_config_id
    target.save(update_fields=["notification_config_id"])

    return TargetDTO.from_orm(target)
