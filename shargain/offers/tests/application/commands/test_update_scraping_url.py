import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.update_scraping_url import update_scraping_url
from shargain.offers.application.dto import ScrapingUrlDTO, WaypointData
from shargain.offers.application.exceptions import ScrapingUrlDoesNotExist, TargetPermissionDenied
from shargain.offers.application.queries.get_target import get_target
from shargain.offers.models import TargetRole
from shargain.offers.tests.factories import ScrapingUrlFactory
from shargain.offers.tests.helpers import grant_access


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
        normalized_filters = {
            "ruleGroups": [
                {
                    "logic": "and",
                    "logicWithNext": None,
                    "rules": [{"case_sensitive": False, "field": "title", "operator": "contains", "value": "test"}],
                }
            ]
        }

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, filters=new_filters)

        assert result_dto.filters == normalized_filters

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

    def test_update_scraping_url_notification_fields_succeeds(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)
        new_notification_fields = {"fields": ["title", "price"]}

        result_dto = update_scraping_url(
            actor=actor, url_id=scraping_url.id, notification_fields=new_notification_fields
        )

        assert result_dto.notification_fields == new_notification_fields

    def test_update_scraping_url_send_map_succeeds(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, send_map_in_notifications=True)
        actor = Actor(user_id=scraping_target.owner_id)

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, send_map_in_notifications=False)

        assert result_dto.send_map_in_notifications is False

    def test_update_scraping_url_preserves_send_map_when_omitted(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, send_map_in_notifications=False)
        actor = Actor(user_id=scraping_target.owner_id)

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, name="New name")

        assert result_dto.send_map_in_notifications is False

    def test_update_scraping_url_for_non_existent_url_raises_error(self):
        actor = Actor(user_id=1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            update_scraping_url(actor=actor, url_id=999, name="New Name")

    def test_update_scraping_url_for_other_user_url_raises_error(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id + 1)

        with pytest.raises(ScrapingUrlDoesNotExist):
            update_scraping_url(actor=actor, url_id=scraping_url.id, name="New Name")

    def test_update_scraping_url_by_editor_succeeds(self, scraping_target):
        editor = UserFactory()
        grant_access(target=scraping_target, user=editor, role=TargetRole.EDITOR)
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, name="Old Name")
        actor = Actor(user_id=editor.id)

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, name="Editor Name")
        assert result_dto.name == "Editor Name"
        scraping_url.refresh_from_db()
        assert scraping_url.name == "Editor Name"

    def test_update_scraping_url_by_viewer_raises_permission_denied(self, scraping_target):
        viewer = UserFactory()
        grant_access(target=scraping_target, user=viewer, role=TargetRole.VIEWER)
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, name="Old Name")
        actor = Actor(user_id=viewer.id)

        with pytest.raises(TargetPermissionDenied):
            update_scraping_url(actor=actor, url_id=scraping_url.id, name="Viewer Name")
        scraping_url.refresh_from_db()
        assert scraping_url.name == "Old Name"

    def test_update_scraping_url_with_mismatched_target_id_raises_error(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target, name="Old Name")
        actor = Actor(user_id=scraping_target.owner_id)

        with pytest.raises(ScrapingUrlDoesNotExist):
            update_scraping_url(
                actor=actor,
                url_id=scraping_url.id,
                target_id=scraping_target.id + 999,
                name="New Name",
            )
        scraping_url.refresh_from_db()
        assert scraping_url.name == "Old Name"

    def test_update_scraping_url_with_invalid_filters_raises_error(self, scraping_target):
        scraping_url = ScrapingUrlFactory(
            scraping_target=scraping_target,
            url="https://www.olx.pl/d/nieruchomosci/mieszkania/",
            filters=None,
        )
        actor = Actor(user_id=scraping_target.owner_id)
        invalid_filters = {
            "ruleGroups": [
                {"logic": "and", "rules": [{"field": "nonexistent_field", "operator": "contains", "value": "x"}]}
            ]
        }

        with pytest.raises(ValueError, match="not available for this URL"):
            update_scraping_url(actor=actor, url_id=scraping_url.id, filters=invalid_filters)

        scraping_url.refresh_from_db()
        assert scraping_url.filters is None

    def test_update_scraping_url_url_succeeds(self, scraping_target):
        scraping_url = ScrapingUrlFactory(
            scraping_target=scraping_target,
            url="https://www.olx.pl/d/nieruchomosci/mieszkania/?search%5Bfilter_float_price%3Ato%5D=500000",
        )
        actor = Actor(user_id=scraping_target.owner_id)
        new_url = "https://www.olx.pl/d/nieruchomosci/mieszkania/?search%5Bfilter_float_price%3Ato%5D=600000"

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, url=new_url)

        assert result_dto.url == new_url
        scraping_url.refresh_from_db()
        assert scraping_url.url == new_url

    def test_update_scraping_url_too_long_raises_error(self, scraping_target):
        scraping_url = ScrapingUrlFactory(scraping_target=scraping_target)
        actor = Actor(user_id=scraping_target.owner_id)
        too_long_url = "https://www.olx.pl/d/nieruchomosci/?" + "a=1&" * 300

        with pytest.raises(ValueError, match="1024"):
            update_scraping_url(actor=actor, url_id=scraping_url.id, url=too_long_url)

    @pytest.mark.parametrize(
        "modified_url",
        [
            "http://www.olx.pl/d/nieruchomosci/mieszkania/?page=1",
            "https://www.otodom.pl/d/nieruchomosci/mieszkania/?page=1",
            "https://www.olx.pl/d/nieruchomosci/domy/?page=1",
            "https://www.olx.pl/d/nieruchomosci/mieszkania/;jsessionid=123?page=1",
            "https://www.olx.pl/d/nieruchomosci/mieszkania/?page=1#section",
        ],
    )
    def test_update_scraping_url_changing_main_part_raises_error(self, scraping_target, modified_url):
        original_url = "https://www.olx.pl/d/nieruchomosci/mieszkania/?page=1"
        scraping_url = ScrapingUrlFactory(
            scraping_target=scraping_target,
            url=original_url,
        )
        actor = Actor(user_id=scraping_target.owner_id)

        with pytest.raises(ValueError, match="Only query parameters can be modified"):
            update_scraping_url(actor=actor, url_id=scraping_url.id, url=modified_url)

        scraping_url.refresh_from_db()
        assert scraping_url.url == original_url

    def test_update_scraping_url_allows_empty_param_value(self, scraping_target):
        scraping_url = ScrapingUrlFactory(
            scraping_target=scraping_target,
            url="https://www.olx.pl/d/nieruchomosci/mieszkania/?page=1",
        )
        actor = Actor(user_id=scraping_target.owner_id)
        new_url = "https://www.olx.pl/d/nieruchomosci/mieszkania/?page="

        result_dto = update_scraping_url(actor=actor, url_id=scraping_url.id, url=new_url)

        assert result_dto.url == new_url
        scraping_url.refresh_from_db()
        assert scraping_url.url == new_url
