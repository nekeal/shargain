"""Registry and resolver for field plugins."""

from shargain.offers.models import Offer
from shargain.offers.field_extraction.plugin import BaseFieldPlugin, FieldDefinition, FieldType, ListUrl, Operator

OPERATOR_LABELS: dict[Operator, str] = {
    Operator.CONTAINS: "Contains",
    Operator.NOT_CONTAINS: "Does not contain",
    Operator.EQUALS: "Equals",
    Operator.NOT_EQUALS: "Not equals",
    Operator.GREATER_THAN: "Greater than",
    Operator.LESS_THAN: "Less than",
    Operator.GTE: "Greater than or equal",
    Operator.LTE: "Less than or equal",
}

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
