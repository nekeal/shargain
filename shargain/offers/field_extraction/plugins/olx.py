"""OLX generic plugin -- extracts source-level fields for all OLX listings."""

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
from shargain.offers.location_parsers import LocationParserFactory

if TYPE_CHECKING:
    from shargain.offers.models import Offer

OLX_DOMAIN = "olx.pl"


class OlxPlugin(BaseFieldPlugin):
    """Extracts source-level fields (currently `address`) for all OLX listings."""

    def matches(self, url: ListUrl) -> bool:
        host = urlparse(url).netloc.lower()
        return host.endswith(f".{OLX_DOMAIN}")

    @property
    def fields(self) -> list[FieldDefinition]:
        return [
            FieldDefinition("address", _("Address"), FieldType.STRING),
        ]

    def extract(self, offer: Offer, url: ListUrl) -> dict:
        parser = LocationParserFactory.get_parser(offer.domain, offer.metadata)
        return {"address": parser.get_location_name()}


olx = OlxPlugin()
