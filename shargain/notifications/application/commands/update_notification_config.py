from shargain.commons.application.actor import Actor
from shargain.notifications.application.dto import NotificationConfigDTO
from shargain.notifications.application.exceptions import NotificationConfigDoesNotExist
from shargain.notifications.models import NotificationConfig


def update_notification_config(actor: Actor, config_id: int, name: str | None) -> NotificationConfigDTO:
    """Update a notification configuration's name.

    Args:
        actor: The actor performing the command
        config_id: The ID of the notification configuration to update
        name: The new display name for the configuration (will be converted to empty string if None)

    Returns:
        A NotificationConfigDTO containing the updated notification configuration data

    Raises:
        NotificationConfigDoesNotExist: If the configuration doesn't exist or
            doesn't belong to the actor
    """
    try:
        config = NotificationConfig.objects.get(id=config_id, owner_id=actor.user_id)
    except NotificationConfig.DoesNotExist as e:
        raise NotificationConfigDoesNotExist() from e

    config.name = name or ""
    config.save()

    return NotificationConfigDTO(
        id=config.id,
        name=config.name,
        channel=config.channel,
        chat_id=config.chatid,
    )
