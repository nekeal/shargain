import pytest
from django.test import Client

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.offer_state import like_offers, mark_offers_seen
from shargain.offers.models import TargetRole
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory
from shargain.offers.tests.helpers import grant_access


@pytest.mark.django_db
class TestOffersApi:
    def test_list_offers_requires_auth(self):
        client = Client()
        resp = client.get("/api/public/targets/1/offers")
        assert resp.status_code == 401

    def test_list_offers_foreign_target_returns_404(self):
        user = UserFactory()
        other_user = UserFactory()
        target = ScrappingTargetFactory(owner=other_user)
        client = Client()
        client.force_login(user)

        resp = client.get(f"/api/public/targets/{target.id}/offers")
        assert resp.status_code == 404

    def test_list_offers_for_shared_user_succeeds(self):
        user = UserFactory()
        other_user = UserFactory()
        target = ScrappingTargetFactory(owner=other_user)
        grant_access(target=target, user=user, role=TargetRole.VIEWER)
        OfferFactory(target=target, passed_filters=True, title="Shared Offer")
        client = Client()
        client.force_login(user)

        resp = client.get(f"/api/public/targets/{target.id}/offers")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["items"][0]["title"] == "Shared Offer"

    def test_list_offers_returns_page_and_does_not_mark_seen(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target, passed_filters=True, title="Test Offer")
        client = Client()
        client.force_login(user)

        resp = client.get(f"/api/public/targets/{target.id}/offers")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["id"] == offer.id
        assert item["title"] == "Test Offer"
        assert item["isSeen"] is False
        assert item["isLiked"] is False
        assert item["seenAt"] is None
        assert item["likedAt"] is None
        assert "mainImageUrl" in item
        assert "publishedAt" in item
        assert "createdAt" in item
        assert "closedAt" in item
        assert "listUrl" in item
        assert "attributes" in item
        assert "location" in item

    def test_list_offers_query_params_seen_and_liked(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        o_seen = OfferFactory(target=target, passed_filters=True)
        o_unseen = OfferFactory(target=target, passed_filters=True)
        mark_offers_seen(actor, [o_seen.id])

        client = Client()
        client.force_login(user)

        resp_unseen = client.get(f"/api/public/targets/{target.id}/offers?seen=false")
        assert resp_unseen.status_code == 200
        assert [i["id"] for i in resp_unseen.json()["items"]] == [o_unseen.id]

        resp_seen = client.get(f"/api/public/targets/{target.id}/offers?seen=true")
        assert resp_seen.status_code == 200
        assert [i["id"] for i in resp_seen.json()["items"]] == [o_seen.id]

        o_liked = OfferFactory(target=target, passed_filters=True)
        like_offers(actor, [o_liked.id])

        resp_liked = client.get(f"/api/public/targets/{target.id}/offers?liked=true")
        assert resp_liked.status_code == 200
        assert [i["id"] for i in resp_liked.json()["items"]] == [o_liked.id]

    def test_list_offers_ordering_and_pagination(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        o1 = OfferFactory(target=target, passed_filters=True)
        o2 = OfferFactory(target=target, passed_filters=True)

        client = Client()
        client.force_login(user)

        # Ordering
        resp_oldest = client.get(f"/api/public/targets/{target.id}/offers?ordering=oldest")
        assert resp_oldest.status_code == 200
        assert [i["id"] for i in resp_oldest.json()["items"]] == [o1.id, o2.id]

        resp_newest = client.get(f"/api/public/targets/{target.id}/offers?ordering=newest")
        assert resp_newest.status_code == 200
        assert [i["id"] for i in resp_newest.json()["items"]] == [o2.id, o1.id]

        # Pagination
        resp_page = client.get(f"/api/public/targets/{target.id}/offers?limit=1&offset=1&ordering=oldest")
        assert resp_page.status_code == 200
        data = resp_page.json()
        assert data["count"] == 2
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == o2.id

    def test_seen_actions(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target, passed_filters=True)
        client = Client()
        client.force_login(user)

        # POST seen
        resp = client.post(f"/api/public/targets/{target.id}/offers/{offer.id}/seen")
        assert resp.status_code == 200
        data = resp.json()
        assert data["offerId"] == offer.id
        assert data["isSeen"] is True
        assert data["seenAt"] is not None

        # DELETE seen
        resp = client.delete(f"/api/public/targets/{target.id}/offers/{offer.id}/seen")
        assert resp.status_code == 200
        data = resp.json()
        assert data["offerId"] == offer.id
        assert data["isSeen"] is False
        assert data["seenAt"] is None

    def test_like_actions(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target, passed_filters=True)
        client = Client()
        client.force_login(user)

        # POST like
        resp = client.post(f"/api/public/targets/{target.id}/offers/{offer.id}/like")
        assert resp.status_code == 200
        data = resp.json()
        assert data["offerId"] == offer.id
        assert data["isLiked"] is True
        assert data["likedAt"] is not None

        # DELETE like
        resp = client.delete(f"/api/public/targets/{target.id}/offers/{offer.id}/like")
        assert resp.status_code == 200
        data = resp.json()
        assert data["offerId"] == offer.id
        assert data["isLiked"] is False
        assert data["likedAt"] is None

    def test_offer_in_another_target_returns_404(self):
        user = UserFactory()
        target1 = ScrappingTargetFactory(owner=user)
        target2 = ScrappingTargetFactory(owner=user)
        offer = OfferFactory(target=target1, passed_filters=True)
        client = Client()
        client.force_login(user)

        # Request offer under wrong target
        resp = client.post(f"/api/public/targets/{target2.id}/offers/{offer.id}/seen")
        assert resp.status_code == 404

        resp_del_seen = client.delete(f"/api/public/targets/{target2.id}/offers/{offer.id}/seen")
        assert resp_del_seen.status_code == 404

        resp_like = client.post(f"/api/public/targets/{target2.id}/offers/{offer.id}/like")
        assert resp_like.status_code == 404

        resp_del_like = client.delete(f"/api/public/targets/{target2.id}/offers/{offer.id}/like")
        assert resp_del_like.status_code == 404

    def test_list_offers_search_and_price_params(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        match = OfferFactory(target=target, passed_filters=True, title="Mieszkanie Mokotów", price=600000)
        OfferFactory(target=target, passed_filters=True, title="Mieszkanie Mokotów", price=900000)
        OfferFactory(target=target, passed_filters=True, title="Kawalerka Wola", price=600000)
        client = Client()
        client.force_login(user)

        resp = client.get(
            f"/api/public/targets/{target.id}/offers",
            {"search": "mokot", "minPrice": 500000, "maxPrice": 700000},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["items"][0]["id"] == match.id

    def test_list_offers_inverted_price_range_is_empty_not_error(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        OfferFactory(target=target, passed_filters=True, price=100)
        client = Client()
        client.force_login(user)

        resp = client.get(f"/api/public/targets/{target.id}/offers", {"minPrice": 300, "maxPrice": 200})
        assert resp.status_code == 200
        assert resp.json()["count"] == 0

    def test_list_offers_blank_search_is_ignored(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        OfferFactory(target=target, passed_filters=True, title="Rower")
        client = Client()
        client.force_login(user)

        resp = client.get(f"/api/public/targets/{target.id}/offers", {"search": "   "})
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

    def test_shared_member_can_triage_offers_independently(self):
        owner = UserFactory()
        viewer = UserFactory()
        target = ScrappingTargetFactory(owner=owner)
        grant_access(target=target, user=viewer, role=TargetRole.VIEWER)
        offer = OfferFactory(target=target, passed_filters=True)

        viewer_client = Client()
        viewer_client.force_login(viewer)

        # Viewer marks offer as seen
        resp_seen = viewer_client.post(f"/api/public/targets/{target.id}/offers/{offer.id}/seen")
        assert resp_seen.status_code == 200
        assert resp_seen.json()["isSeen"] is True

        # Viewer sees it in seen list
        resp_viewer_seen = viewer_client.get(f"/api/public/targets/{target.id}/offers?seen=true")
        assert resp_viewer_seen.status_code == 200
        assert [i["id"] for i in resp_viewer_seen.json()["items"]] == [offer.id]

        # Owner still sees it as unseen
        owner_client = Client()
        owner_client.force_login(owner)
        resp_owner_unseen = owner_client.get(f"/api/public/targets/{target.id}/offers?seen=false")
        assert resp_owner_unseen.status_code == 200
        assert [i["id"] for i in resp_owner_unseen.json()["items"]] == [offer.id]
