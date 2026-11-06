"""
Mark offers as liked/unliked.

This is the application-layer seam for the liked-offers feature. The module is
channel-agnostic: a ``Liker`` is either a real account (``AccountLiker``,
backed by the ``OfferLike.owner`` FK) or an anonymous label (``AnonymousLiker``,
backed by ``OfferLike.liker_label``), so both the Telegram reactions and a
future web dashboard can use the same two functions.

The "exactly one identity" rule and the idempotency behaviour are hidden inside
this module behind a deliberately small interface.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from django.db.models import QuerySet

from shargain.offers.application.exceptions import OfferLikeIdentityError
from shargain.offers.models import Offer, OfferLike


@dataclass(frozen=True)
class AccountLiker:
    """A like attributed to a real Shargain account (the ``owner`` FK)."""

    user_id: int


@dataclass(frozen=True)
class AnonymousLiker:
    """A like attributed to an anonymous identity string (``liker_label``).

    Used when a source cannot be linked to a Shargain account, e.g. a Telegram
    user who never completed registration.
    """

    label: str


Liker = AccountLiker | AnonymousLiker


@dataclass(frozen=True)
class LikeResult:
    """Outcome of the like/unlike operation for a single offer."""

    offer_id: int
    url: str
    is_liked: bool


def like_offers(offers: Sequence[Offer], liker: Liker) -> list[LikeResult]:
    """Mark the given offers as liked by ``liker``.

    Idempotent: an offer already liked by ``liker`` is left untouched.
    """
    if not offers:
        return []
    likes_query = _likes_query_for(OfferLike.objects.filter(offer__in=offers), liker)
    existing = set(likes_query.values_list("offer_id", flat=True))
    fresh = [offer for offer in offers if offer.pk not in existing]
    if fresh:
        OfferLike.objects.bulk_create([_build_like(offer, liker) for offer in fresh], ignore_conflicts=True)

    return [LikeResult(offer_id=offer.pk, url=offer.url, is_liked=True) for offer in offers]


def unlike_offers(offers: Sequence[Offer], liker: Liker) -> list[LikeResult]:
    """Remove ``liker``'s like from the given offers.

    Idempotent: offers not currently liked by ``liker`` are left untouched.
    """
    if not offers:
        return []
    likes_query = _likes_query_for(OfferLike.objects.filter(offer_id__in=[offer.pk for offer in offers]), liker)
    existing = set(likes_query.values_list("offer_id", flat=True))
    if existing:
        likes_query.delete()

    return [LikeResult(offer_id=offer.pk, url=offer.url, is_liked=False) for offer in offers]


def like_offers_by_urls(urls: Sequence[str], liker: Liker) -> list[LikeResult]:
    """Mark the offers matching ``urls`` as liked. Unknown URLs are skipped."""
    offers = list(Offer.objects.filter(url__in=urls))
    return like_offers(offers, liker)


def unlike_offers_by_urls(urls: Sequence[str], liker: Liker) -> list[LikeResult]:
    """Remove likes from the offers matching ``urls``. Unknown URLs are skipped."""
    offers = list(Offer.objects.filter(url__in=urls))
    return unlike_offers(offers, liker)


def _build_like(offer: Offer, liker: Liker) -> OfferLike:
    owner_id, label = _liker_columns(liker)
    return OfferLike(offer=offer, owner_id=owner_id, liker_label=label)


def _likes_query_for(likes_query: QuerySet[OfferLike], liker: Liker) -> QuerySet[OfferLike]:
    """Filter a like queryset down to ``liker``'s identity column."""
    if isinstance(liker, AnonymousLiker):
        return likes_query.filter(liker_label=liker.label)
    return likes_query.filter(owner_id=liker.user_id)


def _liker_columns(liker: Liker) -> tuple[int | None, str]:
    """Map a :class:`Liker` onto the ``OfferLike`` identity columns.

    Returns ``(owner_id, liker_label)`` with exactly one of them non-empty.
    """
    if isinstance(liker, AccountLiker):
        return liker.user_id, ""
    if isinstance(liker, AnonymousLiker) and liker.label:
        return None, liker.label
    raise OfferLikeIdentityError()
