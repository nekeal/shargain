"""Tests for GET /urls/{url_id}/available-fields."""

import pytest

from shargain.offers.tests.factories import ScrapingUrlFactory, ScrappingTargetFactory

pytestmark = pytest.mark.django_db


class TestAvailableFieldsEndpoint:
    def test_returns_fields_for_url(self, client, user):
        client.force_login(user)
        target = ScrappingTargetFactory(owner=user)
        url = ScrapingUrlFactory(scraping_target=target, url="https://olx.pl/oferty/")
        response = client.get(f"/api/public/urls/{url.id}/available-fields")
        assert response.status_code == 200
        data = response.json()
        assert "fields" in data
        field_names = [f["name"] for f in data["fields"]]
        assert "title" in field_names
        assert "price" in field_names

    def test_returns_404_for_non_existent_url(self, client, user):
        client.force_login(user)
        response = client.get("/api/public/urls/99999/available-fields")
        assert response.status_code == 404

    def test_returns_401_for_unauthenticated(self, client):
        response = client.get("/api/public/urls/1/available-fields")
        assert response.status_code == 401

    def test_operator_labels_are_provided(self, client, user):
        client.force_login(user)
        target = ScrappingTargetFactory(owner=user)
        url = ScrapingUrlFactory(scraping_target=target, url="https://example.com/")
        response = client.get(f"/api/public/urls/{url.id}/available-fields")
        data = response.json()
        for field in data["fields"]:
            for op in field["operators"]:
                assert "value" in op
                assert "label" in op
