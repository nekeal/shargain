from collections.abc import Sequence

from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import OfferState
from shargain.offers.models import UserOfferState


def get_offer_states(actor: Actor, offer_ids: Sequence[int]) -> dict[int, OfferState]:
    if not offer_ids:
        return {}
    states = UserOfferState.objects.filter(user_id=actor.user_id, offer_id__in=offer_ids)
    state_map = {s.offer_id: OfferState(offer_id=s.offer_id, seen_at=s.seen_at, liked_at=s.liked_at) for s in states}
    return {oid: state_map.get(oid, OfferState(offer_id=oid, seen_at=None, liked_at=None)) for oid in offer_ids}
