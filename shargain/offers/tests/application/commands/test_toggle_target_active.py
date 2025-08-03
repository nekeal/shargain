import pytest

from shargain.offers.application.actor import Actor
from shargain.offers.application.commands.toggle_target_active import (
    toggle_target_active,
)
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.application.queries.get_target import get_target


@pytest.mark.django_db
class TestToggleTargetActive:
    def test_toggle_target_to_active_succeeds(self, scraping_target):
        scraping_target.is_active = False
        scraping_target.save()
        actor = Actor(user_id=scraping_target.owner_id)

        result = toggle_target_active(actor=actor, target_id=scraping_target.id, is_active=True)

        assert result is not None
        assert result.is_active is True

        target_dto = get_target(actor=actor, target_id=scraping_target.id)
        assert target_dto is not None
        assert target_dto.is_active is True

    def test_toggle_target_to_inactive_succeeds(self, scraping_target):
        scraping_target.is_active = True
        scraping_target.save()
        actor = Actor(user_id=scraping_target.owner_id)

        result = toggle_target_active(actor=actor, target_id=scraping_target.id, is_active=False)

        assert result is not None
        assert result.is_active is False

        target_dto = get_target(actor=actor, target_id=scraping_target.id)
        assert target_dto is not None
        assert target_dto.is_active is False

    def test_toggle_target_active_for_non_existent_target_raises_error(self):
        actor = Actor(user_id=1)

        with pytest.raises(TargetDoesNotExist):
            toggle_target_active(actor=actor, target_id=999, is_active=True)

    def test_toggle_target_active_for_other_user_target_raises_error(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id + 1)

        with pytest.raises(TargetDoesNotExist):
            toggle_target_active(actor=actor, target_id=scraping_target.id, is_active=True)
