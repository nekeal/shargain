from dataclasses import dataclass

from shargain.offers.services.source_plugins.contracts import SourcePlugin, SourceUrlMatcher


@dataclass(frozen=True)
class PluginRegistration:
    plugin: SourcePlugin
    matcher: SourceUrlMatcher


def select_plugin(
    url: str,
    registrations: list[PluginRegistration],
) -> SourcePlugin | None:
    for reg in registrations:
        if reg.matcher.matches(url):
            return reg.plugin
    return None


_REGISTRY: list[PluginRegistration] = []


def register(plugin: SourcePlugin, matcher: SourceUrlMatcher) -> None:
    _REGISTRY.append(PluginRegistration(plugin=plugin, matcher=matcher))


def get_registrations() -> list[PluginRegistration]:
    return list(_REGISTRY)
