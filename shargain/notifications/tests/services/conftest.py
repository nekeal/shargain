import pytest

from shargain.notifications.services.notifications import NewOfferNotificationService
from shargain.notifications.tests.factories import NotificationConfigFactory
from shargain.offers.tests.factories import OfferFactory, ScrappingTargetFactory


@pytest.fixture
def offer():
    return OfferFactory.build()


@pytest.fixture
def notification_service(db):
    config = NotificationConfigFactory()
    target = ScrappingTargetFactory(notification_config=config)
    return NewOfferNotificationService([], target, "NOTIFICATION TITLE")
