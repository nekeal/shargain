from django.test import TestCase

from shargain.offers.models import Offer, ScrapingUrl
from shargain.offers.services.source_plugins.builder import SourceNotificationContextBuilder


class TestBuilderShowLocationDisabled(TestCase):
    def test_no_extra_lines_when_show_location_details_false(self) -> None:
        builder = SourceNotificationContextBuilder()
        offers = [
            self._make_offer(
                url="https://www.olx.pl/oferta/test",
                metadata={"extra": {"map": {"lat": 52.0, "lon": 21.0, "show_detailed": True}}},
            ),
        ]
        scraping_url = self._make_scraping_url(
            url="https://www.olx.pl/oferta/test",
            show_location=False,
        )

        contexts = builder.build_contexts(offers, scraping_url)

        assert len(contexts) == 1
        assert contexts[0].extra_lines == []

    @staticmethod
    def _make_offer(url: str, metadata: dict | None = None) -> "Offer":
        from unittest.mock import MagicMock

        offer = MagicMock(spec=Offer)
        offer.url = url
        offer.metadata = metadata or {}
        offer.domain = "olx.pl"
        offer.title = "Test Offer"
        offer.price = 100
        return offer

    @staticmethod
    def _make_scraping_url(url: str, show_location: bool = True) -> "ScrapingUrl":
        from unittest.mock import MagicMock

        su = MagicMock(spec=ScrapingUrl)
        su.url = url
        su.show_location_map_in_notifications = show_location
        su.waypoints = None
        return su


class TestBuilderWithOlx(TestCase):
    def test_olx_plugin_lines_appear_as_extra_lines(self) -> None:
        builder = SourceNotificationContextBuilder()
        offers = [
            self._make_offer(
                url="https://www.olx.pl/oferta/test",
                metadata={
                    "extra": {
                        "map": {"lat": 52.2297, "lon": 21.0122, "show_detailed": True},
                        "location": {"cityName": "Warsaw", "districtName": "Śródmieście"},
                    },
                },
            ),
        ]
        scraping_url = self._make_scraping_url(url="https://www.olx.pl/oferta/test")

        contexts = builder.build_contexts(offers, scraping_url)

        assert len(contexts) == 1
        lines = contexts[0].extra_lines
        assert "📍 https://maps.google.com/?q=52.2297,21.0122" in lines
        assert "🏙️ Warsaw, Śródmieście" in lines

    def test_olx_with_waypoints_includes_distance_lines(self) -> None:
        builder = SourceNotificationContextBuilder()
        offers = [
            self._make_offer(
                url="https://www.olx.pl/oferta/test",
                metadata={
                    "extra": {
                        "map": {"lat": 52.2297, "lon": 21.0122, "show_detailed": True},
                    },
                },
            ),
        ]
        scraping_url = self._make_scraping_url(
            url="https://www.olx.pl/oferta/test",
            waypoints=[{"name": "Home", "lat": 52.2370, "lon": 21.0170}],
        )

        contexts = builder.build_contexts(offers, scraping_url)

        assert len(contexts) == 1
        lines = contexts[0].extra_lines
        assert any("📏" in line and "Home" in line for line in lines)

    @staticmethod
    def _make_offer(url: str, metadata: dict | None = None) -> "Offer":
        from unittest.mock import MagicMock

        offer = MagicMock(spec=Offer)
        offer.url = url
        offer.metadata = metadata or {}
        offer.domain = "olx.pl"
        offer.title = "Test Offer"
        offer.price = 100
        return offer

    @staticmethod
    def _make_scraping_url(url: str, show_location: bool = True, waypoints: list | None = None) -> "ScrapingUrl":
        from unittest.mock import MagicMock

        su = MagicMock(spec=ScrapingUrl)
        su.url = url
        su.show_location_map_in_notifications = show_location
        su.waypoints = waypoints
        return su


class TestBuilderWithOtodom(TestCase):
    def test_otodom_lines_with_waypoints_no_distances(self) -> None:
        builder = SourceNotificationContextBuilder()
        offers = [
            self._make_offer(
                url="https://www.otodom.pl/oferta/test",
                metadata={
                    "extra": {
                        "location": {
                            "address": {
                                "city": {"name": "Kraków"},
                                "street": {"name": "ul. Jana Dekerta"},
                            },
                        },
                    },
                },
            ),
        ]
        scraping_url = self._make_scraping_url(
            url="https://www.otodom.pl/oferta/test",
            waypoints=[{"name": "Home", "lat": 52.2370, "lon": 21.0170}],
        )

        contexts = builder.build_contexts(offers, scraping_url)

        assert len(contexts) == 1
        lines = contexts[0].extra_lines
        assert "🏙️ Kraków, ul. Jana Dekerta" in lines
        assert not any("📏" in line for line in lines)

    @staticmethod
    def _make_offer(url: str, metadata: dict | None = None) -> "Offer":
        from unittest.mock import MagicMock

        offer = MagicMock(spec=Offer)
        offer.url = url
        offer.metadata = metadata or {}
        offer.domain = "otodom.pl"
        offer.title = "Test Offer"
        offer.price = 100
        return offer

    @staticmethod
    def _make_scraping_url(url: str, show_location: bool = True, waypoints: list | None = None) -> "ScrapingUrl":
        from unittest.mock import MagicMock

        su = MagicMock(spec=ScrapingUrl)
        su.url = url
        su.show_location_map_in_notifications = show_location
        su.waypoints = waypoints
        return su
