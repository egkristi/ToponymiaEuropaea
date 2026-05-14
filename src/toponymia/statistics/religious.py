"""Religious stratigraphy test.

Tests whether Christian church-site names (kirke-, St.-, etc.) are
significantly over-represented at locations with pre-Christian cult-name
elements (hov-, vé-, horg-), indicating Christian overlay on pre-Christian
sacred sites.

Uses a permutation test on co-occurrence frequency.
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


class ReligiousStratigraphyTest(BaseTest):
    """Test for Christian overlay on pre-Christian sacred sites.

    Null hypothesis: The co-occurrence of Christian and pre-Christian
    name elements at the same location is no greater than expected
    by chance given their individual frequencies.

    Alternative: Christian elements are significantly over-represented
    near pre-Christian cult-name sites.

    The test uses a proximity-based co-occurrence measure: for each
    pre-Christian site, count how many Christian-named sites fall
    within a threshold distance. Compare to permutation null.
    """

    test_id = "religious_stratigraphy"
    test_family = StatFamily.RELIGIOUS_STRATIGRAPHY
    description = (
        "Tests whether Christian names co-occur with pre-Christian"
        " cult-site names more than expected by chance"
    )
    null_hypothesis = (
        "Christian site names are randomly distributed with respect"
        " to pre-Christian cult-name locations"
    )
    alternative_hypothesis = (
        "Christian site names are significantly over-represented near pre-Christian cult-name sites"
    )

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 10000,
        *,
        proximity_threshold_km: float = 2.0,
    ) -> TestResult:
        """Run co-occurrence permutation test.

        Uses element_present for pre-Christian sites.
        Uses signal_values as binary indicator for Christian sites (1.0 = Christian).
        Coordinates are in decimal degrees (lon, lat).

        Args:
            data: TestData with coordinates, element_present (pre-Christian),
                  and signal_values (Christian indicator).
            n_permutations: Number of permutations.
            proximity_threshold_km: Distance threshold in km for co-occurrence.
        """
        if data.signal_values is None:
            raise ValueError("signal_values (Christian site indicator) required")

        pre_christian_mask = data.element_present.astype(bool)
        christian_mask = data.signal_values.astype(bool)

        n_pre_christian = int(pre_christian_mask.sum())
        n_christian = int(christian_mask.sum())

        if n_pre_christian < 3 or n_christian < 3:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=data.n_places,
                n_positive=n_pre_christian,
                notes=(
                    f"Insufficient sites: {n_pre_christian} pre-Christian,"
                    f" {n_christian} Christian (need ≥3 each)"
                ),
                region=data.region,
                element_name=data.element_name,
            )

        # Compute pairwise distances (approximate, using Euclidean on degrees)
        # For better accuracy, convert to km using a local approximation
        coords = data.coordinates  # shape (N, 2): lon, lat
        pre_christian_coords = coords[pre_christian_mask]
        christian_coords = coords[christian_mask]

        # Approximate degree → km conversion at mean latitude
        mean_lat = np.mean(coords[:, 1])
        km_per_deg_lat = 111.32
        km_per_deg_lon = 111.32 * np.cos(np.radians(mean_lat))

        # Count observed co-occurrences within threshold
        observed_count = self._count_cooccurrences(
            pre_christian_coords,
            christian_coords,
            proximity_threshold_km,
            km_per_deg_lat,
            km_per_deg_lon,
        )

        # Permutation null: randomly relabel Christian sites
        rng = np.random.default_rng(seed=42)
        perm_counts = np.empty(n_permutations)

        for i in range(n_permutations):
            perm_christian_idx = rng.choice(len(coords), size=n_christian, replace=False)
            perm_christian_coords = coords[perm_christian_idx]
            perm_counts[i] = self._count_cooccurrences(
                pre_christian_coords,
                perm_christian_coords,
                proximity_threshold_km,
                km_per_deg_lat,
                km_per_deg_lon,
            )

        # One-sided p-value: how often is permuted count >= observed?
        p_value = float(np.mean(perm_counts >= observed_count))

        # Effect size: standardized excess co-occurrence
        mean_null = float(np.mean(perm_counts))
        std_null = float(np.std(perm_counts))
        effect_size = (observed_count - mean_null) / std_null if std_null > 0 else 0.0

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
            test_statistic=float(observed_count),
            p_value=p_value,
            effect_size=effect_size,
            n_observations=data.n_places,
            n_positive=n_pre_christian,
            n_permutations=n_permutations,
            parameters={
                "n_christian": n_christian,
                "observed_cooccurrences": int(observed_count),
                "mean_null_cooccurrences": mean_null,
                "proximity_threshold_km": proximity_threshold_km,
            },
            region=data.region,
            element_name=data.element_name,
            signal_name="christian_site_indicator",
        )

    def _count_cooccurrences(
        self,
        pre_christian_coords: np.ndarray,
        christian_coords: np.ndarray,
        threshold_km: float,
        km_per_deg_lat: float,
        km_per_deg_lon: float,
    ) -> float:
        """Count pre-Christian sites that have a Christian site within threshold."""
        count = 0
        for pc_coord in pre_christian_coords:
            # Compute distances from this pre-Christian site to all Christian sites
            dlat = (christian_coords[:, 1] - pc_coord[1]) * km_per_deg_lat
            dlon = (christian_coords[:, 0] - pc_coord[0]) * km_per_deg_lon
            distances = np.sqrt(dlat**2 + dlon**2)

            if np.any(distances <= threshold_km):
                count += 1

        return float(count)

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data.

        Plants Christian sites preferentially near pre-Christian sites
        to test detection power.
        """
        rng = np.random.default_rng(seed=456)
        n_sites = 200
        n_pre_christian = 20
        n_christian = 30

        power_detections = 0
        fpr_rejections = 0

        for _trial in range(n_trials):
            # Base coordinates (spread over ~1 degree area)
            coords = rng.uniform(0, 1, size=(n_sites, 2))

            # Pre-Christian sites: random subset
            element_present = np.zeros(n_sites, dtype=bool)
            pre_idx = rng.choice(n_sites, size=n_pre_christian, replace=False)
            element_present[pre_idx] = True

            # --- Power trial: Christian sites clustered near pre-Christian ---
            signal_power = np.zeros(n_sites, dtype=float)
            # Place Christian sites: 70% near pre-Christian, 30% random
            n_near = int(n_christian * 0.7)
            n_far = n_christian - n_near

            # Near pre-Christian sites (within 0.01 degrees ~ 1 km)
            near_targets = rng.choice(pre_idx, size=n_near)
            near_coords = coords[near_targets] + rng.normal(0, 0.005, size=(n_near, 2))
            # Place these in the coord array
            near_indices = rng.choice(np.where(~element_present)[0], size=n_near, replace=False)
            coords[near_indices] = near_coords
            signal_power[near_indices] = 1.0

            # Far Christian sites (random)
            remaining_non_pre = np.where(~element_present & (signal_power == 0))[0]
            far_indices = rng.choice(
                remaining_non_pre, size=min(n_far, len(remaining_non_pre)), replace=False
            )
            signal_power[far_indices] = 1.0

            data_power = PlaceData(
                coordinates=coords.copy(),
                element_present=element_present.copy(),
                signal_values=signal_power,
                region="synthetic",
                element_name="hov-/vé-",
            )
            result_power = self.run(data_power, n_permutations=499, proximity_threshold_km=1.5)
            if result_power.p_value < 0.05:
                power_detections += 1

            # --- FPR trial: Christian sites placed randomly ---
            signal_null = np.zeros(n_sites, dtype=float)
            null_christian_idx = rng.choice(n_sites, size=n_christian, replace=False)
            signal_null[null_christian_idx] = 1.0

            coords_null = rng.uniform(0, 1, size=(n_sites, 2))
            element_null = np.zeros(n_sites, dtype=bool)
            element_null[rng.choice(n_sites, size=n_pre_christian, replace=False)] = True

            data_null = PlaceData(
                coordinates=coords_null,
                element_present=element_null,
                signal_values=signal_null,
                region="synthetic",
                element_name="control",
            )
            result_null = self.run(data_null, n_permutations=499, proximity_threshold_km=1.5)
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
