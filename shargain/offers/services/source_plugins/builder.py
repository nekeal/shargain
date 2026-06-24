import logging

from shargain.notifications.services.notifications import NotificationMessageContext
from shargain.offers.models import Offer, ScrapingUrl
from shargain.offers.services.source_plugins import select_plugin
from shargain.offers.services.source_plugins.contracts import (
    LegacyUrlNotificationSettings,
    SourcePlugin,
)
from shargain.offers.services.source_plugins.registry import get_registrations

logger = logging.getLogger(__name__)


class SourceNotificationContextBuilder:
    def build_contexts(
        self,
        offers: list[Offer],
        scraping_url: ScrapingUrl | None,
    ) -> list:
        registrations = get_registrations()
        waypoints = scraping_url.waypoints if scraping_url else None
        show_location = scraping_url.show_location_map_in_notifications if scraping_url else False

        contexts: list = []
        for offer in offers:
            plugin = self._select_plugin_for_offer(offer, scraping_url, registrations)
            extra_lines: list[str] = []

            if plugin:
                settings = LegacyUrlNotificationSettings(
                    show_location_details=show_location,
                    waypoints=waypoints,
                )
                details = plugin.build_notification_details(offer.metadata, settings)
                extra_lines = list(details.lines)

            contexts.append(
                NotificationMessageContext(
                    offer=offer,
                    extra_lines=extra_lines,
                )
            )

        return contexts

    @staticmethod
    def _select_plugin_for_offer(
        offer: Offer,
        scraping_url: ScrapingUrl | None,
        registrations: list,
    ) -> SourcePlugin | None:
        candidate_urls = []
        if scraping_url:
            candidate_urls.append(scraping_url.url)
        if offer.url:
            candidate_urls.append(offer.url)

        for url in candidate_urls:
            plugin = select_plugin(url, registrations)
            if plugin is not None:
                return plugin

        return None
