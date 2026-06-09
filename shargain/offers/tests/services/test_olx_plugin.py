from shargain.offers.services.source_plugins.contracts import LegacyUrlNotificationSettings
from shargain.offers.services.source_plugins.olx import OlxSourcePlugin


class TestOlxPluginCoordinates:
    def test_map_link_line_with_exact_coordinates(self) -> None:
        plugin = OlxSourcePlugin()
        metadata = {
            "extra": {
                "map": {"lat": 52.2297, "lon": 21.0122, "show_detailed": True},
                "location": {"cityName": "Warsaw", "districtName": "Śródmieście"},
            },
        }
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert "📍 https://maps.google.com/?q=52.2297,21.0122" in result.lines


class TestOlxPluginWaypoints:
    def test_distance_lines_with_waypoints(self) -> None:
        plugin = OlxSourcePlugin()
        metadata = {
            "extra": {
                "map": {"lat": 52.2297, "lon": 21.0122, "show_detailed": True},
            },
        }
        settings = LegacyUrlNotificationSettings(
            show_location_details=True,
            waypoints=[
                {"name": "Home", "lat": 52.2370, "lon": 21.0170},
                {"name": "Office", "lat": 52.2200, "lon": 21.0100},
            ],
        )

        result = plugin.build_notification_details(metadata, settings)

        assert any("📏" in line and "Home" in line for line in result.lines)
        assert any("📏" in line and "Office" in line for line in result.lines)


class TestOlxPluginApproximate:
    def test_approximate_coordinates_icon(self) -> None:
        plugin = OlxSourcePlugin()
        metadata = {
            "extra": {
                "map": {"lat": 52.2297, "lon": 21.0122, "show_detailed": False},
                "location": {"cityName": "Warsaw", "districtName": "Śródmieście"},
            },
        }
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert "🗺️ https://maps.google.com/?q=52.2297,21.0122" in result.lines


class TestOlxPluginLocationName:
    def test_city_and_district_location_name(self) -> None:
        plugin = OlxSourcePlugin()
        metadata = {
            "extra": {
                "location": {"cityName": "Warsaw", "districtName": "Śródmieście"},
            },
        }
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert "🏙️ Warsaw, Śródmieście" in result.lines

    def test_city_only_location_name(self) -> None:
        plugin = OlxSourcePlugin()
        metadata = {
            "extra": {
                "location": {"cityName": "Warsaw"},
            },
        }
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert "🏙️ Warsaw" in result.lines


class TestOlxPluginEdgeCases:
    def test_malformed_metadata_returns_empty_lines(self) -> None:
        plugin = OlxSourcePlugin()
        metadata = {"extra": {"map": None, "location": None}}
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert result.lines == []

    def test_empty_metadata_returns_empty_lines(self) -> None:
        plugin = OlxSourcePlugin()
        metadata: dict = {}
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert result.lines == []

    def test_show_location_details_false_returns_empty_lines(self) -> None:
        plugin = OlxSourcePlugin()
        metadata = {
            "extra": {
                "map": {"lat": 52.2297, "lon": 21.0122, "show_detailed": True},
                "location": {"cityName": "Warsaw", "districtName": "Śródmieście"},
            },
        }
        settings = LegacyUrlNotificationSettings(show_location_details=False)

        result = plugin.build_notification_details(metadata, settings)

        assert result.lines == []
