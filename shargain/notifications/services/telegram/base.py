import abc
import re
from typing import TypeGuard

from telebot.types import Message


class BaseTelegramHandler(abc.ABC):
    command_regex: re.Pattern

    def __init__(self, message: Message):
        self.message = message
        self._regex_match: re.Match = self.command_regex.match(self.message.text)  # type: ignore

    @classmethod
    def command_is_valid(cls, command_match: re.Match | None) -> TypeGuard[re.Match]:
        return bool(command_match)

    def dispatch(self) -> str:
        if self.command_is_valid(self._regex_match):
            return self.handle()
        return self.handle_invalid_format()

    @property
    def chat_id(self):
        return self.message.chat.id

    @property
    def text(self) -> str:
        return self.message.text or ""

    @abc.abstractmethod
    def handle(self) -> str:
        pass

    @abc.abstractmethod
    def handle_invalid_format(self) -> str:
        pass
