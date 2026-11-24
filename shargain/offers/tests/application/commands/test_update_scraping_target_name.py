import pytest
from telebot.types import User

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.update_scraping_target_name import (
    update_scraping_target_name,
)
from shargain.offers.application.exceptions import TargetDoesNotExist, TargetPermissionDenied
from shargain.offers.models import ScrappingTarget, TargetRole
from shargain.offers.tests.factories import ScrappingTargetFactory
from shargain.offers.tests.helpers import grant_access


class TestUpdateScrapingTargetName:
    def test_update_scraping_target_name(self, scraping_target: ScrappingTarget, user: User):
        """Test that the scraping target name is updated successfully."""
        update_scraping_target_name(Actor(user.id), scraping_target.pk, "New Name")
        scraping_target.refresh_from_db()
        assert scraping_target.name == "New Name"

    def test_update_scraping_target_name_when_target_not_found(self, user: User):
        """Test that an exception is raised when the scraping target is not found."""
        with pytest.raises(TargetDoesNotExist):
            update_scraping_target_name(Actor(user_id=1), 9999, "new name")

    def test_update_scraping_target_does_not_exist_for_different_user(
        self, scraping_target: ScrappingTarget, user: User
    ):
        """Test that an exception is raised when the scraping target does not exist for the user."""

        different_scraping_target = ScrappingTargetFactory.create()
        assert different_scraping_target.owner != user

        with pytest.raises(TargetDoesNotExist):
            update_scraping_target_name(Actor(user.id), different_scraping_target.pk, "New Name")

    def test_admin_can_update_target_name(self, scraping_target: ScrappingTarget):
        admin = UserFactory()
        grant_access(target=scraping_target, user=admin, role=TargetRole.ADMIN)
        update_scraping_target_name(Actor(admin.id), scraping_target.pk, "Admin Name")
        scraping_target.refresh_from_db()
        assert scraping_target.name == "Admin Name"

    def test_editor_cannot_update_target_name(self, scraping_target: ScrappingTarget):
        editor = UserFactory()
        grant_access(target=scraping_target, user=editor, role=TargetRole.EDITOR)
        with pytest.raises(TargetPermissionDenied):
            update_scraping_target_name(Actor(editor.id), scraping_target.pk, "Editor Name")

    def test_viewer_cannot_update_target_name(self, scraping_target: ScrappingTarget):
        viewer = UserFactory()
        grant_access(target=scraping_target, user=viewer, role=TargetRole.VIEWER)
        with pytest.raises(TargetPermissionDenied):
            update_scraping_target_name(Actor(viewer.id), scraping_target.pk, "Viewer Name")
