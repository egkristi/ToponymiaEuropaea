"""Bayesian etymology framework.

Models competing etymological hypotheses as mutually exclusive sets
with explicit priors and evidence-based updating. For example, a place name
"Bergen" might have competing etymologies:
  H1: ON *berg* "mountain" (prior 0.7)
  H2: PGmc *berga-* "to protect" (prior 0.2)
  H3: Celtic *briga* "hill-fort" (prior 0.1)

Evidence (phonological, semantic, geographic) updates these priors
via Bayes' theorem to produce posteriors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Hypothesis:
    """A single etymological hypothesis."""

    id: str
    description: str
    prior: float
    posterior: float | None = None
    language: str | None = None
    element: str | None = None
    meaning: str | None = None

    @property
    def current_probability(self) -> float:
        """Return posterior if computed, else prior."""
        return self.posterior if self.posterior is not None else self.prior


@dataclass
class Evidence:
    """A piece of evidence that updates hypothesis probabilities.

    likelihood_ratios maps hypothesis_id → P(evidence | hypothesis).
    A ratio > 1.0 supports the hypothesis, < 1.0 weakens it.
    """

    id: str
    description: str
    evidence_type: str  # phonological, semantic, geographic, historical
    likelihood_ratios: dict[str, float] = field(default_factory=dict)
    source: str | None = None
    weight: float = 1.0  # Allow downweighting uncertain evidence


@dataclass
class EvidenceRecord:
    """Record of evidence application in the update log."""

    evidence_id: str
    priors: dict[str, float]
    posteriors: dict[str, float]
    description: str = ""


@dataclass
class HypothesisSet:
    """A set of mutually exclusive etymological hypotheses.

    Probabilities must sum to 1.0 within the set.
    """

    place_name: str
    hypotheses: list[Hypothesis] = field(default_factory=list)
    evidence_log: list[EvidenceRecord] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check that probabilities sum to ~1.0."""
        total = sum(h.current_probability for h in self.hypotheses)
        return abs(total - 1.0) < 1e-6

    @property
    def most_likely(self) -> Hypothesis | None:
        """Return the hypothesis with highest current probability."""
        if not self.hypotheses:
            return None
        return max(self.hypotheses, key=lambda h: h.current_probability)

    @property
    def entropy(self) -> float:
        """Shannon entropy of the probability distribution (bits).

        Lower entropy = more certainty; 0 = one hypothesis is certain.
        """
        import math

        total = 0.0
        for h in self.hypotheses:
            p = h.current_probability
            if p > 0:
                total -= p * math.log2(p)
        return total

    def get_hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        """Get hypothesis by ID."""
        for h in self.hypotheses:
            if h.id == hypothesis_id:
                return h
        return None


def create_hypothesis_set(
    place_name: str,
    hypotheses: list[dict[str, Any]],
) -> HypothesisSet:
    """Create a hypothesis set from a list of hypothesis dicts.

    Args:
        place_name: The place name being analyzed.
        hypotheses: List of dicts with keys: id, description, prior,
                    and optionally: language, element, meaning.

    Returns:
        A validated HypothesisSet.

    Raises:
        ValueError: If priors don't sum to 1.0 or are invalid.
    """
    hyps: list[Hypothesis] = []
    for h in hypotheses:
        prior = h["prior"]
        if prior < 0 or prior > 1:
            msg = f"Prior must be in [0,1], got {prior} for {h['id']}"
            raise ValueError(msg)
        hyps.append(
            Hypothesis(
                id=h["id"],
                description=h["description"],
                prior=prior,
                language=h.get("language"),
                element=h.get("element"),
                meaning=h.get("meaning"),
            )
        )

    total = sum(h.prior for h in hyps)
    if abs(total - 1.0) > 1e-6:
        msg = f"Priors must sum to 1.0, got {total}"
        raise ValueError(msg)

    return HypothesisSet(place_name=place_name, hypotheses=hyps)


