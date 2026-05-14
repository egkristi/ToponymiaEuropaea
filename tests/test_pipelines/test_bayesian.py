"""Tests for Bayesian etymology framework."""

from toponymia.pipelines.bayesian import (
    Evidence,
    HypothesisSet,
    bayesian_update,
    create_hypothesis_set,
    hypothesis_set_from_dict,
    hypothesis_set_to_dict,
    sequential_update,
)


class TestCreateHypothesisSet:
    def test_valid_set(self) -> None:
        hs = create_hypothesis_set(
            "Bergen",
            [
                {"id": "h1", "description": "ON berg 'mountain'", "prior": 0.7},
                {"id": "h2", "description": "PGmc berga- 'protect'", "prior": 0.2},
                {"id": "h3", "description": "Celtic briga 'hill-fort'", "prior": 0.1},
            ],
        )
        assert hs.is_valid
        assert len(hs.hypotheses) == 3
        assert hs.place_name == "Bergen"

    def test_priors_must_sum_to_one(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="sum to 1.0"):
            create_hypothesis_set(
                "X",
                [
                    {"id": "h1", "description": "A", "prior": 0.5},
                    {"id": "h2", "description": "B", "prior": 0.3},
                ],
            )

    def test_invalid_prior_range(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="must be in"):
            create_hypothesis_set(
                "X",
                [
                    {"id": "h1", "description": "A", "prior": -0.1},
                    {"id": "h2", "description": "B", "prior": 1.1},
                ],
            )

    def test_optional_fields(self) -> None:
        hs = create_hypothesis_set(
            "Vik",
            [
                {
                    "id": "h1",
                    "description": "ON vík 'bay'",
                    "prior": 1.0,
                    "language": "non",
                    "element": "vík",
                    "meaning": "bay, inlet",
                },
            ],
        )
        h = hs.hypotheses[0]
        assert h.language == "non"
        assert h.element == "vík"
        assert h.meaning == "bay, inlet"


class TestBayesianUpdate:
    def _bergen_set(self) -> HypothesisSet:
        return create_hypothesis_set(
            "Bergen",
            [
                {"id": "mountain", "description": "ON berg 'mountain'", "prior": 0.7},
                {"id": "protect", "description": "PGmc berga- 'protect'", "prior": 0.2},
                {"id": "celtic", "description": "Celtic briga 'hill-fort'", "prior": 0.1},
            ],
        )

    def test_supporting_evidence_increases_probability(self) -> None:
        hs = self._bergen_set()
        evidence = Evidence(
            id="e1",
            description="Place is on a mountain",
            evidence_type="geographic",
            likelihood_ratios={"mountain": 3.0, "protect": 0.5, "celtic": 0.5},
        )
        updated = bayesian_update(hs, evidence)
        mountain = updated.get_hypothesis("mountain")
        assert mountain is not None
        assert mountain.current_probability > 0.7  # Increased from prior

    def test_posteriors_sum_to_one(self) -> None:
        hs = self._bergen_set()
        evidence = Evidence(
            id="e1",
            description="Phonological match to ON",
            evidence_type="phonological",
            likelihood_ratios={"mountain": 5.0, "protect": 1.0, "celtic": 0.2},
        )
        updated = bayesian_update(hs, evidence)
        total = sum(h.current_probability for h in updated.hypotheses)
        assert abs(total - 1.0) < 1e-10

    def test_evidence_log_recorded(self) -> None:
        hs = self._bergen_set()
        evidence = Evidence(
            id="e1",
            description="test evidence",
            evidence_type="semantic",
            likelihood_ratios={"mountain": 2.0},
        )
        updated = bayesian_update(hs, evidence)
        assert len(updated.evidence_log) == 1
        log = updated.evidence_log[0]
        assert log.evidence_id == "e1"
        assert "mountain" in log.priors
        assert "mountain" in log.posteriors
        assert log.posteriors["mountain"] > log.priors["mountain"]

    def test_uninformative_evidence_no_change(self) -> None:
        hs = self._bergen_set()
        evidence = Evidence(
            id="e1",
            description="Uninformative",
            evidence_type="other",
            likelihood_ratios={},  # All default to 1.0
        )
        updated = bayesian_update(hs, evidence)
        for h in updated.hypotheses:
            assert abs(h.current_probability - h.prior) < 1e-10

    def test_evidence_weight(self) -> None:
        """Weight < 1 reduces the effect of evidence."""
        hs1 = self._bergen_set()
        hs2 = self._bergen_set()

        strong = Evidence(
            id="e1",
            description="Strong",
            evidence_type="phonological",
            likelihood_ratios={"mountain": 5.0, "protect": 0.5, "celtic": 0.5},
            weight=1.0,
        )
        weak = Evidence(
            id="e2",
            description="Weak",
            evidence_type="phonological",
            likelihood_ratios={"mountain": 5.0, "protect": 0.5, "celtic": 0.5},
            weight=0.5,
        )

        updated_strong = bayesian_update(hs1, strong)
        updated_weak = bayesian_update(hs2, weak)

        # Strong evidence should move probability more
        mountain_strong = updated_strong.get_hypothesis("mountain")
        mountain_weak = updated_weak.get_hypothesis("mountain")
        assert mountain_strong is not None
        assert mountain_weak is not None
        assert mountain_strong.current_probability > mountain_weak.current_probability


