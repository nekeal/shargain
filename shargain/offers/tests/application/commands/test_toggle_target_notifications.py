"""Tests for the toggle_target_notifications command."""

import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.toggle_target_notifications import (
    toggle_target_notifications,
)
from shargain.offers.application.exceptions import TargetDoesNotExist
from shargain.offers.models import ScrappingTarget
from shargain.offers.tests.factories import ScrappingTargetFactory


@pytest.mark.django_db
class TestToggleTargetNotifications:
    """Test cases for the toggle_target_notifications command."""

    @pytest.fixture
    def user(self):
        """Create a user for testing."""
        return UserFactory()

    @pytest.fixture
    def target_with_notifications(self, user):
        """Create a target with notifications enabled."""
        return ScrappingTargetFactory(owner=user, enable_notifications=True, notification_config=None)

    @pytest.fixture
    def target_without_notifications(self, user):
        """Create a target with notifications disabled."""
        return ScrappingTargetFactory(owner=user, enable_notifications=False, notification_config=None)

    def test_toggle_enable_notifications(self, target_without_notifications):
        """Test enabling notifications."""
        actor = Actor(user_id=target_without_notifications.owner_id)
        result = toggle_target_notifications(actor, target_without_notifications.id, enable=True)
        assert result.enable_notifications is True
        target = ScrappingTarget.objects.get(id=target_without_notifications.id)
        assert target.enable_notifications is True

    def test_toggle_disable_notifications(self, target_with_notifications):
        """Test disabling notifications."""
        actor = Actor(user_id=target_with_notifications.owner_id)
        result = toggle_target_notifications(actor, target_with_notifications.id, enable=False)
        assert result.enable_notifications is False
        target = ScrappingTarget.objects.get(id=target_with_notifications.id)
        assert target.enable_notifications is False

    def test_toggle_notifications_toggle(self, target_with_notifications, target_without_notifications):
        """Test toggling notifications when enable is None."""
        # Test enabling
        actor = Actor(user_id=target_without_notifications.owner_id)
        result = toggle_target_notifications(actor, target_without_notifications.id)
        assert result.enable_notifications is True

        # Test disabling
        actor = Actor(user_id=target_with_notifications.owner_id)
        result = toggle_target_notifications(actor, target_with_notifications.id)
        assert result.enable_notifications is False

    def test_target_not_found_raises_error(self, user):
        """Test that a non-existent target raises an error."""
        actor = Actor(user_id=user.id)
        with pytest.raises(TargetDoesNotExist):
            toggle_target_notifications(actor, 99999)

    def test_target_belongs_to_different_user_raises_error(self, target_with_notifications):
        """Test that a target belonging to a different user raises an error."""
        other_user = UserFactory()
        actor = Actor(user_id=other_user.id)
        with pytest.raises(TargetDoesNotExist):
            toggle_target_notifications(actor, target_with_notifications.id)

    def test_updated_at_changes_on_toggle(self, target_with_notifications):
        """Test that updated_at is updated when notifications are toggled."""
        actor = Actor(user_id=target_with_notifications.owner_id)

        toggle_target_notifications(actor, target_with_notifications.id, enable=False)

        target = ScrappingTarget.objects.get(id=target_with_notifications.id)

        assert not target.enable_notifications

    def test_toggle_notifications_does_not_update_if_state_is_same(self, target_with_notifications):
        """Test that notifications are not updated if the state is already the same."""
        actor = Actor(user_id=target_with_notifications.owner_id)

        toggle_target_notifications(actor, target_with_notifications.id, enable=True)
