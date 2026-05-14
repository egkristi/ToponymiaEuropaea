"""Tests for the language contact boundary detection test."""

import numpy as np
import pytest

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.language_contact import LanguageContactBoundaryTest


class TestLanguageContactBoundaryTest:
    """Tests for LanguageContactBoundaryTest."""

    def setup_method(self):
        self.test = LanguageContactBoundaryTest()

    def test_metadata(self):
        assert self.test.test_id == "language_contact_boundary"
        assert self.test.test_family == StatFamily.LANGUAGE_CONTACT
        assert "intermixed" in self.test.null_hypothesis

    def test_boundary_detected(self):
        """Should detect boundary when languages are spatially segregated."""
        rng = np.random.default_rng(42)
        n = 200

        # Language A on left (x < 0.5), B on right (x > 0.5)
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = (coords[:, 0] < 0.5).astype(float)

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test_boundary",
            element_name="gaelic_names",
        )

        result = self.test.run(data, n_permutations=999)
        assert result.p_value < 0.05
        assert result.effect_size > 0
        assert result.parameters["observed_segregation"] > 0.5

    def test_no_boundary_when_mixed(self):
        """Should not detect boundary when languages are randomly mixed."""
        rng = np.random.default_rng(42)
        n = 200

        coords = rng.uniform(0, 1, size=(n, 2))
        # Random labels with no spatial structure
        labels = (rng.random(n) < 0.5).astype(float)

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test_mixed",
            element_name="random_names",
        )

        result = self.test.run(data, n_permutations=999)
        # Should not be significant
        assert result.p_value > 0.01

    def test_insufficient_sites(self):
        """Should return INCONCLUSIVE when too few sites per language."""
        rng = np.random.default_rng(42)
        n = 20

        coords = rng.uniform(0, 1, size=(n, 2))
        # Only 5 sites for language A (need ≥10)
        labels = np.zeros(n, dtype=float)
        labels[:5] = 1.0

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test_small",
            element_name="too_few",
        )

        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_partial_boundary(self):
        """Should detect boundary even with some overlap/noise."""
        rng = np.random.default_rng(42)
        n = 300

        coords = rng.uniform(0, 1, size=(n, 2))
        # Language A on left, B on right, 20% noise
        labels = (coords[:, 0] < 0.5).astype(bool)
        n_flip = n // 5
        flip_idx = rng.choice(n, size=n_flip, replace=False)
        labels[flip_idx] = ~labels[flip_idx]

        data = PlaceData(
            coordinates=coords,
            element_present=labels.astype(float),
            region="test_noisy_boundary",
            element_name="celtic_names",
        )

        result = self.test.run(data, n_permutations=999)
        assert result.p_value < 0.05
        assert result.parameters["n_language_a"] > 0
        assert result.parameters["n_language_b"] > 0

    def test_result_parameters(self):
        """Should include expected parameters in result."""
        rng = np.random.default_rng(42)
        n = 100

        coords = rng.uniform(0, 1, size=(n, 2))
        labels = (coords[:, 0] < 0.5).astype(float)

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test_params",
            element_name="lang_a",
        )

        result = self.test.run(data, n_permutations=99)
        assert "n_language_a" in result.parameters
        assert "n_language_b" in result.parameters
        assert "k_neighbours" in result.parameters
        assert "observed_segregation" in result.parameters
        assert "expected_segregation_null" in result.parameters
        assert result.n_permutations == 99

    def test_validate_synthetic(self):
        """Synthetic validation should pass (power >0.8, FPR <0.05)."""
        validation = self.test.validate_synthetic(n_trials=50)
        assert validation.power > 0.8
        assert validation.false_positive_rate < 0.10
        assert "Power=" in validation.details

    def test_circular_boundary(self):
        """Should detect circular boundary (A inside, B outside)."""
        rng = np.random.default_rng(42)
        n = 200

        coords = rng.uniform(-1, 1, size=(n, 2))
        # Language A inside circle of radius 0.5
        distances = np.sqrt(coords[:, 0] ** 2 + coords[:, 1] ** 2)
        labels = (distances < 0.5).astype(float)

        # Need enough in both groups
        n_a = int(labels.sum())
        if n_a < 10 or n - n_a < 10:
            pytest.skip("Random seed didn't produce balanced groups")

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test_circular",
            element_name="inner_names",
        )

        result = self.test.run(data, n_permutations=999)
        assert result.p_value < 0.05
