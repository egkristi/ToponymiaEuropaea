"""Language contact boundary detection test.

Detects substrate/superstrate boundaries in toponymic data by testing
whether names from two language traditions (e.g., Celtic vs. Germanic)
show spatial segregation consistent with a contact boundary.

For example, in Scotland the Gaelic/Norse boundary can be detected
through the spatial distribution of gaelic prefix-names (Bal-, Kil-)
vs. Norse suffix-names (-by, -ster, -dale).

Uses a permutation test on the spatial autocorrelation of language
labels, comparing observed boundary sharpness to random shuffles.
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


class LanguageContactBoundaryTest(BaseTest):
    """Test for language contact boundaries in toponymic distributions.

    Null hypothesis: Names from language A and language B are spatially
    intermixed — no systematic boundary separates them.

    Alternative: Names from the two language traditions show spatial
    segregation consistent with a historical contact zone or boundary.

    Method: Compute a spatial segregation index based on k-nearest
    neighbours. For each site, count the proportion of same-language
    neighbours. Under random mixing this should equal the overall
    proportion. Permutation test on the mean segregation index.
    """

    test_id = "language_contact_boundary"
    test_family = StatFamily.LANGUAGE_CONTACT
    description = (
        "Tests whether two toponymic language traditions show spatial"
        " segregation consistent with a contact boundary"
    )
    null_hypothesis = (
        "Names from the two language traditions are spatially intermixed"
        " with no systematic boundary"
    )
    alternative_hypothesis = (
        "Names show spatial segregation, indicating a historical language contact boundary"
    )

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 10000,
    ) -> TestResult:
        """Run language contact boundary test.

        Uses:
        - element_present: boolean array where True = language A, False = language B
        - coordinates: lon/lat positions of all sites
        - signal_values: optional, not used (ignored)

        The test measures spatial autocorrelation of language labels
        via a k-nearest-neighbour segregation index.

        Args:
            data: PlaceData with element_present as language labels.
            n_permutations: Number of permutation trials.
        """
        labels = data.element_present.astype(bool)
        coords = data.coordinates
        n = data.n_places

        n_a = int(labels.sum())
        n_b = n - n_a

        if n_a < 10 or n_b < 10:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n,
                n_positive=n_a,
                notes=(f"Insufficient sites per language: {n_a} A, {n_b} B (need ≥10 each)"),
                region=data.region,
                element_name=data.element_name,
            )

        # Compute pairwise distances
        dists = self._pairwise_distances(coords)

        # k = min(10, smallest group - 1)
        k = min(10, min(n_a, n_b) - 1)
        if k < 3:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n,
                n_positive=n_a,
                notes=f"k too small ({k}), need ≥3 neighbours",
                region=data.region,
                element_name=data.element_name,
            )

        # Observed segregation index
        observed_seg = self._segregation_index(labels, dists, k)

        # Permutation null distribution
        rng = np.random.default_rng(seed=42)
        perm_segs = np.empty(n_permutations)
        for i in range(n_permutations):
            perm_labels = rng.permutation(labels)
            perm_segs[i] = self._segregation_index(perm_labels, dists, k)

        # One-sided p-value: higher segregation = more boundary signal
        p_value = float(np.mean(perm_segs >= observed_seg))

        # Effect size: z-score relative to null
        mean_null = float(np.mean(perm_segs))
        std_null = float(np.std(perm_segs))
        effect_size = (observed_seg - mean_null) / std_null if std_null > 0 else 0.0

        # Confidence interval on null
        ci_low = float(np.percentile(perm_segs, 2.5))
        ci_high = float(np.percentile(perm_segs, 97.5))

        # Expected segregation under no boundary
        prop_a = n_a / n
        expected_seg = prop_a**2 + (1 - prop_a) ** 2

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
            test_statistic=observed_seg,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(ci_low, ci_high),
            n_observations=n,
            n_positive=n_a,
            n_permutations=n_permutations,
            parameters={
                "n_language_a": n_a,
                "n_language_b": n_b,
                "k_neighbours": k,
                "observed_segregation": observed_seg,
                "expected_segregation_null": expected_seg,
                "proportion_language_a": prop_a,
            },
            region=data.region,
            element_name=data.element_name,
            signal_name="language_label",
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data.

        Power: Plant a clear spatial boundary between two language groups.
        FPR: Labels distributed randomly (no spatial structure).
        """
        rng = np.random.default_rng(seed=123)
        n_sites = 200

        power_detections = 0
        fpr_detections = 0

        for _trial in range(n_trials):
            # --- POWER: Plant a spatial boundary ---
            # Language A on the left (x < 0.5), B on the right (x > 0.5)
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            labels = coords[:, 0] < 0.5  # Boundary at x=0.5

            # Add some noise: 10% misclassified
            n_flip = n_sites // 10
            flip_idx = rng.choice(n_sites, size=n_flip, replace=False)
            labels[flip_idx] = ~labels[flip_idx]

            data = PlaceData(
                coordinates=coords,
                element_present=labels.astype(float),
                region="synthetic_boundary",
                element_name="language_a",
            )
            result = self.run(data, n_permutations=499)
            if result.p_value < 0.05:
                power_detections += 1

        for _trial in range(n_trials):
            # --- FPR: No spatial structure ---
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            labels = rng.random(n_sites) < 0.5  # Random labels

            data = PlaceData(
                coordinates=coords,
                element_present=labels.astype(float),
                region="synthetic_null",
                element_name="random_element",
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
                f"Power={power:.2f} (boundary at x=0.5 with 10% noise),"
                f" FPR={fpr:.2f} (random labels)"
            ),
        )

    @staticmethod
    def _pairwise_distances(coords: np.ndarray) -> np.ndarray:
        """Compute pairwise Euclidean distance matrix."""
        diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
        result: np.ndarray = np.sqrt((diff**2).sum(axis=-1))
        return result

    @staticmethod
    def _segregation_index(labels: np.ndarray, dists: np.ndarray, k: int) -> float:
        """Compute mean proportion of same-label k-nearest neighbours.

        Returns a value between 0 and 1. Higher = more segregated.
        Under random mixing, expected = prop_a^2 + prop_b^2.
        """
        n = len(labels)
        seg_scores = np.empty(n)

        for i in range(n):
            # Sort by distance, skip self (index 0 after sort)
            neighbours = np.argsort(dists[i])[1 : k + 1]
            same_label = labels[neighbours] == labels[i]
            seg_scores[i] = float(same_label.mean())

        return float(seg_scores.mean())
