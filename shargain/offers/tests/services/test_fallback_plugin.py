from shargain.offers.services.source_plugins.contracts import LegacyUrlNotificationSettings
from shargain.offers.services.source_plugins.fallback import FallbackSourcePlugin


class TestFallbackPlugin:
    def test_returns_no_lines_regardless_of_input(self) -> None:
        plugin = FallbackSourcePlugin()
        metadata = {"extra": {"map": {"lat": 52.0, "lon": 21.0}}}
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert result.lines == []

    def test_returns_no_lines_with_empty_metadata(self) -> None:
        plugin = FallbackSourcePlugin()
        metadata: dict = {}
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert result.lines == []

    def test_returns_no_lines_with_waypoints(self) -> None:
        plugin = FallbackSourcePlugin()
        metadata = {"extra": {"map": {"lat": 52.0, "lon": 21.0}}}
        settings = LegacyUrlNotificationSettings(
            show_location_details=True,
            waypoints=[{"name": "Home", "lat": 52.2370, "lon": 21.0170}],
        )

        result = plugin.build_notification_details(metadata, settings)

        assert result.lines == []
