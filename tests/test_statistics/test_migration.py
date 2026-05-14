"""Tests for the migration overfrequency statistical test."""

import numpy as np
import pytest

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.migration import MigrationOverfrequencyTest


class TestMigrationOverfrequencyTest:
    """Tests for MigrationOverfrequencyTest."""

    def setup_method(self):
        self.test = MigrationOverfrequencyTest()

    def test_metadata(self):
        assert self.test.test_id == "migration_overfrequency"
        assert self.test.test_family == StatFamily.MIGRATION
        assert "frequency" in self.test.null_hypothesis

    def test_enrichment_detected(self):
        """Should detect enrichment when element is over-represented in target."""
        rng = np.random.default_rng(42)
        n = 200

        coords = rng.uniform(0, 2, size=(n, 2))

        # Target zone: first 60 sites
        signal = np.zeros(n, dtype=float)
        signal[:60] = 1.0

        # Element: 40% in target zone, 5% in background
        element_present = np.zeros(n, dtype=bool)
        # Target: 24/60 = 40%
        target_element_idx = rng.choice(60, size=24, replace=False)
        element_present[target_element_idx] = True
        # Background: 7/140 = 5%
        bg_element_idx = rng.choice(range(60, n), size=7, replace=False)
        element_present[list(bg_element_idx)] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test_region",
            element_name="norse_by_names",
        )

        result = self.test.run(data, n_permutations=999)
        assert result.p_value < 0.05
        assert result.effect_size > 0
        assert (
            result.parameters["proportion_in_target"]
            > result.parameters["proportion_in_background"]
        )

    def test_no_enrichment_when_uniform(self):
        """Should not detect enrichment when element is uniformly distributed."""
        rng = np.random.default_rng(42)
        n = 200

        coords = rng.uniform(0, 2, size=(n, 2))

        # Target zone: random subset
        signal = np.zeros(n, dtype=float)
        target_idx = rng.choice(n, size=60, replace=False)
        signal[target_idx] = 1.0

        # Element: uniform 15% everywhere
        element_present = np.zeros(n, dtype=bool)
        elem_idx = rng.choice(n, size=30, replace=False)
        element_present[elem_idx] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test_region",
            element_name="control_element",
        )

        result = self.test.run(data, n_permutations=999)
        # Uniform distribution shouldn't be significant
        assert result.p_value > 0.01

    def test_insufficient_target_zone(self):
        """Should return INCONCLUSIVE when target zone too small."""
        rng = np.random.default_rng(42)
        n = 100
        coords = rng.uniform(0, 1, size=(n, 2))

        signal = np.zeros(n, dtype=float)
        signal[:3] = 1.0  # Only 3 in target (need ≥5)

        element_present = np.zeros(n, dtype=bool)
        element_present[:10] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test",
            element_name="sparse",
        )

        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE
        assert "Insufficient" in result.notes

    def test_insufficient_elements(self):
        """Should return INCONCLUSIVE when too few element-bearing sites."""
        rng = np.random.default_rng(42)
        n = 100
        coords = rng.uniform(0, 1, size=(n, 2))

        signal = np.zeros(n, dtype=float)
        signal[:40] = 1.0

        element_present = np.zeros(n, dtype=bool)
        element_present[:2] = True  # Only 2 elements (need ≥3)

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test",
            element_name="rare",
        )

        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE
        assert "Too few" in result.notes

    def test_missing_signal_values_raises(self):
        """Should raise ValueError when signal_values not provided."""
        rng = np.random.default_rng(42)
        n = 50
        coords = rng.uniform(0, 1, size=(n, 2))
        element_present = np.zeros(n, dtype=bool)
        element_present[:10] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=None,
            region="test",
            element_name="test",
        )

        with pytest.raises(ValueError, match="signal_values"):
            self.test.run(data, n_permutations=99)

    def test_result_parameters_complete(self):
        """Result should contain all expected parameter keys."""
        rng = np.random.default_rng(42)
        n = 100
        coords = rng.uniform(0, 1, size=(n, 2))

        signal = np.zeros(n, dtype=float)
        signal[:30] = 1.0

        element_present = np.zeros(n, dtype=bool)
        element_present[:15] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test",
            element_name="test_element",
        )

        result = self.test.run(data, n_permutations=99)
        assert "n_target_zone" in result.parameters
        assert "n_background_zone" in result.parameters
        assert "proportion_in_target" in result.parameters
        assert "proportion_in_background" in result.parameters
        assert "observed_proportion_difference" in result.parameters

    @pytest.mark.slow
    def test_synthetic_validation(self):
        """Synthetic validation should demonstrate power and controlled FPR."""
        validation = self.test.validate_synthetic(n_trials=50)
        assert validation.power >= 0.7
        assert validation.false_positive_rate <= 0.15
