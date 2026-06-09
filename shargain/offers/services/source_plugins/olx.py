from collections.abc import Mapping
from typing import Any

from shargain.offers.services.geo_utils import haversine
from shargain.offers.services.source_plugins.contracts import (
    LegacyUrlNotificationSettings,
    NotificationLine,
    SourceNotificationDetails,
)


class OlxSourcePlugin:
    id = "olx"
    display_name = "OLX"

    def build_notification_details(
        self,
        metadata: Mapping[str, Any],
        settings: LegacyUrlNotificationSettings,
    ) -> SourceNotificationDetails:
        if not settings.show_location_details:
            return SourceNotificationDetails(lines=[])

        lines: list[NotificationLine] = []
        extra = metadata.get("extra", {})
        if not isinstance(extra, dict):
            return SourceNotificationDetails(lines=[])

        coords = self._get_coordinates(extra)
        location_name = self._get_location_name(extra)
        is_exact = self._is_location_exact(extra)

        if coords:
            icon = "📍" if is_exact else "🗺️"
            lines.append(f"{icon} https://maps.google.com/?q={coords[0]},{coords[1]}")

            if settings.waypoints:
                for wp in settings.waypoints:
                    distance = haversine(coords[0], coords[1], wp["lat"], wp["lon"])
                    if distance < 1:
                        lines.append(f"📏 {int(distance * 1000)} m from {wp['name']}")
                    else:
                        lines.append(f"📏 {distance:.1f} km from {wp['name']}")

        if location_name:
            lines.append(f"🏙️ {location_name}")

        return SourceNotificationDetails(lines=lines)

    @staticmethod
    def _get_coordinates(extra: dict) -> tuple[float, float] | None:
        map_data = extra.get("map")
        if not isinstance(map_data, dict):
            return None
        lat = map_data.get("lat")
        lon = map_data.get("lon")
        if lat is not None and lon is not None:
            return (lat, lon)
        return None

    @staticmethod
    def _get_location_name(extra: dict) -> str | None:
        location_data = extra.get("location")
        if not isinstance(location_data, dict):
            return None
        city = location_data.get("cityName")
        district = location_data.get("districtName")
        if city and district:
            return f"{city}, {district}"
        return city or district or None

    @staticmethod
    def _is_location_exact(extra: dict) -> bool:
        map_data = extra.get("map")
        if not isinstance(map_data, dict):
            return False
        return bool(map_data.get("show_detailed", False))
