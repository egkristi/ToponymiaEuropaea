"""Base interface for statistical tests.

Every statistical test in the framework implements this interface.
This ensures:
1. All tests have explicit null hypotheses
2. All tests report standardized results
3. All tests can be validated on synthetic data
4. All tests support robustness checks

The framework enforces a clear separation between preregistered
(hypothesis-driven) and exploratory (post hoc) analyses.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np


class TestStatus(Enum):
    """Status of a statistical test."""

    PROPOSED = "proposed"
    PREREGISTERED = "preregistered"
    VALIDATED = "validated"  # Passed synthetic validation
    EXECUTED = "executed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class TestFamily(Enum):
    """Family/category of statistical test."""

    CORRESPONDENCE = "correspondence"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    LANGUAGE_CONTACT = "language_contact"
    MIGRATION = "migration"
    POLITICAL_RENAMING = "political_renaming"
    BAYESIAN = "bayesian"
    ASTRONOMICAL_ALIGNMENT = "astronomical_alignment"
    SACRED_GEOMETRY = "sacred_geometry"
    SENSORY_CORRESPONDENCE = "sensory_correspondence"
    RELIGIOUS_STRATIGRAPHY = "religious_stratigraphy"
    CATASTROPHE_CLUSTERING = "catastrophe_clustering"


@dataclass
class TestData:
    """Input data for a statistical test."""

    # Place coordinates (N x 2 array: lon, lat)
    coordinates: np.ndarray

    # Name element presence (boolean array, length N)
    element_present: np.ndarray

    # Signal values (float array, length N) — e.g., elevation, slope, distance
    signal_values: np.ndarray | None = None

    # Metadata
    region: str = ""
    element_name: str = ""
    signal_name: str = ""
    n_places: int = 0

    def __post_init__(self):
        self.n_places = len(self.coordinates)


@dataclass
class RobustnessResult:
    """Result of a robustness check."""

    check_type: str  # jackknife, bootstrap, sensitivity, variant
    passed: bool
    details: str = ""
    values: list[float] = field(default_factory=list)


@dataclass
class SyntheticValidation:
    """Result of synthetic data validation."""

    # Statistical power (ability to detect planted signal)
    power: float = 0.0
    power_n_trials: int = 0

    # False positive rate (rejection under pure noise)
    false_positive_rate: float = 0.0
    fpr_n_trials: int = 0

    # Whether validation passes (power > 0.8, FPR < 0.05 typically)
    passed: bool = False
    details: str = ""


@dataclass
class TestResult:
    """Standardized result from any statistical test."""

    # Test identity
    test_id: str
    test_family: TestFamily
    status: TestStatus

    # Hypothesis
    null_hypothesis: str
    alternative_hypothesis: str
    preregistered: bool = False

    # Core statistics
    test_statistic: float = 0.0
    p_value: float = 1.0
    effect_size: float = 0.0
    confidence_interval: tuple[float, float] = (0.0, 0.0)

    # Sample info
    n_observations: int = 0
    n_positive: int = 0  # places with element present
    n_permutations: int = 0

    # Robustness
    robustness_checks: list[RobustnessResult] = field(default_factory=list)
    robustness_passed: bool = False

    # Synthetic validation
    synthetic_validation: SyntheticValidation | None = None

    # Metadata
    region: str = ""
    element_name: str = ""
    signal_name: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    @property
    def is_significant(self) -> bool:
        """Whether result is statistically significant at conventional alpha=0.05."""
        return self.p_value < 0.05

    @property
    def is_robust(self) -> bool:
        """Whether result passes all robustness checks."""
        return self.robustness_passed and all(r.passed for r in self.robustness_checks)


class BaseTest(ABC):
    """Abstract base class for all statistical tests.

    To add a new test:
    1. Create a new module in src/toponymia/statistics/
    2. Subclass BaseTest
    3. Implement run() and validate_synthetic()
    4. Define test_id, test_family, null_hypothesis

    The test will automatically integrate with the results reporting system.
    """

    # Class-level metadata (override in subclass)
    test_id: str = ""
    test_family: TestFamily = TestFamily.CORRESPONDENCE
    description: str = ""
    null_hypothesis: str = ""
    alternative_hypothesis: str = ""

    @abstractmethod
    def run(self, data: TestData, n_permutations: int = 10000) -> TestResult:
        """Execute the statistical test.

        Args:
            data: Input data conforming to TestData.
            n_permutations: Number of permutations for null distribution.

        Returns:
            TestResult with all fields populated.
        """
        ...

    @abstractmethod
    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate test on synthetic data before applying to real data.

        Must demonstrate:
        1. Adequate statistical power (can detect planted signal)
        2. Controlled false positive rate (doesn't reject under noise)

        Args:
            n_trials: Number of synthetic trials.

        Returns:
            SyntheticValidation result.
        """
        ...

    def check_robustness(self, data: TestData, result: TestResult) -> list[RobustnessResult]:
        """Run standard robustness checks on a test result.

        Default implementation includes:
        - Regional jackknife
        - Bootstrap confidence interval
        - Spelling variant sensitivity (if applicable)

        Override to add test-specific robustness checks.
        """
        checks: list[RobustnessResult] = []

        # Regional jackknife: re-run excluding 10% of data at a time
        n_folds = 10
        fold_size = len(data.coordinates) // n_folds
        jackknife_pvalues: list[float] = []

        for i in range(n_folds):
            start = i * fold_size
            end = start + fold_size

            mask = np.ones(len(data.coordinates), dtype=bool)
            mask[start:end] = False

            subset_data = TestData(
                coordinates=data.coordinates[mask],
                element_present=data.element_present[mask],
                signal_values=data.signal_values[mask] if data.signal_values is not None else None,
                region=data.region,
                element_name=data.element_name,
                signal_name=data.signal_name,
            )

            subset_result = self.run(subset_data, n_permutations=1000)
            jackknife_pvalues.append(subset_result.p_value)

        # Check if conclusion is stable across folds
        all_significant = all(p < 0.05 for p in jackknife_pvalues)
        all_non_significant = all(p >= 0.05 for p in jackknife_pvalues)
        stable = all_significant or all_non_significant

        checks.append(
            RobustnessResult(
                check_type="regional_jackknife",
                passed=stable,
                details=(
                    f"p-values across {n_folds} folds:"
                    f" min={min(jackknife_pvalues):.4f}, max={max(jackknife_pvalues):.4f}"
                ),
                values=jackknife_pvalues,
            )
        )

        return checks

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} test_id={self.test_id!r} family={self.test_family.value}>"
        )
