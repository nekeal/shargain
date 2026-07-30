"""Core Fields Plugin -- applies to all URLs, extracts basic offer fields."""

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


class CoreFieldsPlugin(BaseFieldPlugin):
    """Provides 'title' and 'price' for all offers. Registered first for backward compat."""

    def matches(self, url: ListUrl) -> bool:
        return True

    @property
    def fields(self) -> list[FieldDefinition]:
        return [
            FieldDefinition("title", _("Title"), FieldType.STRING),
            FieldDefinition("price", _("Price"), FieldType.NUMBER, unit=_("z\u0142")),
        ]

    def extract(self, offer: Offer, url: ListUrl) -> dict:
        return {"title": offer.title, "price": offer.price}


core_fields = CoreFieldsPlugin()
