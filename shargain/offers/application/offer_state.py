from collections.abc import Sequence

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import OfferState
from shargain.offers.application.exceptions import OfferDoesNotExist
from shargain.offers.models import Offer, UserOfferState

User = get_user_model()


def _validate_actor_offers(actor: Actor, offer_ids: Sequence[int], target_id: int | None = None) -> list[int]:
    if not offer_ids:
        return []
    unique_ids = list(dict.fromkeys(offer_ids))
    filters = {"pk__in": unique_ids, "target__owner_id": actor.user_id}
    if target_id is not None:
        filters["target_id"] = target_id
    offers = list(Offer.objects.filter(**filters).values_list("pk", flat=True))
    if len(offers) != len(unique_ids):
        raise OfferDoesNotExist()
    return unique_ids


def get_offer_states(actor: Actor, offer_ids: Sequence[int]) -> dict[int, OfferState]:
    if not offer_ids:
        return {}
    db_states = {
        s.offer_id: OfferState(offer_id=s.offer_id, seen_at=s.seen_at, liked_at=s.liked_at)
        for s in UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=offer_ids)
    }
    return {oid: db_states.get(oid, OfferState(offer_id=oid, seen_at=None, liked_at=None)) for oid in offer_ids}


def _mutate_seen(
    actor: Actor,
    offer_ids: Sequence[int],
    seen: bool,
    target_id: int | None = None,
) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids, target_id=target_id)

        if seen:
            now = timezone.now()
            UserOfferState.objects.bulk_create(
                [UserOfferState(user_id=actor.user_id, offer_id=oid, seen_at=now) for oid in valid_ids],
                ignore_conflicts=True,
            )
            UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=True).update(
                seen_at=now
            )
        else:
            UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=True).delete()
            UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=False).update(
                seen_at=None
            )

        states = get_offer_states(actor, valid_ids)
        return [states[oid] for oid in valid_ids]


def _mutate_liked(
    actor: Actor,
    offer_ids: Sequence[int],
    liked: bool,
    target_id: int | None = None,
) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids, target_id=target_id)

        if liked:
            now = timezone.now()
            UserOfferState.objects.bulk_create(
                [UserOfferState(user_id=actor.user_id, offer_id=oid, liked_at=now) for oid in valid_ids],
                ignore_conflicts=True,
            )
            UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=True).update(
                liked_at=now
            )
        else:
            UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=True).delete()
            UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=False).update(
                liked_at=None
            )

        states = get_offer_states(actor, valid_ids)
        return [states[oid] for oid in valid_ids]


def mark_offers_seen(actor: Actor, offer_ids: Sequence[int], target_id: int | None = None) -> list[OfferState]:
    return _mutate_seen(actor, offer_ids, seen=True, target_id=target_id)


def mark_offers_unseen(actor: Actor, offer_ids: Sequence[int], target_id: int | None = None) -> list[OfferState]:
    return _mutate_seen(actor, offer_ids, seen=False, target_id=target_id)


def like_offers(actor: Actor, offer_ids: Sequence[int], target_id: int | None = None) -> list[OfferState]:
    return _mutate_liked(actor, offer_ids, liked=True, target_id=target_id)


def unlike_offers(actor: Actor, offer_ids: Sequence[int], target_id: int | None = None) -> list[OfferState]:
    return _mutate_liked(actor, offer_ids, liked=False, target_id=target_id)
