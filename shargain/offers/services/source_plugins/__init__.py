from shargain.offers.services.source_plugins.contracts import (
    LegacyUrlNotificationSettings,
    NotificationLine,
    SourceNotificationDetails,
    SourcePlugin,
    SourceUrlMatcher,
)
from shargain.offers.services.source_plugins.fallback import FallbackSourcePlugin
from shargain.offers.services.source_plugins.matchers import DomainMatcher
from shargain.offers.services.source_plugins.olx import OlxSourcePlugin
from shargain.offers.services.source_plugins.otodom import OtodomSourcePlugin
from shargain.offers.services.source_plugins.registry import register, select_plugin

register(olx := OlxSourcePlugin(), DomainMatcher("olx.pl"))
register(otodom := OtodomSourcePlugin(), DomainMatcher("otodom.pl"))

__all__ = [
    "DomainMatcher",
    "FallbackSourcePlugin",
    "LegacyUrlNotificationSettings",
    "NotificationLine",
    "OlxSourcePlugin",
    "OtodomSourcePlugin",
    "SourceNotificationDetails",
    "SourcePlugin",
    "SourceUrlMatcher",
    "olx",
    "otodom",
    "register",
    "select_plugin",
]
