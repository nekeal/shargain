"""OLX apartment listing plugin -- extracts fields from OLX listing params."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from shargain.offers.field_extraction.plugin import (
    BaseFieldPlugin,
    FieldDefinition,
    FieldType,
    ListUrl,
)

if TYPE_CHECKING:
    from shargain.offers.models import Offer

OLX_APARTMENT_URL_FRAGMENT = "olx.pl/nieruchomosci/mieszkania"

_ROOMS_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
}


def _param(extra: dict, key: str) -> dict | None:
    """Return the params entry with the given key, or None."""
    for entry in extra.get("params") or []:
        if isinstance(entry, dict) and entry.get("key") == key:
            return entry
    return None


def _normalized(entry: dict | None) -> object:
    if entry is None:
        return None
    value = entry.get("normalizedValue")
    if value is None:
        return entry.get("value")
    return value


def _to_float(value: object) -> float | None:
    if not isinstance(value, (int, float, str)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: object) -> int | None:
    if not isinstance(value, (int, float, str)):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_floor(extra: dict) -> int | None:
    value = _normalized(_param(extra, "floor_select"))
    if not isinstance(value, str) or not value.startswith("floor_"):
        return None
    return _to_int(value.removeprefix("floor_"))


def _extract_rooms(extra: dict) -> int | None:
    value = _normalized(_param(extra, "rooms"))
    if isinstance(value, str):
        return _ROOMS_MAP.get(value)
    return None


def _extract_winda(extra: dict) -> bool | None:
    entry = _param(extra, "winda")
    if entry is None:
        return None
    value = _normalized(entry)
    if value is None:
        return None
    return value == "Tak"


def _extract_parking(extra: dict) -> bool | None:
    entry = _param(extra, "parking")
    if entry is None:
        return None
    value = _normalized(entry)
    if value is None:
        return None
    if isinstance(value, list):
        choices = value
    else:
        choices = [value]
    has_parking = any(choice != "brak" for choice in choices if isinstance(choice, str))
    return has_parking


def _extract_text(extra: dict, key: str) -> str | None:
    value = _normalized(_param(extra, key))
    if isinstance(value, str):
        return value
    return None


class OlxApartmentPlugin(BaseFieldPlugin):
    """Extracts apartment fields from OLX `nieruchomosci/mieszkania` listings."""

    def matches(self, url: ListUrl) -> bool:
        return OLX_APARTMENT_URL_FRAGMENT in url

    @property
    def fields(self) -> list[FieldDefinition]:
        return [
            FieldDefinition("price_per_m2", _("Price per m2"), FieldType.NUMBER, unit=_("z\u0142/m\u00b2")),
            FieldDefinition("area", _("Area"), FieldType.NUMBER, unit=_("m\u00b2")),
            FieldDefinition("floor", _("Floor"), FieldType.NUMBER),
            FieldDefinition("rooms", _("Rooms"), FieldType.NUMBER),
            FieldDefinition("winda", _("Elevator"), FieldType.BOOLEAN),
            FieldDefinition("parking", _("Parking"), FieldType.BOOLEAN),
            FieldDefinition("builttype", _("Building type"), FieldType.STRING),
            FieldDefinition("market", _("Market"), FieldType.STRING),
        ]

    def extract(self, offer: Offer, url: ListUrl) -> dict:
        extra = offer.metadata.get("extra") or {}
        return {
            "price_per_m2": _to_float(_normalized(_param(extra, "price_per_m"))),
            "area": _to_float(_normalized(_param(extra, "m"))),
            "floor": _extract_floor(extra),
            "rooms": _extract_rooms(extra),
            "winda": _extract_winda(extra),
            "parking": _extract_parking(extra),
            "builttype": _extract_text(extra, "builttype"),
            "market": _extract_text(extra, "market"),
        }


olx_apartment = OlxApartmentPlugin()
