"""Core types for the field plugin system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, NewType

from pydantic import BaseModel

if TYPE_CHECKING:
    from shargain.offers.models import Offer

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


@dataclass(frozen=True)
class FieldDefinition:
    name: str
    label: str
    field_type: FieldType
    allowed_operators: list[Operator] | None = None
    unit: str | None = None


@dataclass
class ExtractedOffer:
    """Extracted offer data for filtering and notifications.

    TODO: Once location parser is refactored as a plugin, remove `_offer` and
    include required fields directly (id, url, title, price, published_at, domain, metadata).
    """

    _offer: Offer
    fields: dict[str, int | float | str | bool | None]

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
    def extract(self, offer: Offer, url: ListUrl) -> dict[str, int | float | str | bool | None]:
        """Return {field_name: value} for all declared fields."""
