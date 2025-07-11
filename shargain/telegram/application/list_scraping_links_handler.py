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

    def get_urls_by_chat_id(self, chat_id: int) -> Iterable[ScrapingUrl]:
        notification_config = NotificationConfig.objects.filter(chatid=chat_id).first()
        if not notification_config:
            return []

        scraping_target = ScrappingTarget.objects.filter(notification_config=notification_config).first()
        if not scraping_target:
            return []

        return self.get_scraping_urls(scraping_target)

    def handle(self, chat_id: int) -> HandlerResult:
        """
        Handle the list command with given chat_id

        Args:
            chat_id: The chat ID to list scraping links for

        Returns:
            HandlerResult: Success or failure with appropriate message
        """
        scraping_urls = self.get_urls_by_chat_id(chat_id)

        if not scraping_urls:
            return HandlerResult.as_success(_("You don't have any added links yet"))

        return HandlerResult.as_success(self.format_output(scraping_urls))
