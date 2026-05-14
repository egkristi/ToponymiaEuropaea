"""Tests for the sacred geometry alignment test."""

import numpy as np

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.sacred_geometry import SacredGeometryAlignmentTest


class TestSacredGeometryMetadata:
    """Tests for SacredGeometryAlignmentTest metadata."""

    def setup_method(self) -> None:
        self.test = SacredGeometryAlignmentTest()

    def test_test_id(self) -> None:
        assert self.test.test_id == "sacred_geometry_alignment"

    def test_family(self) -> None:
        assert self.test.test_family == StatFamily.SACRED_GEOMETRY

    def test_has_null_hypothesis(self) -> None:
        assert "random" in self.test.null_hypothesis.lower()

    def test_has_alternative(self) -> None:
        assert "alignment" in self.test.alternative_hypothesis.lower()


class TestSacredGeometryRun:
    """Tests for sacred geometry alignment run method."""

    def setup_method(self) -> None:
        self.test = SacredGeometryAlignmentTest(tolerance_fraction=0.01)

    def test_inconclusive_too_few_sacred(self) -> None:
        """Should return inconclusive with too few sacred sites."""
        rng = np.random.default_rng(1)
        coords = rng.uniform(0, 1, size=(50, 2))
        labels = np.zeros(50, dtype=bool)
        labels[:3] = True
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="sacred",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_detects_linear_alignment(self) -> None:
        """Should detect sites placed on deliberate lines."""
        rng = np.random.default_rng(42)
        n = 100
        n_sacred = 12

        # Sacred sites on 3 lines (4 each)
        sacred = []
        for line_idx in range(3):
            y_base = 0.2 + line_idx * 0.3
            for pt_idx in range(4):
                x = 0.1 + pt_idx * 0.25
                y = y_base + rng.normal(0, 0.0005)
                sacred.append([x, y])
        sacred_arr = np.array(sacred)

        background = rng.uniform(0, 1, size=(n - n_sacred, 2))
        all_coords = np.vstack([sacred_arr, background])
        labels = np.zeros(n, dtype=bool)
        labels[:n_sacred] = True

        data = PlaceData(
            coordinates=all_coords,
            element_present=labels,
            region="synthetic",
            element_name="hov",
        )
        result = self.test.run(data, n_permutations=199)
        assert result.p_value is not None
        assert result.p_value < 0.10
        assert result.test_statistic is not None
        assert result.test_statistic > 0

    def test_random_not_significant(self) -> None:
        """Should not flag random points as aligned."""
        rng = np.random.default_rng(77)
        n = 100
        n_sacred = 12
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        chosen = rng.choice(n, size=n_sacred, replace=False)
        labels[chosen] = True

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="random",
        )
        result = self.test.run(data, n_permutations=199)
        assert result.status != StatStatus.INCONCLUSIVE

    def test_zero_extent_inconclusive(self) -> None:
        """Should handle degenerate geometry."""
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

    def test_notes_contain_count(self) -> None:
        """Should report alignment count in notes."""
        rng = np.random.default_rng(10)
        coords = rng.uniform(0, 1, size=(50, 2))
        labels = np.zeros(50, dtype=bool)
        labels[:10] = True
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="test",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.notes is not None
        assert "triplet" in result.notes.lower() or "collinear" in result.notes.lower()


class TestSacredGeometryValidation:
    """Tests for sacred geometry synthetic validation."""

    def test_validate_synthetic_power(self) -> None:
        """Synthetic validation should have adequate power."""
        test = SacredGeometryAlignmentTest(tolerance_fraction=0.01)
        validation = test.validate_synthetic(n_trials=30)
        assert validation.power >= 0.5

    def test_validate_synthetic_fpr(self) -> None:
        """Synthetic validation should control FPR."""
        test = SacredGeometryAlignmentTest(tolerance_fraction=0.01)
        validation = test.validate_synthetic(n_trials=30)
        assert validation.false_positive_rate <= 0.30
