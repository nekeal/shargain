import pytest

from shargain.offers.application.actor import Actor
from shargain.offers.application.queries.list_target_urls import (
    ListTargetUrlsQuery,
    list_target_urls,
)
from shargain.offers.tests.factories import ScrapingUrlFactory


@pytest.mark.django_db
class TestListTargetUrls:
    def test_list_target_urls(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        query = ListTargetUrlsQuery(target_id=scraping_target.id)
        actor = Actor(user_id=scraping_target.owner_id)

        result = list_target_urls(query, actor)

        assert len(result) == 1
        assert result[0].id == scraping_url.id
        assert result[0].url == scraping_url.url

    def test_list_target_urls_empty(self, scraping_target):
        query = ListTargetUrlsQuery(target_id=scraping_target.id)
        actor = Actor(user_id=scraping_target.owner_id)

        result = list_target_urls(query, actor)

        assert len(result) == 0

    def test_list_target_urls_other_user(self, scraping_target):
        ScrapingUrlFactory(scraping_target=scraping_target)
        query = ListTargetUrlsQuery(target_id=scraping_target.id)
        actor = Actor(user_id=scraping_target.owner_id + 1)

        result = list_target_urls(query, actor)

        assert len(result) == 0
