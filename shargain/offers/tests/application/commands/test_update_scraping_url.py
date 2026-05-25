import pytest

from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.update_scraping_url import update_scraping_url
from shargain.offers.application.dto import ScrapingUrlDTO, WaypointData
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
            is_active=scraping_url.is_active,
            name=new_name,
            show_location_map_in_notifications=scraping_url.show_location_map_in_notifications,
            waypoints=scraping_url.waypoints,
        )

    def test_update_scraping_url_filters_succeeds(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)
        new_filters = {
            "ruleGroups": [{"logic": "and", "rules": [{"field": "title", "operator": "contains", "value": "test"}]}]
        }

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, filters=new_filters)

        assert result_dto.filters == new_filters

    def test_update_scraping_url_location_map_succeeds(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, show_location_map_in_notifications=False)
        actor = Actor(user_id=scraping_target.owner_id)

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, show_location_map_in_notifications=True)

        assert result_dto.show_location_map_in_notifications is True

    def test_update_scraping_url_waypoints_succeeds(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)
        new_waypoints: list[WaypointData] = [
            {"name": "Metro Centrum", "lat": 52.23, "lon": 21.00},
            {"name": "Office", "lat": 52.19, "lon": 21.04},
        ]

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, waypoints=new_waypoints)

        assert result_dto.waypoints == new_waypoints

    def test_update_scraping_url_for_non_existent_url_raises_error(self):
        actor = Actor(user_id=1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            update_scraping_url(actor=actor, url_id=999, name="New Name")

    def test_update_scraping_url_for_other_user_url_raises_error(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id + 1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            update_scraping_url(actor=actor, url_id=scraping_url.id, name="New Name")
