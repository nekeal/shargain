import logging
import re
from functools import cached_property

from django.db import transaction
from django.utils.text import slugify

from shargain.notifications.models import NotificationChannelChoices, NotificationConfig
from shargain.offers.models import ScrappingTarget
from shargain.telegram.models import TelegramRegisterToken, TelegramUser

from .base import HandlerResult

logger = logging.getLogger(__name__)


class SetupScrapingTargetHandler:
    command_regex = re.compile(r"^/configure (?P<token>\w+)$")

    @cached_property
    def token(self) -> str:
        return self._regex_match.group("token")  # type: ignore

    @staticmethod
    def get_notification_config_name(register_token: TelegramRegisterToken) -> str:
        return slugify(register_token.user.username)

    @staticmethod
    def get_scraping_target_name(register_token: TelegramRegisterToken) -> str:
        return slugify(register_token.user.username)

    def create_objects(
        self, chat_id: str, register_token: TelegramRegisterToken
    ) -> tuple[NotificationConfig, ScrappingTarget]:
        notification_config = NotificationConfig.objects.create(
            channel=NotificationChannelChoices.TELEGRAM,
            chatid=chat_id,
            owner=register_token.user,
        )
        scraping_target = ScrappingTarget.objects.create(
            notification_config=notification_config,
            owner=register_token.user,
        )
        return notification_config, scraping_target

    def handle(self, chat_id: str, token_str: str) -> HandlerResult:
        with transaction.atomic():
            token_qs = TelegramRegisterToken.objects.filter(is_used=False, register_token=token_str)
            if not (token := token_qs.first()):
                logger.info("Token is invalid or already used [token=%s]", token_str)
                return HandlerResult.as_failure("This token is invalid or already used")
            token_qs.update(is_used=True)

            TelegramUser.objects.get_or_create(
                user=token.user,
                telegram_id=chat_id,
                defaults={"is_active": True},
            )

            if (
                NotificationConfig.objects.filter(owner=token.user, chatid=chat_id).exists()
                or ScrappingTarget.objects.filter(owner=token.user).exists()
            ):
                logger.info(
                    "Target already exists [target_name=%s] [chat_id=%s]",
                    self.get_scraping_target_name(token),
                    chat_id,
                )
                return HandlerResult.as_failure(
                    "This name is already taken or notifications are already configured for this chat"
                )

            self.create_objects(chat_id, token)
            logger.info(
                "Target created [target_name=%s] [chat_id=%s]",
                self.get_scraping_target_name(token),
                chat_id,
            )
        return HandlerResult.as_success(
            "Notifications configured successfully. Now you can add links to track using /add command"
        )

    def handle_invalid_format(self, chat_id: str) -> HandlerResult:
        logger.info(
            "Invalid format of message [chat_id=%s] [message=%s]",
            chat_id,
        )
        return HandlerResult.as_failure("Invalid format of message. Please use /configure <token> format")
