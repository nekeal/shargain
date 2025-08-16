from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationConfigDTO:
    id: int
    name: str | None
    channel: str
    chat_id: str | None
