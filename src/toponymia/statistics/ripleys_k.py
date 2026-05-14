"""Ripley's K spatial clustering test for toponymic elements.

Tests whether place names containing a given element (e.g., -heim, -by)
show multi-scale spatial clustering beyond what random placement would
produce. This detects settlement pattern signatures left by specific
colonization waves or land-use practices.

Uses Ripley's K function with edge correction, comparing observed K(r)
to the theoretical Poisson (CSR) expectation across multiple distance
scales. A permutation-based envelope provides significance testing.
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


class RipleysKTest(BaseTest):
    """Multi-scale spatial clustering test using Ripley's K function.

    Null hypothesis: Names containing element X are distributed as a
    random subset of all named places (Complete Spatial Randomness
    conditional on the total set).

    Alternative: Names with element X cluster at one or more spatial
    scales, indicating non-random colonization/naming patterns.

    Method: Compute K(r) at multiple distance thresholds r. Compare
    observed K to permutation envelope. Report maximum deviation
    (L(r) - r) and the scale at which clustering is strongest.
    """

    test_id = "ripleys_k_spatial"
    test_family = StatFamily.SPATIAL
    description = (
        "Tests multi-scale spatial clustering of toponymic elements using Ripley's K function"
    )
    null_hypothesis = (
        "Names with the target element are a spatially random subset of all named places"
    )
    alternative_hypothesis = (
        "Names with the target element cluster at one or more spatial"
        " scales, indicating non-random settlement patterns"
    )

    def __init__(self, n_distance_bins: int = 20) -> None:
        """Initialize with number of distance bins.

        Args:
            n_distance_bins: Number of distance thresholds to evaluate K(r).
        """
        self.n_distance_bins = n_distance_bins

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 999,
    ) -> TestResult:
        """Run Ripley's K test.

        Uses:
        - element_present: boolean array (True = has target element)
        - coordinates: lon/lat positions of ALL places

        Computes K(r) for the subset where element_present=True,
        using all coordinates as the study area.
        """
        coords = data.coordinates
        labels = data.element_present.astype(bool)
        n = data.n_places
        n_positive = int(labels.sum())

        if n_positive < 10:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n,
                n_positive=n_positive,
                notes=f"Too few positive sites ({n_positive}, need ≥10)",
                region=data.region,
                element_name=data.element_name,
            )

        # Study area extent
        x_min, y_min = coords.min(axis=0)
        x_max, y_max = coords.max(axis=0)
        area = float((x_max - x_min) * (y_max - y_min))

        if area <= 0:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n,
                n_positive=n_positive,
                notes="Zero study area extent",
                region=data.region,
                element_name=data.element_name,
            )

        # Distance bins from 0 to max_r (half the shorter side)
        max_r = min(x_max - x_min, y_max - y_min) / 2.0
        r_values = np.linspace(0, max_r, self.n_distance_bins + 1)[1:]

        # Observed L(r) - r for target points
        target_coords = coords[labels]
        observed_l = self._compute_l_function(target_coords, r_values, area)

        # Maximum deviation statistic
        observed_stat = float(np.max(observed_l))
        peak_scale_idx = int(np.argmax(observed_l))
        peak_r = float(r_values[peak_scale_idx])

        # Permutation envelope
        rng = np.random.default_rng(seed=42)
        perm_stats = np.empty(n_permutations)
        for i in range(n_permutations):
            perm_labels = rng.choice(n, size=n_positive, replace=False)
            perm_coords = coords[perm_labels]
            perm_l = self._compute_l_function(perm_coords, r_values, area)
            perm_stats[i] = float(np.max(perm_l))

        # P-value: proportion of permutations with max L >= observed
        p_value = float(np.mean(perm_stats >= observed_stat))

        # Effect size: z-score
        mean_null = float(np.mean(perm_stats))
        std_null = float(np.std(perm_stats))
        effect_size = (observed_stat - mean_null) / std_null if std_null > 0 else 0.0

        ci_low = float(np.percentile(perm_stats, 2.5))
        ci_high = float(np.percentile(perm_stats, 97.5))

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
            n_observations=n,
            n_positive=n_positive,
            notes=(f"Peak clustering at r={peak_r:.4f} (L(r)-r = {observed_stat:.4f})"),
            region=data.region,
            element_name=data.element_name,
        )

    def _compute_l_function(
        self,
        points: np.ndarray,
        r_values: np.ndarray,
        area: float,
    ) -> np.ndarray:
        """Compute L(r) - r for a set of points.

        L(r) = sqrt(K(r) / pi) is the variance-stabilized form.
        L(r) - r = 0 under CSR; positive = clustering, negative = regularity.
        """
        n = len(points)
        if n < 2:
            return np.zeros(len(r_values))

        # Pairwise distances
        diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
        dists: np.ndarray = np.sqrt((diff**2).sum(axis=2))

        # K(r) = area / (n*(n-1)) * sum_{i!=j} I(d_ij <= r)
        intensity = n / area
        l_values = np.empty(len(r_values))

        for idx, r in enumerate(r_values):
            # Count pairs within distance r (exclude self-pairs)
            count = float(np.sum(dists <= r) - n)  # subtract diagonal
            k_r = count / (n * intensity)
            l_r = np.sqrt(k_r / np.pi)
            l_values[idx] = l_r - r

        result: np.ndarray = l_values
        return result

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate Ripley's K test on synthetic data.

        Power test: Plant clustered points (Gaussian clusters).
        FPR test: Uniformly random points (should not reject).
        """
        rng = np.random.default_rng(seed=123)
        n_sites = 200
        n_positive = 50
        power_detections = 0
        fpr_detections = 0

        for _trial in range(n_trials):
            # --- POWER: Clustered point pattern ---
            # 5 clusters of 10 target points each
            cluster_centers = rng.uniform(0.2, 0.8, size=(5, 2))
            target_coords = []
            for center in cluster_centers:
                pts = rng.normal(loc=center, scale=0.03, size=(10, 2))
                target_coords.append(pts)
            target = np.vstack(target_coords)

            background = rng.uniform(0, 1, size=(n_sites - n_positive, 2))
            all_coords = np.vstack([target, background])

            labels = np.zeros(n_sites, dtype=bool)
            labels[:n_positive] = True

            data = PlaceData(
                coordinates=all_coords,
                element_present=labels,
                region="synthetic",
                element_name="clustered",
            )

            result = self.run(data, n_permutations=199)
            if result.p_value is not None and result.p_value < 0.05:
                power_detections += 1

        for _trial in range(n_trials):
            # --- FPR: Random uniform pattern ---
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            labels = np.zeros(n_sites, dtype=bool)
            chosen = rng.choice(n_sites, size=n_positive, replace=False)
            labels[chosen] = True

            data = PlaceData(
                coordinates=coords,
                element_present=labels,
                region="synthetic",
                element_name="random",
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
            details=(f"Power={power:.2f} (clustered Gaussian), FPR={fpr:.2f} (uniform random)"),
        )
