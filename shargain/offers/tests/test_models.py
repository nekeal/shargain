import pytest
from django.utils import timezone

from shargain.offers.models import Offer, ScrappingTarget


@pytest.fixture
def test_target():
    """Create a test ScrappingTarget instance."""
    return ScrappingTarget.objects.create(
        name="Test Target",
        url=["https://example.com"],
        enable_notifications=True,
        is_active=True,
    )


@pytest.fixture
def offer_data(test_target):
    """Provide default offer data for tests."""
    return {
        "url": "https://example.com/offer/123",
        "title": "Test Offer",
        "price": 1000,
        "main_image_url": "https://example.com/image.jpg",
        "list_url": "https://example.com/offers",
        "target": test_target,
        "published_at": timezone.now(),
    }


@pytest.mark.django_db
def test_create_offer_without_list_url(offer_data):
    """Test that list_url is optional when creating an offer."""
    offer_data.pop("list_url")
    offer = Offer.objects.create(**offer_data)

    assert offer.list_url == ""
