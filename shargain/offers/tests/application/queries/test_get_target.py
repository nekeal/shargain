import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.dto import TargetDTO
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.application.queries.get_target import get_target, get_target_by_user
from shargain.offers.models import TargetRole
from shargain.offers.tests.factories import ScrapingUrlFactory, ScrappingTargetFactory
from shargain.offers.tests.helpers import grant_access


@pytest.mark.django_db
class TestGetTargetQuery:
    def test_get_target_succeeds(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id)

        result = get_target(actor, target_id=scraping_target.id)

        assert result == TargetDTO.from_orm(scraping_target)

    def test_get_target_with_urls_succeeds(self, scraping_target):
        url_a = ScrapingUrlFactory(scraping_target=scraping_target)
        url_b = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)

        result = get_target(actor, target_id=scraping_target.id)

        assert result is not None
        assert len(result.urls) == 2
        assert result.urls[0].id == url_a.id
        assert result.urls[1].id == url_b.id

    def test_get_target_if_target_doesnt_exist_raises_error(self):
        actor = Actor(user_id=1)

        with pytest.raises(TargetDoesNotExist):
            get_target(actor, target_id=999)

    def test_get_target_if_target_belongs_to_another_user_raises_error(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id + 1)

        with pytest.raises(TargetDoesNotExist):
            get_target(actor, target_id=scraping_target.id)

    def test_get_target_succeeds_for_shared_user(self, scraping_target):
        shared_user = UserFactory()
        grant_access(target=scraping_target, user=shared_user, role=TargetRole.VIEWER)
        actor = Actor(user_id=shared_user.id)

        result = get_target(actor, target_id=scraping_target.id)
        assert result.id == scraping_target.id

    def test_get_target_by_user_prioritizes_owned_over_shared(self):
        user = UserFactory()
        other_user = UserFactory()
        shared_target = ScrappingTargetFactory(owner=other_user)
        grant_access(target=shared_target, user=user, role=TargetRole.VIEWER)
        owned_target = ScrappingTargetFactory(owner=user)

        actor = Actor(user_id=user.id)
        result = get_target_by_user(actor)
        assert result.id == owned_target.id

    def test_get_target_by_user_returns_shared_when_no_owned(self):
        user = UserFactory()
        shared_target = ScrappingTargetFactory()
        grant_access(target=shared_target, user=user, role=TargetRole.VIEWER)

        actor = Actor(user_id=user.id)
        result = get_target_by_user(actor)
        assert result.id == shared_target.id
