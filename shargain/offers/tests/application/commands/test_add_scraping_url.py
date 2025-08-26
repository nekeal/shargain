import pytest

from shargain.offers.application.actor import Actor
from shargain.offers.application.commands.add_scraping_url import add_scraping_url
from shargain.offers.application.dto import ScrapingUrlDTO
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.application.queries.get_target import get_target


@pytest.mark.django_db
class TestAddScrapingUrl:
    def test_add_scraping_url_succeeds(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id)
        url = "https://example.com"
        name = "Example URL"

        result_dto = add_scraping_url(actor=actor, target_id=scraping_target.id, url=url, name=name)

        target_dto = get_target(actor=actor, target_id=scraping_target.id)
        assert target_dto is not None
        assert len(target_dto.urls) == 1
        assert target_dto.urls[0] == ScrapingUrlDTO(
            id=result_dto.id,
            url=url,
            name=name,
            is_active=True,
        )

    def test_add_scraping_url_with_no_name_defaults_to_url(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id)
        url = "https://example.com"

        result_dto = add_scraping_url(actor=actor, target_id=scraping_target.id, url=url)

        target_dto = get_target(actor=actor, target_id=scraping_target.id)
        assert target_dto is not None
        assert len(target_dto.urls) == 1
        assert target_dto.urls[0] == ScrapingUrlDTO(
            id=result_dto.id,
            url=url,
            name="",
            is_active=True,
        )

    def test_add_scraping_url_to_non_existent_target_raises_error(self):
        actor = Actor(user_id=1)

        with pytest.raises(TargetDoesNotExist):
            add_scraping_url(actor=actor, target_id=999, url="https://example.com")

    def test_add_scraping_url_to_other_user_target_raises_error(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id + 1)

        with pytest.raises(TargetDoesNotExist):
            add_scraping_url(actor=actor, target_id=scraping_target.id, url="https://example.com")
