import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.set_scraping_url_active_status import set_scraping_url_active_status
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist, TargetPermissionDenied
from shargain.offers.models import ScrapingUrl, TargetRole
from shargain.offers.tests.factories import ScrapingUrlFactory
from shargain.offers.tests.helpers import grant_access


@pytest.mark.django_db
class TestSetScrapingUrlActiveStatus:
    @pytest.fixture
    def active_scraping_url(self) -> ScrapingUrl:
        return ScrapingUrlFactory.create(is_active=True)

    @pytest.fixture
    def inactive_scraping_url(self) -> ScrapingUrl:
        return ScrapingUrlFactory.create(is_active=False)

    def test_set_url_to_active(self, inactive_scraping_url):
        actor = Actor(user_id=inactive_scraping_url.scraping_target.owner_id)

        set_scraping_url_active_status(
            actor, inactive_scraping_url.id, inactive_scraping_url.scraping_target.id, is_active=True
        )

        inactive_scraping_url.refresh_from_db()
        assert inactive_scraping_url.is_active is True

    def test_set_url_to_inactive(self, inactive_scraping_url):
        actor = Actor(user_id=inactive_scraping_url.scraping_target.owner_id)

        set_scraping_url_active_status(
            actor, inactive_scraping_url.id, inactive_scraping_url.scraping_target.id, is_active=False
        )

        inactive_scraping_url.refresh_from_db()
        assert inactive_scraping_url.is_active is False

    def test_set_active_status_for_non_existent_url_raises_error(self):
        actor = Actor(user_id=1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            set_scraping_url_active_status(actor, 999, 1, is_active=True)

    def test_set_active_status_for_other_user_url_raises_error(self, active_scraping_url):
        actor = Actor(user_id=active_scraping_url.scraping_target.owner_id + 1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            set_scraping_url_active_status(
                actor, active_scraping_url.id, active_scraping_url.scraping_target.id, is_active=True
            )

    def test_editor_can_set_active_status(self, inactive_scraping_url):
        editor = UserFactory()
        grant_access(target=inactive_scraping_url.scraping_target, user=editor, role=TargetRole.EDITOR)
        actor = Actor(user_id=editor.id)

        set_scraping_url_active_status(
            actor, inactive_scraping_url.id, inactive_scraping_url.scraping_target.id, is_active=True
        )

        inactive_scraping_url.refresh_from_db()
        assert inactive_scraping_url.is_active is True

    def test_viewer_cannot_set_active_status(self, inactive_scraping_url):
        viewer = UserFactory()
        grant_access(target=inactive_scraping_url.scraping_target, user=viewer, role=TargetRole.VIEWER)
        actor = Actor(user_id=viewer.id)

        with pytest.raises(TargetPermissionDenied):
            set_scraping_url_active_status(
                actor, inactive_scraping_url.id, inactive_scraping_url.scraping_target.id, is_active=True
            )
        inactive_scraping_url.refresh_from_db()
        assert inactive_scraping_url.is_active is False
