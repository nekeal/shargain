import logging

from django.db.models import QuerySet
from django.utils.translation import gettext as _

from shargain.notifications.models import NotificationConfig
from shargain.offers.models import ScrapingUrl, ScrappingTarget

from .base import HandlerResult
from .list_scraping_links_handler import ListScrapingLinksHandler

logger = logging.getLogger(__name__)


class DeleteScrapingLinkHandler:
    @staticmethod
    def handle(chat_id: int, index: int) -> HandlerResult:
        if not (notification_config := NotificationConfig.objects.filter(chatid=chat_id).first()):
            logger.info("Notification config does not exist [chat_id=%s]", chat_id)
            return HandlerResult.as_failure(_("You need to configure notifications first. Use /configure command"))

        if not (scraping_target := ScrappingTarget.objects.filter(notification_config=notification_config).first()):
            return HandlerResult.as_failure(
                _("You haven't configured this chat yet (use /configure command or contact administrator)")
            )

        scraping_urls = ListScrapingLinksHandler.get_scraping_urls(scraping_target)
        return DeleteScrapingLinkHandler.delete_scraping_url_by_index(scraping_urls, index)

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
