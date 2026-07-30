"""Registry and resolver for field plugins."""

from __future__ import annotations

from typing import TYPE_CHECKING

from shargain.offers.field_extraction.plugin import (
    BaseFieldPlugin,
    ExtractedFieldValue,
    FieldDefinition,
    FieldType,
    ListUrl,
    Operator,
)

if TYPE_CHECKING:
    from shargain.offers.models import Offer

TYPE_OPERATORS: dict[FieldType, list[Operator]] = {
    FieldType.STRING: [Operator.CONTAINS, Operator.NOT_CONTAINS, Operator.EQUALS],
    FieldType.NUMBER: [
        Operator.EQUALS,
        Operator.NOT_EQUALS,
        Operator.GREATER_THAN,
        Operator.LESS_THAN,
        Operator.GTE,
        Operator.LTE,
    ],
    FieldType.BOOLEAN: [Operator.EQUALS],
}


def get_operators_for_type(
    field_type: FieldType,
    custom: list[Operator] | None = None,
) -> list[Operator]:
    if custom is not None:
        return custom
    return TYPE_OPERATORS.get(field_type, [])


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
                    resolved_ops = (
                        field.allowed_operators
                        if field.allowed_operators is not None
                        else get_operators_for_type(field.field_type)
                    )
                    resolved_field = FieldDefinition(
                        name=field.name,
                        label=field.label,
                        field_type=field.field_type,
                        allowed_operators=resolved_ops,
                        unit=field.unit,
                    )
                    result.append(resolved_field)
        return result

    @classmethod
    def extract(cls, offer: Offer, url: ListUrl) -> dict[str, ExtractedFieldValue]:
        result: dict[str, ExtractedFieldValue] = {}

        for plugin in cls._plugins:
            if not plugin.matches(url):
                continue
            values = plugin.extract(offer, url)
            for key, value in values.items():
                if key not in result:
                    result[key] = value

        return result
