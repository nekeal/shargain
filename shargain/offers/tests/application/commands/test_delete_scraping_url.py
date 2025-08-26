import pytest

from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.delete_scraping_url import delete_scraping_url
from shargain.offers.models import ScrapingUrl
from shargain.offers.tests.factories import ScrapingUrlFactory


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
