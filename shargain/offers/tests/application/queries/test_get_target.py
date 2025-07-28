import pytest

from shargain.offers.application.actor import Actor
from shargain.offers.application.queries.get_target import GetTargetQuery, get_target


class TestGetTargetQuery:
    pytestmark = pytest.mark.django_db

    def test_get_target_returns_correct_target(self, scraping_target):
        query = GetTargetQuery(id=scraping_target.id)
        actor = Actor(user_id=scraping_target.owner_id)

        result = get_target(query, actor)

        assert result is not None
        assert result.id == scraping_target.id
        assert result.name == scraping_target.name

    def test_get_target_returns_none_if_target_doesnt_exist(self):
        query = GetTargetQuery(id=999)
        actor = Actor(user_id=1)

        result = get_target(query, actor)

        assert result is None

    def test_get_target_returns_none_if_target_belongs_to_another_user(self, scraping_target):
        query = GetTargetQuery(id=scraping_target.id)
        actor = Actor(user_id=scraping_target.owner_id + 1)

        result = get_target(query, actor)

        assert result is None
