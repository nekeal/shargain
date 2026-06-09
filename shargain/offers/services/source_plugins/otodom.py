from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from shargain.offers.services.source_plugins.contracts import (
    LegacyUrlNotificationSettings,
    NotificationLine,
    SourceNotificationDetails,
)


class OtodomSourcePlugin:
    id = "otodom"
    display_name = "Otodom"

    def build_notification_details(
        self,
        metadata: Mapping[str, Any],
        settings: LegacyUrlNotificationSettings,
    ) -> SourceNotificationDetails:
        if not settings.show_location_details:
            return SourceNotificationDetails(lines=[])

        extra = metadata.get("extra", {})
        if not isinstance(extra, dict):
            return SourceNotificationDetails(lines=[])

        try:
            address = extra["location"]["address"]
            city_name = address["city"]["name"]
        except (KeyError, TypeError):
            return SourceNotificationDetails(lines=[])

        lines: list[NotificationLine] = []

        if street_name := address.get("street", {}).get("name"):
            location_str = f"{city_name}, {street_name}"
        else:
            location_str = city_name

        lines.append(f"📍 https://maps.google.com/?q={quote(location_str)}")
        lines.append(f"🏙️ {location_str}")

        return SourceNotificationDetails(lines=lines)
