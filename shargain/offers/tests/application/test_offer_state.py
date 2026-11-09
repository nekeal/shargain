import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.exceptions import OfferDoesNotExist
from shargain.offers.application.offer_state import (
    get_offer_states,
    like_offers,
    mark_offers_seen,
    mark_offers_unseen,
    unlike_offers,
)
from shargain.offers.models import UserOfferState
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory


@pytest.mark.django_db
class TestOfferStateCommands:
    def test_mark_offers_seen_is_idempotent(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        states1 = mark_offers_seen(actor, [offer.id])
        assert len(states1) == 1
        assert states1[0].offer_id == offer.id
        assert states1[0].seen_at is not None
        assert states1[0].liked_at is None

        seen_at_orig = states1[0].seen_at
        states2 = mark_offers_seen(actor, [offer.id])
        assert states2[0].seen_at == seen_at_orig

    def test_like_offers_is_idempotent(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        states1 = like_offers(actor, [offer.id])
        assert states1[0].liked_at is not None
        assert states1[0].seen_at is None

        liked_at_orig = states1[0].liked_at
        states2 = like_offers(actor, [offer.id])
        assert states2[0].liked_at == liked_at_orig

    def test_unseen_deletes_row_if_not_liked(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        mark_offers_seen(actor, [offer.id])
        assert UserOfferState.objects.filter(user=user, offer=offer).exists()

        states = mark_offers_unseen(actor, [offer.id])
        assert states[0].seen_at is None
        assert not UserOfferState.objects.filter(user=user, offer=offer).exists()

    def test_unlike_clears_liked_at_but_keeps_row_if_seen(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        mark_offers_seen(actor, [offer.id])
        like_offers(actor, [offer.id])

        states = unlike_offers(actor, [offer.id])
        assert states[0].liked_at is None
        assert states[0].seen_at is not None

        row = UserOfferState.objects.get(user=user, offer=offer)
        assert row.liked_at is None
        assert row.seen_at is not None

    def test_unlike_deletes_row_if_not_seen(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        like_offers(actor, [offer.id])
        assert UserOfferState.objects.filter(user=user, offer=offer).exists()

        states = unlike_offers(actor, [offer.id])
        assert states[0].liked_at is None
        assert not UserOfferState.objects.filter(user=user, offer=offer).exists()

    def test_unseen_clears_seen_at_but_keeps_row_if_liked(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target)
        actor = Actor(user_id=user.id)

        mark_offers_seen(actor, [offer.id])
        like_offers(actor, [offer.id])

        states = mark_offers_unseen(actor, [offer.id])
        assert states[0].seen_at is None
        assert states[0].liked_at is not None

        row = UserOfferState.objects.get(user=user, offer=offer)
        assert row.seen_at is None
        assert row.liked_at is not None

    def test_empty_offer_ids_returns_empty_list(self):
        user = UserFactory()
        actor = Actor(user_id=user.id)
        assert mark_offers_seen(actor, []) == []
        assert mark_offers_unseen(actor, []) == []
        assert like_offers(actor, []) == []
        assert unlike_offers(actor, []) == []

    def test_foreign_or_missing_offer_raises_exception_and_no_mutation(self):
        user = UserFactory()
        other_user = UserFactory()
        target_own = ScrappingTargetFactory(owner=user)
        target_other = ScrappingTargetFactory(owner=other_user)
        offer_own = OfferFactory(target=target_own)
        offer_foreign = OfferFactory(target=target_other)
        actor = Actor(user_id=user.id)

        with pytest.raises(OfferDoesNotExist):
            mark_offers_seen(actor, [offer_own.id, offer_foreign.id])

        assert not UserOfferState.objects.filter(user=user).exists()


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
