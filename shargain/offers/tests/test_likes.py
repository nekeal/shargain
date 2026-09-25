import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.application.exceptions import OfferLikeIdentityError
from shargain.offers.likes import (
    AccountLiker,
    AnonymousLiker,
    like_offers,
    like_offers_by_urls,
    unlike_offers,
    unlike_offers_by_urls,
)
from shargain.offers.models import OfferLike
from shargain.offers.tests.factories import OfferFactory, OfferLikeFactory, ScrappingTargetFactory


@pytest.mark.django_db
class TestLikeOffers:
    def test_like_offers_by_account_sets_owner(self):
        offer = OfferFactory()
        user = UserFactory()

        result = like_offers([offer], AccountLiker(user_id=user.pk))

        assert result[0].offer_id == offer.pk
        assert result[0].is_liked is True
        like = OfferLike.objects.get(offer=offer)
        assert like.owner == user
        assert like.liker_label == ""

    def test_like_offers_by_anonymous_sets_label(self):
        offer = OfferFactory()

        like_offers([offer], AnonymousLiker(label="tg:42"))

        like = OfferLike.objects.get(offer=offer)
        assert like.owner_id is None
        assert like.liker_label == "tg:42"

    def test_like_offers_is_idempotent(self):
        offer = OfferFactory()
        OfferLikeFactory(offer=offer, liker_label="tg:42")

        like_offers([offer], AnonymousLiker(label="tg:42"))

        assert OfferLike.objects.filter(offer=offer).count() == 1

    def test_like_offers_rejects_empty_identity(self):
        offer = OfferFactory()

        with pytest.raises(OfferLikeIdentityError):
            like_offers([offer], AnonymousLiker(label=""))

    def test_like_offers_accepts_empty_offers(self):
        assert like_offers([], AnonymousLiker(label="tg:42")) == []

    def test_like_offers_by_urls_skips_unknown_urls(self):
        offer = OfferFactory()

        result = like_offers_by_urls(["https://unknown.example.com/x", offer.url], AnonymousLiker(label="tg:42"))

        assert len(result) == 1
        assert OfferLike.objects.filter(offer=offer, liker_label="tg:42").exists()


@pytest.mark.django_db
class TestUnlikeOffers:
    def test_unlike_offers_deletes_likes(self):
        offer = OfferFactory()
        OfferLikeFactory(offer=offer, liker_label="tg:42")

        result = unlike_offers([offer], AnonymousLiker(label="tg:42"))

        assert result[0].is_liked is False
        assert OfferLike.objects.filter(offer=offer).exists() is False

    def test_unlike_offers_is_idempotent(self):
        offer = OfferFactory()

        result = unlike_offers([offer], AnonymousLiker(label="tg:42"))

        assert result[0].is_liked is False

    def test_unlike_offers_by_urls(self):
        offer = OfferFactory()
        OfferLikeFactory(offer=offer, liker_label="tg:42")

        result = unlike_offers_by_urls([offer.url], AnonymousLiker(label="tg:42"))

        assert result[0].is_liked is False

    def test_unlike_offers_affects_only_matching_label(self):
        offer = OfferFactory()
        OfferLikeFactory(offer=offer, liker_label="tg:42")
        OfferLikeFactory(offer=offer, liker_label="tg:99")

        unlike_offers([offer], AnonymousLiker(label="tg:42"))

        assert OfferLike.objects.filter(offer=offer, liker_label="tg:99").exists()

    def test_unlike_offers_affects_only_matching_account(self):
        offer = OfferFactory()
        OfferLikeFactory(offer=offer, liker_label="tg:42")
        OfferLikeFactory(offer=offer, liker_label="tg:99")

        unlike_offers([offer], AnonymousLiker(label="tg:99"))

        assert OfferLike.objects.filter(offer=offer, liker_label="tg:42").exists()


@pytest.mark.django_db
def test_likes_group_under_scraping_target():
    target = ScrappingTargetFactory()
    offer = OfferFactory(target=target)
    OfferLikeFactory(offer=offer, liker_label="tg:1")
    OfferLikeFactory(offer=offer, liker_label="tg:2")

    assert OfferLike.objects.filter(offer__target=target).count() == 2
