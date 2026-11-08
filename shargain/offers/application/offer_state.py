from collections.abc import Sequence

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import OfferState
from shargain.offers.application.exceptions import OfferDoesNotExist
from shargain.offers.models import Offer, UserOfferState

User = get_user_model()


def _validate_actor_offers(actor: Actor, offer_ids: Sequence[int]) -> list[int]:
    if not offer_ids:
        return []
    offers = list(Offer.objects.filter(pk__in=offer_ids, target__owner_id=actor.user_id).values_list("pk", flat=True))
    if len(offers) != len(set(offer_ids)):
        raise OfferDoesNotExist()
    return list(offer_ids)


def _load_states(user_id: int, offer_ids: Sequence[int]) -> list[OfferState]:
    db_states = {s.offer_id: s for s in UserOfferState.objects.filter(user_id=user_id, offer_id__in=offer_ids)}
    return [
        OfferState(
            offer_id=oid,
            seen_at=db_states[oid].seen_at if oid in db_states else None,
            liked_at=db_states[oid].liked_at if oid in db_states else None,
        )
        for oid in offer_ids
    ]


def mark_offers_seen(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids)
        now = timezone.now()

        existing_states = {
            s.offer_id: s for s in UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids)
        }
        to_create = [
            UserOfferState(user_id=actor.user_id, offer_id=oid, seen_at=now)
            for oid in set(valid_ids)
            if oid not in existing_states
        ]
        if to_create:
            UserOfferState.objects.bulk_create(to_create, ignore_conflicts=True)

        UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=True).update(
            seen_at=now
        )

        return _load_states(actor.user_id, valid_ids)


def mark_offers_unseen(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids)

        UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=True).delete()

        UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=False).update(
            seen_at=None
        )

        return _load_states(actor.user_id, valid_ids)


def like_offers(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids)
        now = timezone.now()

        existing_states = {
            s.offer_id: s for s in UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids)
        }
        to_create = [
            UserOfferState(user_id=actor.user_id, offer_id=oid, liked_at=now)
            for oid in set(valid_ids)
            if oid not in existing_states
        ]
        if to_create:
            UserOfferState.objects.bulk_create(to_create, ignore_conflicts=True)

        UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, liked_at__isnull=True).update(
            liked_at=now
        )

        return _load_states(actor.user_id, valid_ids)


def unlike_offers(actor: Actor, offer_ids: Sequence[int]) -> list[OfferState]:
    if not offer_ids:
        return []
    with transaction.atomic():
        User.objects.select_for_update().get(pk=actor.user_id)
        valid_ids = _validate_actor_offers(actor, offer_ids)

        UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=True).delete()

        UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=valid_ids, seen_at__isnull=False).update(
            liked_at=None
        )

        return _load_states(actor.user_id, valid_ids)
