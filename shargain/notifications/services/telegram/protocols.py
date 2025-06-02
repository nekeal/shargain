from typing import Protocol


class MessageProtocol(Protocol):
    """Protocol defining the interface for message objects used by handlers."""

    @property
    def text(self) -> str | None:
        """The text content of the message."""
        ...

    @property
    def chat_id(self) -> int:
        """The chat ID where the message was sent."""
        ...

    @property
    def from_user(self) -> int:
        """The user who sent the message."""
        ...
