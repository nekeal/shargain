import dataclasses

from django.db.models import QuerySet

from shargain.notifications.application.actor import Actor
from shargain.notifications.application.dto import NotificationConfigDTO
from shargain.notifications.models import NotificationConfig


@dataclasses.dataclass
class ListNotificationConfigsDTO:
    configs: list[NotificationConfigDTO]


def list_notification_configs(actor: Actor) -> ListNotificationConfigsDTO:
    """List all notification configurations for an actor.

    Args:
        actor: The actor performing the query

    Returns:
        A ListNotificationConfigsDTO containing the notification configurations
    """
    configs: QuerySet[NotificationConfig] = NotificationConfig.objects.filter(owner_id=actor.user_id)

    config_dtos = [
        NotificationConfigDTO(
            id=config.id,
            name=config.name,
            channel=config.channel,
            chat_id=config.chatid,
        )
        for config in configs
    ]

    return ListNotificationConfigsDTO(configs=config_dtos)
