"""Sensory correspondence test for colour/sound toponyms.

Tests whether place names containing colour terms (e.g., "Svart-", "Hvit-",
"Rød-", "Grønn-") correlate with measurable environmental properties at
those locations. For example:
- "Svartdal" (Black valley) → darker vegetation/shadow
- "Grønland" (Green land) → higher NDVI/vegetation density
- "Rødberg" (Red mountain) → reddish geological substrate

Uses signal_values as the continuous environmental measurement (e.g.,
reflectance, NDVI, soil iron content) and tests whether sites with the
colour element have significantly different values than other sites.

Method: Two-sided permutation test on mean difference (unlike catastrophe
clustering which is one-sided, colour correspondence can go either way).
"""

from __future__ import annotations

import numpy as np

from toponymia.statistics.base import (
    BaseTest,
    PlaceData,
    StatFamily,
    StatStatus,
    SyntheticValidation,
    TestResult,
)


class SensoryCorrespondenceTest(BaseTest):
    """Test for correlation between sensory toponyms and environmental signals.

    Null hypothesis: Places with colour/sensory name elements have the same
    environmental signal values as other places in the region.

    Alternative: Sensory-named places have significantly different signal
    values, indicating that the name encodes a real perceptual feature.

    Method: Compare mean signal_values for element_present=True vs False.
    Two-sided permutation test on the absolute mean difference.
    """

    test_id = "sensory_correspondence"
    test_family = StatFamily.SENSORY_CORRESPONDENCE
    description = (
        "Tests whether colour/sensory toponyms correlate with measurable environmental properties"
    )
    null_hypothesis = (
        "Sensory-named places have the same environmental signal"
        " as non-sensory-named places in the region"
    )
    alternative_hypothesis = (
        "Sensory-named places have significantly different"
        " environmental signal values, encoding perceptual features"
    )
    min_sensory_sites: int = 5

    def run(self, data: PlaceData, n_permutations: int = 999) -> TestResult:
        """Run the sensory correspondence permutation test."""
        n_sensory = int(np.sum(data.element_present))
        n_other = data.n_places - n_sensory

        # Need signal values
        if data.signal_values is None:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=data.n_places,
                n_positive=n_sensory,
                notes="No signal values provided (need spectral/environmental data)",
            )

        # Need enough sites in both groups
        if n_sensory < self.min_sensory_sites or n_other < self.min_sensory_sites:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=data.n_places,
                n_positive=n_sensory,
                notes=(
                    f"Too few sites: {n_sensory} sensory, {n_other} other"
                    f" (need {self.min_sensory_sites} each)"
                ),
            )

        signal = data.signal_values
        mask = data.element_present.astype(bool)

        # Observed mean difference
        mean_sensory = float(np.mean(signal[mask]))
        mean_other = float(np.mean(signal[~mask]))
        observed_diff = mean_sensory - mean_other
        observed_abs_diff = abs(observed_diff)

        # Permutation test (two-sided)
        rng = np.random.default_rng(42)
        n_extreme = 0
        for _ in range(n_permutations):
            perm = rng.permutation(len(signal))
            perm_signal = signal[perm]
            perm_diff = float(np.mean(perm_signal[mask])) - float(np.mean(perm_signal[~mask]))
            if abs(perm_diff) >= observed_abs_diff:
                n_extreme += 1

        p_value = (n_extreme + 1) / (n_permutations + 1)

        # Effect size: Cohen's d
        std_sensory = float(np.std(signal[mask], ddof=1)) if n_sensory > 1 else 1.0
        std_other = float(np.std(signal[~mask], ddof=1)) if n_other > 1 else 1.0
        pooled_std = float(
            np.sqrt(
                ((n_sensory - 1) * std_sensory**2 + (n_other - 1) * std_other**2)
                / (n_sensory + n_other - 2)
            )
        )
        effect_size = observed_diff / pooled_std if pooled_std > 0 else 0.0

        # Determine status
        if p_value < 0.05:
            status = StatStatus.CONFIRMED
        elif p_value > 0.95:
            status = StatStatus.REJECTED
        else:
            status = StatStatus.EXECUTED

        direction = "higher" if observed_diff > 0 else "lower"
        notes = (
            f"Mean signal: sensory={mean_sensory:.4f}, other={mean_other:.4f}. "
            f"Sensory sites have {direction} values (diff={observed_diff:.4f}). "
            f"Cohen's d={effect_size:.3f}."
        )

        return TestResult(
            test_id=self.test_id,
            test_family=self.test_family,
            status=status,
            null_hypothesis=self.null_hypothesis,
            alternative_hypothesis=self.alternative_hypothesis,
            test_statistic=observed_diff,
            p_value=p_value,
            effect_size=effect_size,
            n_observations=data.n_places,
            n_positive=n_sensory,
            n_permutations=n_permutations,
            notes=notes,
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data with planted signal."""
        rng = np.random.default_rng(123)
        n_sites = 150
        n_sensory = 25
        power_detections = 0
        fpr_detections = 0

        for _ in range(n_trials):
            # POWER: sensory sites have shifted signal
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            labels = np.zeros(n_sites, dtype=bool)
            labels[:n_sensory] = True

            signal = rng.normal(0.5, 0.2, size=n_sites)
            signal[:n_sensory] += 0.4  # Planted shift

            data = PlaceData(
                coordinates=coords,
                element_present=labels,
                signal_values=signal,
                region="synthetic",
                element_name="colour",
            )
            result = self.run(data, n_permutations=199)
            if result.p_value < 0.05:
                power_detections += 1

        for _ in range(n_trials):
            # FPR: no correlation between labels and signal
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            labels = np.zeros(n_sites, dtype=bool)
            chosen = rng.choice(n_sites, size=n_sensory, replace=False)
            labels[chosen] = True

            signal = rng.normal(0.5, 0.2, size=n_sites)

            data = PlaceData(
                coordinates=coords,
                element_present=labels,
                signal_values=signal,
                region="synthetic",
                element_name="random",
            )
            result = self.run(data, n_permutations=199)
            if result.p_value < 0.05:
                fpr_detections += 1

        power = power_detections / n_trials
        fpr = fpr_detections / n_trials

        return SyntheticValidation(
            power=power,
            power_n_trials=n_trials,
            false_positive_rate=fpr,
            fpr_n_trials=n_trials,
            passed=power >= 0.8 and fpr <= 0.10,
            details=(
                f"Sensory correspondence: power={power:.2f}, FPR={fpr:.2f}. "
                f"Planted +0.4 shift in signal for sensory sites."
            ),
        )
