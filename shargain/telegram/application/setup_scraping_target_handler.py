import logging
import re
from functools import cached_property

from django.db import transaction
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

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
    ) -> tuple[NotificationConfig, ScrappingTarget | None]:
        """Create notification config and a new scraping target.

        Returns:
            Tuple of (notification_config, scraping_target)
        """
        notification_config, _ = NotificationConfig.objects.get_or_create(
            channel=NotificationChannelChoices.TELEGRAM,
            chatid=chat_id,
            owner=register_token.user,
            defaults={
                "name": register_token.name or f"Telegram-{chat_id}",
            },
        )

        # Link to the notification config
        if len(existing_scraping_targets := ScrappingTarget.objects.filter(owner=register_token.user)) == 1:
            existing_scraping_targets[0].notification_config = (
                existing_scraping_targets[0].notification_config or notification_config
            )
            existing_scraping_targets[0].save(update_fields=["notification_config"])
            return notification_config, existing_scraping_targets[0]

        # if user have no scraping targets, or multiple scraping targets, create a new one
        scraping_target = ScrappingTarget.objects.create(
            name=f"Target-{chat_id}",
            notification_config=notification_config,
            owner=register_token.user,
        )
        return notification_config, scraping_target

    def handle(self, chat_id: str, token_str: str) -> HandlerResult:
        with transaction.atomic():
            # Get the token if it exists and is not used
            token_qs = TelegramRegisterToken.objects.select_for_update().filter(is_used=False, register_token=token_str)
            if not (token := token_qs.first()):
                logger.info("Token is invalid or already used [token=%s]", token_str)
                return HandlerResult.as_failure("This token is invalid or already used")

            # Mark token as used
            token_qs.update(is_used=True)

            # Create or update Telegram user
            TelegramUser.objects.get_or_create(
                user=token.user,
                telegram_id=chat_id,
                defaults={"is_active": True},
            )

            # Create the notification config and a new scraping target
            notification_config, scraping_target = self.create_objects(chat_id, token)

            logger.info(
                "New target and notification config created [target_id=%s] [chat_id=%s] [config_id=%s]",
                scraping_target.id if scraping_target else "N/A",
                chat_id,
                notification_config.id,
            )
            message = _("Notifications configured successfully. Now you can use Shargain. See /menu for more info")

        return HandlerResult.as_success(str(message))

    def handle_invalid_format(self, chat_id: str) -> HandlerResult:
        logger.info(
            "Invalid format of message [chat_id=%s] [message=%s]",
            chat_id,
        )
        return HandlerResult.as_failure("Invalid format of message. Please use /configure <token> format")
