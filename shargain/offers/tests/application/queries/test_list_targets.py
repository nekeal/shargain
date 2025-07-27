class TestListTargets:
    """Test cases for the list_targets query handler."""

    def test_returns_empty_list_when_user_has_no_targets(self):
        """
        Test that an empty list is returned when the user has no scraping targets.
        """
        pass

    def test_returns_list_of_targets_for_authenticated_user(self):
        """
        Test that all targets belonging to the authenticated user are returned.
        """
        pass

    def test_does_not_return_targets_from_other_users(self):
        """
        Test that targets belonging to other users are not included in the results.
        """
        pass

    def test_handles_pagination_parameters(self):
        """
        Test that the page and per_page parameters correctly limit the result set.
        """
        pass

    def test_returns_targets_ordered_by_id_descending(self):
        """
        Test that targets are returned in descending order of their last update time.
        """
        pass
