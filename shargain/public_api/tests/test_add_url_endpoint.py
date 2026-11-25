import pytest
from django.test import Client

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.application.exceptions import TargetPermissionDenied
from shargain.offers.models import ScrapingUrl, TargetRole
from shargain.offers.tests.factories import ScrappingTargetFactory
from shargain.offers.tests.helpers import grant_access

INVALID_FIELD_FILTERS = {
    "ruleGroups": [{"logic": "and", "rules": [{"field": "nonexistent_field", "operator": "contains", "value": "x"}]}]
}
URL = "https://www.olx.pl/d/nieruchomosci/mieszkania/"


class TestAddUrlEndpoint:
    pytestmark = pytest.mark.django_db

    def test_viewer_with_invalid_filters_returns_403_not_400(self):
        owner = UserFactory()
        viewer = UserFactory()
        target = ScrappingTargetFactory(owner=owner)
        grant_access(target=target, user=viewer, role=TargetRole.VIEWER)

        client = Client()
        client.force_login(viewer)
        response = client.post(
            f"/api/public/targets/{target.id}/add-url",
            data={"url": URL, "filters": INVALID_FIELD_FILTERS},
            content_type="application/json",
        )

        assert response.status_code == 403
        assert response.json()["code"] == TargetPermissionDenied.code
        assert not ScrapingUrl.objects.filter(scraping_target=target).exists()

    def test_editor_with_invalid_filters_returns_400(self):
        owner = UserFactory()
        editor = UserFactory()
        target = ScrappingTargetFactory(owner=owner)
        grant_access(target=target, user=editor, role=TargetRole.EDITOR)

        client = Client()
        client.force_login(editor)
        response = client.post(
            f"/api/public/targets/{target.id}/add-url",
            data={"url": URL, "filters": INVALID_FIELD_FILTERS},
            content_type="application/json",
        )

        assert response.status_code == 400
        assert not ScrapingUrl.objects.filter(scraping_target=target).exists()
