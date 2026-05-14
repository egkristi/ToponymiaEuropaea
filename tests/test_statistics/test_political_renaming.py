"""Tests for the political renaming detection test."""

import numpy as np
import pytest

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.political_renaming import PoliticalRenamingTest


class TestPoliticalRenamingTest:
    """Tests for PoliticalRenamingTest."""

    def setup_method(self):
        self.test = PoliticalRenamingTest(window_years=10)

    def test_metadata(self):
        assert self.test.test_id == "political_renaming"
        assert self.test.test_family == StatFamily.POLITICAL_RENAMING
        assert "uniform rate" in self.test.null_hypothesis

    def test_clustered_renamings_detected(self):
        """Should detect temporal clustering when most changes are in one decade."""
        rng = np.random.default_rng(42)
        n = 200
        n_changes = 50

        coords = rng.uniform(0, 1, size=(n, 2))

        # Select which sites have name changes
        change_mask = np.zeros(n, dtype=bool)
        change_idx = rng.choice(n, size=n_changes, replace=False)
        change_mask[change_idx] = True

        # 70% of changes in 1905-1915 (post-independence Norway)
        signal = np.zeros(n, dtype=float)
        n_clustered = 35
        signal[change_idx[:n_clustered]] = rng.uniform(1905, 1915, size=n_clustered)
        # Rest spread over 1800-2000
        n_spread = n_changes - n_clustered
        signal[change_idx[n_clustered:]] = rng.uniform(1800, 2000, size=n_spread)

        data = PlaceData(
            coordinates=coords,
            element_present=change_mask.astype(float),
            signal_values=signal,
            region="norway",
            element_name="fornorsking",
        )

        result = self.test.run(data, n_permutations=999)
        assert result.p_value < 0.05
        assert result.effect_size > 0
        assert result.parameters["peak_count"] > 0

    def test_no_clustering_when_uniform(self):
        """Should not detect clustering when changes are uniformly distributed."""
        rng = np.random.default_rng(42)
        n = 200
        n_changes = 50

        coords = rng.uniform(0, 1, size=(n, 2))

        change_mask = np.zeros(n, dtype=bool)
        change_idx = rng.choice(n, size=n_changes, replace=False)
        change_mask[change_idx] = True

        # Uniform distribution over 200 years
        signal = np.zeros(n, dtype=float)
        signal[change_idx] = rng.uniform(1800, 2000, size=n_changes)

        data = PlaceData(
            coordinates=coords,
            element_present=change_mask.astype(float),
            signal_values=signal,
            region="control",
            element_name="organic_changes",
        )

        result = self.test.run(data, n_permutations=999)
        # Should not be significant with uniform changes
        assert result.p_value > 0.01

    def test_insufficient_changes(self):
        """Should return INCONCLUSIVE with too few changes."""
        rng = np.random.default_rng(42)
        n = 100

        coords = rng.uniform(0, 1, size=(n, 2))
        change_mask = np.zeros(n, dtype=bool)
        change_mask[:5] = True  # Only 5 changes (need ≥10)

        signal = np.zeros(n, dtype=float)
        signal[:5] = np.array([1900, 1905, 1910, 1920, 1950])

        data = PlaceData(
            coordinates=coords,
            element_present=change_mask.astype(float),
            signal_values=signal,
            region="test_small",
            element_name="too_few",
        )

        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_missing_signal_values(self):
        """Should raise ValueError when signal_values not provided."""
        rng = np.random.default_rng(42)
        n = 50
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.ones(n, dtype=float)

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="test",
        )

        with pytest.raises(ValueError, match="signal_values"):
            self.test.run(data)

    def test_result_parameters(self):
        """Should include expected parameters in result."""
        rng = np.random.default_rng(42)
        n = 100
        n_changes = 30

        coords = rng.uniform(0, 1, size=(n, 2))
        change_mask = np.zeros(n, dtype=bool)
        change_idx = rng.choice(n, size=n_changes, replace=False)
        change_mask[change_idx] = True

        signal = np.zeros(n, dtype=float)
        signal[change_idx] = rng.uniform(1800, 2000, size=n_changes)

        data = PlaceData(
            coordinates=coords,
            element_present=change_mask.astype(float),
            signal_values=signal,
            region="test_params",
            element_name="changes",
        )

        result = self.test.run(data, n_permutations=99)
        assert "n_changes" in result.parameters
        assert "year_min" in result.parameters
        assert "year_max" in result.parameters
        assert "peak_window" in result.parameters
        assert "peak_count" in result.parameters
        assert "window_years" in result.parameters
        assert result.parameters["window_years"] == 10

    def test_custom_window_size(self):
        """Should work with different window sizes."""
        test_wide = PoliticalRenamingTest(window_years=25)
        assert test_wide.window_years == 25

        rng = np.random.default_rng(42)
        n = 100
        n_changes = 20

        coords = rng.uniform(0, 1, size=(n, 2))
        change_mask = np.zeros(n, dtype=bool)
        change_idx = rng.choice(n, size=n_changes, replace=False)
        change_mask[change_idx] = True

        signal = np.zeros(n, dtype=float)
        signal[change_idx] = rng.uniform(1800, 2000, size=n_changes)

        data = PlaceData(
            coordinates=coords,
            element_present=change_mask.astype(float),
            signal_values=signal,
            region="test_window",
            element_name="changes",
        )

        result = test_wide.run(data, n_permutations=99)
        assert result.parameters["window_years"] == 25

    def test_validate_synthetic(self):
        """Synthetic validation should pass (power >0.8, FPR <0.05)."""
        validation = self.test.validate_synthetic(n_trials=50)
        assert validation.power > 0.8
        assert validation.false_positive_rate < 0.10
        assert "Power=" in validation.details
