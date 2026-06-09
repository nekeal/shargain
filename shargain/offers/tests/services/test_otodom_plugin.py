from shargain.offers.services.source_plugins.contracts import LegacyUrlNotificationSettings
from shargain.offers.services.source_plugins.otodom import OtodomSourcePlugin


class TestOtodomPluginAddress:
    def test_city_and_street_location_name(self) -> None:
        plugin = OtodomSourcePlugin()
        metadata = {
            "extra": {
                "location": {
                    "address": {
                        "city": {"name": "Kraków"},
                        "street": {"name": "ul. Jana Dekerta"},
                    },
                },
            },
        }
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert "🏙️ Kraków, ul. Jana Dekerta" in result.lines

    def test_google_maps_search_url(self) -> None:
        plugin = OtodomSourcePlugin()
        metadata = {
            "extra": {
                "location": {
                    "address": {
                        "city": {"name": "Kraków"},
                        "street": {"name": "ul. Jana Dekerta"},
                    },
                },
            },
        }
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert any("maps.google.com/?q=Krak%C3%B3w%2C%20ul.%20Jana%20Dekerta" in line for line in result.lines)

    def test_city_only_location_name(self) -> None:
        plugin = OtodomSourcePlugin()
        metadata = {
            "extra": {
                "location": {
                    "address": {
                        "city": {"name": "Warsaw"},
                    },
                },
            },
        }
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert "🏙️ Warsaw" in result.lines
        assert any("maps.google.com/?q=Warsaw" in line for line in result.lines)


class TestOtodomPluginEdgeCases:
    def test_malformed_metadata_returns_empty_lines(self) -> None:
        plugin = OtodomSourcePlugin()
        metadata = {"extra": {"location": None}}
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert result.lines == []

    def test_empty_metadata_returns_empty_lines(self) -> None:
        plugin = OtodomSourcePlugin()
        metadata: dict = {}
        settings = LegacyUrlNotificationSettings(show_location_details=True)

        result = plugin.build_notification_details(metadata, settings)

        assert result.lines == []


class TestOtodomPluginWaypoints:
    def test_no_distance_lines_with_waypoints(self) -> None:
        plugin = OtodomSourcePlugin()
        metadata = {
            "extra": {
                "location": {
                    "address": {
                        "city": {"name": "Kraków"},
                    },
                },
            },
        }
        settings = LegacyUrlNotificationSettings(
            show_location_details=True,
            waypoints=[
                {"name": "Home", "lat": 52.2370, "lon": 21.0170},
            ],
        )

        result = plugin.build_notification_details(metadata, settings)

        assert not any("📏" in line for line in result.lines)
