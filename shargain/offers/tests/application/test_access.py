import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.application.access import (
    can_delete_target,
    can_manage_target,
    can_manage_urls,
    can_view_target,
    get_user_role,
)
from shargain.offers.models import TargetRole
from shargain.offers.tests.factories import ScrappingTargetFactory
from shargain.offers.tests.helpers import grant_access


@pytest.mark.django_db
class TestTargetAccessPolicies:
    def test_owner_has_all_permissions(self):
        owner = UserFactory()
        target = ScrappingTargetFactory(owner=owner)

        assert get_user_role(owner.id, target) == "owner"
        assert can_view_target(owner.id, target) is True
        assert can_manage_urls(owner.id, target) is True
        assert can_manage_target(owner.id, target) is True
        assert can_delete_target(owner.id, target) is True

    def test_admin_role_permissions(self):
        admin_user = UserFactory()
        target = ScrappingTargetFactory()
        grant_access(target=target, user=admin_user, role=TargetRole.ADMIN)

        assert get_user_role(admin_user.id, target) == TargetRole.ADMIN
        assert can_view_target(admin_user.id, target) is True
        assert can_manage_urls(admin_user.id, target) is True
        assert can_manage_target(admin_user.id, target) is True
        assert can_delete_target(admin_user.id, target) is False

    def test_editor_role_permissions(self):
        editor_user = UserFactory()
        target = ScrappingTargetFactory()
        grant_access(target=target, user=editor_user, role=TargetRole.EDITOR)

        assert get_user_role(editor_user.id, target) == TargetRole.EDITOR
        assert can_view_target(editor_user.id, target) is True
        assert can_manage_urls(editor_user.id, target) is True
        assert can_manage_target(editor_user.id, target) is False
        assert can_delete_target(editor_user.id, target) is False

    def test_viewer_role_permissions(self):
        viewer_user = UserFactory()
        target = ScrappingTargetFactory()
        grant_access(target=target, user=viewer_user, role=TargetRole.VIEWER)

        assert get_user_role(viewer_user.id, target) == TargetRole.VIEWER
        assert can_view_target(viewer_user.id, target) is True
        assert can_manage_urls(viewer_user.id, target) is False
        assert can_manage_target(viewer_user.id, target) is False
        assert can_delete_target(viewer_user.id, target) is False

    def test_user_without_access_has_no_permissions(self):
        other_user = UserFactory()
        target = ScrappingTargetFactory()

        assert get_user_role(other_user.id, target) is None
        assert can_view_target(other_user.id, target) is False
        assert can_manage_urls(other_user.id, target) is False
        assert can_manage_target(other_user.id, target) is False
        assert can_delete_target(other_user.id, target) is False
