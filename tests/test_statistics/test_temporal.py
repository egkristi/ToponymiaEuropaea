"""Tests for the temporal layer consistency statistical test."""

import numpy as np
import pytest

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.temporal import TemporalLayerConsistencyTest


class TestTemporalLayerConsistencyTest:
    """Tests for TemporalLayerConsistencyTest."""

    def setup_method(self):
        self.test = TemporalLayerConsistencyTest()

    def test_metadata(self):
        assert self.test.test_id == "temporal_layer_consistency"
        assert self.test.test_family == StatFamily.TEMPORAL
        assert "temporal layer" in self.test.null_hypothesis

    def test_clustered_layer_detected(self):
        """Should detect spatial coherence when layer forms a cluster."""
        rng = np.random.default_rng(42)
        n = 200

        # Background: uniform over 2x2 degrees
        coords = rng.uniform(0, 2, size=(n, 2))

        # Layer: tight cluster around (1.0, 1.0)
        n_layer = 25
        layer_idx = rng.choice(n, size=n_layer, replace=False)
        coords[layer_idx] = rng.normal([1.0, 1.0], 0.03, size=(n_layer, 2))

        element_present = np.zeros(n, dtype=bool)
        element_present[layer_idx] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            region="test_region",
            element_name="viking_by_names",
        )

        result = self.test.run(data, n_permutations=999)
        assert result.p_value < 0.05
        assert result.effect_size > 0
        assert result.n_positive == n_layer
        assert result.n_observations == n

    def test_random_layer_not_detected(self):
        """Should not detect coherence when layer is random subset."""
        rng = np.random.default_rng(42)
        n = 200

        # All points uniform
        coords = rng.uniform(0, 2, size=(n, 2))

        # Layer: random subset (no clustering)
        n_layer = 25
        layer_idx = rng.choice(n, size=n_layer, replace=False)

        element_present = np.zeros(n, dtype=bool)
        element_present[layer_idx] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            region="test_region",
            element_name="random_names",
        )

        result = self.test.run(data, n_permutations=999)
        # Random layer shouldn't produce significant clustering
        # (might occasionally by chance, but generally p > 0.05)
        assert result.p_value > 0.01  # lenient check for stability

    def test_insufficient_layer_members(self):
        """Should return INCONCLUSIVE when layer has too few members."""
        rng = np.random.default_rng(42)
        n = 100
        coords = rng.uniform(0, 1, size=(n, 2))

        element_present = np.zeros(n, dtype=bool)
        element_present[:3] = True  # Only 3 members (need ≥5)

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            region="test",
            element_name="sparse",
        )

        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE
        assert "Insufficient" in result.notes

    def test_layer_covers_all_sites(self):
        """Should return INCONCLUSIVE when layer = all sites."""
        rng = np.random.default_rng(42)
        n = 50
        coords = rng.uniform(0, 1, size=(n, 2))

        element_present = np.ones(n, dtype=bool)  # All sites in layer

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            region="test",
            element_name="all_sites",
        )

        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_result_contains_parameters(self):
        """Result should contain expected parameter keys."""
        rng = np.random.default_rng(42)
        n = 100
        coords = rng.uniform(0, 1, size=(n, 2))
        element_present = np.zeros(n, dtype=bool)
        element_present[:15] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            region="test",
            element_name="test_layer",
        )

        result = self.test.run(data, n_permutations=99)
        assert "observed_mean_nnd_km" in result.parameters
        assert "null_mean_nnd_km" in result.parameters
        assert "null_std_nnd_km" in result.parameters

    def test_effect_size_positive_for_clustered(self):
        """Effect size should be positive when layer is clustered."""
        rng = np.random.default_rng(123)
        n = 150

        coords = rng.uniform(0, 3, size=(n, 2))

        # Very tight cluster
        n_layer = 20
        layer_idx = rng.choice(n, size=n_layer, replace=False)
        coords[layer_idx] = rng.normal([1.5, 1.5], 0.02, size=(n_layer, 2))

        element_present = np.zeros(n, dtype=bool)
        element_present[layer_idx] = True

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            region="test",
            element_name="tight_cluster",
        )

        result = self.test.run(data, n_permutations=499)
        assert result.effect_size > 0

    @pytest.mark.slow
    def test_synthetic_validation(self):
        """Synthetic validation should demonstrate power and controlled FPR."""
        validation = self.test.validate_synthetic(n_trials=50)
        assert validation.power >= 0.7  # Lenient threshold for fast test
        assert validation.false_positive_rate <= 0.15
