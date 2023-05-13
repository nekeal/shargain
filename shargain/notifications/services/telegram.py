import abc
import logging
import re
from dataclasses import dataclass
from functools import cached_property
from typing import Iterable, TypeGuard

from django.core.validators import URLValidator
from django.db.models import Q, QuerySet
from django.utils.translation import gettext as _
from telebot.types import Message
from typing_extensions import reveal_type

from shargain.accounts.models import RegisterToken
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig
from shargain.offers.models import ScrapingUrl, ScrappingTarget

logger = logging.getLogger(__name__)


@dataclass
class TelegramActionResult:
    success: bool
    message: str


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

    @abc.abstractmethod
    def handle(self):
        pass

    @abc.abstractmethod
    def handle_invalid_format(self):
        pass


class SetupScrapingTargetWithNotificationsHandler(BaseTelegramHandler):
    command_regex = re.compile(r"^/configure (?P<token>\w+) (?P<name>[\w\-_\s]+)$")

    @cached_property
    def target_name(self) -> str:
        return self._regex_match.group("name")

    @cached_property
    def token(self) -> str:
        return self._regex_match.group("token")

    def create_objects(self) -> tuple[NotificationConfig, ScrappingTarget]:
        notification_config = NotificationConfig.objects.create(
            name=self.target_name,
            channel=NotificationChannelChoices.TELEGRAM,
            chatid=self.chat_id,
        )
        scraping_target = ScrappingTarget.objects.create(
            name=self.target_name,
            enable_notifications=True,
            is_active=True,
            notification_config=notification_config,
        )
        return notification_config, scraping_target

    def handle(self) -> str:
        if (
            RegisterToken.objects.filter(already_used=False, token=self.token).update(
                already_used=True
            )
            == 0
        ):
            logger.info("Token is invalid or already used [token=%s]", self.token)
            return _("This token is invalid or already used")
        if (
            NotificationConfig.objects.filter(
                Q(name=self.target_name) | Q(chatid=self.message.chat.id)
            ).exists()
            or ScrappingTarget.objects.filter(name=self.target_name).exists()
        ):
            logger.info(
                "Target already exists [target_name=%s] [chat_id=%s]",
                self.target_name,
                self.chat_id,
            )
            return _(
                "This name is already taken or notifications"
                " are already configured for this chat"
            )
        self.create_objects()
        logger.info(
            "Target created [target_name=%s] [chat_id=%s]",
            self.target_name,
            self.chat_id,
        )
        return _(
            "Notifications configured successfully. Now you can add links to track using /add command"
        )

    def handle_invalid_format(self) -> str:
        logger.info(
            "Invalid format of message [chat_id=%s] [message=%s]",
            self.chat_id,
            self.message.text,
        )
        return _(
            "Invalid format of message. Please use /configure <token> <name> format"
        )


class AddScrapingLinkHandler(BaseTelegramHandler):
    command_regex = re.compile(r"^/add (?P<url>\S+)\s?(?P<name>[\w+\-_\s]+)?$")

    @cached_property
    def url(self):
        return self._regex_match.group("url")

    @cached_property
    def name(self) -> str:
        if self._regex_match.group("name"):
            return self._regex_match.group("name").strip()
        return ""

    @classmethod
    def command_is_valid(cls, command_match: re.Match | None) -> TypeGuard[re.Match]:
        if not super().command_is_valid(command_match):
            return False
        if not URLValidator.regex.match(command_match.group("url")):  # type: ignore
            return False
        return True

    def handle(self):
        if not (
            notification_config := NotificationConfig.objects.filter(
                chatid=self.chat_id
            ).first()
        ):
            logger.info("Notification config does not exist [chat_id=%s]", self.chat_id)
            return _(
                "You need to configure notifications first. Use /configure command"
            )
        if not (
            scraping_target := ScrappingTarget.objects.get(
                notification_config=notification_config
            )
        ):
            return _(
                "You haven't configured this chat yet (use /configure command or contact administrator)"
            )
        ScrapingUrl.objects.create(
            url=self.url, scraping_target=scraping_target, name=self.name
        )
        return _("Link added successfully. You will be notified about new offers soon")

    def handle_invalid_format(self):
        logger.info(
            "Invalid format of message [chat_id=%s] [message=%s]",
            self.chat_id,
            self.message.text,
        )
        return _("Invalid format of message. Please use /add <url> [name] format")


class ListScrapingLinksHandler(BaseTelegramHandler):
    command_regex = re.compile(r"^/list$")

    @staticmethod
    def get_scraping_urls(scraping_target: ScrappingTarget):
        return scraping_target.scrapingurl_set.order_by("id")

    @staticmethod
    def format_output(scraping_urls: Iterable[ScrapingUrl]) -> str:
        result = ""
        for i, scraping_url in enumerate(scraping_urls, 1):
            name_segment = f" ({scraping_url.name}): " if scraping_url.name else ""
            result += f"{i}. {name_segment}{scraping_url.url}\n"
        return result or _("You don't have any added links yet")

    def handle(self):
        if not (
            notification_config := NotificationConfig.objects.filter(
                chatid=self.chat_id
            ).first()
        ):
            logger.info("Notification config does not exist [chat_id=%s]", self.chat_id)
            return _(
                "You need to configure notifications first. Use /configure command"
            )
        if not (
            scraping_target := ScrappingTarget.objects.filter(
                notification_config=notification_config
            ).first()
        ):
            return _(
                "You haven't configured this chat yet (use /configure command or contact administrator)"
            )
        scraping_urls = self.get_scraping_urls(scraping_target)
        if not scraping_urls:
            return _("You don't have any added links yet")
        return self.format_output(scraping_urls)

    def handle_invalid_format(self):
        return _("Invalid format of message. Please use /list format")


class DeleteScrapingLinkHandler(BaseTelegramHandler):
    command_regex = re.compile(r"^/delete (?P<index>\d+)$")

    @property
    def index(self) -> int:
        """
        Index of scraping url to delete. Indexes start from 1 from user perspective but from 0 in the code.
        """
        return int(self._regex_match.group("index")) - 1

    @staticmethod
    def delete_scraping_url_by_index(
        scraping_urls: QuerySet[ScrapingUrl], index: int
    ) -> TelegramActionResult:
        if index >= scraping_urls.count():
            return TelegramActionResult(
                success=False,
                message=_(
                    "Scraping url with this index does not exist. Check /list command"
                ),
            )
        list_scraping_urls = list(scraping_urls)
        scraping_urls[index].delete()
        list_scraping_urls.pop(index)
        return TelegramActionResult(
            success=True,
            message=ListScrapingLinksHandler.format_output(list_scraping_urls),
        )

    def handle(self):
        if not (
            notification_config := NotificationConfig.objects.filter(
                chatid=self.chat_id
            ).first()
        ):
            logger.info("Notification config does not exist [chat_id=%s]", self.chat_id)
            return _(
                "You need to configure notifications first. Use /configure command"
            )
        if not (
            scraping_target := ScrappingTarget.objects.filter(
                notification_config=notification_config
            ).first()
        ):
            return _(
                "You haven't configured this chat yet (use /configure command or contact administrator)"
            )
        result = self.delete_scraping_url_by_index(
            ListScrapingLinksHandler.get_scraping_urls(scraping_target), self.index
        )
        return result.message

    def handle_invalid_format(self):
        return _(
            "Invalid format of message. Please use /delete <number> format."
            " Where number is a number of link from /list command"
        )
