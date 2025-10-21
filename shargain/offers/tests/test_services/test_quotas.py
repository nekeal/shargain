from datetime import timedelta

import pytest
from django.utils import timezone

from shargain.accounts.tests.factories import UserFactory
from shargain.offers.models import Offer, ScrappingTarget
from shargain.offers.services.offers_batch_create import OfferBatchCreateService
from shargain.offers.services.quota import QuotaService
from shargain.offers.tests.factories import OfferQuotaFactory


@pytest.fixture
def user():
    return UserFactory(username="testuser", email="test@example.com", password="testpass123")


@pytest.fixture
def target(user):
    """Create a test target."""
    target = ScrappingTarget.objects.create(name="Test Target", owner=user)
    return target


@pytest.fixture
def active_quota(target):
    return OfferQuotaFactory.create_active(target=target)


@pytest.fixture
def expired_quota(target):
    return OfferQuotaFactory.create_expired(target=target)


@pytest.fixture
def future_quota(target):
    return OfferQuotaFactory.create_future(target=target)


@pytest.fixture
def indefinite_quota(target):
    return OfferQuotaFactory.create_indefinite(target=target)


@pytest.fixture
def unlimited_quota(target):
    return OfferQuotaFactory.create_unlimited(target=target)


@pytest.fixture
def indefinite_unlimited_quota(target):
    return OfferQuotaFactory.create_indefinite_unlimited(target=target)


@pytest.mark.django_db
class TestQuotaService:
    def test_get_active_quota_returns_infinite_quota_when_no_quota_exists(self, user, target):
        """Test that get_active_quota returns None when no quota exists."""
        quota = QuotaService.get_active_quota(target)
        assert quota.remaining_offers == float("inf")

    def test_get_active_quota_returns_active_quota(self, active_quota):
        """Test that get_active_quota returns the active quota."""
        result = QuotaService.get_active_quota(active_quota.target)
        assert result
        assert result.id == active_quota.id

    def test_get_active_quota_returns_infinite_quota_when_quota_is_expired(self, expired_quota):
        """Test that get_active_quota returns None when quota is expired."""
        result = QuotaService.get_active_quota(expired_quota.target)
        assert result.remaining_offers == float("inf")

    def test_get_active_quota_returns_infinite_quota_when_quota_not_yet_started(self, future_quota):
        """Test that get_active_quota returns None when quota period hasn't started."""
        result = QuotaService.get_active_quota(future_quota.target)
        assert result.remaining_offers == float("inf")

    def test_set_new_quota_creates_quota(self, target):
        """Test that set_new_quota creates a new quota."""
        period_start = timezone.now() - timedelta(hours=1)
        period_end = timezone.now() + timedelta(hours=1)

        quota = QuotaService.set_new_quota(
            target=target, max_offers_per_period=5, period_start=period_start, period_end=period_end
        )

        result = QuotaService.get_active_quota(target)
        assert result
        assert result.id == quota.pk
        assert result.remaining_offers == 5

    def test_set_new_quota_updates_existing_quota(self, target):
        """Test that set_new_quota updates an existing quota."""
        period_start = timezone.now() - timedelta(hours=1)
        period_end = timezone.now() + timedelta(hours=1)

        original_quota = QuotaService.set_new_quota(
            target=target, max_offers_per_period=5, period_start=period_start, period_end=period_end
        )

        updated_quota = QuotaService.set_new_quota(
            target=target,
            period_start=period_start,
            period_end=period_end,
            max_offers_per_period=10,
            used_offers_count=3,
        )

        assert updated_quota.pk == original_quota.pk
        assert updated_quota.max_offers_per_period == 10
        assert updated_quota.used_offers_count == 3

    def test_increment_usage_increments_count(self, active_quota):
        """Test that increment_usage increments the count."""
        initial_quota = QuotaService.get_active_quota(active_quota.target)
        assert initial_quota

        QuotaService.increment_usage(active_quota.id, 3)
        updated_quota = QuotaService.get_active_quota(active_quota.target)
        assert updated_quota
        assert updated_quota.remaining_offers == initial_quota.remaining_offers - 3

    def test_increment_usage_can_exceed_max_limit(self):
        """Test that increment_usage can exceed the maximum."""
        quota = OfferQuotaFactory.create_active(
            max_offers_per_period=3,
            used_offers_count=2,
        )
        QuotaService.increment_usage(quota.pk, 3)

        updated_quota = QuotaService.get_active_quota(quota.target)
        assert updated_quota
        assert updated_quota.remaining_offers == 0

    def test_is_quota_available_returns_true_when_no_quota_exists(self, target):
        """Test that is_quota_available returns True when no quota exists (unlimited)."""
        result = QuotaService.is_quota_available(target)
        assert result is True

    def test_is_quota_available_returns_true_when_quota_available(self):
        """Test that is_quota_available returns True when quota exists and is available."""
        quota = OfferQuotaFactory.create_active(
            max_offers_per_period=5,
            used_offers_count=2,  # 3 remaining
        )

        result = QuotaService.is_quota_available(quota.target)
        assert result is True

    def test_is_quota_available_returns_false_when_quota_exhausted(self):
        """Test that is_quota_available returns False when quota is exhausted."""
        quota = OfferQuotaFactory.create_active(
            max_offers_per_period=2,
            used_offers_count=2,  # No remaining
        )

        result = QuotaService.is_quota_available(quota.target)
        assert result is False

    def test_is_quota_available_returns_true_for_unlimited_quota(self):
        """Test that is_quota_available returns True for unlimited quota."""
        quota = OfferQuotaFactory.create_unlimited(
            used_offers_count=100,  # Even with high usage
        )

        result = QuotaService.is_quota_available(quota.target)
        assert result is True


