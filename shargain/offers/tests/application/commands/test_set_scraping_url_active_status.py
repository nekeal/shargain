import pytest

from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.set_scraping_url_active_status import set_scraping_url_active_status
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist
from shargain.offers.models import ScrapingUrl
from shargain.offers.tests.factories import ScrapingUrlFactory


@pytest.mark.django_db
class TestSetScrapingUrlActiveStatus:
    @pytest.fixture
    def active_scraping_url(self) -> ScrapingUrl:
        return ScrapingUrlFactory.create(is_active=True)

    @pytest.fixture
    def inactive_scraping_url(self) -> ScrapingUrl:
        return ScrapingUrlFactory.create(is_active=False)

    def test_set_url_to_active(self, active_scraping_url):
        actor = Actor(user_id=active_scraping_url.scraping_target.owner_id)

        set_scraping_url_active_status(
            actor, active_scraping_url.id, active_scraping_url.scraping_target.id, is_active=True
        )

        active_scraping_url.refresh_from_db()
        assert active_scraping_url.is_active is True

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
