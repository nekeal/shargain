import pytest
from django.test import Client

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.tests.factories import ScrapingUrlFactory, ScrappingTargetFactory

FILTERS = {
    "ruleGroups": [{"logic": "and", "rules": [{"field": "title", "operator": "contains", "value": "apartment"}]}]
}


class TestUpdateScrapingUrlEndpoint:
    pytestmark = pytest.mark.django_db

    def test_clears_filters_when_null_is_sent(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        url = ScrapingUrlFactory(scraping_target=target, filters=FILTERS)

        client = Client()
        client.force_login(user)
        response = client.patch(
            f"/api/public/targets/{target.id}/urls/{url.id}",
            data={"filters": None},
            content_type="application/json",
        )

        assert response.status_code == 200
        url.refresh_from_db()
        assert url.filters is None

    def test_omitted_filters_are_left_unchanged(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        url = ScrapingUrlFactory(scraping_target=target, filters=FILTERS)

        client = Client()
        client.force_login(user)
        response = client.patch(
            f"/api/public/targets/{target.id}/urls/{url.id}",
            data={"showLocationMapInNotifications": True},
            content_type="application/json",
        )

        assert response.status_code == 200
        url.refresh_from_db()
        assert url.filters == FILTERS

    def test_updates_filters_when_config_is_sent(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        url = ScrapingUrlFactory(scraping_target=target, filters=FILTERS)
        new_filters = {
            "ruleGroups": [{"logic": "and", "rules": [{"field": "title", "operator": "contains", "value": "villa"}]}]
        }
        stored_filters = {
            "ruleGroups": [
                {
                    "logic": "and",
                    "logicWithNext": None,
                    "rules": [{"case_sensitive": False, "field": "title", "operator": "contains", "value": "villa"}],
                }
            ]
        }

        client = Client()
        client.force_login(user)
        response = client.patch(
            f"/api/public/targets/{target.id}/urls/{url.id}",
            data={"filters": new_filters},
            content_type="application/json",
        )

        assert response.status_code == 200
        url.refresh_from_db()
        assert url.filters == stored_filters
