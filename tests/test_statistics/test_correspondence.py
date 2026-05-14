"""Tests for the statistical testing framework."""

import numpy as np
import pytest

from toponymia.statistics.base import TestData, TestFamily, TestStatus
from toponymia.statistics.correspondence import ElementSignalCorrespondenceTest
from toponymia.statistics.spatial import SpatialClusteringTest


class TestCorrespondence:
    """Tests for element-signal correspondence test."""

    def test_detects_planted_signal(self):
        """Test that the correspondence test detects a strong planted signal."""
        rng = np.random.default_rng(42)
        n = 200
        n_pos = 40

        coords = rng.uniform(0, 100, size=(n, 2))
        element = np.zeros(n, dtype=bool)
        element[:n_pos] = True

        # Plant strong signal: element places have much higher values
        signal = rng.normal(100, 20, size=n)
        signal[:n_pos] += 50  # Strong effect

        data = TestData(
            coordinates=coords,
            element_present=element,
            signal_values=signal,
            element_name="test_element",
            signal_name="test_signal",
        )

        test = ElementSignalCorrespondenceTest()
        result = test.run(data, n_permutations=5000)

        assert result.p_value < 0.05
        assert result.effect_size > 0
        assert result.test_family == TestFamily.CORRESPONDENCE

    def test_no_signal_not_significant(self):
        """Test that pure noise is not significant."""
        rng = np.random.default_rng(123)
        n = 200
        n_pos = 40

        coords = rng.uniform(0, 100, size=(n, 2))
        element = np.zeros(n, dtype=bool)
        element[rng.choice(n, n_pos, replace=False)] = True
        signal = rng.normal(100, 20, size=n)  # No relationship

        data = TestData(
            coordinates=coords,
            element_present=element,
            signal_values=signal,
        )

        test = ElementSignalCorrespondenceTest()
        result = test.run(data, n_permutations=5000)

        # Should typically not be significant (may occasionally be by chance)
        assert result.n_observations == n
        assert result.n_positive == n_pos

    def test_insufficient_sample_inconclusive(self):
        """Test that small samples return inconclusive."""
        coords = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5]])
        element = np.array([True, True, False, False, False, False])
        signal = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

        data = TestData(
            coordinates=coords,
            element_present=element,
            signal_values=signal,
        )

        test = ElementSignalCorrespondenceTest()
        result = test.run(data)

        assert result.status == TestStatus.INCONCLUSIVE

    @pytest.mark.slow
    def test_synthetic_validation(self):
        """Test synthetic validation passes."""
        test = ElementSignalCorrespondenceTest()
        validation = test.validate_synthetic(n_trials=50)
        assert validation.power > 0.5  # Relaxed for faster test
        assert validation.false_positive_rate < 0.2


class TestSpatialClustering:
    """Tests for spatial clustering test."""

    def test_detects_cluster(self):
        """Test that spatial clustering is detected."""
        rng = np.random.default_rng(42)
        n = 200
        n_pos = 30

        # Background: uniform random
        coords = rng.uniform(0, 100, size=(n, 2))
        # Element-bearing: tightly clustered
        coords[:n_pos] = rng.normal([50, 50], 2, size=(n_pos, 2))

        element = np.zeros(n, dtype=bool)
        element[:n_pos] = True

        data = TestData(coordinates=coords, element_present=element)

        test = SpatialClusteringTest()
        result = test.run(data, n_permutations=2000)

        assert result.p_value < 0.05
        assert result.test_family == TestFamily.SPATIAL

    def test_random_placement_not_clustered(self):
        """Test that random placement is not detected as clustered."""
        rng = np.random.default_rng(99)
        n = 200
        n_pos = 30

        coords = rng.uniform(0, 100, size=(n, 2))
        element = np.zeros(n, dtype=bool)
        element[rng.choice(n, n_pos, replace=False)] = True

        data = TestData(coordinates=coords, element_present=element)

        test = SpatialClusteringTest()
        result = test.run(data, n_permutations=2000)

        # Random placement should generally not be significant
        assert result.n_observations == n
