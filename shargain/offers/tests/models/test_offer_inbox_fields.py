import pytest

from shargain.offers.models import Offer
from shargain.offers.tests.factories import ScrappingTargetFactory


@pytest.mark.django_db
def test_offer_passed_filters_defaults_to_none():
    target = ScrappingTargetFactory()
    offer = Offer.objects.create(
        url="https://example.com/item/1",
        title="Test Item",
        target=target,
    )
    offer.refresh_from_db()
    assert offer.passed_filters is None


@pytest.mark.django_db
def test_offer_inbox_index_exists():
    index_names = [idx.name for idx in Offer._meta.indexes]
    assert "offer_inbox_idx" in index_names
    inbox_idx = next(idx for idx in Offer._meta.indexes if idx.name == "offer_inbox_idx")
    assert inbox_idx.fields == ["target", "passed_filters", "created_at", "id"]
