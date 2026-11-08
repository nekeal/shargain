import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.offer_state import like_offers, mark_offers_seen
from shargain.offers.application.queries.get_offer_states import get_offer_states
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory


@pytest.mark.django_db
def test_get_offer_states_returns_state_and_defaults_missing():
    user = UserFactory()
    target = ScrappingTargetFactory(owner=user)
    o1 = OfferFactory(target=target)
    o2 = OfferFactory(target=target)
    o3 = OfferFactory(target=target)
    actor = Actor(user_id=user.id)

    mark_offers_seen(actor, [o1.id])
    like_offers(actor, [o2.id])

    states = get_offer_states(actor, [o1.id, o2.id, o3.id])

    assert states[o1.id].seen_at is not None
    assert states[o1.id].liked_at is None
    assert states[o1.id].is_seen is True
    assert states[o1.id].is_liked is False

    assert states[o2.id].seen_at is None
    assert states[o2.id].liked_at is not None
    assert states[o2.id].is_seen is False
    assert states[o2.id].is_liked is True

    assert states[o3.id].seen_at is None
    assert states[o3.id].liked_at is None
    assert states[o3.id].is_seen is False
    assert states[o3.id].is_liked is False


@pytest.mark.django_db
def test_get_offer_states_empty_ids_returns_empty_dict():
    user = UserFactory()
    actor = Actor(user_id=user.id)
    assert get_offer_states(actor, []) == {}
