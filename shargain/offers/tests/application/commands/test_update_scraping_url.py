import pytest

from shargain.offers.application.actor import Actor
from shargain.offers.application.commands.update_scraping_url import update_scraping_url
from shargain.offers.application.dto import ScrapingUrlDTO
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist
from shargain.offers.application.queries.get_target import get_target
from shargain.offers.tests.factories import ScrapingUrlFactory


@pytest.mark.django_db
class TestUpdateScrapingUrl:
    def test_update_scraping_url_name_succeeds(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, name="Old Name")
        actor = Actor(user_id=scraping_target.owner_id)
        new_name = "New Name"

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, name=new_name)

        assert result_dto.name == new_name

        target_dto = get_target(actor=actor, target_id=scraping_target.id)
        assert len(target_dto.urls) == 1
        assert target_dto.urls[0] == ScrapingUrlDTO(
            id=scraping_url.id,
            url=scraping_url.url,
            name=new_name,
        )

    def test_update_scraping_url_for_non_existent_url_raises_error(self):
        actor = Actor(user_id=1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            update_scraping_url(actor=actor, url_id=999, name="New Name")

    def test_update_scraping_url_for_other_user_url_raises_error(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id + 1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            update_scraping_url(actor=actor, url_id=scraping_url.id, name="New Name")
