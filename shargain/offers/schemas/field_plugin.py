"""Core types for the field plugin system."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import NewType

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
    offer: Offer
    fields: dict[str, int | float | str | bool | None]


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
