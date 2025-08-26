from shargain.commons.application.actor import Actor
from shargain.notifications.application.dto import NotificationConfigDTO
from shargain.notifications.application.exceptions import NotificationConfigDoesNotExist
from shargain.notifications.models import NotificationConfig


def get_notification_config(actor: Actor, config_id: int) -> NotificationConfigDTO:
    """Get a notification configuration by ID for an actor.

    Args:
        actor: The actor performing the query
        config_id: The ID of the notification configuration to retrieve

    Returns:
        A NotificationConfigDTO containing the notification configuration data

    Raises:
        NotificationConfigDoesNotExist: If the configuration doesn't exist or
            doesn't belong to the actor
    """
    try:
        config = NotificationConfig.objects.get(id=config_id, owner_id=actor.user_id)
    except NotificationConfig.DoesNotExist as e:
        raise NotificationConfigDoesNotExist() from e

    return NotificationConfigDTO(
        id=config.id,
        name=config.name,
        channel=config.channel,
        chat_id=config.chatid,
    )
