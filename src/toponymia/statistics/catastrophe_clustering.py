"""Catastrophe clustering test for disaster-related toponyms.

Tests whether place names indicating natural disasters (flood, fire,
landslide, avalanche) cluster near known hazard zones significantly
more than random placement. This validates the "landscape memory"
hypothesis — that communities encode environmental hazard information
in place names.

Uses a point-process approach: compare the mean hazard signal at
disaster-name sites vs. non-disaster sites, with permutation inference.
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


class CatastropheClusteringTest(BaseTest):
    """Test for correlation between disaster toponyms and hazard zones.

    Null hypothesis: Places with disaster-related names are not
    associated with higher hazard signals than other places.

    Alternative: Disaster-named places have significantly higher
    hazard values, indicating toponymic encoding of environmental risk.

    Method: Compare mean signal_values for element_present=True vs False.
    Permutation test on the mean difference.
    """

    test_id = "catastrophe_clustering"
    test_family = StatFamily.CATASTROPHE_CLUSTERING
    description = (
        "Tests whether disaster-related toponyms correlate with environmental hazard zones"
    )
    null_hypothesis = (
        "Disaster-named places have the same hazard exposure as non-disaster-named places"
    )
    alternative_hypothesis = (
        "Disaster-named places have significantly higher hazard"
        " values, encoding environmental memory in toponymy"
    )

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 10000,
    ) -> TestResult:
        """Run catastrophe clustering test.

        Uses:
        - element_present: boolean (True = has disaster element)
        - signal_values: hazard metric (e.g., flood risk, slope angle)
        - coordinates: positions (for spatial context)
        """
        if data.signal_values is None:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=data.n_places,
                n_positive=0,
                notes="No signal_values (hazard data) provided",
                region=data.region,
                element_name=data.element_name,
            )

        labels = data.element_present.astype(bool)
        signal = data.signal_values
        n = data.n_places
        n_positive = int(labels.sum())
        n_negative = n - n_positive

        if n_positive < 5 or n_negative < 5:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n,
                n_positive=n_positive,
                notes=(
                    f"Insufficient sites: {n_positive} disaster, "
                    f"{n_negative} non-disaster (need ≥5 each)"
                ),
                region=data.region,
                element_name=data.element_name,
            )

        # Observed mean difference
        mean_disaster = float(np.mean(signal[labels]))
        mean_other = float(np.mean(signal[~labels]))
        observed_diff = mean_disaster - mean_other

        # Permutation test
        rng = np.random.default_rng(seed=42)
        perm_diffs = np.empty(n_permutations)
        for i in range(n_permutations):
            perm_labels = rng.permutation(labels)
            perm_diff = float(np.mean(signal[perm_labels])) - float(np.mean(signal[~perm_labels]))
            perm_diffs[i] = perm_diff

        # One-sided p-value (disaster names should have HIGHER hazard)
        p_value = float(np.mean(perm_diffs >= observed_diff))

        # Effect size: Cohen's d
        pooled_std = float(np.std(signal))
        effect_size = observed_diff / pooled_std if pooled_std > 0 else 0.0

        ci_low = float(np.percentile(perm_diffs, 2.5))
        ci_high = float(np.percentile(perm_diffs, 97.5))

        if p_value < 0.05 and effect_size > 0.5:
            status = StatStatus.CONFIRMED
        elif p_value < 0.05:
            status = StatStatus.EXECUTED
        else:
            status = StatStatus.EXECUTED

        return TestResult(
            test_id=self.test_id,
            test_family=self.test_family,
            status=status,
            null_hypothesis=self.null_hypothesis,
            alternative_hypothesis=self.alternative_hypothesis,
            test_statistic=observed_diff,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(ci_low, ci_high),
            n_observations=n,
            n_positive=n_positive,
            notes=(
                f"Mean hazard: disaster={mean_disaster:.3f}, "
                f"other={mean_other:.3f}, diff={observed_diff:.3f}"
            ),
            region=data.region,
            element_name=data.element_name,
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate catastrophe test on synthetic data.

        Power test: Disaster names placed in high-hazard zones.
        FPR test: No correlation between names and hazard.
        """
        rng = np.random.default_rng(seed=321)
        n_sites = 200
        n_disaster = 30
        power_detections = 0
        fpr_detections = 0

        for _trial in range(n_trials):
            # --- POWER: Disaster names in high-hazard areas ---
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            labels = np.zeros(n_sites, dtype=bool)
            labels[:n_disaster] = True

            # Hazard signal: disaster sites get higher values
            signal = rng.normal(0.3, 0.2, size=n_sites)
            signal[:n_disaster] += 0.8  # Boost disaster sites

            data = PlaceData(
                coordinates=coords,
                element_present=labels,
                signal_values=signal,
                region="synthetic",
                element_name="disaster_power",
            )

            result = self.run(data, n_permutations=199)
            if result.p_value is not None and result.p_value < 0.05:
                power_detections += 1

        for _trial in range(n_trials):
            # --- FPR: No correlation ---
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            labels = np.zeros(n_sites, dtype=bool)
            chosen = rng.choice(n_sites, size=n_disaster, replace=False)
            labels[chosen] = True

            # Same hazard distribution for all
            signal = rng.normal(0.5, 0.3, size=n_sites)

            data = PlaceData(
                coordinates=coords,
                element_present=labels,
                signal_values=signal,
                region="synthetic",
                element_name="disaster_fpr",
            )

            result = self.run(data, n_permutations=199)
            if result.p_value is not None and result.p_value < 0.05:
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
                f"Power={power:.2f} (hazard-correlated placement), FPR={fpr:.2f} (uncorrelated)"
            ),
        )
