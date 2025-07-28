import pytest

from shargain.offers.application.actor import Actor
from shargain.offers.application.commands.add_scraping_url import (
    AddScrapingUrlCommand,
    add_scraping_url,
)
from shargain.offers.models import ScrapingUrl


@pytest.mark.django_db
class TestAddScrapingUrl:
    def test_add_scraping_url(self, scraping_target):
        command = AddScrapingUrlCommand(url="https://example.com", target_id=scraping_target.id)
        actor = Actor(user_id=scraping_target.owner_id)

        result = add_scraping_url(command, actor)

        assert ScrapingUrl.objects.filter(id=result.id).exists()

    def test_add_scraping_url_target_not_found(self, db):
        command = AddScrapingUrlCommand(url="https://example.com", target_id=123)
        actor = Actor(user_id=1)

        with pytest.raises(ValueError, match="Target does not exist"):
            add_scraping_url(command, actor)
