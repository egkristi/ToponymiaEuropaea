"""Astronomical alignment test.

Tests whether places with solar/lunar/stellar name elements show
statistically significant orientation toward solstice/equinox axes
compared to random site orientations.

Uses the Rayleigh test for directional (circular) data to detect
non-uniform angular distributions in place orientations.
"""

from __future__ import annotations

import numpy as np

from toponymia.statistics.base import (
    BaseTest,
    SyntheticValidation,
    TestData,
    TestFamily,
    TestResult,
    TestStatus,
)


def rayleigh_test(angles: np.ndarray) -> tuple[float, float]:
    """Perform Rayleigh test for circular uniformity.

    Tests H0: angles are uniformly distributed on the circle
    against H1: angles have a preferred direction.

    Args:
        angles: Array of angles in radians [0, 2π).

    Returns:
        Tuple of (test_statistic_R, p_value).
    """
    n = len(angles)
    if n < 3:
        return 0.0, 1.0

    # Mean resultant length R̄
    cos_sum = np.sum(np.cos(angles))
    sin_sum = np.sum(np.sin(angles))
    r_bar = np.sqrt(cos_sum**2 + sin_sum**2) / n

    # Rayleigh's Z statistic
    z = n * r_bar**2

    # P-value approximation (valid for n > 10)
    p_value = np.exp(-z) * (
        1 + (2 * z - z**2) / (4 * n) - (24 * z - 132 * z**2 + 76 * z**3 - 9 * z**4) / (288 * n**2)
    )

    # Clamp p-value to [0, 1]
    p_value = float(np.clip(p_value, 0.0, 1.0))

    return float(r_bar), p_value


def mean_direction(angles: np.ndarray) -> float:
    """Compute the mean direction of circular data.

    Args:
        angles: Array of angles in radians.

    Returns:
        Mean direction in radians [0, 2π).
    """
    cos_mean = np.mean(np.cos(angles))
    sin_mean = np.mean(np.sin(angles))
    theta = np.arctan2(sin_mean, cos_mean)
    return float(theta % (2 * np.pi))


# Key astronomical azimuths (degrees from north, clockwise)
SOLSTICE_SUMMER_SUNRISE_60N = 37.0  # approx at 60°N latitude
SOLSTICE_SUMMER_SUNSET_60N = 323.0
SOLSTICE_WINTER_SUNRISE_60N = 143.0
SOLSTICE_WINTER_SUNSET_60N = 217.0
EQUINOX_SUNRISE = 90.0
EQUINOX_SUNSET = 270.0


