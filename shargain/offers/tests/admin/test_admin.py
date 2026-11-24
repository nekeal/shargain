import pytest
from django.test import Client
from django.urls import reverse

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.admin.forms import TargetAccessForm
from shargain.offers.field_extraction import NotificationFieldsSelection
from shargain.offers.models import TargetAccess, TargetRole
from shargain.offers.tests.factories import (
    ScrapingUrlFactory,
    ScrappingTargetFactory,
    TargetAccessFactory,
)


@pytest.fixture
def admin_user(db):
    return UserFactory.create(is_staff=True, is_superuser=True)


@pytest.fixture
def admin_client(admin_user) -> Client:
    client = Client()
    client.force_login(admin_user)
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

    def test_change_page_renders_target_access_inline(self, admin_client):
        target = ScrappingTargetFactory()
        TargetAccessFactory(target=target, role=TargetRole.VIEWER)
        response = admin_client.get(reverse("admin:offers_scrappingtarget_change", args=[target.id]))
        assert response.status_code == 200
        assert "accesses" in response.content.decode()

    def test_owner_cannot_be_in_target_access_form_validation(self, db):
        target = ScrappingTargetFactory()
        form = TargetAccessForm(data={"target": target.id, "user": target.owner_id, "role": TargetRole.EDITOR})
        assert not form.is_valid()
        assert "user" in form.errors

    def test_target_access_admin_changelist_and_change_page(self, admin_client):
        access = TargetAccessFactory()
        list_resp = admin_client.get(reverse("admin:offers_targetaccess_changelist"))
        assert list_resp.status_code == 200
        change_resp = admin_client.get(reverse("admin:offers_targetaccess_change", args=[access.id]))
        assert change_resp.status_code == 200

    def test_save_formset_populates_granted_by(self, admin_client, admin_user):
        target = ScrappingTargetFactory()
        user = UserFactory()
        data = {
            "name": target.name,
            "owner": target.owner_id,
            "accesses-TOTAL_FORMS": "1",
            "accesses-INITIAL_FORMS": "0",
            "accesses-MIN_NUM_FORMS": "0",
            "accesses-MAX_NUM_FORMS": "1000",
            "accesses-0-user": user.id,
            "accesses-0-role": TargetRole.EDITOR,
            "scrapingurl_set-TOTAL_FORMS": "0",
            "scrapingurl_set-INITIAL_FORMS": "0",
            "scrapingurl_set-MIN_NUM_FORMS": "0",
            "scrapingurl_set-MAX_NUM_FORMS": "1000",
            "_save": "Save",
        }
        response = admin_client.post(reverse("admin:offers_scrappingtarget_change", args=[target.id]), data)
        assert response.status_code == 302
        access = TargetAccess.objects.get(target=target, user=user)
        assert access.granted_by == admin_user