class TestSequentialUpdate:
    def test_multiple_evidence(self) -> None:
        hs = create_hypothesis_set(
            "Nes",
            [
                {"id": "headland", "description": "ON nes 'headland'", "prior": 0.6},
                {"id": "nose", "description": "ON nǫs 'nose' (metaphor)", "prior": 0.4},
            ],
        )
        evidence_list = [
            Evidence(
                id="e1",
                description="Place is on a promontory",
                evidence_type="geographic",
                likelihood_ratios={"headland": 3.0, "nose": 0.5},
            ),
            Evidence(
                id="e2",
                description="No nose-shaped feature nearby",
                evidence_type="geographic",
                likelihood_ratios={"headland": 1.5, "nose": 0.3},
            ),
        ]
        updated = sequential_update(hs, evidence_list)
        assert len(updated.evidence_log) == 2
        headland = updated.get_hypothesis("headland")
        assert headland is not None
        assert headland.current_probability > 0.9  # Strong cumulative evidence

    def test_conflicting_evidence(self) -> None:
        """Conflicting evidence should moderate probabilities."""
        hs = create_hypothesis_set(
            "Holm",
            [
                {"id": "island", "description": "ON holmr 'islet'", "prior": 0.5},
                {"id": "meadow", "description": "ON holmr 'meadow'", "prior": 0.5},
            ],
        )
        evidence_list = [
            Evidence(
                id="e1",
                description="Place is on an island",
                evidence_type="geographic",
                likelihood_ratios={"island": 5.0, "meadow": 0.5},
            ),
            Evidence(
                id="e2",
                description="Historical records say 'meadow'",
                evidence_type="historical",
                likelihood_ratios={"island": 0.3, "meadow": 4.0},
            ),
        ]
        updated = sequential_update(hs, evidence_list)
        # Neither should dominate completely
        island = updated.get_hypothesis("island")
        meadow = updated.get_hypothesis("meadow")
        assert island is not None
        assert meadow is not None
        assert 0.2 < island.current_probability < 0.8


class TestHypothesisSet:
    def test_most_likely(self) -> None:
        hs = create_hypothesis_set(
            "X",
            [
                {"id": "a", "description": "A", "prior": 0.8},
                {"id": "b", "description": "B", "prior": 0.2},
            ],
        )
        assert hs.most_likely is not None
        assert hs.most_likely.id == "a"

    def test_entropy_certain(self) -> None:
        """Single certain hypothesis = 0 entropy."""
        hs = create_hypothesis_set(
            "X",
            [
                {"id": "a", "description": "A", "prior": 1.0},
            ],
        )
        assert hs.entropy == 0.0

    def test_entropy_uniform(self) -> None:
        """Uniform distribution = maximum entropy."""
        hs = create_hypothesis_set(
            "X",
            [
                {"id": "a", "description": "A", "prior": 0.5},
                {"id": "b", "description": "B", "prior": 0.5},
            ],
        )
        assert abs(hs.entropy - 1.0) < 1e-10  # log2(2) = 1 bit

    def test_get_hypothesis(self) -> None:
        hs = create_hypothesis_set(
            "X",
            [
                {"id": "a", "description": "A", "prior": 0.5},
                {"id": "b", "description": "B", "prior": 0.5},
            ],
        )
        assert hs.get_hypothesis("a") is not None
        assert hs.get_hypothesis("nonexistent") is None


class TestSerialization:
    def test_roundtrip(self) -> None:
        hs = create_hypothesis_set(
            "Bergen",
            [
                {
                    "id": "mountain",
                    "description": "ON berg",
                    "prior": 0.7,
                    "language": "non",
                },
                {"id": "protect", "description": "PGmc berga-", "prior": 0.3},
            ],
        )
        evidence = Evidence(
            id="e1",
            description="Geographic",
            evidence_type="geographic",
            likelihood_ratios={"mountain": 2.0, "protect": 0.5},
        )
        updated = bayesian_update(hs, evidence)

        data = hypothesis_set_to_dict(updated)
        restored = hypothesis_set_from_dict(data)

        assert restored.place_name == "Bergen"
        assert len(restored.hypotheses) == 2
        assert len(restored.evidence_log) == 1
        m = restored.get_hypothesis("mountain")
        assert m is not None
        assert abs(m.posterior - updated.get_hypothesis("mountain").posterior) < 1e-10

    def test_to_dict_structure(self) -> None:
        hs = create_hypothesis_set(
            "X",
            [
                {"id": "a", "description": "A", "prior": 1.0},
            ],
        )
        data = hypothesis_set_to_dict(hs)
        assert "place_name" in data
        assert "hypotheses" in data
        assert "evidence_log" in data
        assert data["hypotheses"][0]["id"] == "a"
