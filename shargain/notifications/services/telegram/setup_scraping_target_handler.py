import logging
import re
from functools import cached_property

from django.db.models import Q
from django.utils.text import slugify

from shargain.accounts.models import RegisterToken
from shargain.notifications.models import NotificationChannelChoices, NotificationConfig
from shargain.offers.models import ScrappingTarget

from .base import BaseTelegramHandler, HandlerResult

logger = logging.getLogger(__name__)


class SetupScrapingTargetHandler(BaseTelegramHandler):
    command_regex = re.compile(r"^/configure (?P<token>\w+)$")

    @cached_property
    def token(self) -> str:
        return self._regex_match.group("token")  # type: ignore

    @staticmethod
    def get_notification_config_name(register_token: RegisterToken) -> str:
        return slugify(register_token.description)

    @staticmethod
    def get_scraping_target_name(register_token: RegisterToken) -> str:
        return slugify(register_token.description)

    def create_objects(self, register_token: RegisterToken) -> tuple[NotificationConfig, ScrappingTarget]:
        notification_config = NotificationConfig.objects.create(
            name=self.get_notification_config_name(register_token),
            channel=NotificationChannelChoices.TELEGRAM,
            chatid=self.chat_id,
        )
        scraping_target = ScrappingTarget.objects.create(
            name=self.get_scraping_target_name(register_token),
            notification_config=notification_config,
        )
        return notification_config, scraping_target

    def handle(self) -> HandlerResult:
        token_qs = RegisterToken.objects.filter(already_used=False, token=self.token)
        if not (token := token_qs.first()):
            logger.info("Token is invalid or already used [token=%s]", self.token)
            return HandlerResult.as_failure("This token is invalid or already used")
        token_qs.update(already_used=True)

        if (
            NotificationConfig.objects.filter(
                Q(name=self.get_notification_config_name(token)) | Q(chatid=self.chat_id)
            ).exists()
            or ScrappingTarget.objects.filter(name=self.get_scraping_target_name(token)).exists()
        ):
            logger.info(
                "Target already exists [target_name=%s] [chat_id=%s]",
                self.get_scraping_target_name(token),
                self.chat_id,
            )
            return HandlerResult.as_failure(
                "This name is already taken or notifications are already configured for this chat"
            )

        self.create_objects(token)
        logger.info(
            "Target created [target_name=%s] [chat_id=%s]",
            self.get_scraping_target_name(token),
            self.chat_id,
        )
        return HandlerResult.as_success(
            "Notifications configured successfully. Now you can add links to track using /add command"
        )

    def handle_invalid_format(self) -> HandlerResult:
        logger.info(
            "Invalid format of message [chat_id=%s] [message=%s]",
            self.chat_id,
            self.message.text,
        )
        return HandlerResult.as_failure("Invalid format of message. Please use /configure <token> format")
