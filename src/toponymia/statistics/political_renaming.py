"""Political renaming detection test.

Detects statistical signals of coordinated political renaming events
by testing whether name changes cluster temporally beyond what would
be expected from gradual organic evolution.

Examples:
- Soviet-era renamings (Tsaritsyn→Stalingrad→Volgograd)
- Norwegian post-1905 fornorsking (Kristiania→Oslo)
- Post-colonial renaming waves (Rhodesia→Zimbabwe)

The test compares the observed temporal clustering of name changes
against a null model of uniform/Poisson change rate.
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


class PoliticalRenamingTest(BaseTest):
    """Test for coordinated political renaming events.

    Null hypothesis: Name changes occur at a uniform rate over time —
    no temporal clustering beyond random variation.

    Alternative: Name changes are temporally clustered, suggesting
    a coordinated political renaming event or policy.

    Method: Divide the time span into windows and compare observed
    clustering (max count in any window / total changes) against
    permuted timestamps. A spike indicates a political event.
    """

    test_id = "political_renaming"
    test_family = StatFamily.POLITICAL_RENAMING
    description = (
        "Tests whether name changes are temporally clustered,"
        " indicating coordinated political renaming events"
    )
    null_hypothesis = (
        "Name changes occur at a uniform rate over time with no"
        " temporal clustering beyond random variation"
    )
    alternative_hypothesis = (
        "Name changes are temporally clustered, indicating a coordinated political renaming event"
    )

    def __init__(self, window_years: int = 10) -> None:
        """Initialize with window size for temporal binning.

        Args:
            window_years: Size of temporal bins in years.
        """
        self.window_years = window_years

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 10000,
    ) -> TestResult:
        """Run political renaming detection test.

        Uses:
        - signal_values: float array of change years (e.g., 1905, 1924, ...)
          Only non-zero values are treated as actual change events.
        - element_present: boolean, True = name was changed (filter mask)
        - coordinates: for reference/reporting

        Args:
            data: PlaceData with signal_values as change years.
            n_permutations: Number of permutation trials.
        """
        if data.signal_values is None:
            raise ValueError("signal_values (change years) required")

        # Extract change years from sites that have changes
        change_mask = data.element_present.astype(bool)
        change_years = data.signal_values[change_mask]

        n_changes = len(change_years)
        n_total = data.n_places

        if n_changes < 10:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n_total,
                n_positive=n_changes,
                notes=(f"Too few name changes: {n_changes} (need ≥10)"),
                region=data.region,
                element_name=data.element_name,
            )

        # Compute observed clustering statistic
        year_min = float(change_years.min())
        year_max = float(change_years.max())
        time_span = year_max - year_min

        if time_span < self.window_years:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n_total,
                n_positive=n_changes,
                notes=(f"Time span too short: {time_span:.0f} years (need ≥{self.window_years})"),
                region=data.region,
                element_name=data.element_name,
            )

        observed_stat = self._clustering_statistic(change_years, year_min, year_max)

        # Permutation null: shuffle change years uniformly over time span
        rng = np.random.default_rng(seed=42)
        perm_stats = np.empty(n_permutations)

        for i in range(n_permutations):
            perm_years = rng.uniform(year_min, year_max, size=n_changes)
            perm_stats[i] = self._clustering_statistic(perm_years, year_min, year_max)

        # One-sided p-value: higher clustering = more political signal
        p_value = float(np.mean(perm_stats >= observed_stat))

        # Effect size
        mean_null = float(np.mean(perm_stats))
        std_null = float(np.std(perm_stats))
        effect_size = (observed_stat - mean_null) / std_null if std_null > 0 else 0.0

        # Confidence interval on null
        ci_low = float(np.percentile(perm_stats, 2.5))
        ci_high = float(np.percentile(perm_stats, 97.5))

        # Find the peak window
        n_windows = max(1, int(np.ceil(time_span / self.window_years)))
        bins = np.linspace(year_min, year_max, n_windows + 1)
        counts, _ = np.histogram(change_years, bins=bins)
        peak_window_idx = int(np.argmax(counts))
        peak_start = float(bins[peak_window_idx])
        peak_end = float(bins[peak_window_idx + 1])
        peak_count = int(counts[peak_window_idx])

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
            test_statistic=observed_stat,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(ci_low, ci_high),
            n_observations=n_total,
            n_positive=n_changes,
            n_permutations=n_permutations,
            parameters={
                "n_changes": n_changes,
                "year_min": year_min,
                "year_max": year_max,
                "time_span_years": time_span,
                "window_years": self.window_years,
                "n_windows": n_windows,
                "peak_window": f"{peak_start:.0f}–{peak_end:.0f}",
                "peak_count": peak_count,
                "max_proportion_in_window": observed_stat,
            },
            region=data.region,
            element_name=data.element_name,
            signal_name="change_year",
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data.

        Power: Plant a spike of changes in one decade.
        FPR: Changes distributed uniformly over 200 years.
        """
        rng = np.random.default_rng(seed=456)
        n_sites = 200
        n_changes = 50

        power_detections = 0
        fpr_detections = 0

        for _trial in range(n_trials):
            # --- POWER: Plant a political renaming event ---
            # 60% of changes in one decade (1900-1910)
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            change_mask = np.zeros(n_sites, dtype=bool)
            change_idx = rng.choice(n_sites, size=n_changes, replace=False)
            change_mask[change_idx] = True

            signal = np.zeros(n_sites, dtype=float)
            # 30 changes clustered in 1900-1910
            n_clustered = 30
            signal[change_idx[:n_clustered]] = rng.uniform(1900, 1910, size=n_clustered)
            # 20 changes spread over 1800-2000
            n_spread = n_changes - n_clustered
            signal[change_idx[n_clustered:]] = rng.uniform(1800, 2000, size=n_spread)

            data = PlaceData(
                coordinates=coords,
                element_present=change_mask.astype(float),
                signal_values=signal,
                region="synthetic_event",
                element_name="renamed_places",
            )
            result = self.run(data, n_permutations=499)
            if result.p_value < 0.05:
                power_detections += 1

        for _trial in range(n_trials):
            # --- FPR: No clustering ---
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            change_mask = np.zeros(n_sites, dtype=bool)
            change_idx = rng.choice(n_sites, size=n_changes, replace=False)
            change_mask[change_idx] = True

            signal = np.zeros(n_sites, dtype=float)
            signal[change_idx] = rng.uniform(1800, 2000, size=n_changes)

            data = PlaceData(
                coordinates=coords,
                element_present=change_mask.astype(float),
                signal_values=signal,
                region="synthetic_null",
                element_name="no_event",
            )
            result = self.run(data, n_permutations=499)
            if result.p_value < 0.05:
                fpr_detections += 1

        power = power_detections / n_trials
        fpr = fpr_detections / n_trials
        passed = power > 0.8 and fpr < 0.05

        return SyntheticValidation(
            power=power,
            power_n_trials=n_trials,
            false_positive_rate=fpr,
            fpr_n_trials=n_trials,
            passed=passed,
            details=(
                f"Power={power:.2f} (60% clustered in 10yr window),"
                f" FPR={fpr:.2f} (uniform over 200yr)"
            ),
        )

    def _clustering_statistic(
        self,
        years: np.ndarray,
        year_min: float,
        year_max: float,
    ) -> float:
        """Compute clustering statistic: max proportion in any window.

        Higher values indicate more temporal clustering.
        """
        time_span = year_max - year_min
        n_windows = max(1, int(np.ceil(time_span / self.window_years)))
        bins = np.linspace(year_min, year_max, n_windows + 1)
        counts, _ = np.histogram(years, bins=bins)
        n_total = len(years)
        if n_total == 0:
            return 0.0
        return float(counts.max()) / n_total
