"""Core types for the field plugin system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, NewType

from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise

    from shargain.offers.models import Offer

ExtractedScalar = bool | int | float | str | None


@dataclass(frozen=True)
class RichValue:
    """Wrapper carrying a filterable scalar plus an optional display string."""

    value: ExtractedScalar
    display: str | None = None

    def get_value(self) -> ExtractedScalar:
        return self.value


ExtractedFieldValue = ExtractedScalar | RichValue

ListUrl = NewType("ListUrl", str)


class FieldType(StrEnum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


class Operator(StrEnum):
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GTE = "gte"
    LTE = "lte"

    @property
    def label(self) -> StrOrPromise:
        return _OPERATOR_LABELS[self]


_OPERATOR_LABELS: dict[Operator, StrOrPromise] = {
    Operator.CONTAINS: _("Contains"),
    Operator.NOT_CONTAINS: _("Does not contain"),
    Operator.EQUALS: _("Equals"),
    Operator.NOT_EQUALS: _("Not equals"),
    Operator.GREATER_THAN: _("Greater than"),
    Operator.LESS_THAN: _("Less than"),
    Operator.GTE: _("Greater than or equal"),
    Operator.LTE: _("Less than or equal"),
}


@dataclass(frozen=True)
class FieldDefinition:
    name: str
    label: StrOrPromise
    field_type: FieldType
    allowed_operators: list[Operator] | None = None
    unit: StrOrPromise | None = None


@dataclass
class ExtractedOffer:
    """Extracted offer data for filtering and notifications.

    TODO: Once location parser is refactored as a plugin, remove `_offer` and
    include required fields directly (id, url, title, price, published_at, domain, metadata).
    """

    _offer: Offer
    fields: dict[str, ExtractedFieldValue]

    @property
    def id(self) -> int:
        return self._offer.id

    @property
    def url(self) -> str:
        return self._offer.url

    @property
    def title(self) -> str:
        return self._offer.title

    @property
    def price(self) -> int | None:
        return self._offer.price

    @property
    def published_at(self) -> datetime | None:
        return self._offer.published_at

    @property
    def domain(self) -> str:
        return self._offer.domain

    @property
    def metadata(self) -> dict:
        return self._offer.metadata


@dataclass(frozen=True)
class ExtractedFieldEntry:
    name: str
    value: ExtractedFieldValue


class NotificationFieldsSelection(BaseModel):
    fields: list[str] = []


class BaseFieldPlugin(ABC):
    """Abstract base for a field plugin.
    Each plugin is a singleton object stored in OfferFieldResolver.
    """

    @abstractmethod
    def matches(self, url: ListUrl) -> bool:
        """Return True if this plugin supports the given listing URL."""

    @property
    @abstractmethod
    def fields(self) -> list[FieldDefinition]:
        """The fields this plugin can extract."""

    @abstractmethod
    def extract(self, offer: Offer, url: ListUrl) -> dict[str, ExtractedFieldValue]:
        """Return {field_name: value} for all declared fields."""
