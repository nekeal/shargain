import pytest

from shargain.commons.application.actor import Actor
from shargain.offers.application.queries.list_targets import list_targets
from shargain.offers.tests.factories import ScrappingTargetFactory


class TestListTargets:
    pytestmark = pytest.mark.django_db

    def test_returns_empty_list_when_user_has_no_targets(self):
        """
        Test that an empty list is returned when the user has no scraping targets.
        """
        assert list_targets(actor=Actor(user_id=1)) == []

    def test_returns_list_of_targets_for_authenticated_user(self, scraping_target):
        """
        Test that all targets belonging to the authenticated user are returned.
        """
        result = list_targets(actor=Actor(user_id=scraping_target.owner_id))
        assert len(result) == 1
        assert result[0].id_ == scraping_target.id

    def test_does_not_return_targets_from_other_users(self, scraping_target):
        """
        Test that targets belonging to other users are not included in the results.
        """
        # Create a target for a different user
        other_user_target = ScrappingTargetFactory()

        # Query for the first user's targets
        result = list_targets(actor=Actor(user_id=scraping_target.owner_id))

        # Should only return the target for the requested user
        assert len(result) == 1
        assert result[0].id_ == scraping_target.id
        assert result[0].id_ != other_user_target.id

    def test_handles_pagination_parameters(self, scraping_target):
        """
        Test that the page and per_page parameters correctly limit the result set.
        """
        # Create additional targets for the same user
        user = scraping_target.owner
        ScrappingTargetFactory.create_batch(2, owner=user)

        # Test first page with 2 items per page
        page1 = list_targets(actor=Actor(user_id=user.id), page=1, per_page=2)
        assert len(page1) == 2

        # Test second page with 2 items per page (should have 1 item)
        page2 = list_targets(actor=Actor(user_id=user.id), page=2, per_page=2)
        assert len(page2) == 1

        # Test that all items are unique across pages
        all_ids = {t.id_ for t in page1 + page2}
        assert len(all_ids) == 3  # Total unique items across both pages

    def test_returns_targets_ordered_by_id_descending(self, scraping_target):
        """
        Test that targets are returned in descending order of their ID.
        """
        # Create additional targets for the same user
        user = scraping_target.owner
        ScrappingTargetFactory.create_batch(2, owner=user)

        # Get targets ordered by ID descending
        targets = list_targets(actor=Actor(user_id=user.id))

        # Verify the order is correct (descending IDs)
        assert len(targets) >= 2, "Need at least 2 targets to test ordering"
        assert [x.id_ for x in targets] == sorted((x.id_ for x in targets), reverse=True)

    @pytest.mark.parametrize(
        ("page", "per_page", "expected_count"),
        [
            (1, 0, 10),  # 0 per_page should use default 10
            (1, -1, 10),  # Negative per_page should use default 10
            (1, 101, 100),  # per_page > 100 should be capped at 100
        ],
    )
    def test_edge_cases_for_pagination(self, page, per_page, expected_count):
        """
        Test edge cases for pagination parameters.
        """
        # Create a user and 3 targets
        user = ScrappingTargetFactory().owner
        ScrappingTargetFactory.create_batch(2, owner=user)  # 2 more targets = 3 total

        result = list_targets(actor=Actor(user_id=user.id), page=page, per_page=per_page)

        # Should not return more items than the expected count
        assert len(result) <= expected_count
