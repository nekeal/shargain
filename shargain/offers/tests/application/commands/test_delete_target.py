import pytest

from shargain.accounts.tests.factories import UserFactory
from shargain.commons.application.actor import Actor
from shargain.offers.application.commands.delete_target import delete_target
from shargain.offers.application.exceptions import TargetPermissionDenied
from shargain.offers.models import ScrappingTarget, TargetRole
from shargain.offers.tests.factories import TargetAccessFactory


@pytest.mark.django_db
class TestDeleteTarget:
    def test_delete_target(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id)
        delete_target(actor, scraping_target.id)
        assert not ScrappingTarget.objects.filter(id=scraping_target.id).exists()

    def test_delete_target_not_found(self, db):
        actor = Actor(user_id=1)
        delete_target(actor, 123)
        assert not ScrappingTarget.objects.filter(id=123).exists()

    def test_delete_target_other_user(self, scraping_target):
        actor = Actor(user_id=scraping_target.owner_id + 1)
        delete_target(actor, scraping_target.id)
        assert ScrappingTarget.objects.filter(id=scraping_target.id).exists()

    def test_admin_member_cannot_delete_target(self, scraping_target):
        """Only the target owner can delete a target; admin members are denied."""
        admin = UserFactory()
        TargetAccessFactory(target=scraping_target, user=admin, role=TargetRole.ADMIN)
        actor = Actor(user_id=admin.id)

        with pytest.raises(TargetPermissionDenied):
            delete_target(actor, scraping_target.id)
        assert ScrappingTarget.objects.filter(id=scraping_target.id).exists()
