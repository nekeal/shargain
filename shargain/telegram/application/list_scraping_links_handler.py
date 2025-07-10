import logging
from collections.abc import Iterable

from django.db.models import QuerySet
from django.utils.translation import gettext as _

from shargain.notifications.models import NotificationConfig
from shargain.offers.models import ScrapingUrl, ScrappingTarget
from shargain.telegram.application.base import HandlerResult

logger = logging.getLogger(__name__)


class ListScrapingLinksHandler:
    @staticmethod
    def get_scraping_urls(scraping_target: ScrappingTarget) -> QuerySet[ScrapingUrl]:
        return scraping_target.scrapingurl_set.order_by("id")

    @classmethod
    def format_output(cls, scraping_urls: Iterable[ScrapingUrl]) -> str:
        if not scraping_urls:
            return _("📭 You don't have any added links yet")

        result = "<b>{header}</b>\n\n".format(header=_("Your Tracked Links"))

        for i, scraping_url in enumerate(scraping_urls, 1):
            name = scraping_url.name or _("Link {number}").format(number=i)
            result += f"{i}. <b>{name}</b> - 🔗 <a href='{scraping_url.url}'>{scraping_url.url}</a>\n"

        result += _("\n📝 Use /delete &lt;number&gt; to remove a link")
        return result

    def handle(self, chat_id: int) -> HandlerResult:
        """
        Handle the list command with given chat_id

        Args:
            chat_id: The chat ID to list scraping links for

        Returns:
            HandlerResult: Success or failure with appropriate message
        """
        if not (notification_config := NotificationConfig.objects.filter(chatid=chat_id).first()):
            logger.info("Notification config does not exist [chat_id=%s]", chat_id)
            return HandlerResult.as_failure(_("You need to configure notifications first. Use /configure command"))

        if not (scraping_target := ScrappingTarget.objects.filter(notification_config=notification_config).first()):
            return HandlerResult.as_failure(
                _("You haven't configured this chat yet (use /configure command or contact administrator)")
            )

        scraping_urls = self.get_scraping_urls(scraping_target)

        if not scraping_urls:
            return HandlerResult.as_success(_("You don't have any added links yet"))

        return HandlerResult.as_success(self.format_output(scraping_urls))
