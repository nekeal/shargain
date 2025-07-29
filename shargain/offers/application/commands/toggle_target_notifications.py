"""
Toggle notifications for a ScrapingTarget.

This command enables or disables notifications for an existing scraping target.
"""

from shargain.offers.application.actor import Actor
from shargain.offers.application.dto import TargetDTO
from shargain.offers.models import ScrappingTarget


def toggle_target_notifications(
    actor: Actor,
    target_id: int,
    enable: bool | None = None,
) -> TargetDTO:
    """Toggle notifications for a target.

    If `enable` is None, the current setting will be toggled.
    If `enable` is True/False, notifications will be set to that value.

    Args:
        actor: The user performing the action.
        target_id: ID of the target to update.
        enable: Whether to enable notifications. If None, toggles current state.

    Returns:
        TargetDTO: Updated target data with new notification status.

    Raises:
        ValueError: If the target doesn't exist or doesn't belong to the user.
    """
    try:
        target = ScrappingTarget.objects.get(id=target_id, owner_id=actor.user_id)
    except ScrappingTarget.DoesNotExist as exc:
        raise ValueError("Target not found or access denied") from exc

    # Determine a new notification state
    new_state = not target.enable_notifications if enable is None else enable

    # Only update if the state is actually changing
    if target.enable_notifications != new_state:
        target.enable_notifications = new_state
        target.save(update_fields=["enable_notifications"])

    return TargetDTO.from_orm(target)
