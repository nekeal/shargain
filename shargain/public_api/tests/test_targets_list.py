import pytest
from django.test import Client

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.tests.factories import ScrapingUrlFactory, ScrappingTargetFactory


class TestTargetsListEndpoint:
    pytestmark = pytest.mark.django_db

    def test_returns_list_of_targets(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        ScrapingUrlFactory.create_batch(3, scraping_target=target)
        ScrappingTargetFactory(owner=user)

        client = Client()
        client.force_login(user)
        response = client.get("/api/public/targets")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for item in data:
            assert "id" in item
            assert "name" in item
            assert "isActive" in item
            assert "enableNotifications" in item
            assert "urlCount" in item
        target_entry = next(t for t in data if t["id"] == target.id)
        assert target_entry["urlCount"] == 3

    def test_returns_empty_list_when_user_has_no_targets(self):
        user = UserFactory()

        client = Client()
        client.force_login(user)
        response = client.get("/api/public/targets")

        assert response.status_code == 200
        assert response.json() == []

    def test_requires_authentication(self):
        client = Client()
        response = client.get("/api/public/targets")

        assert response.status_code == 401
