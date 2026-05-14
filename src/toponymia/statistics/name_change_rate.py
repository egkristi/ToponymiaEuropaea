"""Name change rate test for temporal frequency analysis.

Tests whether the rate of toponymic changes (renamings, spelling reforms,
status changes) in a region significantly differs from a baseline rate,
indicating periods of intensive renaming activity.

This differs from political_renaming.py (which detects temporal clustering)
by measuring the *rate* over longer periods and comparing between regions
or against an expected background rate.
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


class NameChangeRateTest(BaseTest):
    """Test for anomalous name change rates by region or period.

    Null hypothesis: The rate of name changes in the target region/period
    equals the baseline rate (uniform Poisson process).

    Alternative: The rate is significantly elevated or suppressed,
    indicating policy intervention, cultural shift, or conquest.

    Method: Model name changes as a Poisson process. Compare observed
    count in a period to the expected count given the baseline rate.
    Uses a permutation test to handle non-Poisson overdispersion.
    """

    test_id = "name_change_rate"
    test_family = StatFamily.TEMPORAL
    description = (
        "Tests whether name change frequency in a region/period differs from baseline rates"
    )
    null_hypothesis = "Name changes occur at a uniform background rate across all regions/periods"
    alternative_hypothesis = (
        "The target region/period has a significantly different"
        " name change rate, indicating external intervention"
    )

    def __init__(self, period_years: int = 50) -> None:
        """Initialize with analysis period length.

        Args:
            period_years: Length of each time bin for rate calculation.
        """
        self.period_years = period_years

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 10000,
    ) -> TestResult:
        """Run name change rate test.

        Uses:
        - signal_values: years of name changes (float array of change dates)
        - element_present: boolean mask (True = in target region/subset)
        - coordinates: positions (for spatial context)

        Computes per-period rates for target vs non-target subsets.
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
                notes="No signal_values (change years) provided",
                region=data.region,
                element_name=data.element_name,
            )

        change_years = data.signal_values
        target_mask = data.element_present.astype(bool)
        n = data.n_places
        n_target = int(target_mask.sum())
        n_control = n - n_target

        if n_target < 5 or n_control < 5:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n,
                n_positive=n_target,
                notes=(
                    f"Insufficient sites: {n_target} target, {n_control} control (need ≥5 each)"
                ),
                region=data.region,
                element_name=data.element_name,
            )

        # Compute rate statistic: target rate / control rate
        target_years = change_years[target_mask]
        control_years = change_years[~target_mask]

        # Rate = count of valid changes / number of sites
        target_rate = self._compute_rate(target_years, n_target)
        control_rate = self._compute_rate(control_years, n_control)

        # Rate ratio as test statistic
        if control_rate > 0:
            observed_ratio = target_rate / control_rate
        else:
            observed_ratio = target_rate * 10.0 if target_rate > 0 else 1.0

        # Permutation test on rate ratio
        rng = np.random.default_rng(seed=42)
        perm_ratios = np.empty(n_permutations)
        for i in range(n_permutations):
            perm_mask = rng.permutation(target_mask)
            perm_target = change_years[perm_mask]
            perm_control = change_years[~perm_mask]
            perm_t_rate = self._compute_rate(perm_target, n_target)
            perm_c_rate = self._compute_rate(perm_control, n_control)
            if perm_c_rate > 0:
                perm_ratios[i] = perm_t_rate / perm_c_rate
            else:
                perm_ratios[i] = perm_t_rate * 10.0 if perm_t_rate > 0 else 1.0

        # Two-sided p-value (elevated OR suppressed)
        p_value = float(
            np.mean(np.abs(np.log(perm_ratios + 1e-10)) >= np.abs(np.log(observed_ratio + 1e-10)))
        )

        # Effect size: log rate ratio z-score
        log_obs = np.log(observed_ratio + 1e-10)
        log_perms = np.log(perm_ratios + 1e-10)
        mean_null = float(np.mean(log_perms))
        std_null = float(np.std(log_perms))
        effect_size = (log_obs - mean_null) / std_null if std_null > 0 else 0.0

        ci_low = float(np.percentile(perm_ratios, 2.5))
        ci_high = float(np.percentile(perm_ratios, 97.5))

        if p_value < 0.05 and abs(effect_size) > 0.5:
            status = StatStatus.CONFIRMED
        elif p_value < 0.05:
            status = StatStatus.EXECUTED
        else:
            status = StatStatus.EXECUTED

        direction = "elevated" if observed_ratio > 1.0 else "suppressed"

        return TestResult(
            test_id=self.test_id,
            test_family=self.test_family,
            status=status,
            null_hypothesis=self.null_hypothesis,
            alternative_hypothesis=self.alternative_hypothesis,
            test_statistic=observed_ratio,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(ci_low, ci_high),
            n_observations=n,
            n_positive=n_target,
            notes=(
                f"Rate ratio={observed_ratio:.3f} ({direction}), "
                f"target_rate={target_rate:.4f}, "
                f"control_rate={control_rate:.4f}"
            ),
            region=data.region,
            element_name=data.element_name,
        )

    def _compute_rate(self, years: np.ndarray, n_sites: int) -> float:
        """Compute name change rate as changes per site.

        Counts non-zero years (0 means no change observed).
        """
        if n_sites == 0:
            return 0.0
        # Count actual changes (non-zero values indicate a change year)
        n_changes = int(np.sum(years > 0))
        return n_changes / n_sites

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate name change rate test on synthetic data.

        Power test: Target region has 3x the change rate of control.
        FPR test: Both regions have equal rates.
        """
        rng = np.random.default_rng(seed=456)
        n_sites = 200
        n_target = 50
        power_detections = 0
        fpr_detections = 0

        for _trial in range(n_trials):
            # --- POWER: Target has 3x higher change rate ---
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            target_mask = np.zeros(n_sites, dtype=bool)
            target_mask[:n_target] = True

            # Target: 70% have changes, Control: 25% have changes
            change_years = np.zeros(n_sites)
            for i in range(n_sites):
                if target_mask[i]:
                    if rng.random() < 0.70:
                        change_years[i] = rng.uniform(1850, 1950)
                else:
                    if rng.random() < 0.25:
                        change_years[i] = rng.uniform(1850, 1950)

            data = PlaceData(
                coordinates=coords,
                element_present=target_mask,
                signal_values=change_years,
                region="synthetic",
                element_name="power_test",
            )

            result = self.run(data, n_permutations=199)
            if result.p_value is not None and result.p_value < 0.05:
                power_detections += 1

        for _trial in range(n_trials):
            # --- FPR: Equal rates in both groups ---
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            target_mask = np.zeros(n_sites, dtype=bool)
            target_mask[:n_target] = True

            # Both: 30% have changes
            change_years = np.zeros(n_sites)
            for i in range(n_sites):
                if rng.random() < 0.30:
                    change_years[i] = rng.uniform(1850, 1950)

            data = PlaceData(
                coordinates=coords,
                element_present=target_mask,
                signal_values=change_years,
                region="synthetic",
                element_name="fpr_test",
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
            details=(f"Power={power:.2f} (3x rate difference), FPR={fpr:.2f} (equal rates)"),
        )
