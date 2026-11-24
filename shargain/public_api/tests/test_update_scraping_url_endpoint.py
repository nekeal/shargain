import pytest
from django.test import Client

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.application.exceptions import TargetPermissionDenied
from shargain.offers.models import TargetRole
from shargain.offers.tests.factories import ScrapingUrlFactory, ScrappingTargetFactory
from shargain.offers.tests.helpers import grant_access

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

    def test_updates_send_map_flag(self):
        user = UserFactory()
        target = ScrappingTargetFactory(owner=user)
        url = ScrapingUrlFactory(scraping_target=target, send_map_in_notifications=True)

        client = Client()
        client.force_login(user)
        response = client.patch(
            f"/api/public/targets/{target.id}/urls/{url.id}",
            data={"sendMapInNotifications": False},
            content_type="application/json",
        )

        assert response.status_code == 200
        url.refresh_from_db()
        assert url.send_map_in_notifications is False
        assert response.json()["sendMapInNotifications"] is False

    def test_editor_can_update_scraping_url(self):
        owner = UserFactory()
        editor = UserFactory()
        target = ScrappingTargetFactory(owner=owner)
        grant_access(target=target, user=editor, role=TargetRole.EDITOR)
        url = ScrapingUrlFactory(scraping_target=target, send_map_in_notifications=True)

        client = Client()
        client.force_login(editor)
        response = client.patch(
            f"/api/public/targets/{target.id}/urls/{url.id}",
            data={"sendMapInNotifications": False},
            content_type="application/json",
        )
        assert response.status_code == 200
        url.refresh_from_db()
        assert url.send_map_in_notifications is False

    def test_viewer_update_scraping_url_returns_403(self):
        owner = UserFactory()
        viewer = UserFactory()
        target = ScrappingTargetFactory(owner=owner)
        grant_access(target=target, user=viewer, role=TargetRole.VIEWER)
        url = ScrapingUrlFactory(scraping_target=target, send_map_in_notifications=True)

        client = Client()
        client.force_login(viewer)
        response = client.patch(
            f"/api/public/targets/{target.id}/urls/{url.id}",
            data={"sendMapInNotifications": False},
            content_type="application/json",
        )
        assert response.status_code == 403
        assert response.json()["code"] == TargetPermissionDenied.code
        url.refresh_from_db()
        assert url.send_map_in_notifications is True

    def test_update_url_belonging_to_another_target_returns_404(self):
        owner = UserFactory()
        target_a = ScrappingTargetFactory(owner=owner)
        target_b = ScrappingTargetFactory(owner=owner)
        url_b = ScrapingUrlFactory(scraping_target=target_b)

        client = Client()
        client.force_login(owner)
        response = client.patch(
            f"/api/public/targets/{target_a.id}/urls/{url_b.id}",
            data={"sendMapInNotifications": False},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_viewer_with_invalid_filters_returns_403_not_400(self):
        owner = UserFactory()
        viewer = UserFactory()
        target = ScrappingTargetFactory(owner=owner)
        grant_access(target=target, user=viewer, role=TargetRole.VIEWER)
        url = ScrapingUrlFactory(scraping_target=target, url="https://www.olx.pl/d/nieruchomosci/mieszkania/")

        invalid_field_filters = {
            "ruleGroups": [
                {"logic": "and", "rules": [{"field": "nonexistent_field", "operator": "contains", "value": "x"}]}
            ]
        }

        client = Client()
        client.force_login(viewer)
        response = client.patch(
            f"/api/public/targets/{target.id}/urls/{url.id}",
            data={"filters": invalid_field_filters},
            content_type="application/json",
        )
        assert response.status_code == 403
        assert response.json()["code"] == TargetPermissionDenied.code
