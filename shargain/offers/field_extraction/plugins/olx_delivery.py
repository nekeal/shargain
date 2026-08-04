"""OLX delivery plugin -- extracts OLX delivery availability from listing metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from django.utils.translation import gettext_lazy as _

from shargain.offers.field_extraction.plugin import (
    BaseFieldPlugin,
    FieldDefinition,
    FieldType,
    ListUrl,
)

if TYPE_CHECKING:
    from shargain.offers.models import Offer

OLX_DOMAIN = "olx.pl"


class OlxDeliveryPlugin(BaseFieldPlugin):
    """Extracts OLX delivery availability for all OLX listings."""

    def matches(self, url: ListUrl) -> bool:
        host = urlparse(url).netloc.lower()
        return host.endswith(f".{OLX_DOMAIN}")

    @property
    def fields(self) -> list[FieldDefinition]:
        return [
            FieldDefinition("olx_delivery", _("OLX delivery"), FieldType.BOOLEAN),
        ]

    def extract(self, offer: Offer, url: ListUrl) -> dict:
        extra = offer.metadata.get("extra") or {}
        rock = (extra.get("delivery") or {}).get("rock") or {}
        active = rock.get("active")
        return {"olx_delivery": active if isinstance(active, bool) else None}


olx_delivery = OlxDeliveryPlugin()
