from shargain.commons.application.actor import Actor
from shargain.notifications.application.exceptions import NotificationConfigDoesNotExist
from shargain.notifications.models import NotificationConfig


def delete_notification_config(actor: Actor, config_id: int) -> None:
    """Delete a notification configuration.

    Args:
        actor: The actor performing the command
        config_id: The ID of the notification configuration to delete

    Raises:
        NotificationConfigDoesNotExist: If the configuration doesn't exist or
            doesn't belong to the actor
    """
    try:
        config = NotificationConfig.objects.get(id=config_id, owner_id=actor.user_id)
    except NotificationConfig.DoesNotExist as e:
        raise NotificationConfigDoesNotExist() from e

    config.delete()
