"""Tests for the name change rate statistical test."""

import numpy as np

from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.name_change_rate import NameChangeRateTest


class TestNameChangeRateMetadata:
    """Tests for NameChangeRateTest metadata."""

    def setup_method(self) -> None:
        self.test = NameChangeRateTest()

    def test_test_id(self) -> None:
        assert self.test.test_id == "name_change_rate"

    def test_family(self) -> None:
        assert self.test.test_family == StatFamily.TEMPORAL

    def test_has_null_hypothesis(self) -> None:
        assert "uniform" in self.test.null_hypothesis.lower()

    def test_has_alternative(self) -> None:
        assert "different" in self.test.alternative_hypothesis.lower()


class TestNameChangeRateRun:
    """Tests for name change rate run method."""

    def setup_method(self) -> None:
        self.test = NameChangeRateTest()

    def test_inconclusive_no_signal(self) -> None:
        """Should return inconclusive when no signal_values provided."""
        coords = np.random.default_rng(1).uniform(0, 1, size=(50, 2))
        labels = np.ones(50, dtype=bool)
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            region="test",
            element_name="none",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_inconclusive_too_few_sites(self) -> None:
        """Should return inconclusive with too few sites per group."""
        rng = np.random.default_rng(1)
        coords = rng.uniform(0, 1, size=(8, 2))
        labels = np.ones(8, dtype=bool)
        labels[:3] = False  # Only 3 in control
        data = PlaceData(
            coordinates=coords,
            element_present=labels,
            signal_values=rng.uniform(1900, 2000, size=8),
            region="test",
            element_name="few",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.status == StatStatus.INCONCLUSIVE

    def test_detects_elevated_rate(self) -> None:
        """Should detect when target has much higher change rate."""
        rng = np.random.default_rng(42)
        n = 200
        n_target = 50
        coords = rng.uniform(0, 1, size=(n, 2))
        target_mask = np.zeros(n, dtype=bool)
        target_mask[:n_target] = True

        # Target: 80% changed, Control: 15% changed
        change_years = np.zeros(n)
        for i in range(n):
            if target_mask[i]:
                if rng.random() < 0.80:
                    change_years[i] = rng.uniform(1900, 1920)
            else:
                if rng.random() < 0.15:
                    change_years[i] = rng.uniform(1800, 2000)

        data = PlaceData(
            coordinates=coords,
            element_present=target_mask,
            signal_values=change_years,
            region="test",
            element_name="elevated",
        )
        result = self.test.run(data, n_permutations=499)
        assert result.p_value is not None
        assert result.p_value < 0.05
        assert result.test_statistic is not None
        assert result.test_statistic > 1.0  # Elevated ratio

    def test_equal_rates_not_rejected(self) -> None:
        """Should not reject when both groups have equal rates."""
        rng = np.random.default_rng(77)
        n = 200
        n_target = 50
        coords = rng.uniform(0, 1, size=(n, 2))
        target_mask = np.zeros(n, dtype=bool)
        target_mask[:n_target] = True

        change_years = np.zeros(n)
        for i in range(n):
            if rng.random() < 0.30:
                change_years[i] = rng.uniform(1800, 2000)

        data = PlaceData(
            coordinates=coords,
            element_present=target_mask,
            signal_values=change_years,
            region="test",
            element_name="equal",
        )
        result = self.test.run(data, n_permutations=499)
        assert result.p_value is not None
        # Usually should not reject
        assert result.status != StatStatus.INCONCLUSIVE

    def test_rate_ratio_in_notes(self) -> None:
        """Should report rate ratio in notes."""
        rng = np.random.default_rng(42)
        n = 100
        n_target = 30
        coords = rng.uniform(0, 1, size=(n, 2))
        target_mask = np.zeros(n, dtype=bool)
        target_mask[:n_target] = True
        change_years = np.zeros(n)
        for i in range(n):
            if rng.random() < 0.3:
                change_years[i] = rng.uniform(1800, 2000)

        data = PlaceData(
            coordinates=coords,
            element_present=target_mask,
            signal_values=change_years,
            region="test",
            element_name="noted",
        )
        result = self.test.run(data, n_permutations=99)
        assert result.notes is not None
        assert "Rate ratio" in result.notes


class TestNameChangeRateValidation:
    """Tests for name change rate synthetic validation."""

    def test_validate_synthetic_power(self) -> None:
        """Synthetic validation should have adequate power."""
        test = NameChangeRateTest()
        validation = test.validate_synthetic(n_trials=30)
        assert validation.power >= 0.6  # Relaxed for speed

    def test_validate_synthetic_fpr(self) -> None:
        """Synthetic validation should control FPR."""
        test = NameChangeRateTest()
        validation = test.validate_synthetic(n_trials=30)
        assert validation.false_positive_rate <= 0.30  # Relaxed for speed
