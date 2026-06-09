from shargain.offers.services.source_plugins import (
    DomainMatcher,
    FallbackSourcePlugin,
    select_plugin,
)
from shargain.offers.services.source_plugins.registry import PluginRegistration, get_registrations


class TestPluginRegistration:
    def test_registration_holds_plugin_and_matcher(self) -> None:
        plugin = FallbackSourcePlugin()
        matcher = DomainMatcher("example.com")
        reg = PluginRegistration(plugin=plugin, matcher=matcher)
        assert reg.plugin is plugin
        assert reg.matcher is matcher


class TestRegistryOnImport:
    def test_registry_contains_olx_and_otodom_on_import(self) -> None:
        registrations = get_registrations()
        plugin_ids = {r.plugin.id for r in registrations}
        assert "olx" in plugin_ids
        assert "otodom" in plugin_ids

    def test_plugins_are_available_without_db_lookup(self) -> None:
        registrations = get_registrations()
        assert len(registrations) >= 2
        for reg in registrations:
            assert reg.plugin is not None
            assert reg.matcher is not None


class TestSelectPlugin:
    def test_selects_olx_plugin_for_olx_url(self) -> None:
        result = select_plugin("https://www.olx.pl/oferta/test", get_registrations())
        assert result is not None
        assert result.id == "olx"

    def test_selects_otodom_plugin_for_otodom_url(self) -> None:
        result = select_plugin("https://www.otodom.pl/oferta/test", get_registrations())
        assert result is not None
        assert result.id == "otodom"

    def test_returns_none_for_unmatched_url(self) -> None:
        result = select_plugin("https://www.example.com/item", get_registrations())
        assert result is None

    def test_returns_none_for_invalid_url(self) -> None:
        result = select_plugin("not-a-url", get_registrations())
        assert result is None

    def test_uses_scraping_url_when_provided(self) -> None:
        olx_result = select_plugin("https://www.olx.pl/oferta/test", get_registrations())
        assert olx_result is not None
        assert olx_result.id == "olx"

        offer_result = select_plugin("https://www.example.com/offer/123", get_registrations())
        assert offer_result is None
