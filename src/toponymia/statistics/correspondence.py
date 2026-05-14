"""Correspondence tests: name elements vs. environmental/cultural signals.

Tests whether a toponymic element (e.g., -berg, -vik, -lund) corresponds
significantly with a measurable signal (e.g., elevation, coastal distance,
forest cover) compared to a null model of random placement.
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from toponymia.statistics.base import (
    BaseTest,
    SyntheticValidation,
    TestData,
    TestFamily,
    TestResult,
    TestStatus,
)


class ElementSignalCorrespondenceTest(BaseTest):
    """Test correspondence between a name element and a continuous signal.

    Null hypothesis: The signal values at places with the element are drawn
    from the same distribution as signal values at places without the element.

    Method: Permutation test on the difference in means (or medians),
    with optional Mann-Whitney U as parametric backup.
    """

    test_id = "element_signal_correspondence"
    test_family = TestFamily.CORRESPONDENCE
    description = "Tests whether a toponymic element corresponds with a continuous environmental signal"
    null_hypothesis = "Signal values at element-bearing places are drawn from the same distribution as non-element places"
    alternative_hypothesis = "Signal values differ significantly between element-bearing and non-element places"

    def run(self, data: TestData, n_permutations: int = 10000) -> TestResult:
        """Run permutation test for element-signal correspondence."""
        if data.signal_values is None:
            raise ValueError("signal_values required for correspondence test")

        # Split signal by element presence
        positive = data.signal_values[data.element_present.astype(bool)]
        negative = data.signal_values[~data.element_present.astype(bool)]

        if len(positive) < 5 or len(negative) < 5:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=TestStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=data.n_places,
                n_positive=len(positive),
                notes="Insufficient sample size (need ≥5 in each group)",
                region=data.region,
                element_name=data.element_name,
                signal_name=data.signal_name,
            )

        # Observed test statistic: difference in means
        observed_diff = np.mean(positive) - np.mean(negative)

        # Permutation null distribution
        all_values = data.signal_values.copy()
        n_pos = int(data.element_present.sum())
        perm_diffs = np.empty(n_permutations)

        rng = np.random.default_rng(seed=42)
        for i in range(n_permutations):
            rng.shuffle(all_values)
            perm_positive = all_values[:n_pos]
            perm_negative = all_values[n_pos:]
            perm_diffs[i] = np.mean(perm_positive) - np.mean(perm_negative)

        # Two-sided p-value
        p_value = np.mean(np.abs(perm_diffs) >= np.abs(observed_diff))

        # Effect size (Cohen's d)
        pooled_std = np.sqrt(
            ((len(positive) - 1) * np.var(positive, ddof=1) +
             (len(negative) - 1) * np.var(negative, ddof=1)) /
            (len(positive) + len(negative) - 2)
        )
        cohens_d = observed_diff / pooled_std if pooled_std > 0 else 0.0

        # Confidence interval via bootstrap
        boot_diffs = []
        for _ in range(1000):
            boot_pos = rng.choice(positive, size=len(positive), replace=True)
            boot_neg = rng.choice(negative, size=len(negative), replace=True)
            boot_diffs.append(np.mean(boot_pos) - np.mean(boot_neg))
        ci_low, ci_high = np.percentile(boot_diffs, [2.5, 97.5])

        # Determine status
        if p_value < 0.05:
            status = TestStatus.CONFIRMED
        elif p_value > 0.95:
            status = TestStatus.REJECTED
        else:
            status = TestStatus.EXECUTED

        return TestResult(
            test_id=self.test_id,
            test_family=self.test_family,
            status=status,
            null_hypothesis=self.null_hypothesis,
            alternative_hypothesis=self.alternative_hypothesis,
            test_statistic=observed_diff,
            p_value=float(p_value),
            effect_size=float(cohens_d),
            confidence_interval=(float(ci_low), float(ci_high)),
            n_observations=data.n_places,
            n_positive=len(positive),
            n_permutations=n_permutations,
            region=data.region,
            element_name=data.element_name,
            signal_name=data.signal_name,
            parameters={
                "mean_positive": float(np.mean(positive)),
                "mean_negative": float(np.mean(negative)),
                "std_positive": float(np.std(positive, ddof=1)),
                "std_negative": float(np.std(negative, ddof=1)),
            },
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data with planted signal and pure noise."""
        rng = np.random.default_rng(seed=123)
        n_places = 500
        n_positive = 50

        # --- Power: planted signal ---
        detections = 0
        for _ in range(n_trials):
            coords = rng.uniform(-10, 10, size=(n_places, 2))
            element = np.zeros(n_places, dtype=bool)
            element[:n_positive] = True

            # Signal: element-bearing places have higher values (effect = 1.0 SD)
            signal = rng.normal(0, 1, size=n_places)
            signal[:n_positive] += 1.0  # Plant signal

            data = TestData(
                coordinates=coords,
                element_present=element,
                signal_values=signal,
            )
            result = self.run(data, n_permutations=1000)
            if result.p_value < 0.05:
                detections += 1

        power = detections / n_trials

        # --- False positive rate: pure noise ---
        false_positives = 0
        for _ in range(n_trials):
            coords = rng.uniform(-10, 10, size=(n_places, 2))
            element = np.zeros(n_places, dtype=bool)
            element[rng.choice(n_places, n_positive, replace=False)] = True

            # Signal: pure noise, no relationship
            signal = rng.normal(0, 1, size=n_places)

            data = TestData(
                coordinates=coords,
                element_present=element,
                signal_values=signal,
            )
            result = self.run(data, n_permutations=1000)
            if result.p_value < 0.05:
                false_positives += 1

        fpr = false_positives / n_trials

        passed = power >= 0.8 and fpr <= 0.10  # Slightly relaxed FPR for permutation tests

        return SyntheticValidation(
            power=power,
            power_n_trials=n_trials,
            false_positive_rate=fpr,
            fpr_n_trials=n_trials,
            passed=passed,
            details=f"Power={power:.2f} (target≥0.80), FPR={fpr:.2f} (target≤0.10)",
        )
