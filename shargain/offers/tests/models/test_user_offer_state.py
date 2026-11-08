import pytest
from django.db import IntegrityError
from django.utils import timezone

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.models import UserOfferState
from shargain.offers.tests.factories import OfferFactory


@pytest.mark.django_db
class TestUserOfferStateModel:
    def test_can_create_liked_only_state(self):
        user = UserFactory()
        offer = OfferFactory()
        state = UserOfferState.objects.create(user=user, offer=offer, liked_at=timezone.now())
        assert state.liked_at is not None
        assert state.seen_at is None

    def test_can_create_seen_only_state(self):
        user = UserFactory()
        offer = OfferFactory()
        state = UserOfferState.objects.create(user=user, offer=offer, seen_at=timezone.now())
        assert state.seen_at is not None
        assert state.liked_at is None

    def test_cannot_create_state_without_either_timestamp(self):
        user = UserFactory()
        offer = OfferFactory()
        with pytest.raises(IntegrityError):
            UserOfferState.objects.create(user=user, offer=offer, seen_at=None, liked_at=None)

    def test_unique_user_offer_constraint(self):
        user = UserFactory()
        offer = OfferFactory()
        now = timezone.now()
        UserOfferState.objects.create(user=user, offer=offer, seen_at=now)
        with pytest.raises(IntegrityError):
            UserOfferState.objects.create(user=user, offer=offer, liked_at=now)
