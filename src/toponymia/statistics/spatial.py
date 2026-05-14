"""Spatial distribution tests for place name elements.

Tests whether toponymic elements exhibit spatial patterns
(clustering, directional bias, gradients) that deviate from
what would be expected under spatial randomness.
"""

from __future__ import annotations

import numpy as np
from scipy.spatial.distance import pdist, squareform  # type: ignore[import-untyped]

from toponymia.statistics.base import (
    BaseTest,
    PlaceData,
    StatFamily,
    StatStatus,
    SyntheticValidation,
    TestResult,
)


class SpatialClusteringTest(BaseTest):
    """Test whether element-bearing places cluster more than expected.

    Uses a permutation-based approach on the mean nearest-neighbour
    distance among element-bearing places, compared to random subsets
    of the same size drawn from all places.

    Null hypothesis: Element-bearing places are a random spatial subset
    of all places (no excess clustering).
    """

    test_id = "spatial_clustering"
    test_family = StatFamily.SPATIAL
    description = "Tests whether places with a given element cluster spatially"
    null_hypothesis = "Element-bearing places are a spatially random subset of all places"
    alternative_hypothesis = "Element-bearing places are more clustered than expected"

    def run(self, data: PlaceData, n_permutations: int = 10000) -> TestResult:
        """Run spatial clustering test via permutation of element labels."""
        mask = data.element_present.astype(bool)
        n_pos = mask.sum()

        if n_pos < 5 or n_pos > len(data.coordinates) - 5:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=data.n_places,
                n_positive=int(n_pos),
                notes="Insufficient sample size for spatial clustering test",
            )

        # Compute pairwise distances (using Haversine approximation for small areas)
        all_distances = squareform(pdist(data.coordinates, metric="euclidean"))

        # Observed: mean nearest-neighbour distance among element-bearing places
        pos_indices = np.where(mask)[0]
        pos_distances = all_distances[np.ix_(pos_indices, pos_indices)]
        np.fill_diagonal(pos_distances, np.inf)
        observed_mnn = np.mean(np.min(pos_distances, axis=1))

        # Permutation null: random subsets of same size
        rng = np.random.default_rng(seed=42)
        perm_mnn = np.empty(n_permutations)

        for i in range(n_permutations):
            perm_indices = rng.choice(len(data.coordinates), size=int(n_pos), replace=False)
            perm_dist = all_distances[np.ix_(perm_indices, perm_indices)]
            np.fill_diagonal(perm_dist, np.inf)
            perm_mnn[i] = np.mean(np.min(perm_dist, axis=1))

        # One-sided p-value (testing for MORE clustering = SMALLER distances)
        p_value = np.mean(perm_mnn <= observed_mnn)

        # Effect size: standardized difference
        effect_size = (
            (np.mean(perm_mnn) - observed_mnn) / np.std(perm_mnn) if np.std(perm_mnn) > 0 else 0.0
        )

        status = StatStatus.CONFIRMED if p_value < 0.05 else StatStatus.EXECUTED

        return TestResult(
            test_id=self.test_id,
            test_family=self.test_family,
            status=status,
            null_hypothesis=self.null_hypothesis,
            alternative_hypothesis=self.alternative_hypothesis,
            test_statistic=float(observed_mnn),
            p_value=float(p_value),
            effect_size=float(effect_size),
            n_observations=data.n_places,
            n_positive=int(n_pos),
            n_permutations=n_permutations,
            region=data.region,
            element_name=data.element_name,
            parameters={
                "observed_mean_nn_distance": float(observed_mnn),
                "null_mean_nn_distance": float(np.mean(perm_mnn)),
                "null_std_nn_distance": float(np.std(perm_mnn)),
            },
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate with planted clusters and random placement."""
        rng = np.random.default_rng(seed=456)
        n_places = 300
        n_positive = 30

        # --- Power: planted cluster ---
        detections = 0
        for _ in range(n_trials):
            # Background: uniform random
            coords = rng.uniform(0, 100, size=(n_places, 2))
            # Element-bearing: clustered around a center
            cluster_center = rng.uniform(20, 80, size=2)
            coords[:n_positive] = rng.normal(cluster_center, 3, size=(n_positive, 2))

            element = np.zeros(n_places, dtype=bool)
            element[:n_positive] = True

            data = PlaceData(coordinates=coords, element_present=element)
            result = self.run(data, n_permutations=500)
            if result.p_value < 0.05:
                detections += 1

        power = detections / n_trials

        # --- FPR: random placement ---
        false_positives = 0
        for _ in range(n_trials):
            coords = rng.uniform(0, 100, size=(n_places, 2))
            element = np.zeros(n_places, dtype=bool)
            element[rng.choice(n_places, n_positive, replace=False)] = True

            data = PlaceData(coordinates=coords, element_present=element)
            result = self.run(data, n_permutations=500)
            if result.p_value < 0.05:
                false_positives += 1

        fpr = false_positives / n_trials

        passed = power >= 0.8 and fpr <= 0.10

        return SyntheticValidation(
            power=power,
            power_n_trials=n_trials,
            false_positive_rate=fpr,
            fpr_n_trials=n_trials,
            passed=passed,
            details=f"Power={power:.2f}, FPR={fpr:.2f}",
        )
