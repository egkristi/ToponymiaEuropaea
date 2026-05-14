"""Tests for the catastrophe clustering test."""

import numpy as np

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.catastrophe_clustering import CatastropheClusteringTest


class TestCatastropheMetadata:
    """Tests for CatastropheClusteringTest metadata."""

    def setup_method(self) -> None:
        self.test = CatastropheClusteringTest()

    def test_test_id(self) -> None:
        assert self.test.test_id == "catastrophe_clustering"

    def test_family(self) -> None:
        assert self.test.test_family == StatFamily.CATASTROPHE_CLUSTERING

    def test_has_null_hypothesis(self) -> None:
        assert "disaster" in self.test.null_hypothesis.lower()

    def test_has_alternative(self) -> None:
        assert "hazard" in self.test.alternative_hypothesis.lower()


class TestCatastropheRun:
    """Tests for catastrophe clustering run method."""

    def setup_method(self) -> None:
        self.test = CatastropheClusteringTest()

    def test_inconclusive_no_signal(self) -> None:
        """Should return inconclusive without hazard data."""
        rng = np.random.default_rng(1)
        coords = rng.uniform(0, 1, size=(50, 2))
        labels = np.ones(50, dtype=bool)
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="flood",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_inconclusive_too_few(self) -> None:
        """Should return inconclusive with too few disaster sites."""
        rng = np.random.default_rng(1)
        coords = rng.uniform(0, 1, size=(10, 2))
        labels = np.zeros(10, dtype=bool)
        labels[:2] = True
        signal = rng.uniform(0, 1, size=10)
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=signal,
            region="test",
            element_name="fire",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_detects_hazard_correlation(self) -> None:
        """Should detect when disaster names are in high-hazard areas."""
        rng = np.random.default_rng(42)
        n = 200
        n_disaster = 30
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        labels[:n_disaster] = True

        signal = rng.normal(0.3, 0.2, size=n)
        signal[:n_disaster] += 1.0  # Disaster sites in high-hazard zones

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=signal,
            region="test",
            element_name="flood",
        )
        result = self.test.run(data, n_permutations=499)
        assert result.p_value is not None
        assert result.p_value < 0.05
        assert result.test_statistic is not None
        assert result.test_statistic > 0
        assert result.effect_size is not None
        assert result.effect_size > 0.3

    def test_no_correlation_not_rejected(self) -> None:
        """Should not reject when hazard is uncorrelated with names."""
        rng = np.random.default_rng(99)
        n = 200
        n_disaster = 30
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        chosen = rng.choice(n, size=n_disaster, replace=False)
        labels[chosen] = True

        signal = rng.normal(0.5, 0.3, size=n)

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=signal,
            region="test",
            element_name="random",
        )
        result = self.test.run(data, n_permutations=499)
        assert result.p_value is not None
        assert result.status != StatStatus.INCONCLUSIVE

    def test_notes_contain_means(self) -> None:
        """Should report mean hazard values in notes."""
        rng = np.random.default_rng(42)
        n = 100
        n_disaster = 20
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        labels[:n_disaster] = True
        signal = rng.uniform(0, 1, size=n)

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=signal,
            region="test",
            element_name="test",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.notes is not None
        assert "Mean hazard" in result.notes


class TestCatastropheValidation:
    """Tests for catastrophe clustering synthetic validation."""

    def test_validate_synthetic_power(self) -> None:
        """Synthetic validation should have adequate power."""
        test = CatastropheClusteringTest()
        validation = test.validate_synthetic(n_trials=30)
        assert validation.power >= 0.7

    def test_validate_synthetic_fpr(self) -> None:
        """Synthetic validation should control FPR."""
        test = CatastropheClusteringTest()
        validation = test.validate_synthetic(n_trials=30)
        assert validation.false_positive_rate <= 0.20
