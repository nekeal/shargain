import logging

from shargain.notifications.models import NotificationConfig
from shargain.offers.models import ScrapingUrl, ScrappingTarget

from .base import HandlerResult

logger = logging.getLogger(__name__)


class AddScrapingLinkHandler:
    @staticmethod
    def handle(chat_id: int, url: str, name: str) -> HandlerResult:
        if not (notification_config := NotificationConfig.objects.filter(chatid=chat_id).first()):
            logger.info("Notification config does not exist [chat_id=%s]", chat_id)
            return HandlerResult.as_failure("You need to configure notifications first. Use /configure command")
        if not (scraping_target := ScrappingTarget.objects.filter(notification_config=notification_config).first()):
            return HandlerResult.as_failure(
                "You haven't configured this chat yet (use /configure command or contact administrator)"
            )
        ScrapingUrl.objects.create(url=url, scraping_target=scraping_target, name=name)
        return HandlerResult.as_success("Link added successfully. You will be notified about new offers soon")
