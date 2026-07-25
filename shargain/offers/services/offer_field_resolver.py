"""Registry and resolver for field plugins."""

from shargain.offers.models import Offer
from shargain.offers.schemas.field_plugin import BaseFieldPlugin, FieldDefinition, ListUrl


class OfferFieldResolver:
    _plugins: list[BaseFieldPlugin] = []

    @classmethod
    def register(cls, plugin: BaseFieldPlugin) -> None:
        cls._plugins.append(plugin)

    @classmethod
    def get_fields(cls, url: ListUrl) -> list[FieldDefinition]:
        seen_names: set[str] = set()
        result: list[FieldDefinition] = []

        for plugin in cls._plugins:
            if not plugin.matches(url):
                continue
            for field in plugin.fields:
                if field.name not in seen_names:
                    seen_names.add(field.name)
                    result.append(field)

        return result

    @classmethod
    def extract(cls, offer: Offer, url: ListUrl) -> dict[str, int | float | str | bool | None]:
        result: dict[str, int | float | str | bool | None] = {}

        for plugin in cls._plugins:
            if not plugin.matches(url):
                continue
            values = plugin.extract(offer, url)
            for key, value in values.items():
                if key not in result:
                    result[key] = value

        return result