@pytest.mark.django_db
class TestOfferCreationWithQuota:
    def test_offer_creation_respects_quota_limit(self):
        """Test that offer creation is limited by quota."""
        quota = OfferQuotaFactory.create_active(
            max_offers_per_period=2,
            used_offers_count=1,
        )
        service = OfferBatchCreateService(
            serializer_kwargs={
                "data": {
                    "target": quota.target.pk,
                    "offers": [
                        {
                            "url": "https://example.com/offer1",
                            "title": "Test Offer 1",
                            "price": 1000,
                            "list_url": "https://example.com/list1",
                        }
                    ],
                }
            }
        )
        result = service.run()
        quota.refresh_from_db()
        assert len(result) == 1

        # Create third offer - should be rejected due to quota limit
        service = OfferBatchCreateService(
            serializer_kwargs={
                "data": {
                    "target": quota.target.pk,
                    "offers": [
                        {
                            "url": "https://example.com/offer3",
                            "title": "Test Offer 3",
                            "price": 3000,
                            "list_url": "https://example.com/list1",
                        }
                    ],
                }
            }
        )
        result = service.run()
        quota.refresh_from_db()
        assert len(result) == 0  # No new offers created

    def test_offer_creation_with_no_quota_allows_unlimited_offers(self, target):
        """Test that offer creation is unlimited when no quota exists."""
        offer_data = {
            "url": "https://example.com/offer1",
            "title": "Test Offer 1",
            "price": 1000,
            "list_url": "https://example.com/list1",
        }
        service = OfferBatchCreateService(
            serializer_kwargs={
                "data": {
                    "target": target.pk,
                    "offers": [
                        offer_data,
                        offer_data | {"url": "https://example.com/offer2"},
                        offer_data | {"url": "https://example.com/offer3"},
                    ],
                }
            }
        )
        result = service.run()
        assert len(result) == 3

    def test_existing_offers_not_counted_towards_quota(self, user, target):
        """Test that existing offers (not newly created) don't affect quota."""
        Offer.objects.create(url="https://example.com/existing", title="Existing Offer", target=target)

        now = timezone.now()
        QuotaService.set_new_quota(
            target=target,
            max_offers_per_period=2,
            used_offers_count=1,
            period_start=now - timedelta(days=1),
            period_end=now + timedelta(days=1),
        )

        # Create new offer - should succeed since existing offer doesn't count
        service = OfferBatchCreateService(
            serializer_kwargs={
                "data": {
                    "target": target.pk,
                    "offers": [
                        {
                            "url": "https://example.com/new1",
                            "title": "New Offer 1",
                            "price": 1000,
                            "list_url": "https://example.com/list1",
                        }
                    ],
                }
            }
        )
        result = service.run()
        assert len(result) == 1

        service = OfferBatchCreateService(
            serializer_kwargs={
                "data": {
                    "target": target.pk,
                    "offers": [
                        {
                            "url": "https://example.com/new2",
                            "title": "New Offer 2",
                            "price": 2000,
                            "list_url": "https://example.com/list1",
                        }
                    ],
                }
            }
        )
        result = service.run()
        assert len(result) == 0
