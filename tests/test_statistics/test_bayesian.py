"""Tests for Bayesian comparison statistical test."""

import numpy as np

from toponymia.pipelines.bayesian import Evidence
from toponymia.statistics.base import PlaceData, StatFamily, StatStatus
from toponymia.statistics.bayesian import BayesianComparisonTest


def _dummy_data() -> PlaceData:
    return PlaceData(
        coordinates=np.zeros((1, 2)),
        element_present=np.array([True]),
    )


class TestBayesianComparisonTest:
    def _bergen_hypotheses(self) -> list[dict]:
        return [
            {"id": "mountain", "description": "ON berg 'mountain'", "prior": 0.7},
            {"id": "protect", "description": "PGmc berga- 'protect'", "prior": 0.2},
            {"id": "celtic", "description": "Celtic briga 'hill-fort'", "prior": 0.1},
        ]

    def test_strong_evidence_confirms(self) -> None:
        """Strong supporting evidence leads to CONFIRMED status."""
        evidence = [
            Evidence(
                id="e1",
                description="Geographic: place on mountain",
                evidence_type="geographic",
                likelihood_ratios={"mountain": 5.0, "protect": 0.3, "celtic": 0.2},
            ),
            Evidence(
                id="e2",
                description="Phonological: matches ON berg perfectly",
                evidence_type="phonological",
                likelihood_ratios={"mountain": 4.0, "protect": 0.5, "celtic": 0.3},
            ),
        ]
        test = BayesianComparisonTest("Bergen", self._bergen_hypotheses(), evidence)
        result = test.run(_dummy_data())
        assert result.status == StatStatus.CONFIRMED
        assert result.parameters["winning_hypothesis"] == "mountain"
        assert result.test_statistic > 3.2  # Strong evidence

    def test_no_evidence_inconclusive(self) -> None:
        """No evidence = inconclusive (priors alone aren't decisive enough)."""
        # With priors 0.33/0.33/0.34, no evidence should be inconclusive
        hyps = [
            {"id": "a", "description": "A", "prior": 0.34},
            {"id": "b", "description": "B", "prior": 0.33},
            {"id": "c", "description": "C", "prior": 0.33},
        ]
        test = BayesianComparisonTest("Test", hyps, [])
        result = test.run(_dummy_data())
        assert result.status == StatStatus.INCONCLUSIVE

    def test_conflicting_evidence(self) -> None:
        """Conflicting evidence keeps result moderate."""
        evidence = [
            Evidence(
                id="e1",
                description="Supports mountain",
                evidence_type="geographic",
                likelihood_ratios={"mountain": 5.0, "protect": 0.5, "celtic": 0.5},
            ),
            Evidence(
                id="e2",
                description="Supports celtic",
                evidence_type="historical",
                likelihood_ratios={"mountain": 0.3, "protect": 0.5, "celtic": 6.0},
            ),
        ]
        test = BayesianComparisonTest("Bergen", self._bergen_hypotheses(), evidence)
        result = test.run(_dummy_data())
        # Should not be strongly confirmed with conflicting evidence
        assert result.test_statistic < 5.0

    def test_result_metadata(self) -> None:
        """Result contains expected metadata."""
        test = BayesianComparisonTest("Bergen", self._bergen_hypotheses(), [])
        result = test.run(_dummy_data())
        assert result.test_id == "bayesian_comparison"
        assert result.test_family == StatFamily.BAYESIAN
        assert result.element_name == "Bergen"
        assert "entropy_reduction" in result.parameters
        assert "posterior_odds" in result.parameters

    def test_validate_synthetic(self) -> None:
        """Synthetic validation demonstrates adequate power and low FPR."""
        test = BayesianComparisonTest(
            "Test",
            [
                {"id": "h0", "description": "H0", "prior": 1.0 / 3},
                {"id": "h1", "description": "H1", "prior": 1.0 / 3},
                {"id": "h2", "description": "H2", "prior": 1.0 / 3},
            ],
        )
        validation = test.validate_synthetic(n_trials=50)
        assert validation.power > 0.7  # Should detect planted signal
        assert validation.false_positive_rate < 0.05  # Low FPR
        assert validation.passed

    def test_entropy_reduction_with_evidence(self) -> None:
        """Evidence should reduce entropy (increase certainty)."""
        evidence = [
            Evidence(
                id="e1",
                description="Strong support",
                evidence_type="phonological",
                likelihood_ratios={"mountain": 10.0, "protect": 0.5, "celtic": 0.5},
            ),
        ]
        test = BayesianComparisonTest("Bergen", self._bergen_hypotheses(), evidence)
        result = test.run(_dummy_data())
        assert result.effect_size > 0  # Entropy reduced

    def test_two_hypotheses(self) -> None:
        """Works with just two hypotheses."""
        hyps = [
            {"id": "bay", "description": "ON vík 'bay'", "prior": 0.7},
            {"id": "village", "description": "Latin vicus 'village'", "prior": 0.3},
        ]
        evidence = [
            Evidence(
                id="e1",
                description="Place is coastal",
                evidence_type="geographic",
                likelihood_ratios={"bay": 4.0, "village": 0.5},
            ),
        ]
        test = BayesianComparisonTest("Vik", hyps, evidence)
        result = test.run(_dummy_data())
        assert result.parameters["winning_hypothesis"] == "bay"
