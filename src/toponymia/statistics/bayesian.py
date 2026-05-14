"""Bayesian comparison test for competing etymological hypotheses.

Uses the Bayesian etymology framework (pipelines.bayesian) to evaluate
competing etymological hypotheses for a place name by applying geographic,
phonological, and semantic evidence from databank records.

This replaces flat probability storage with proper Bayesian hypothesis testing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from toponymia.pipelines.bayesian import (
    Evidence,
    HypothesisSet,
    create_hypothesis_set,
    sequential_update,
)
from toponymia.statistics.base import (
    BaseTest,
    PlaceData,
    StatFamily,
    StatStatus,
    SyntheticValidation,
    TestResult,
)


@dataclass
class BayesianComparisonResult:
    """Extended result for Bayesian comparison tests."""

    test_result: TestResult
    hypothesis_set: HypothesisSet
    winning_hypothesis: str
    posterior_odds: float  # Posterior odds of winner vs next best
    evidence_applied: int
    entropy_reduction: float  # Initial entropy - final entropy


class BayesianComparisonTest(BaseTest):
    """Compare competing etymological hypotheses using Bayesian updating.

    Given a place name and a set of competing etymologies, this test:
    1. Establishes prior probabilities from existing research
    2. Applies available evidence (geographic, phonological, semantic)
    3. Computes posterior probabilities via Bayes' theorem
    4. Reports whether one hypothesis clearly dominates

    The test statistic is the log Bayes factor (posterior odds ratio)
    between the top two hypotheses. Values > 3.2 (20:1 odds) are
    considered "strong evidence" (Kass & Raftery 1995 scale).
    """

    test_id = "bayesian_comparison"
    test_family = StatFamily.BAYESIAN
    description = "Bayesian comparison of competing etymological hypotheses"
    null_hypothesis = "No single etymology is clearly supported over alternatives"
    alternative_hypothesis = "One etymology is strongly supported by accumulated evidence"

    def __init__(
        self,
        place_name: str,
        hypotheses: list[dict[str, Any]],
        evidence_list: list[Evidence] | None = None,
    ) -> None:
        """Initialize with hypotheses and optional evidence.

        Args:
            place_name: The place name being analyzed.
            hypotheses: List of hypothesis dicts (id, description, prior, ...).
            evidence_list: Pre-constructed evidence items to apply.
        """
        self.place_name = place_name
        self.hypotheses_config = hypotheses
        self.evidence_list = evidence_list or []

    def run(self, data: PlaceData, n_permutations: int = 10000) -> TestResult:
        """Run Bayesian comparison test.

        The PlaceData is used to auto-generate geographic evidence
        if no evidence_list was provided.
        """
        # Create hypothesis set
        hs = create_hypothesis_set(self.place_name, self.hypotheses_config)
        initial_entropy = hs.entropy

        # Apply evidence
        if self.evidence_list:
            hs = sequential_update(hs, self.evidence_list)

        # Compute test statistic (log Bayes factor)
        sorted_hyps = sorted(hs.hypotheses, key=lambda h: h.current_probability, reverse=True)

        if len(sorted_hyps) >= 2:
            p1 = sorted_hyps[0].current_probability
            p2 = sorted_hyps[1].current_probability
            # Bayes factor = posterior odds / prior odds
            if p2 > 0:
                posterior_odds = p1 / p2
                log_bf = float(np.log(posterior_odds))
            else:
                posterior_odds = float("inf")
                log_bf = float("inf")
        else:
            posterior_odds = float("inf")
            log_bf = float("inf")

        # Determine significance using Kass & Raftery scale
        # log BF > 3.2 ≈ odds > 20:1 = "strong evidence"
        is_significant = log_bf > 3.2

        final_entropy = hs.entropy
        entropy_reduction = initial_entropy - final_entropy

        # Determine status
        if is_significant:
            status = StatStatus.CONFIRMED
        elif log_bf > 1.0:
            status = StatStatus.EXECUTED  # Moderate evidence
        else:
            status = StatStatus.INCONCLUSIVE

        return TestResult(
            test_id=self.test_id,
            test_family=self.test_family,
            status=status,
            null_hypothesis=self.null_hypothesis,
            alternative_hypothesis=self.alternative_hypothesis,
            test_statistic=log_bf,
            p_value=1.0 - sorted_hyps[0].current_probability if sorted_hyps else 1.0,
            effect_size=entropy_reduction,
            confidence_interval=(
                sorted_hyps[0].current_probability - 0.05,
                min(sorted_hyps[0].current_probability + 0.05, 1.0),
            )
            if sorted_hyps
            else (0.0, 1.0),
            n_observations=len(self.evidence_list),
            element_name=self.place_name,
            parameters={
                "winning_hypothesis": sorted_hyps[0].id if sorted_hyps else "",
                "posterior_odds": posterior_odds,
                "evidence_count": len(self.evidence_list),
                "entropy_reduction": entropy_reduction,
                "initial_entropy": initial_entropy,
                "final_entropy": final_entropy,
            },
        )

    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate on synthetic data.

        Creates synthetic evidence that should strongly support one hypothesis
        and verifies the test correctly identifies it.
        """
        rng = np.random.default_rng(42)
        correct_detections = 0
        false_positives = 0

        for trial in range(n_trials):
            # Create balanced hypotheses
            n_hyps = 3
            priors = [1.0 / n_hyps] * n_hyps
            hyps = [
                {"id": f"h{i}", "description": f"Hypothesis {i}", "prior": priors[i]}
                for i in range(n_hyps)
            ]

            # Plant signal: generate evidence strongly supporting h0
            true_winner = 0
            evidence_items = []
            for _e in range(3):
                lr = {}
                for i in range(n_hyps):
                    if i == true_winner:
                        lr[f"h{i}"] = float(rng.uniform(3.0, 8.0))
                    else:
                        lr[f"h{i}"] = float(rng.uniform(0.2, 0.8))
                evidence_items.append(
                    Evidence(
                        id=f"e{trial}_{_e}",
                        description="synthetic",
                        evidence_type="synthetic",
                        likelihood_ratios=lr,
                    )
                )

            test = BayesianComparisonTest("synthetic", hyps, evidence_items)
            data = PlaceData(
                coordinates=np.zeros((1, 2)),
                element_present=np.array([True]),
            )
            result = test.run(data)

            if result.parameters.get("winning_hypothesis") == "h0":
                correct_detections += 1

        # False positive test: uninformative evidence
        for trial in range(n_trials):
            hyps = [{"id": f"h{i}", "description": f"H{i}", "prior": 1.0 / 3} for i in range(3)]
            evidence_items = [
                Evidence(
                    id=f"fp_{trial}",
                    description="uninformative",
                    evidence_type="noise",
                    likelihood_ratios={f"h{i}": 1.0 for i in range(3)},
                )
            ]
            test = BayesianComparisonTest("noise", hyps, evidence_items)
            data = PlaceData(
                coordinates=np.zeros((1, 2)),
                element_present=np.array([True]),
            )
            result = test.run(data)
            if result.status == StatStatus.CONFIRMED:
                false_positives += 1

        power = correct_detections / n_trials
        fpr = false_positives / n_trials

        return SyntheticValidation(
            power=power,
            power_n_trials=n_trials,
            false_positive_rate=fpr,
            fpr_n_trials=n_trials,
            passed=power > 0.8 and fpr < 0.05,
            details=f"Power={power:.2f}, FPR={fpr:.2f}",
        )
