"""Otodom apartment listing plugin -- extracts fields from Otodom listing extra."""

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

OTODOM_APARTMENT_URL_FRAGMENT = "otodom.pl/pl/wyniki/sprzedaz/mieszkanie"

_FLOOR_MAP = {
    "GROUND": 0,
    "FIRST": 1,
    "SECOND": 2,
    "THIRD": 3,
    "FOURTH": 4,
    "FIFTH": 5,
    "SIXTH": 6,
    "SEVENTH": 7,
    "EIGHTH": 8,
    "NINTH": 9,
    "ABOVE_TENTH": 0,
}

_ROOMS_MAP = {
    "ONE": 1,
    "TWO": 2,
    "THREE": 3,
    "FOUR": 4,
    "FIVE": 5,
    "SIX": 6,
}


def _to_float(value: object) -> float | None:
    if not isinstance(value, (int, float, str)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _has_tag(extra: dict, tag_value: str) -> bool | None:
    tags = extra.get("tags")
    if tags is None:
        return None
    if not isinstance(tags, list):
        return None
    return any(isinstance(tag, dict) and tag.get("value") == tag_value for tag in tags)


class OtodomApartmentPlugin(BaseFieldPlugin):
    """Extracts apartment fields from Otodom `sprzedaz/mieszkanie` listings."""

    def matches(self, url: ListUrl) -> bool:
        return OTODOM_APARTMENT_URL_FRAGMENT in url

    @property
    def fields(self) -> list[FieldDefinition]:
        return [
            FieldDefinition("price_per_m2", _("Price per m2"), FieldType.NUMBER, unit=_("z\u0142/m\u00b2")),
            FieldDefinition("area", _("Area"), FieldType.NUMBER, unit=_("m\u00b2")),
            FieldDefinition("floor", _("Floor"), FieldType.NUMBER),
            FieldDefinition("rooms", _("Rooms"), FieldType.NUMBER),
            FieldDefinition("parking", _("Parking"), FieldType.BOOLEAN),
            FieldDefinition("balcony", _("Balcony"), FieldType.BOOLEAN),
        ]

    def extract(self, offer: Offer, url: ListUrl) -> dict:
        extra: dict = offer.metadata.get("extra") or {}
        price_per_m2 = (extra.get("pricePerSquareMeter") or {}).get("value")
        floor_number = extra.get("floorNumber")
        rooms_number = extra.get("roomsNumber")
        return {
            "price_per_m2": _to_float(price_per_m2),
            "area": _to_float(extra.get("areaInSquareMeters")),
            "floor": _FLOOR_MAP.get(floor_number) if isinstance(floor_number, str) else None,
            "rooms": _ROOMS_MAP.get(rooms_number) if isinstance(rooms_number, str) else None,
            "parking": _has_tag(extra, "PARKING_SPOT"),
            "balcony": _has_tag(extra, "BALCONY"),
        }


otodom_apartment = OtodomApartmentPlugin()
