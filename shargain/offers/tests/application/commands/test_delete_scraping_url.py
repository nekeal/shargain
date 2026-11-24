import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.delete_scraping_url import delete_scraping_url
from shargain.offers.application.exceptions import TargetPermissionDenied
from shargain.offers.models import ScrapingUrl, TargetRole
from shargain.offers.tests.factories import ScrapingUrlFactory
from shargain.offers.tests.helpers import grant_access


@pytest.mark.django_db
class TestDeleteScrapingUrl:
    def test_delete_scraping_url(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)

        delete_scraping_url(actor, scraping_url.id)

        assert not ScrapingUrl.objects.filter(id=scraping_url.id).exists()

    def test_delete_scraping_url_not_found(self, db):
        actor = Actor(user_id=1)
        delete_scraping_url(actor, 123)
        assert not ScrapingUrl.objects.filter(id=123).exists()

    def test_delete_scraping_url_other_user(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id + 1)

        delete_scraping_url(actor, scraping_url.id)

        assert ScrapingUrl.objects.filter(id=scraping_url.id).exists()

    def test_delete_scraping_url_by_editor_succeeds(self, scraping_target):
        editor = UserFactory()
        grant_access(target=scraping_target, user=editor, role=TargetRole.EDITOR)
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=editor.id)

        delete_scraping_url(actor, scraping_url.id)

        assert not ScrapingUrl.objects.filter(id=scraping_url.id).exists()

    def test_delete_scraping_url_by_viewer_raises_permission_denied(self, scraping_target):
        viewer = UserFactory()
        grant_access(target=scraping_target, user=viewer, role=TargetRole.VIEWER)
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=viewer.id)

        with pytest.raises(TargetPermissionDenied):
            delete_scraping_url(actor, scraping_url.id)

        assert ScrapingUrl.objects.filter(id=scraping_url.id).exists()

    def test_delete_scraping_url_with_mismatched_target_id_does_not_delete(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)

        delete_scraping_url(actor, scraping_url.id, target_id=scraping_target.id + 999)

        assert ScrapingUrl.objects.filter(id=scraping_url.id).exists()
