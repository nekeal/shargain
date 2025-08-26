import pytest

from shargain.accounts.models import CustomUser
from shargain.accounts.tests.factories import UserFactory
from shargain.offers.models import ScrappingTarget
from shargain.offers.tests.factories import ScrappingTargetFactory


@pytest.fixture
def user(db) -> CustomUser:
    return UserFactory.create()


@pytest.fixture
def scraping_target(user) -> ScrappingTarget:
    return ScrappingTargetFactory(owner=user)
