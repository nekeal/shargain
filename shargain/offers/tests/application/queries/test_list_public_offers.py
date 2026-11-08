from unittest.mock import patch

import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import OfferAttribute
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.application.offer_state import like_offers, mark_offers_seen
from shargain.offers.application.queries.list_public_offers import list_public_offers
from shargain.offers.field_extraction import (
    BaseFieldPlugin,
    FieldDefinition,
    FieldType,
    ListUrl,
    OfferFieldResolver,
    RichValue,
)
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory


@pytest.mark.django_db
class TestListPublicOffers:
    def test_target_ownership_enforced(self):
        user = UserFactory()
        other_user = UserFactory()
        target = ScrappingTargetFactory(owner=other_user)
        actor = Actor(user_id=user.id)

        with pytest.raises(TargetDoesNotExist):
            list_public_offers(actor, target.id)

    def test_target_not_found(self):
        user = UserFactory()
        actor = Actor(user_id=user.id)

        with pytest.raises(TargetDoesNotExist):
            list_public_offers(actor, 999999)

    def test_excludes_passed_filters_null_or_false(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        OfferFactory(target=target, passed_filters=None)
        OfferFactory(target=target, passed_filters=False)
        o_valid = OfferFactory(target=target, passed_filters=True)

        page = list_public_offers(actor, target.id)
        assert page.count == 1
        assert len(page.items) == 1
        assert page.items[0].id == o_valid.id

    def test_filter_seen_and_unseen(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        o_seen = OfferFactory(target=target, passed_filters=True)
        o_unseen = OfferFactory(target=target, passed_filters=True)
        mark_offers_seen(actor, [o_seen.id])

        page_unseen = list_public_offers(actor, target.id, seen=False)
        assert [i.id for i in page_unseen.items] == [o_unseen.id]
        assert page_unseen.count == 1
        assert page_unseen.items[0].is_seen is False

        page_seen = list_public_offers(actor, target.id, seen=True)
        assert [i.id for i in page_seen.items] == [o_seen.id]
        assert page_seen.count == 1
        assert page_seen.items[0].is_seen is True

        page_all = list_public_offers(actor, target.id, seen=None)
        assert page_all.count == 2

    def test_filter_liked(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        o_liked = OfferFactory(target=target, passed_filters=True)
        o_unliked = OfferFactory(target=target, passed_filters=True)
        like_offers(actor, [o_liked.id])

        page_liked = list_public_offers(actor, target.id, liked=True)
        assert [i.id for i in page_liked.items] == [o_liked.id]
        assert page_liked.count == 1
        assert page_liked.items[0].is_liked is True

        page_unliked = list_public_offers(actor, target.id, liked=False)
        assert [i.id for i in page_unliked.items] == [o_unliked.id]
        assert page_unliked.count == 1
        assert page_unliked.items[0].is_liked is False

        page_all = list_public_offers(actor, target.id, liked=None)
        assert page_all.count == 2

    def test_ordering_oldest_and_newest(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        o1 = OfferFactory(target=target, passed_filters=True)
        o2 = OfferFactory(target=target, passed_filters=True)

        page_oldest = list_public_offers(actor, target.id, ordering="oldest")
        assert [i.id for i in page_oldest.items] == [o1.id, o2.id]

        page_newest = list_public_offers(actor, target.id, ordering="newest")
        assert [i.id for i in page_newest.items] == [o2.id, o1.id]

    def test_pagination(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        offers = [OfferFactory(target=target, passed_filters=True) for _ in range(5)]

        page1 = list_public_offers(actor, target.id, limit=2, offset=0)
        assert page1.count == 5
        assert [i.id for i in page1.items] == [offers[0].id, offers[1].id]

        page2 = list_public_offers(actor, target.id, limit=2, offset=2)
        assert page2.count == 5
        assert [i.id for i in page2.items] == [offers[2].id, offers[3].id]

        page3 = list_public_offers(actor, target.id, limit=2, offset=4)
        assert page3.count == 5
        assert [i.id for i in page3.items] == [offers[4].id]

    def test_attributes_excludes_title_and_price(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)
        OfferFactory(
            target=target,
            passed_filters=True,
            list_url="https://www.olx.pl/d/nieruchomosci/mieszkania/",
            title="Mieszkanie 2 pokoje",
            price=2500,
            metadata={"extra": {}},
        )

        page = list_public_offers(actor, target.id)
        attr_names = [attr.name for attr in page.items[0].attributes]
        assert "title" not in attr_names
        assert "price" not in attr_names

    def test_attributes_preserves_display_and_types_and_skips_none(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        class CustomPlugin(BaseFieldPlugin):
            name = "custom"

            def matches(self, url: ListUrl) -> bool:
                return "custom-test" in url

            @property
            def fields(self) -> list[FieldDefinition]:
                return [
                    FieldDefinition("title", "Title", FieldType.STRING),
                    FieldDefinition("price", "Price", FieldType.NUMBER, unit="zł"),
                    FieldDefinition("rooms", "Rooms", FieldType.NUMBER),
                    FieldDefinition("area", "Area", FieldType.NUMBER, unit="m²"),
                    FieldDefinition("empty_field", "Empty", FieldType.STRING),
                ]

            def extract(self, offer, url: ListUrl):
                return {
                    "title": "Ignored Title",
                    "price": 1000,
                    "rooms": RichValue(value=3, display="3 pokoje"),
                    "area": 54.5,
                    "empty_field": None,
                }

        plugin = CustomPlugin()
        OfferFieldResolver.register(plugin)
        try:
            OfferFactory(
                target=target,
                passed_filters=True,
                list_url="https://custom-test.com/offers",
            )

            page = list_public_offers(actor, target.id)
            attrs = page.items[0].attributes

            assert len(attrs) == 2
            assert attrs[0] == OfferAttribute(
                name="rooms",
                label="Rooms",
                type="number",
                unit=None,
                value=3,
                display="3 pokoje",
            )
            assert attrs[1] == OfferAttribute(
                name="area",
                label="Area",
                type="number",
                unit="m²",
                value=54.5,
                display=None,
            )
        finally:
            OfferFieldResolver._plugins.remove(plugin)

    def test_empty_list_url_returns_empty_attributes(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)
        OfferFactory(
            target=target,
            passed_filters=True,
            list_url="",
        )

        page = list_public_offers(actor, target.id)
        assert page.items[0].attributes == []

    def test_location_projection(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        OfferFactory(
            target=target,
            passed_filters=True,
            url="https://www.olx.pl/d/oferta/mieszkanie-ID123.html",
            metadata={
                "extra": {
                    "location": {
                        "cityName": "Warszawa",
                        "districtName": "Mokotów",
                    },
                    "map": {
                        "lat": 52.20,
                        "lon": 21.01,
                    },
                }
            },
        )
        OfferFactory(
            target=target,
            passed_filters=True,
            url="https://www.unknown.pl/d/oferta/ID456.html",
            metadata={},
        )

        page = list_public_offers(actor, target.id, ordering="oldest")
        loc1 = page.items[0].location
        assert loc1 is not None
        assert loc1.name == "Warszawa, Mokotów"
        assert loc1.latitude == 52.20
        assert loc1.longitude == 21.01
        assert "maps.google.com" in (loc1.map_url or "")
        assert loc1.is_exact is False

        loc2 = page.items[1].location
        assert loc2 is None

    def test_main_image_url_normalization(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        OfferFactory(target=target, passed_filters=True, main_image_url="")
        OfferFactory(target=target, passed_filters=True, main_image_url="https://img.example.com/1.jpg")

        page = list_public_offers(actor, target.id, ordering="oldest")
        assert page.items[0].main_image_url is None
        assert page.items[1].main_image_url == "https://img.example.com/1.jpg"

    def test_fail_soft_resilience(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        OfferFactory(
            target=target,
            passed_filters=True,
            list_url="https://www.olx.pl/d/nieruchomosci/",
        )

        with (
            patch(
                "shargain.offers.application.queries.list_public_offers.OfferFieldResolver.extract",
                side_effect=RuntimeError("Plugin explosion"),
            ),
            patch(
                "shargain.offers.application.queries.list_public_offers.LocationParserFactory.get_parser",
                side_effect=RuntimeError("Parser explosion"),
            ),
        ):
            page = list_public_offers(actor, target.id)
            assert page.count == 1
            assert page.items[0].attributes == []
            assert page.items[0].location is None

    def test_single_hydration_query_no_n_plus_1(self, django_assert_num_queries):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        actor = Actor(user_id=user.id)

        offers = [OfferFactory(target=target, passed_filters=True) for _ in range(10)]
        mark_offers_seen(actor, [offers[0].id, offers[1].id])
        like_offers(actor, [offers[0].id])

        # Expected queries:
        # 1. Target ownership check: ScrappingTarget.objects.filter(...).exists()
        # 2. Offer count: Offer.objects.filter(...).count()
        # 3. Offer page: Offer.objects.filter(...)[offset:offset+limit]
        # 4. UserOfferState hydration: UserOfferState.objects.filter(user_id=..., offer_id__in=...)
        with django_assert_num_queries(4):
            page = list_public_offers(actor, target.id, limit=10)
            assert page.count == 10
            assert len(page.items) == 10
