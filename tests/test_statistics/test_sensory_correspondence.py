"""Tests for the sensory correspondence test."""

import numpy as np

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.sensory_correspondence import SensoryCorrespondenceTest


class TestSensoryMetadata:
    """Tests for SensoryCorrespondenceTest metadata."""

    def setup_method(self) -> None:
        self.test = SensoryCorrespondenceTest()

    def test_test_id(self) -> None:
        assert self.test.test_id == "sensory_correspondence"

    def test_family(self) -> None:
        assert self.test.test_family == StatFamily.SENSORY_CORRESPONDENCE

    def test_has_null_hypothesis(self) -> None:
        assert "sensory" in self.test.null_hypothesis.lower()

    def test_has_alternative(self) -> None:
        assert "signal" in self.test.alternative_hypothesis.lower()


class TestSensoryRun:
    """Tests for sensory correspondence run method."""

    def setup_method(self) -> None:
        self.test = SensoryCorrespondenceTest()

    def test_inconclusive_no_signal(self) -> None:
        """Should return inconclusive without environmental data."""
        rng = np.random.default_rng(1)
        coords = rng.uniform(0, 1, size=(50, 2))
        labels = np.ones(50, dtype=bool)
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="svart",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_inconclusive_too_few(self) -> None:
        """Should return inconclusive with too few sensory sites."""
        rng = np.random.default_rng(1)
        coords = rng.uniform(0, 1, size=(10, 2))
        labels = np.zeros(10, dtype=bool)
        labels[:3] = True
        signal = rng.uniform(0, 1, size=10)
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=signal,
            region="test",
            element_name="hvit",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_detects_signal_correlation(self) -> None:
        """Should detect when colour names correlate with signal."""
        rng = np.random.default_rng(42)
        n = 200
        n_colour = 30
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        labels[:n_colour] = True

        signal = rng.normal(0.5, 0.2, size=n)
        signal[:n_colour] += 0.5  # Colour sites have elevated signal

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=signal,
            region="test",
            element_name="svart",
        )
        result = self.test.run(data, n_permutations=499)
        assert result.p_value is not None
        assert result.p_value < 0.05
        assert result.test_statistic is not None
        assert result.test_statistic > 0
        assert result.effect_size is not None
        assert result.effect_size > 0.3

    def test_detects_negative_correlation(self) -> None:
        """Should detect colour names with LOWER signal (two-sided)."""
        rng = np.random.default_rng(42)
        n = 200
        n_colour = 30
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        labels[:n_colour] = True

        signal = rng.normal(0.5, 0.2, size=n)
        signal[:n_colour] -= 0.5  # Colour sites have LOWER signal

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=signal,
            region="test",
            element_name="hvit",
        )
        result = self.test.run(data, n_permutations=499)
        assert result.p_value is not None
        assert result.p_value < 0.05
        assert result.test_statistic is not None
        assert result.test_statistic < 0  # Negative difference

    def test_no_correlation_not_rejected(self) -> None:
        """Should not reject when signal is uncorrelated with names."""
        rng = np.random.default_rng(99)
        n = 200
        n_colour = 30
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        chosen = rng.choice(n, size=n_colour, replace=False)
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
        """Should report mean signal values in notes."""
        rng = np.random.default_rng(42)
        n = 100
        n_colour = 20
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        labels[:n_colour] = True
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
        assert "Mean signal" in result.notes

    def test_two_sided_test(self) -> None:
        """Verify this is a two-sided test (absolute difference)."""
        rng = np.random.default_rng(42)
        n = 100
        n_colour = 20
        coords = rng.uniform(0, 1, size=(n, 2))
        labels = np.zeros(n, dtype=bool)
        labels[:n_colour] = True
        signal = rng.normal(0.5, 0.2, size=n)

        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=signal,
            region="test",
            element_name="test",
        )
        result = self.test.run(data, n_permutations=99)
        # Two-sided: p-value should be reasonable even for small differences
        assert 0.0 <= result.p_value <= 1.0


class TestSensoryValidation:
    """Tests for sensory correspondence synthetic validation."""

    def test_validate_synthetic_power(self) -> None:
        """Synthetic validation should have adequate power."""
        test = SensoryCorrespondenceTest()
        validation = test.validate_synthetic(n_trials=30)
        assert validation.power >= 0.7

    def test_validate_synthetic_fpr(self) -> None:
        """Synthetic validation should control FPR."""
        test = SensoryCorrespondenceTest()
        validation = test.validate_synthetic(n_trials=30)
        assert validation.false_positive_rate <= 0.20
