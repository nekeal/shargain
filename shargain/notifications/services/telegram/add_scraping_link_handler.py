import logging
import re
from functools import cached_property
from typing import TypeGuard

from django.core.validators import URLValidator

from shargain.notifications.models import NotificationConfig
from shargain.offers.models import ScrapingUrl, ScrappingTarget

from .base import BaseTelegramHandler

logger = logging.getLogger(__name__)


class AddScrapingLinkHandler(BaseTelegramHandler):
    command_regex = re.compile(r"^/add (?P<url>\S+)\s?(?P<name>[\w+\-_\s]+)?$")

    @cached_property
    def url(self):
        return self._regex_match.group("url")  # type: ignore

    @cached_property
    def name(self) -> str:
        if self._regex_match.group("name"):  # type: ignore
            return self._regex_match.group("name").strip()  # type: ignore
        return ""

    @classmethod
    def command_is_valid(cls, command_match: re.Match | None) -> TypeGuard[re.Match]:
        if not super().command_is_valid(command_match):
            return False
        if not URLValidator.regex.match(command_match.group("url")):  # type: ignore
            return False
        return True

    def handle(self):
        if not (notification_config := NotificationConfig.objects.filter(chatid=self.chat_id).first()):
            logger.info("Notification config does not exist [chat_id=%s]", self.chat_id)
            return "You need to configure notifications first. Use /configure command"
        if not (scraping_target := ScrappingTarget.objects.get(notification_config=notification_config)):
            return "You haven't configured this chat yet (use /configure command or contact administrator)"
        ScrapingUrl.objects.create(url=self.url, scraping_target=scraping_target, name=self.name)
        return "Link added successfully. You will be notified about new offers soon"

    def handle_invalid_format(self):
        logger.info(
            "Invalid format of message [chat_id=%s] [message=%s]",
            self.chat_id,
            self.message.text,
        )
        return "Invalid format of message. Please use /add <url> [name] format"
