import pytest

from shargain.offers.application.actor import Actor
from shargain.offers.application.dto import ScrapingUrlDTO, TargetDTO
from shargain.offers.application.queries.get_target import get_target
from shargain.offers.tests.factories import ScrapingUrlFactory


@pytest.mark.django_db
class TestGetTargetQuery:
    def test_get_target_succeeds(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id)

        result = get_target(actor, target_id=scraping_target.id)

        assert result == TargetDTO.from_orm(scraping_target)

    def test_get_target_with_urls_succeeds(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)

        result = get_target(actor, target_id=scraping_target.id)

        assert result is not None
        assert len(result.urls) == 1
        assert result.urls[0] == ScrapingUrlDTO.from_orm(scraping_url)

    def test_get_target_if_target_doesnt_exist_returns_none(self):
        actor = Actor(user_id=1)

        result = get_target(actor, target_id=999)

        assert result is None

    def test_get_target_if_target_belongs_to_another_user_returns_none(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id + 1)

        result = get_target(actor, target_id=scraping_target.id)

        assert result is None
