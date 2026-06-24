from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from shargain.offers.application.dto import WaypointData

NotificationLine = str


class SourceUrlMatcher(Protocol):
    def matches(self, url: str) -> bool: ...


@dataclass(frozen=True)
class SourceNotificationDetails:
    lines: list[NotificationLine] = field(default_factory=list)


@dataclass(frozen=True)
class LegacyUrlNotificationSettings:
    show_location_details: bool = True
    waypoints: list[WaypointData] | None = None


class SourcePlugin(Protocol):
    id: str
    display_name: str

    def build_notification_details(
        self,
        metadata: Mapping[str, Any],
        settings: LegacyUrlNotificationSettings,
    ) -> SourceNotificationDetails: ...
