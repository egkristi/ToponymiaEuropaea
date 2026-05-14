"""Sacred geometry alignment test for toponymic patterns.

Tests whether place names with ritual/sacred elements (e.g., -hov, -vi,
-kirk, temple-) align along straight lines significantly more than
random placement would produce. This provides a statistical framework
for evaluating "ley line" hypotheses without pseudoscientific assumptions.

The null hypothesis is strict: random points will form approximate
alignments by chance. The test properly accounts for this by comparing
observed alignment counts to the permutation distribution.
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


class SacredGeometryAlignmentTest(BaseTest):
    """Test for anomalous linear alignments among sacred-element sites.

    Null hypothesis: Sites with sacred elements show no more linear
    alignment than random subsets of equal size.

    Alternative: Sites show statistically significant linear alignment,
    suggesting deliberate placement or landscape-constrained positioning.

    Method: For each triplet of sites, compute the collinearity
    (minimum distance of the middle point from the line through the
    outer two). Count triplets below a tolerance threshold. Compare
    to permutation distribution.

    Note: This is a rigorous statistical test that accounts for the
    multiple-comparison problem inherent in alignment-seeking. Most
    "ley line" claims fail this test.
    """

    test_id = "sacred_geometry_alignment"
    test_family = StatFamily.SACRED_GEOMETRY
    description = (
        "Tests whether sacred-element sites show linear alignment beyond chance expectation"
    )
    null_hypothesis = (
        "Sacred-element sites are no more linearly aligned than random subsets of equal size"
    )
    alternative_hypothesis = (
        "Sacred-element sites show statistically significant linear"
        " alignment, suggesting deliberate or landscape-constrained placement"
    )

    def __init__(self, tolerance_fraction: float = 0.01) -> None:
        """Initialize with alignment tolerance.

        Args:
            tolerance_fraction: Fraction of study area diagonal used as
                alignment tolerance. Default 0.01 = 1% of diagonal.
        """
        self.tolerance_fraction = tolerance_fraction

    def run(
        self,
        data: PlaceData,
        n_permutations: int = 999,
    ) -> TestResult:
        """Run sacred geometry alignment test.

        Uses:
        - element_present: boolean (True = has sacred element)
        - coordinates: positions of ALL places
        """
        coords = data.coordinates
        labels = data.element_present.astype(bool)
        n = data.n_places
        n_positive = int(labels.sum())

        if n_positive < 5:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=StatStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=n,
                n_positive=n_positive,
                notes=f"Too few sacred sites ({n_positive}, need ≥5)",
                region=data.region,
                element_name=data.element_name,
            )

        # Study area diagonal for tolerance
        x_min, y_min = coords.min(axis=0)
        x_max, y_max = coords.max(axis=0)
        diagonal = float(np.sqrt((x_max - x_min) ** 2 + (y_max - y_min) ** 2))

        if diagonal <= 0:
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

        tolerance = diagonal * self.tolerance_fraction

        # Observed alignment count for sacred sites
        sacred_coords = coords[labels]
        observed_alignments = self._count_alignments(sacred_coords, tolerance)

        # Permutation null: random subsets of same size from all coords
        rng = np.random.default_rng(seed=42)
        perm_alignments = np.empty(n_permutations)
        for i in range(n_permutations):
            perm_idx = rng.choice(n, size=n_positive, replace=False)
            perm_coords = coords[perm_idx]
            perm_alignments[i] = self._count_alignments(perm_coords, tolerance)

        # One-sided p-value (more alignments = more evidence)
        p_value = float(np.mean(perm_alignments >= observed_alignments))

        # Effect size: z-score
        mean_null = float(np.mean(perm_alignments))
        std_null = float(np.std(perm_alignments))
        effect_size = (observed_alignments - mean_null) / std_null if std_null > 0 else 0.0

        ci_low = float(np.percentile(perm_alignments, 2.5))
        ci_high = float(np.percentile(perm_alignments, 97.5))

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
            test_statistic=float(observed_alignments),
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(ci_low, ci_high),
            n_observations=n,
            n_positive=n_positive,
            notes=(
                f"Observed {observed_alignments} near-collinear triplets "
                f"(tolerance={tolerance:.4f}, "
                f"null mean={mean_null:.1f})"
            ),
            region=data.region,
            element_name=data.element_name,
        )

    def _count_alignments(self, points: np.ndarray, tolerance: float) -> int:
        """Count near-collinear triplets among a set of points.

        For efficiency, samples up to 500 random triplets when n > 15
        (full enumeration is O(n^3)).
        """
        n = len(points)
        if n < 3:
            return 0

        # For small n, enumerate all triplets
        max_triplets = 500
        if n <= 15:
            count = 0
            for i in range(n):
                for j in range(i + 1, n):
                    for k in range(j + 1, n):
                        if self._is_collinear(points[i], points[j], points[k], tolerance):
                            count += 1
            return count

        # For larger n, sample random triplets
        rng = np.random.default_rng(seed=0)
        count = 0
        for _ in range(max_triplets):
            idx = rng.choice(n, size=3, replace=False)
            if self._is_collinear(points[idx[0]], points[idx[1]], points[idx[2]], tolerance):
                count += 1
        return count

    def _is_collinear(
        self,
        p1: np.ndarray,
        p2: np.ndarray,
        p3: np.ndarray,
        tolerance: float,
    ) -> bool:
        """Check if three points are approximately collinear.

        Uses the area of the triangle formed by the three points.
        Area = 0.5 * |cross product|. If area / base < tolerance,
        they are approximately collinear.
        """
        # Cross product magnitude gives 2x triangle area
        v1 = p2 - p1
        v2 = p3 - p1
        cross = abs(float(v1[0] * v2[1] - v1[1] * v2[0]))

        # Base = max distance between any two points
        d12 = float(np.sqrt(np.sum((p2 - p1) ** 2)))
        d13 = float(np.sqrt(np.sum((p3 - p1) ** 2)))
        d23 = float(np.sqrt(np.sum((p3 - p2) ** 2)))
        base = max(d12, d13, d23)

        if base == 0:
            return True

        # Height = area / base (distance of farthest point from line)
        height = cross / base
        return height < tolerance

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate alignment test on synthetic data.

        Power test: Points deliberately placed on lines.
        FPR test: Random uniform points.
        """
        rng = np.random.default_rng(seed=789)
        n_sites = 100
        n_sacred = 15
        power_detections = 0
        fpr_detections = 0

        for _trial in range(n_trials):
            # --- POWER: Place sacred sites on 3 lines ---
            background = rng.uniform(0, 1, size=(n_sites - n_sacred, 2))

            # 15 sacred sites on 3 lines (5 each)
            sacred = []
            for line_idx in range(3):
                y_base = 0.2 + line_idx * 0.3
                for pt_idx in range(5):
                    x = 0.1 + pt_idx * 0.2
                    y = y_base + rng.normal(0, 0.001)
                    sacred.append([x, y])
            sacred_arr = np.array(sacred)

            all_coords = np.vstack([sacred_arr, background])
            labels = np.zeros(n_sites, dtype=bool)
            labels[:n_sacred] = True

            data = PlaceData(
                coordinates=all_coords,
                element_present=labels,
                region="synthetic",
                element_name="aligned",
            )

            result = self.run(data, n_permutations=99)
            if result.p_value is not None and result.p_value < 0.05:
                power_detections += 1

        for _trial in range(n_trials):
            # --- FPR: Uniform random ---
            coords = rng.uniform(0, 1, size=(n_sites, 2))
            labels = np.zeros(n_sites, dtype=bool)
            chosen = rng.choice(n_sites, size=n_sacred, replace=False)
            labels[chosen] = True

            data = PlaceData(
                coordinates=coords,
                element_present=labels,
                region="synthetic",
                element_name="random",
            )

            result = self.run(data, n_permutations=99)
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
            details=(f"Power={power:.2f} (linear placement), FPR={fpr:.2f} (uniform random)"),
        )
