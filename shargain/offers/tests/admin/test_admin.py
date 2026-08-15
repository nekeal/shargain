import pytest
from django.test import Client
from django.urls import reverse

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.field_extraction import NotificationFieldsSelection
from shargain.offers.tests.factories import ScrapingUrlFactory


@pytest.fixture
def admin_client(db) -> Client:
    user = UserFactory.create(is_staff=True, is_superuser=True)
    client = Client()
    client.force_login(user)
    return client


class TestScrapingUrlAdmin:
    def test_change_page_renders_notification_fields(self, admin_client):
        url = ScrapingUrlFactory(notification_fields=NotificationFieldsSelection(fields=["price", "title"]))
        response = admin_client.get(reverse("admin:offers_scrapingurl_change", args=[url.id]))
        assert response.status_code == 200

    def test_change_page_saves_notification_fields(self, admin_client):
        url = ScrapingUrlFactory(name="Test URL")
        response = admin_client.post(
            reverse("admin:offers_scrapingurl_change", args=[url.id]),
            {
                "name": url.name,
                "url": url.url,
                "is_active": "on",
                "show_location_map_in_notifications": "",
                "notification_fields": '{"fields": ["price", "title"]}',
                "scraping_target": url.scraping_target_id,
                "_save": "Save",
            },
        )
        assert response.status_code == 302
        url.refresh_from_db()
        assert url.notification_fields == NotificationFieldsSelection(fields=["price", "title"])


class TestScrappingTargetAdmin:
    def test_change_page_renders_inline_with_notification_fields(self, admin_client):
        url = ScrapingUrlFactory(notification_fields=NotificationFieldsSelection(fields=["price", "title"]))
        response = admin_client.get(reverse("admin:offers_scrappingtarget_change", args=[url.scraping_target_id]))
        assert response.status_code == 200
