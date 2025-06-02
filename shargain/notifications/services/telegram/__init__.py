"""
Telegram bot handlers for the notifications service.

This package contains handlers for processing Telegram bot commands.
"""

from .add_scraping_link_handler import AddScrapingLinkHandler
from .base import BaseTelegramHandler
from .delete_scraping_link_handler import DeleteScrapingLinkHandler
from .list_scraping_links_handler import ListScrapingLinksHandler
from .setup_scraping_target_handler import SetupScrapingTargetHandler

__all__ = [
    "BaseTelegramHandler",
    "SetupScrapingTargetHandler",
    "AddScrapingLinkHandler",
    "ListScrapingLinksHandler",
    "DeleteScrapingLinkHandler",
]
