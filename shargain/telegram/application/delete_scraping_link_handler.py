import logging
import re

from django.db.models import QuerySet
from django.utils.translation import gettext as _

from shargain.notifications.models import NotificationConfig
from shargain.offers.models import ScrapingUrl, ScrappingTarget

from .base import BaseTelegramHandler, HandlerResult
from .list_scraping_links_handler import ListScrapingLinksHandler

logger = logging.getLogger(__name__)


class DeleteScrapingLinkHandler(BaseTelegramHandler):
    command_regex = re.compile(r"^/delete (?P<index>\d+)$")

    @property
    def index(self) -> int:
        """
        Index of scraping url to delete. Indexes start from 1 from user perspective but from 0 in the code.
        """
        return int(self._regex_match.group("index")) - 1  # type: ignore

    @staticmethod
    def delete_scraping_url_by_index(scraping_urls: QuerySet[ScrapingUrl], index: int) -> HandlerResult:
        if index >= scraping_urls.count():
            return HandlerResult.as_failure(_("Scraping url with this index does not exist. Check /list command"))

        list_scraping_urls = list(scraping_urls)
        scraping_urls[index].delete()
        list_scraping_urls.pop(index)

        if not list_scraping_urls:
            return HandlerResult.as_success(_("Link deleted. No more links to display."))

        result = _("Link deleted. Remaining links:\n\n")
        for i, url in enumerate(list_scraping_urls, 1):
            name_segment = f" ({url.name})" if url.name else ""
            result += f"{i}. {name_segment}: {url.url}\n"
        return HandlerResult.as_success(result)

    def handle(self) -> HandlerResult:
        if not (notification_config := NotificationConfig.objects.filter(chatid=self.chat_id).first()):
            logger.info("Notification config does not exist [chat_id=%s]", self.chat_id)
            return HandlerResult.as_failure(_("You need to configure notifications first. Use /configure command"))

        if not (scraping_target := ScrappingTarget.objects.filter(notification_config=notification_config).first()):
            return HandlerResult.as_failure(
                _("You haven't configured this chat yet (use /configure command or contact administrator)")
            )

        scraping_urls = ListScrapingLinksHandler.get_scraping_urls(scraping_target)
        return self.delete_scraping_url_by_index(scraping_urls, self.index)

    def handle_invalid_format(self) -> HandlerResult:
        return HandlerResult.as_failure(
            _(
                "Invalid format of message. Please use /delete <number> format."
                " Where number is a number of link from /list command"
            )
        )
