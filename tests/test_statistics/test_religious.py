"""Tests for the religious stratigraphy statistical test."""

import numpy as np
import pytest

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.religious import ReligiousStratigraphyTest


class TestReligiousStratigraphyTest:
    """Tests for ReligiousStratigraphyTest."""

    def setup_method(self):
        self.test = ReligiousStratigraphyTest()

    def test_metadata(self):
        assert self.test.test_id == "religious_stratigraphy"
        assert self.test.test_family == StatFamily.RELIGIOUS_STRATIGRAPHY
        assert "Christian" in self.test.null_hypothesis

    def test_significant_cooccurrence_detected(self):
        """Should detect over-representation when Christian sites cluster near pre-Christian."""
        rng = np.random.default_rng(42)
        n = 150

        coords = rng.uniform(0, 2, size=(n, 2))

        # Pre-Christian sites: first 20
        element_present = np.zeros(n, dtype=bool)
        element_present[:20] = True

        # Christian sites: placed NEAR pre-Christian sites
        signal = np.zeros(n, dtype=float)
        # Place 15 Christian sites very close to pre-Christian ones
        for i in range(15):
            # Place near pre-Christian site i
            coords[20 + i] = coords[i] + rng.normal(0, 0.005, size=2)
            signal[20 + i] = 1.0
        # Additional random Christian sites
        for i in range(35, 45):
            signal[i] = 1.0

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test_region",
            element_name="hov-/vé-",
        )

        result = self.test.run(data, n_permutations=999, proximity_threshold_km=1.5)
        assert result.p_value < 0.05
        assert result.effect_size > 0

    def test_no_signal_when_random(self):
        """Should not detect signal when Christian sites are randomly placed."""
        rng = np.random.default_rng(42)
        n = 150

        coords = rng.uniform(0, 2, size=(n, 2))

        # Pre-Christian sites: random subset
        element_present = np.zeros(n, dtype=bool)
        element_present[:20] = True

        # Christian sites: random placement (no relation to pre-Christian)
        signal = np.zeros(n, dtype=float)
        christian_idx = rng.choice(range(20, n), size=25, replace=False)
        signal[christian_idx] = 1.0

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test_region",
            element_name="control",
        )

        result = self.test.run(data, n_permutations=999, proximity_threshold_km=1.5)
        # Should generally not be significant (p > 0.05)
        # Allow some statistical variation
        assert result.p_value > 0.01  # Not strongly significant

    def test_insufficient_sites_inconclusive(self):
        """Should return inconclusive with too few sites."""
        coords = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]])
        element_present = np.array([True, True, False, False, False])
        signal = np.array([0.0, 0.0, 1.0, 0.0, 0.0])

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test",
            element_name="hov-",
        )

        result = self.test.run(data, n_permutations=99, proximity_threshold_km=200)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_missing_signal_values(self):
        """Should raise ValueError without signal_values."""
        coords = np.array([[0, 0], [1, 1]])
        element_present = np.array([True, False])

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=None,
        )

        with pytest.raises(ValueError, match="signal_values"):
            self.test.run(data)

    def test_result_parameters(self):
        """Test that result includes expected parameters."""
        rng = np.random.default_rng(42)
        n = 50

        coords = rng.uniform(0, 1, size=(n, 2))
        element_present = np.zeros(n, dtype=bool)
        element_present[:10] = True
        signal = np.zeros(n, dtype=float)
        signal[10:20] = 1.0

        data = PlaceData(
            coordinates=coords,
            element_present=element_present,
            signal_values=signal,
            region="test",
            element_name="hov-",
        )

        result = self.test.run(data, n_permutations=99, proximity_threshold_km=20)
        assert "n_christian" in result.parameters
        assert "observed_cooccurrences" in result.parameters
        assert "proximity_threshold_km" in result.parameters

    def test_validate_synthetic(self):
        """Synthetic validation should pass (relaxed for speed)."""
        validation = self.test.validate_synthetic(n_trials=15)
        # Relaxed thresholds for 15 trials
        assert validation.power >= 0.5
        assert validation.false_positive_rate <= 0.30
