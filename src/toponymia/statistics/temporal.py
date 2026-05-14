"""Temporal layer consistency test.

Tests whether place names assigned to a specific historical/linguistic
layer form geographically coherent clusters, as expected if they
reflect a real settlement pattern, rather than being randomly scattered.

For example, Viking Age -by names in England should cluster in the
Danelaw region. If a proposed temporal layer is truly coherent,
its members should be significantly more clustered than random
subsets of the same size.

Uses average nearest-neighbor distance within the layer compared
to permutation null distribution.
"""

from __future__ import annotations

import numpy as np
from scipy.spatial.distance import cdist  # type: ignore[import-untyped]

from toponymia.statistics.base import (
    BaseTest,
    PlaceData,
    StatFamily,
    StatStatus,
    SyntheticValidation,
    TestResult,
)


class TemporalLayerConsistencyTest(BaseTest):
    """Test for geographic coherence of temporal/linguistic name layers.

    Null hypothesis: The spatial distribution of names in the proposed
    temporal layer is indistinguishable from a random subset of the
    same size drawn from all names in the study area.

    Alternative: Names in the temporal layer are significantly more
    spatially clustered than random subsets, indicating a geographically
    coherent settlement/naming event.

    Method: Compute the mean nearest-neighbor distance (NND) among
    layer members. Compare to the distribution of mean NND for random
    subsets of equal size via permutation.
    """

    test_id = "temporal_layer_consistency"
    test_family = StatFamily.TEMPORAL
    description = (
        "Tests whether a proposed temporal name layer shows"
        " geographic coherence (spatial clustering) beyond chance"
    )
    null_hypothesis = (
        "Names assigned to the temporal layer are spatially distributed"
        " indistinguishably from a random subset of the same size"
    )
    alternative_hypothesis = (
        "Names in the temporal layer are significantly more clustered"
        " than random subsets, indicating geographic coherence"
    )

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 10000,
    ) -> TestResult:
        """Run temporal layer consistency test.

        Uses element_present as the layer membership indicator (True = in layer).
        Coordinates are decimal degrees (lon, lat).

        Args:
            data: TestData with coordinates and element_present (layer membership).
            n_permutations: Number of permutation trials.
        """
        layer_mask = data.element_present.astype(bool)
        n_layer = int(layer_mask.sum())
        n_total = data.n_places

        if n_layer < 5:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n_total,
                n_positive=n_layer,
                notes=f"Insufficient layer members: {n_layer} (need ≥5)",
                region=data.region,
                element_name=data.element_name,
            )

        if n_layer >= n_total:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n_total,
                n_positive=n_layer,
                notes="Layer covers all sites; no comparison possible",
                region=data.region,
                element_name=data.element_name,
            )

        # Convert coordinates to km for distance calculations
        coords = data.coordinates  # (N, 2): lon, lat
        mean_lat = np.mean(coords[:, 1])
        km_per_deg_lat = 111.32
        km_per_deg_lon = 111.32 * np.cos(np.radians(mean_lat))

        coords_km = np.column_stack([coords[:, 0] * km_per_deg_lon, coords[:, 1] * km_per_deg_lat])

        # Observed mean NND for the layer
        layer_coords_km = coords_km[layer_mask]
        observed_mean_nnd = self._mean_nearest_neighbor_distance(layer_coords_km)

        # Permutation null: random subsets of size n_layer
        rng = np.random.default_rng(seed=42)
        perm_mean_nnds = np.empty(n_permutations)

        for i in range(n_permutations):
            perm_idx = rng.choice(n_total, size=n_layer, replace=False)
            perm_coords = coords_km[perm_idx]
            perm_mean_nnds[i] = self._mean_nearest_neighbor_distance(perm_coords)

        # One-sided p-value: layer is MORE clustered = LOWER mean NND
        p_value = float(np.mean(perm_mean_nnds <= observed_mean_nnd))

        # Effect size: how many SDs below the null mean
        mean_null = float(np.mean(perm_mean_nnds))
        std_null = float(np.std(perm_mean_nnds))
        effect_size = (mean_null - observed_mean_nnd) / std_null if std_null > 0 else 0.0

        # Confidence interval on the null distribution
        ci_low = float(np.percentile(perm_mean_nnds, 2.5))
        ci_high = float(np.percentile(perm_mean_nnds, 97.5))

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
            test_statistic=observed_mean_nnd,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(ci_low, ci_high),
            n_observations=n_total,
            n_positive=n_layer,
            n_permutations=n_permutations,
            parameters={
                "observed_mean_nnd_km": observed_mean_nnd,
                "null_mean_nnd_km": mean_null,
                "null_std_nnd_km": std_null,
            },
            region=data.region,
            element_name=data.element_name,
        )

    @staticmethod
    def _mean_nearest_neighbor_distance(coords_km: np.ndarray) -> float:
        """Compute mean nearest-neighbor distance for a set of points.

        Args:
            coords_km: (n, 2) array of coordinates in km.

        Returns:
            Mean nearest-neighbor distance in km.
        """
        if len(coords_km) < 2:
            return 0.0

        dist_matrix = cdist(coords_km, coords_km)
        # Set diagonal to infinity so each point doesn't match itself
        np.fill_diagonal(dist_matrix, np.inf)
        nn_distances = dist_matrix.min(axis=1)
        return float(np.mean(nn_distances))

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data.

        Power: Plants a clustered layer (points drawn from tight Gaussian).
        FPR: Layer membership is random (no spatial pattern).
        """
        rng = np.random.default_rng(seed=789)
        n_sites = 300
        n_layer = 30

        power_detections = 0
        fpr_rejections = 0

        for _trial in range(n_trials):
            # --- Power trial: Layer forms a cluster ---
            # Background points: uniform over a ~2x2 degree area
            coords = rng.uniform(0, 2, size=(n_sites, 2))

            # Layer members: tight cluster around (1.0, 1.0)
            cluster_center = np.array([1.0, 1.0])
            cluster_std = 0.05  # ~5.5 km spread
            layer_coords = rng.normal(cluster_center, cluster_std, size=(n_layer, 2))

            # Replace some background points with layer points
            layer_idx = rng.choice(n_sites, size=n_layer, replace=False)
            coords[layer_idx] = layer_coords

            element_present = np.zeros(n_sites, dtype=bool)
            element_present[layer_idx] = True

            data_power = PlaceData(
                coordinates=coords,
                element_present=element_present,
                region="synthetic",
                element_name="clustered_layer",
            )
            result_power = self.run(data_power, n_permutations=499)
            if result_power.p_value < 0.05:
                power_detections += 1

            # --- FPR trial: Layer membership is random ---
            coords_null = rng.uniform(0, 2, size=(n_sites, 2))
            element_null = np.zeros(n_sites, dtype=bool)
            null_idx = rng.choice(n_sites, size=n_layer, replace=False)
            element_null[null_idx] = True

            data_null = PlaceData(
                coordinates=coords_null,
                element_present=element_null,
                region="synthetic",
                element_name="random_layer",
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
