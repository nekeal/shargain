"""Otodom generic plugin -- extracts source-level fields for all Otodom listings."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from django.utils.translation import gettext_lazy as _

from shargain.offers.field_extraction.cleaners import clean_html_description
from shargain.offers.field_extraction.plugin import (
    BaseFieldPlugin,
    FieldDefinition,
    FieldType,
    ListUrl,
)
from shargain.offers.location_parsers import LocationParserFactory

if TYPE_CHECKING:
    from shargain.offers.models import Offer

OTODOM_DOMAIN = "otodom.pl"


class OtodomPlugin(BaseFieldPlugin):
    """Extracts source-level fields (currently `address` and `description`) for all Otodom listings."""

    def matches(self, url: ListUrl) -> bool:
        host = urlparse(url).netloc.lower()
        return host.endswith(f".{OTODOM_DOMAIN}")

    @property
    def fields(self) -> list[FieldDefinition]:
        return [
            FieldDefinition("address", _("Address"), FieldType.STRING),
            FieldDefinition("description", _("Description"), FieldType.STRING),
        ]

    def extract(self, offer: Offer, url: ListUrl) -> dict:
        parser = LocationParserFactory.get_parser(offer.domain, offer.metadata)
        extra = (offer.metadata or {}).get("extra") or {}
        raw_desc = (
            extra.get("description")
            or extra.get("shortDescription")
            or extra.get("description_clean")
            or (offer.metadata or {}).get("description")
        )
        return {
            "address": parser.get_location_name(),
            "description": clean_html_description(raw_desc),
        }


otodom = OtodomPlugin()
