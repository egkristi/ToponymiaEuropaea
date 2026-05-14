"""Migration overfrequency test.

Tests whether toponymic elements associated with a source region
appear at significantly higher frequency in a proposed target/diaspora
region than expected by chance.

For example, if Norse settlers brought place-name elements like -by,
-thorp, -thwaite to the Danelaw, these elements should appear at
higher frequency in the Danelaw than in non-Norse areas of England.

Uses a proportion test comparing element frequency in the target
area vs. the overall background, validated by permutation.
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


class MigrationOverfrequencyTest(BaseTest):
    """Test for diaspora toponymic elements in target areas.

    Null hypothesis: The frequency of the migration-associated name
    element in the target area is consistent with its overall frequency
    in the study region (no enrichment).

    Alternative: The element appears at significantly higher frequency
    in the target area than expected from the regional background,
    indicating a migration/settlement event.

    Method: Compare proportion of element-bearing names in target zone
    vs. background. Use permutation test on the difference in proportions.
    """

    test_id = "migration_overfrequency"
    test_family = StatFamily.MIGRATION
    description = (
        "Tests whether a migration-associated name element is"
        " over-represented in the proposed target/diaspora area"
    )
    null_hypothesis = (
        "The frequency of the toponymic element in the target area"
        " equals its background frequency across the study region"
    )
    alternative_hypothesis = (
        "The element is significantly more frequent in the target"
        " area, indicating a migration/settlement signal"
    )

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 10000,
    ) -> TestResult:
        """Run migration overfrequency test.

        Uses:
        - element_present: boolean array indicating which sites have the
          migration-associated name element
        - signal_values: binary indicator for target/diaspora zone
          (1.0 = in target area, 0.0 = background)
        - coordinates: for reference/reporting

        Args:
            data: TestData with element_present and signal_values.
            n_permutations: Number of permutation trials.
        """
        if data.signal_values is None:
            raise ValueError("signal_values (target zone indicator) required")

        element_mask = data.element_present.astype(bool)
        target_mask = data.signal_values.astype(bool)

        n_total = data.n_places
        n_element = int(element_mask.sum())
        n_target = int(target_mask.sum())
        n_background = n_total - n_target

        if n_target < 5 or n_background < 5:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n_total,
                n_positive=n_element,
                notes=(
                    f"Insufficient zone sizes: {n_target} target,"
                    f" {n_background} background (need ≥5 each)"
                ),
                region=data.region,
                element_name=data.element_name,
            )

        if n_element < 3:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n_total,
                n_positive=n_element,
                notes=f"Too few element-bearing sites: {n_element} (need ≥3)",
                region=data.region,
                element_name=data.element_name,
            )

        # Observed: proportion of element in target vs. background
        n_element_in_target = int((element_mask & target_mask).sum())
        n_element_in_background = int((element_mask & ~target_mask).sum())

        prop_target = n_element_in_target / n_target
        prop_background = n_element_in_background / n_background
        observed_diff = prop_target - prop_background

        # Permutation null: shuffle target zone labels
        rng = np.random.default_rng(seed=42)
        perm_diffs = np.empty(n_permutations)

        for i in range(n_permutations):
            perm_target = np.zeros(n_total, dtype=bool)
            perm_target[rng.choice(n_total, size=n_target, replace=False)] = True

            perm_n_in_target = int((element_mask & perm_target).sum())
            perm_n_in_background = int((element_mask & ~perm_target).sum())

            perm_prop_target = perm_n_in_target / n_target
            perm_prop_background = perm_n_in_background / n_background
            perm_diffs[i] = perm_prop_target - perm_prop_background

        # One-sided p-value: enrichment in target
        p_value = float(np.mean(perm_diffs >= observed_diff))

        # Effect size: standardized difference
        mean_null = float(np.mean(perm_diffs))
        std_null = float(np.std(perm_diffs))
        effect_size = (observed_diff - mean_null) / std_null if std_null > 0 else 0.0

        # Confidence interval on null
        ci_low = float(np.percentile(perm_diffs, 2.5))
        ci_high = float(np.percentile(perm_diffs, 97.5))

        # Status
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
            n_observations=n_total,
            n_positive=n_element,
            n_permutations=n_permutations,
            parameters={
                "n_target_zone": n_target,
                "n_background_zone": n_background,
                "n_element_in_target": n_element_in_target,
                "n_element_in_background": n_element_in_background,
                "proportion_in_target": prop_target,
                "proportion_in_background": prop_background,
                "observed_proportion_difference": observed_diff,
            },
            region=data.region,
            element_name=data.element_name,
            signal_name="target_zone_indicator",
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data.

        Power: Plant enrichment of element in target zone.
        FPR: Element distributed uniformly regardless of zone.
        """
        rng = np.random.default_rng(seed=321)
        n_sites = 300
        n_target = 100  # Target zone = 1/3 of sites
        element_base_rate = 0.10  # 10% base rate

        power_detections = 0
        fpr_rejections = 0

        for _trial in range(n_trials):
            coords = rng.uniform(0, 2, size=(n_sites, 2))

            # Define target zone (first n_target sites)
            signal = np.zeros(n_sites, dtype=float)
            target_idx = rng.choice(n_sites, size=n_target, replace=False)
            signal[target_idx] = 1.0
            target_mask = signal.astype(bool)

            # --- Power trial: Element enriched in target ---
            element_power = np.zeros(n_sites, dtype=bool)
            # Background rate: 10%
            bg_idx = np.where(~target_mask)[0]
            n_bg_element = int(len(bg_idx) * element_base_rate)
            element_power[rng.choice(bg_idx, size=n_bg_element, replace=False)] = True
            # Target rate: 40% (4x enrichment)
            tgt_idx = np.where(target_mask)[0]
            n_tgt_element = int(len(tgt_idx) * 0.40)
            element_power[rng.choice(tgt_idx, size=n_tgt_element, replace=False)] = True

            data_power = PlaceData(
                coordinates=coords.copy(),
                element_present=element_power,
                signal_values=signal.copy(),
                region="synthetic",
                element_name="diaspora_element",
            )
            result_power = self.run(data_power, n_permutations=499)
            if result_power.p_value < 0.05:
                power_detections += 1

            # --- FPR trial: Element uniformly distributed ---
            element_null = np.zeros(n_sites, dtype=bool)
            n_total_element = int(n_sites * element_base_rate)
            element_null[rng.choice(n_sites, size=n_total_element, replace=False)] = True

            signal_null = np.zeros(n_sites, dtype=float)
            null_target_idx = rng.choice(n_sites, size=n_target, replace=False)
            signal_null[null_target_idx] = 1.0

            data_null = PlaceData(
                coordinates=rng.uniform(0, 2, size=(n_sites, 2)),
                element_present=element_null,
                signal_values=signal_null,
                region="synthetic",
                element_name="control",
            )
            result_null = self.run(data_null, n_permutations=499)
            if result_null.p_value < 0.05:
                fpr_rejections += 1

        power = power_detections / n_trials
        fpr = fpr_rejections / n_trials

        return SyntheticValidation(
            power=power,
            power_n_trials=n_trials,
            false_positive_rate=fpr,
            fpr_n_trials=n_trials,
            passed=(power >= 0.8 and fpr <= 0.10),
            details=f"Power={power:.2f} (target≥0.80), FPR={fpr:.2f} (target≤0.10)",
        )
