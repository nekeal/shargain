from collections.abc import Mapping
from typing import Any

from shargain.offers.services.source_plugins.contracts import (
    LegacyUrlNotificationSettings,
    SourceNotificationDetails,
)


class FallbackSourcePlugin:
    id = "fallback"
    display_name = "Fallback"

    def build_notification_details(
        self,
        metadata: Mapping[str, Any],
        settings: LegacyUrlNotificationSettings,
    ) -> SourceNotificationDetails:
        return SourceNotificationDetails(lines=[])