def bayesian_update(
    hypothesis_set: HypothesisSet,
    evidence: Evidence,
) -> HypothesisSet:
    """Apply Bayesian update to a hypothesis set given new evidence.

    Uses Bayes' theorem:
        P(H|E) = P(E|H) * P(H) / P(E)

    where P(E) = sum over all H of P(E|H)*P(H) (normalization).

    Hypotheses not mentioned in evidence.likelihood_ratios are treated
    as having likelihood ratio 1.0 (evidence is uninformative for them).

    Args:
        hypothesis_set: The current hypothesis set.
        evidence: Evidence with likelihood ratios per hypothesis.

    Returns:
        Updated HypothesisSet with new posteriors and log entry.
    """
    # Record priors before update
    priors = {h.id: h.current_probability for h in hypothesis_set.hypotheses}

    # Compute unnormalized posteriors
    unnormalized: dict[str, float] = {}
    for h in hypothesis_set.hypotheses:
        lr = evidence.likelihood_ratios.get(h.id, 1.0)
        # Apply weight: lr^weight (reduces effect of uncertain evidence)
        effective_lr = lr**evidence.weight
        unnormalized[h.id] = h.current_probability * effective_lr

    # Normalize (sum to 1.0)
    total = sum(unnormalized.values())
    if total == 0:
        msg = "All hypotheses have zero probability after update"
        raise ValueError(msg)

    posteriors: dict[str, float] = {hid: p / total for hid, p in unnormalized.items()}

    # Apply posteriors
    for h in hypothesis_set.hypotheses:
        h.posterior = posteriors[h.id]

    # Record in evidence log
    hypothesis_set.evidence_log.append(
        EvidenceRecord(
            evidence_id=evidence.id,
            priors=priors,
            posteriors=posteriors,
            description=evidence.description,
        )
    )

    return hypothesis_set


def sequential_update(
    hypothesis_set: HypothesisSet,
    evidence_list: list[Evidence],
) -> HypothesisSet:
    """Apply multiple evidence items sequentially.

    Each update uses the posterior from the previous step as the new prior.

    Args:
        hypothesis_set: Initial hypothesis set.
        evidence_list: Ordered list of evidence to apply.

    Returns:
        Updated HypothesisSet after all evidence applied.
    """
    for evidence in evidence_list:
        hypothesis_set = bayesian_update(hypothesis_set, evidence)
    return hypothesis_set


def hypothesis_set_to_dict(hs: HypothesisSet) -> dict[str, Any]:
    """Serialize a HypothesisSet to a dict for JSON storage."""
    return {
        "place_name": hs.place_name,
        "hypotheses": [
            {
                "id": h.id,
                "description": h.description,
                "prior": h.prior,
                "posterior": h.posterior,
                "language": h.language,
                "element": h.element,
                "meaning": h.meaning,
            }
            for h in hs.hypotheses
        ],
        "evidence_log": [
            {
                "evidence_id": e.evidence_id,
                "priors": e.priors,
                "posteriors": e.posteriors,
                "description": e.description,
            }
            for e in hs.evidence_log
        ],
        "metadata": hs.metadata,
    }


def hypothesis_set_from_dict(data: dict[str, Any]) -> HypothesisSet:
    """Deserialize a HypothesisSet from a dict."""
    hypotheses = [
        Hypothesis(
            id=h["id"],
            description=h["description"],
            prior=h["prior"],
            posterior=h.get("posterior"),
            language=h.get("language"),
            element=h.get("element"),
            meaning=h.get("meaning"),
        )
        for h in data["hypotheses"]
    ]
    evidence_log = [
        EvidenceRecord(
            evidence_id=e["evidence_id"],
            priors=e["priors"],
            posteriors=e["posteriors"],
            description=e.get("description", ""),
        )
        for e in data.get("evidence_log", [])
    ]
    return HypothesisSet(
        place_name=data["place_name"],
        hypotheses=hypotheses,
        evidence_log=evidence_log,
        metadata=data.get("metadata", {}),
    )
