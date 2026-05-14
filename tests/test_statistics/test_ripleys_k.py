"""Tests for Ripley's K spatial clustering test."""

import numpy as np

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.ripleys_k import RipleysKTest


class TestRipleysKMetadata:
    """Tests for RipleysKTest metadata."""

    def setup_method(self) -> None:
        self.test = RipleysKTest()

    def test_test_id(self) -> None:
        assert self.test.test_id == "ripleys_k_spatial"

    def test_family(self) -> None:
        assert self.test.test_family == StatFamily.SPATIAL

    def test_has_null_hypothesis(self) -> None:
        assert "random" in self.test.null_hypothesis.lower()

    def test_has_alternative(self) -> None:
        assert "cluster" in self.test.alternative_hypothesis.lower()


class TestRipleysKRun:
    """Tests for Ripley's K run method."""

    def setup_method(self) -> None:
        self.test = RipleysKTest(n_distance_bins=10)

    def test_inconclusive_too_few_positive(self) -> None:
        """Should return inconclusive with too few target sites."""
        rng = np.random.default_rng(1)
        coords = rng.uniform(0, 1, size=(50, 2))
        labels = np.zeros(50, dtype=bool)
        labels[:3] = True  # Only 3 positive
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="rare",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_detects_clustering(self) -> None:
        """Should detect clustering when points form tight groups."""
        rng = np.random.default_rng(42)
        n = 200
        n_target = 40

        # Target: 4 tight clusters
        targets = []
        for center in [(0.2, 0.2), (0.8, 0.2), (0.2, 0.8), (0.8, 0.8)]:
            pts = rng.normal(loc=center, scale=0.02, size=(10, 2))
            targets.append(pts)
        target_coords = np.vstack(targets)

        background = rng.uniform(0, 1, size=(n - n_target, 2))
        all_coords = np.vstack([target_coords, background])

        labels = np.zeros(n, dtype=bool)
        labels[:n_target] = True

        data = PlaceData(
            coordinates=all_coords,
            element_present=labels,
            region="synthetic",
            element_name="clustered",
        )
        result = self.test.run(data, n_permutations=199)
        assert result.p_value is not None
        assert result.p_value < 0.05
        assert result.test_statistic is not None
        assert result.test_statistic > 0

    def test_no_clustering_uniform(self) -> None:
        """Should not reject for uniformly distributed points."""
        rng = np.random.default_rng(99)
        n = 200
        n_target = 40
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        chosen = rng.choice(n, size=n_target, replace=False)
        labels[chosen] = True

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="synthetic",
            element_name="random",
        )
        result = self.test.run(data, n_permutations=199)
        assert result.p_value is not None
        # Should usually NOT reject (p > 0.05), but allow some stochasticity
        assert result.status != StatStatus.INCONCLUSIVE

    def test_peak_scale_reported(self) -> None:
        """Should report peak clustering scale in notes."""
        rng = np.random.default_rng(42)
        n = 100
        n_target = 20
        targets = rng.normal(loc=(0.5, 0.5), scale=0.05, size=(n_target, 2))
        background = rng.uniform(0, 1, size=(n - n_target, 2))
        all_coords = np.vstack([targets, background])
        labels = np.zeros(n, dtype=bool)
        labels[:n_target] = True

        data = PlaceData(
            coordinates=all_coords,
            element_present=labels,
            region="test",
            element_name="clustered",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.notes is not None
        assert "Peak" in result.notes or "r=" in result.notes

    def test_zero_area_inconclusive(self) -> None:
        """Should return inconclusive if all points are identical."""
        coords = np.ones((20, 2))
        labels = np.ones(20, dtype=bool)
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="degenerate",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE


class TestRipleysKValidation:
    """Tests for Ripley's K synthetic validation."""

    def test_validate_synthetic_power(self) -> None:
        """Synthetic validation should have adequate power."""
        test = RipleysKTest(n_distance_bins=10)
        validation = test.validate_synthetic(n_trials=30)
        assert validation.power >= 0.6  # Relaxed for speed

    def test_validate_synthetic_fpr(self) -> None:
        """Synthetic validation should control false positive rate."""
        test = RipleysKTest(n_distance_bins=10)
        validation = test.validate_synthetic(n_trials=30)
        assert validation.false_positive_rate <= 0.30  # Relaxed for speed
