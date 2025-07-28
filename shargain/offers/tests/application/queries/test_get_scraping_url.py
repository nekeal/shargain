import pytest

from shargain.offers.application.actor import Actor
from shargain.offers.application.queries.get_scraping_url import (
    get_scraping_url,
)
from shargain.offers.tests.factories import ScrapingUrlFactory


@pytest.mark.django_db
class TestGetScrapingUrl:
    def test_get_scraping_url(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)

        result = get_scraping_url(actor, scraping_url.id)

        assert result is not None
        assert result.id == scraping_url.id
        assert result.url == scraping_url.url
        assert result.target_id == scraping_target.id

    def test_get_scraping_url_not_found(self, db):
        actor = Actor(user_id=1)

        result = get_scraping_url(actor, 123)

        assert result is None

    def test_get_scraping_url_other_user(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id + 1)

        result = get_scraping_url(actor, scraping_url.id)

        assert result is None
