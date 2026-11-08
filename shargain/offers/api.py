from datetime import datetime
from typing import Literal

from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from shargain.commons.application.actor import Actor
from shargain.offers.application import exceptions
from shargain.offers.application.offer_state import (
    like_offers,
    mark_offers_seen,
    mark_offers_unseen,
    unlike_offers,
)
from shargain.offers.application.queries.list_public_offers import list_public_offers

router = Router(tags=["offers"])


class BaseSchema(Schema):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class OfferAttributeSchema(BaseSchema):
    name: str
    label: str
    type: str
    unit: str | None = None
    value: bool | int | float | str
    display: str | None = None


class OfferLocationSchema(BaseSchema):
    name: str | None = None
    map_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_exact: bool


class PublicOfferSchema(BaseSchema):
    id: int
    url: str
    title: str
    price: int | None = None
    main_image_url: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    closed_at: datetime | None = None
    list_url: str
    is_seen: bool
    seen_at: datetime | None = None
    is_liked: bool
    liked_at: datetime | None = None
    attributes: list[OfferAttributeSchema]
    location: OfferLocationSchema | None = None


class PublicOfferPageSchema(BaseSchema):
    count: int
    items: list[PublicOfferSchema]


class OfferStateResponseSchema(BaseSchema):
    offer_id: int
    is_seen: bool
    seen_at: datetime | None = None
    is_liked: bool
    liked_at: datetime | None = None


def _get_actor(request: HttpRequest) -> Actor:
    if not request.user or not request.user.is_authenticated:
        raise HttpError(401, "Unauthorized")
    return Actor(user_id=request.user.id)


@router.get("/targets/{target_id}/offers", response=PublicOfferPageSchema, by_alias=True)
def get_target_offers(
    request: HttpRequest,
    target_id: int,
    seen: bool | None = None,
    liked: bool | None = None,
    ordering: Literal["oldest", "newest"] = "oldest",
    limit: int = 20,
    offset: int = 0,
):
    actor = _get_actor(request)
    try:
        return list_public_offers(
            actor=actor,
            target_id=target_id,
            seen=seen,
            liked=liked,
            ordering=ordering,
            limit=limit,
            offset=offset,
        )
    except exceptions.TargetDoesNotExist as e:
        raise HttpError(404, "Target not found") from e


@router.post("/targets/{target_id}/offers/{offer_id}/seen", response=OfferStateResponseSchema, by_alias=True)
def mark_offer_seen(request: HttpRequest, target_id: int, offer_id: int):
    actor = _get_actor(request)
    try:
        states = mark_offers_seen(actor, [offer_id], target_id=target_id)
        return states[0]
    except exceptions.OfferDoesNotExist as e:
        raise HttpError(404, "Offer not found") from e


@router.delete("/targets/{target_id}/offers/{offer_id}/seen", response=OfferStateResponseSchema, by_alias=True)
def mark_offer_unseen(request: HttpRequest, target_id: int, offer_id: int):
    actor = _get_actor(request)
    try:
        states = mark_offers_unseen(actor, [offer_id], target_id=target_id)
        return states[0]
    except exceptions.OfferDoesNotExist as e:
        raise HttpError(404, "Offer not found") from e


@router.post("/targets/{target_id}/offers/{offer_id}/like", response=OfferStateResponseSchema, by_alias=True)
def like_offer(request: HttpRequest, target_id: int, offer_id: int):
    actor = _get_actor(request)
    try:
        states = like_offers(actor, [offer_id], target_id=target_id)
        return states[0]
    except exceptions.OfferDoesNotExist as e:
        raise HttpError(404, "Offer not found") from e


@router.delete("/targets/{target_id}/offers/{offer_id}/like", response=OfferStateResponseSchema, by_alias=True)
def unlike_offer(request: HttpRequest, target_id: int, offer_id: int):
    actor = _get_actor(request)
    try:
        states = unlike_offers(actor, [offer_id], target_id=target_id)
        return states[0]
    except exceptions.OfferDoesNotExist as e:
        raise HttpError(404, "Offer not found") from e