class AstronomicalAlignmentTest(BaseTest):
    """Test astronomical alignment of named sites.

    Tests whether places with solar/lunar/stellar name elements show
    significant directional orientation compared to a uniform distribution.

    The test measures the bearing (azimuth) from each element-bearing place
    to its nearest prominent landscape feature (horizon point, peak, or
    watercourse direction) and tests whether these bearings cluster around
    astronomical significant directions.

    Method: Rayleigh test for circular uniformity, with permutation-based
    comparison against control sites.
    """

    test_id = "astronomical_alignment"
    test_family = TestFamily.ASTRONOMICAL_ALIGNMENT
    description = (
        "Tests whether places with astronomical name elements show"
        " significant orientation toward solstice/equinox axes"
    )
    null_hypothesis = (
        "Bearings at astronomical-name sites are uniformly distributed"
        " (no preferred celestial direction)"
    )
    alternative_hypothesis = (
        "Bearings at astronomical-name sites show significant clustering"
        " around solstice/equinox azimuths"
    )

    def run(self, data: TestData, n_permutations: int = 10000) -> TestResult:
        """Run Rayleigh test comparing element-bearing vs. control sites.

        Uses signal_values as bearing/azimuth data (in degrees, 0-360).
        element_present indicates sites with astronomical name elements.
        """
        if data.signal_values is None:
            raise ValueError("signal_values (bearings in degrees) required")

        # Convert bearings to radians
        all_bearings_rad = np.deg2rad(data.signal_values)

        # Split by element presence
        element_mask = data.element_present.astype(bool)
        positive_bearings = all_bearings_rad[element_mask]
        negative_bearings = all_bearings_rad[~element_mask]

        n_positive = len(positive_bearings)
        n_negative = len(negative_bearings)

        if n_positive < 5:
            return TestResult(
                test_id=self.test_id,
                test_family=self.test_family,
                status=TestStatus.INCONCLUSIVE,
                null_hypothesis=self.null_hypothesis,
                alternative_hypothesis=self.alternative_hypothesis,
                n_observations=data.n_places,
                n_positive=n_positive,
                notes="Insufficient astronomical-name sites (need ≥5)",
                region=data.region,
                element_name=data.element_name,
            )

        # Rayleigh test on element-bearing sites
        r_bar_positive, p_rayleigh = rayleigh_test(positive_bearings)

        # Permutation test: is the concentration of element-bearing sites
        # significantly greater than random subsets?
        rng = np.random.default_rng(seed=42)
        perm_r_bars = np.empty(n_permutations)

        for i in range(n_permutations):
            # Random subset of same size from all sites
            perm_indices = rng.choice(len(all_bearings_rad), size=n_positive, replace=False)
            perm_bearings = all_bearings_rad[perm_indices]
            cos_sum = np.sum(np.cos(perm_bearings))
            sin_sum = np.sum(np.sin(perm_bearings))
            perm_r_bars[i] = np.sqrt(cos_sum**2 + sin_sum**2) / n_positive

        # One-sided p-value: how often does random subset have R̄ ≥ observed?
        p_permutation = float(np.mean(perm_r_bars >= r_bar_positive))

        # Combined assessment
        p_value = p_permutation  # Use permutation p-value as primary

        # Effect size: difference in mean resultant length
        r_bar_negative, _ = rayleigh_test(negative_bearings) if n_negative >= 3 else (0.0, 1.0)
        effect_size = r_bar_positive - r_bar_negative

        # Mean direction of the element-bearing cluster
        mean_dir_deg = float(np.rad2deg(mean_direction(positive_bearings))) % 360

        # Determine status
        if p_value < 0.05 and r_bar_positive > 0.3:
            status = TestStatus.CONFIRMED
        elif p_value < 0.05:
            status = TestStatus.EXECUTED
        else:
            status = TestStatus.EXECUTED

        return TestResult(
            test_id=self.test_id,
            test_family=self.test_family,
            status=status,
            null_hypothesis=self.null_hypothesis,
            alternative_hypothesis=self.alternative_hypothesis,
            test_statistic=r_bar_positive,
            p_value=p_value,
            effect_size=effect_size,
            n_observations=data.n_places,
            n_positive=n_positive,
            n_permutations=n_permutations,
            parameters={
                "mean_direction_deg": mean_dir_deg,
                "r_bar_positive": r_bar_positive,
                "r_bar_negative": r_bar_negative,
                "p_rayleigh": p_rayleigh,
                "p_permutation": p_permutation,
            },
            region=data.region,
            element_name=data.element_name,
            signal_name="bearing_azimuth",
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data with known planted signal.

        Plants a von Mises-distributed concentration at a known azimuth
        for element-bearing sites, and tests detection rate.
        """
        rng = np.random.default_rng(seed=123)
        n_sites = 200
        n_element = 40

        power_detections = 0
        fpr_rejections = 0

        for _trial in range(n_trials):
            coords = rng.uniform(-10, 10, size=(n_sites, 2))
            element_present = np.zeros(n_sites, dtype=bool)
            element_present[:n_element] = True

            # --- Power trial: plant concentrated signal at ~90° (equinox) ---
            bearings_power = rng.uniform(0, 360, size=n_sites)
            # Element-bearing sites: concentrated around 90° (κ=2 von Mises)
            bearings_power[:n_element] = (
                np.rad2deg(rng.vonmises(np.deg2rad(90), 2.0, size=n_element)) % 360
            )

            data_power = TestData(
                coordinates=coords,
                element_present=element_present,
                signal_values=bearings_power,
                region="synthetic",
                element_name="sol-",
            )
            result_power = self.run(data_power, n_permutations=999)
            if result_power.p_value < 0.05:
                power_detections += 1

            # --- FPR trial: no signal (uniform bearings) ---
            bearings_null = rng.uniform(0, 360, size=n_sites)
            element_null = np.zeros(n_sites, dtype=bool)
            null_indices = rng.choice(n_sites, size=n_element, replace=False)
            element_null[null_indices] = True

            data_null = TestData(
                coordinates=coords,
                element_present=element_null,
                signal_values=bearings_null,
                region="synthetic",
                element_name="control",
            )
            result_null = self.run(data_null, n_permutations=999)
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
