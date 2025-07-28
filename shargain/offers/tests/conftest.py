import pytest

from shargain.offers.models import ScrappingTarget
from shargain.offers.tests.factories import ScrappingTargetFactory


@pytest.fixture
def scraping_target(db) -> ScrappingTarget:
    return ScrappingTargetFactory()
