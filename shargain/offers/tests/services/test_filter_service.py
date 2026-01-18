"""Tests for OfferFilterService."""

import pytest

from shargain.offers.models import Offer, ScrapingUrl, ScrappingTarget
from shargain.offers.services.filter_service import OfferFilterService


@pytest.mark.django_db
class TestOfferFilterService:
    """Tests for the OfferFilterService class."""

    @pytest.fixture
    def scraping_target(self, django_user_model):
        """Create a scraping target for testing."""
        user = django_user_model.objects.create_user(username="testuser", password="testpass")
        return ScrappingTarget.objects.create(name="Test Target", owner=user, is_active=True)

    @pytest.fixture
    def scraping_url(self, scraping_target):
        """Create a scraping URL without filters."""
        return ScrapingUrl.objects.create(
            name="Test URL", url="https://example.com/search", scraping_target=scraping_target
        )

    @pytest.fixture
    def offer_apartment(self, scraping_target):
        """Create an offer with 'apartment' in title."""
        return Offer.objects.create(
            url="https://example.com/offer1",
            title="Beautiful apartment in city center",
            target=scraping_target,
            list_url="https://example.com/search",
        )

    @pytest.fixture
    def offer_studio(self, scraping_target):
        """Create an offer with 'studio apartment' in title."""
        return Offer.objects.create(
            url="https://example.com/offer2",
            title="Cozy studio apartment for rent",
            target=scraping_target,
            list_url="https://example.com/search",
        )

    @pytest.fixture
    def offer_flat(self, scraping_target):
        """Create an offer with 'flat' in title."""
        return Offer.objects.create(
            url="https://example.com/offer3",
            title="Modern flat with great view",
            target=scraping_target,
            list_url="https://example.com/search",
        )

    @pytest.fixture
    def offer_house(self, scraping_target):
        """Create an offer with 'house' in title."""
        return Offer.objects.create(
            url="https://example.com/offer4",
            title="Spacious house with garden",
            target=scraping_target,
            list_url="https://example.com/search",
        )

    def test_no_filters_passes_all(self, scraping_url, offer_apartment, offer_studio, offer_flat, offer_house):
        """Test that missing filters passes all offers."""
        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_studio, offer_flat, offer_house]
        filtered = service.apply_filters(offers)
        assert len(filtered) == 4

    def test_empty_rule_groups_passes_all(self, scraping_url, offer_apartment, offer_studio, offer_flat):
        """Test that empty ruleGroups array passes all offers."""
        scraping_url.filters = {"ruleGroups": []}
        scraping_url.save()
        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_studio, offer_flat]
        filtered = service.apply_filters(offers)
        assert len(filtered) == 3

    def test_filter_title_contains(self, scraping_url, offer_apartment, offer_studio, offer_house):
        """Test that 'contains' operator filters correctly."""
        scraping_url.filters = {
            "ruleGroups": [{"rules": [{"field": "title", "operator": "contains", "value": "apartment"}]}]
        }
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_studio, offer_house]
        filtered = service.apply_filters(offers)

        assert len(filtered) == 2
        assert offer_apartment in filtered
        assert offer_studio in filtered
        assert offer_house not in filtered

    def test_filter_title_not_contains(self, scraping_url, offer_apartment, offer_studio, offer_house):
        """Test that 'not_contains' operator filters correctly."""
        scraping_url.filters = {
            "ruleGroups": [{"rules": [{"field": "title", "operator": "not_contains", "value": "studio"}]}]
        }
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_studio, offer_house]
        filtered = service.apply_filters(offers)

        assert len(filtered) == 2
        assert offer_apartment in filtered
        assert offer_studio not in filtered
        assert offer_house in filtered

    def test_multiple_and_rules_in_single_group(self, scraping_url, offer_apartment, offer_studio, offer_house):
        """Test multiple rules with AND logic within a group."""
        scraping_url.filters = {
            "ruleGroups": [
                {
                    "rules": [
                        {"field": "title", "operator": "contains", "value": "apartment"},
                        {"field": "title", "operator": "not_contains", "value": "studio"},
                    ]
                }
            ]
        }
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_studio, offer_house]
        filtered = service.apply_filters(offers)

        # Only apartment (not studio apartment) should pass
        assert len(filtered) == 1
        assert offer_apartment in filtered
        assert offer_studio not in filtered  # Contains studio
        assert offer_house not in filtered  # Doesn't contain apartment

    def test_or_logic_between_groups(self, scraping_url, offer_apartment, offer_studio, offer_flat, offer_house):
        """Test that ANY passing group allows the offer through with OR logic."""
        scraping_url.filters = {
            "ruleGroups": [
                {
                    "logic": "and",
                    "logicWithNext": "or",
                    "rules": [
                        {"field": "title", "operator": "contains", "value": "apartment"},
                        {"field": "title", "operator": "not_contains", "value": "studio"},
                    ],
                },
                {"rules": [{"field": "title", "operator": "contains", "value": "flat"}]},
            ]
        }
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_studio, offer_flat, offer_house]
        filtered = service.apply_filters(offers)

        # apartment (group 1) and flat (group 2) should pass
        assert len(filtered) == 2
        assert offer_apartment in filtered
        assert offer_flat in filtered
        assert offer_studio not in filtered
        assert offer_house not in filtered

    def test_and_logic_between_groups(self, scraping_url, offer_apartment, offer_studio, offer_flat):
        """Test that ALL passing groups are required with AND logic."""
        offer_apartment_with_flat = Offer.objects.create(
            url="https://example.com/offer5",
            title="Modern apartment flat",
            target=scraping_url.scraping_target,
            list_url="https://example.com/search",
        )
        scraping_url.filters = {
            "ruleGroups": [
                {
                    "logic": "and",
                    "logicWithNext": "and",
                    "rules": [{"field": "title", "operator": "contains", "value": "apartment"}],
                },
                {"rules": [{"field": "title", "operator": "contains", "value": "flat"}]},
            ]
        }
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_studio, offer_flat, offer_apartment_with_flat]
        filtered = service.apply_filters(offers)

        # Only offer with both "apartment" and "flat" should pass
        assert len(filtered) == 1
        assert offer_apartment_with_flat in filtered

    def test_complex_filter_and_or_combination(
        self, scraping_url, offer_apartment, offer_studio, offer_flat, offer_house
    ):
        """Test (A AND B) OR C logic combinations."""
        offer_house_with_garden = Offer.objects.create(
            url="https://example.com/offer6",
            title="A beautiful house with a garden",
            target=scraping_url.scraping_target,
            list_url="https://example.com/search",
        )
        scraping_url.filters = {
            "ruleGroups": [
                {
                    "logic": "and",
                    "logicWithNext": "and",
                    "rules": [
                        {"field": "title", "operator": "contains", "value": "apartment"},
                    ],
                },
                {
                    "logic": "and",
                    "logicWithNext": "or",
                    "rules": [
                        {"field": "title", "operator": "not_contains", "value": "studio"},
                    ],
                },
                {
                    "logic": "and",
                    "rules": [
                        {"field": "title", "operator": "contains", "value": "house"},
                        {"field": "title", "operator": "contains", "value": "garden"},
                    ],
                },
            ]
        }
        # This evaluates to:
        # (contains "apartment" AND not contains "studio") OR (contains "house" AND contains "garden")
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_studio, offer_flat, offer_house, offer_house_with_garden]
        filtered = service.apply_filters(offers)

        # offer_apartment: passes (contains "apartment" and not "studio")
        # offer_house_with_garden: passes (contains "house" and "garden")
        # offer_house: passes (contains "house" and "garden")
        assert len(filtered) == 3
        assert offer_apartment in filtered
        assert offer_house_with_garden in filtered
        assert offer_house in filtered
        assert offer_studio not in filtered
        assert offer_flat not in filtered

    def test_single_rule_single_group(self, scraping_url, offer_apartment, offer_house):
        """Test simple filter with one rule in one group."""
        scraping_url.filters = {
            "ruleGroups": [{"rules": [{"field": "title", "operator": "contains", "value": "apartment"}]}]
        }
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        offers = [offer_apartment, offer_house]
        filtered = service.apply_filters(offers)

        assert len(filtered) == 1
        assert offer_apartment in filtered

    def test_case_insensitive_matching(self, scraping_url, scraping_target):
        """Test case-insensitive matching by default."""
        offer_upper = Offer.objects.create(
            url="https://example.com/offer_upper",
            title="LUXURY APARTMENT",
            target=scraping_target,
            list_url="https://example.com/search",
        )

        scraping_url.filters = {
            "ruleGroups": [{"rules": [{"field": "title", "operator": "contains", "value": "apartment"}]}]
        }
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        filtered = service.apply_filters([offer_upper])

        assert len(filtered) == 1
        assert offer_upper in filtered

    def test_unicode_and_special_chars(self, scraping_url, scraping_target):
        """Test filters with unicode and special characters."""
        offer_unicode = Offer.objects.create(
            url="https://example.com/offer_unicode",
            title="Apartament w Krakowie - świetna lokalizacja!",
            target=scraping_target,
            list_url="https://example.com/search",
        )

        scraping_url.filters = {
            "ruleGroups": [{"rules": [{"field": "title", "operator": "contains", "value": "świetna"}]}]
        }
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        filtered = service.apply_filters([offer_unicode])

        assert len(filtered) == 1
        assert offer_unicode in filtered

    def test_unknown_operator_raises_error(self, scraping_url, offer_apartment):
        """Test that unknown operators raise ValueError."""
        scraping_url.filters = {"ruleGroups": [{"rules": [{"field": "title", "operator": "equals", "value": "test"}]}]}
        scraping_url.save()

        service = OfferFilterService(scraping_url.filters)
        with pytest.raises(ValueError, match="Unknown operator"):
            service.apply_filters([offer_apartment])
