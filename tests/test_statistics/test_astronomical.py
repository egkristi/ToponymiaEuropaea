"""Tests for the astronomical alignment statistical test."""

import numpy as np

from toponymia.statistics.astronomical import (
    AstronomicalAlignmentTest,
    mean_direction,
    rayleigh_test,
)
from toponymia.statistics.base import TestData, TestFamily, TestStatus


class TestRayleighFunction:
    """Tests for the Rayleigh test implementation."""

    def test_uniform_distribution(self):
        """Uniform angles should not be significant."""
        angles = np.linspace(0, 2 * np.pi, 100, endpoint=False)
        r_bar, p_value = rayleigh_test(angles)
        assert p_value > 0.05
        assert r_bar < 0.2

    def test_concentrated_distribution(self):
        """Concentrated angles should be significant."""
        rng = np.random.default_rng(42)
        angles = rng.vonmises(np.pi / 2, 3.0, size=50)  # concentrated at 90°
        r_bar, p_value = rayleigh_test(angles)
        assert p_value < 0.05
        assert r_bar > 0.3

    def test_too_few_samples(self):
        """Should return non-significant for < 3 samples."""
        angles = np.array([1.0, 2.0])
        r_bar, p_value = rayleigh_test(angles)
        assert p_value == 1.0


class TestMeanDirection:
    """Tests for mean direction computation."""

    def test_east(self):
        """All angles at east (π/2) should give mean ~ π/2."""
        angles = np.array([np.pi / 2] * 10)
        result = mean_direction(angles)
        assert abs(result - np.pi / 2) < 0.01

    def test_north(self):
        """All angles at north (0) should give mean ~ 0."""
        angles = np.array([0.0] * 10)
        result = mean_direction(angles)
        assert result < 0.01 or result > 2 * np.pi - 0.01


class TestAstronomicalAlignmentTest:
    """Tests for the full AstronomicalAlignmentTest."""

    def setup_method(self):
        self.test = AstronomicalAlignmentTest()

    def test_metadata(self):
        assert self.test.test_id == "astronomical_alignment"
        assert self.test.test_family == TestFamily.ASTRONOMICAL_ALIGNMENT
        assert (
            "solstice" in self.test.description.lower()
            or "astronomical" in self.test.description.lower()
        )

    def test_concentrated_signal_detected(self):
        """Should detect concentrated bearings at element-bearing sites."""
        rng = np.random.default_rng(42)
        n = 100
        n_elem = 30

        coords = rng.uniform(0, 10, size=(n, 2))
        element_present = np.zeros(n, dtype=bool)
        element_present[:n_elem] = True

        # Element-bearing sites: concentrated around 90° (east = equinox sunrise)
        bearings = rng.uniform(0, 360, size=n)
        bearings[:n_elem] = np.rad2deg(rng.vonmises(np.deg2rad(90), 3.0, size=n_elem)) % 360

        data = TestData(
            coordinates=coords,
            element_present=element_present,
            signal_values=bearings,
            region="test",
            element_name="sol-",
        )

        result = self.test.run(data, n_permutations=999)
        assert result.p_value < 0.05
        assert result.test_statistic > 0.2  # R-bar should be notable
        assert "mean_direction_deg" in result.parameters

    def test_uniform_not_detected(self):
        """Should not detect signal when bearings are uniform."""
        rng = np.random.default_rng(42)
        n = 100
        n_elem = 30

        coords = rng.uniform(0, 10, size=(n, 2))
        element_present = np.zeros(n, dtype=bool)
        element_present[:n_elem] = True

        # All bearings uniform — no concentration
        bearings = rng.uniform(0, 360, size=n)

        data = TestData(
            coordinates=coords,
            element_present=element_present,
            signal_values=bearings,
            region="test",
            element_name="control",
        )

        result = self.test.run(data, n_permutations=999)
        assert result.p_value > 0.05

    def test_insufficient_samples(self):
        """Should return inconclusive with too few element sites."""
        coords = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])
        element_present = np.array([True, True, False, False])
        bearings = np.array([90.0, 91.0, 180.0, 270.0])

        data = TestData(
            coordinates=coords,
            element_present=element_present,
            signal_values=bearings,
            region="test",
            element_name="sol-",
        )

        result = self.test.run(data, n_permutations=99)
        assert result.status == TestStatus.INCONCLUSIVE

    def test_missing_signal_values(self):
        """Should raise ValueError without signal_values."""
        import pytest

        coords = np.array([[0, 0], [1, 1]])
        element_present = np.array([True, False])

        data = TestData(
            coordinates=coords,
            element_present=element_present,
            signal_values=None,
        )

        with pytest.raises(ValueError, match="signal_values"):
            self.test.run(data)

    def test_validate_synthetic(self):
        """Synthetic validation should pass with adequate power."""
        validation = self.test.validate_synthetic(n_trials=20)
        assert validation.power >= 0.7  # Relaxed for speed (20 trials)
        assert validation.false_positive_rate <= 0.20
        # Full 100-trial validation should pass stricter thresholds
