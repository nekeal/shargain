import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist
from shargain.offers.application.queries.get_scraping_url import (
    get_scraping_url,
)
from shargain.offers.models import TargetRole
from shargain.offers.tests.factories import ScrapingUrlFactory
from shargain.offers.tests.helpers import grant_access


@pytest.mark.django_db
class TestGetScrapingUrl:
    def test_get_scraping_url(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)

        result = get_scraping_url(actor, scraping_url.id)

        assert result is not None
        assert result.id == scraping_url.id
        assert result.url == scraping_url.url
        assert result.target_id == scraping_target.id

    def test_get_scraping_url_not_found(self, db):
        actor = Actor(user_id=1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            get_scraping_url(actor, 123)

    def test_get_scraping_url_other_user(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id + 1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            get_scraping_url(actor, scraping_url.id)

    def test_get_scraping_url_shared_member_can_retrieve_url(self, scraping_target):
        viewer = UserFactory()
        grant_access(target=scraping_target, user=viewer, role=TargetRole.VIEWER)
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=viewer.id)

        result = get_scraping_url(actor, scraping_url.id)

        assert result is not None
        assert result.id == scraping_url.id
        assert result.target_id == scraping_target.id
