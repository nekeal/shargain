"""Tests for geo utility functions."""

import pytest

from shargain.offers.services.geo_utils import haversine


class TestHaversine:
    """Tests for the haversine distance function."""

    def test_same_point_returns_zero(self):
        """Same point should have distance 0."""
        lat, lon = 52.229, 21.012
        assert haversine(lat, lon, lat, lon) == 0.0

    def test_warsaw_to_krakow(self):
        """Warsaw to Krakow should be approximately 252 km."""
        distance = haversine(52.229, 21.012, 50.064, 19.945)
        assert distance == pytest.approx(252, abs=1)

    def test_north_pole_to_equator(self):
        """North Pole to Equator should be approximately 10007.5 km."""
        distance = haversine(90.0, 0.0, 0.0, 0.0)
        assert distance == pytest.approx(10007.5, abs=1)
