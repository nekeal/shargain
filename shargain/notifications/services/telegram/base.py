import abc
from dataclasses import dataclass
from re import Match, Pattern
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


@dataclass
class HandlerResult:
    success: bool
    message: str

    def __bool__(self) -> bool:
        return self.success

    @classmethod
    def as_success(cls, message: str) -> "HandlerResult":
        return cls(success=True, message=message)

    @classmethod
    def as_failure(cls, message: str) -> "HandlerResult":
        return cls(success=False, message=message)


class BaseTelegramHandler(abc.ABC):
    command_regex: Pattern[str]

    def __init__(self, message: MessageProtocol):
        self.message = message
        self._regex_match: Match[str] | None = None
        if self.message.text:
            self._regex_match = self.command_regex.match(self.message.text)

    @classmethod
    def command_is_valid(cls, command_match: Match[str] | None) -> bool:
        return bool(command_match)

    def dispatch(self) -> HandlerResult:
        if self.command_is_valid(self._regex_match):
            return self.handle()
        return self.handle_invalid_format()

    @property
    def chat_id(self) -> int:
        return self.message.chat_id

    @property
    def text(self) -> str:
        return self.message.text or ""

    @property
    def from_user_id(self) -> int:
        return self.message.from_user

    @abc.abstractmethod
    def handle(self) -> HandlerResult: ...

    def handle_invalid_format(self) -> HandlerResult:
        return HandlerResult.as_failure("Invalid command format.")
