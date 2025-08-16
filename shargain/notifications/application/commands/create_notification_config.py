from shargain.notifications.application.actor import Actor
from shargain.notifications.application.dto import NotificationConfigDTO
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig


def create_notification_config(
    actor: Actor,
    name: str | None,
    chat_id: str,
    channel: NotificationChannelChoices = NotificationChannelChoices.TELEGRAM,
) -> NotificationConfigDTO:
    """Create a new notification configuration.

    Args:
        actor: The actor performing the command
        name: The display name for the configuration (will be converted to empty string if None)
        chat_id: The Telegram chat ID
        channel: The notification channel (defaults to Telegram)

    Returns:
        A NotificationConfigDTO containing the created notification configuration data
    """
    name = name or ""

    config = NotificationConfig.objects.create(
        name=name,
        channel=channel,
        chatid=chat_id,
        owner_id=actor.user_id,
    )

    return NotificationConfigDTO(
        id=config.id,
        name=config.name,
        channel=config.channel,
        chat_id=config.chatid,
    )
