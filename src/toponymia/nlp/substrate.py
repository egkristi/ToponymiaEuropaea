"""Substrate detection via distributional phonotactic analysis.

Identifies potential non-Indo-European or pre-Germanic elements in
place-name corpora by detecting phonotactic anomalies — sequences of
sounds that don't fit the regular patterns of known language modules.

Approach:
1. Build a phonotactic model (bigram/trigram) from known IE elements
2. Score all place-name elements against this model
3. Elements with low probability → candidate substrate

This feeds Perspective U (PIE/Deep-Time substrate) and helps identify
Old European hydronymy (Krahe), Sami, and unknown pre-IE layers.

References:
- Krahe 1964. "Unsere ältesten Flussnamen."
- Kitson 1996. "British and European River-Names."
- de Bernardo Stempel 2000. "Ptolemy's Celtic Italy and Ireland."
"""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Common Germanic/IE phonotactic patterns (consonant clusters)
_IE_ONSET_CLUSTERS = {
    "bl",
    "br",
    "dr",
    "fl",
    "fr",
    "gl",
    "gr",
    "kl",
    "kr",
    "pl",
    "pr",
    "sk",
    "sl",
    "sm",
    "sn",
    "sp",
    "st",
    "str",
    "sv",
    "tr",
    "thr",
    "skr",
    "spr",
}

# Phonemes typical of Germanic languages
_GERMANIC_PHONEMES = set("abcdefghijklmnoprstuvwxyzæøåäöþð")

# Known substrate indicators (non-IE phonotactic patterns)
_SUBSTRATE_INDICATORS: list[str] = [
    # Double vowels unusual in Germanic (possible Sami/Finnic)
    r"[aeiou]{3,}",
    # Unusual consonant clusters for Germanic
    r"(?:^|[aeiou])(?:tk|kp|tp|bz|dz|gz|pn|ks(?:t)|tl|dl)",
    # Word-initial ng (possible pre-IE)
    r"^ng",
    # Non-Germanic final clusters
    r"(?:mk|nk|lk|rk)$",
]


@dataclass
class SubstrateCandidate:
    """A name element identified as potential substrate."""

    element: str
    score: float  # Lower = more anomalous
    reasons: list[str] = field(default_factory=list)
    possible_origin: str = ""  # "sami", "finnic", "pre-ie", "unknown"


@dataclass
class PhonotacticModel:
    """Character n-gram model for phonotactic analysis."""

    bigrams: Counter = field(default_factory=Counter)
    trigrams: Counter = field(default_factory=Counter)
    total_bigrams: int = 0
    total_trigrams: int = 0
    vocabulary: set = field(default_factory=set)

    def train(self, elements: list[str]) -> None:
        """Train the model on a list of known IE elements."""
        for element in elements:
            padded = f"^{element.lower()}$"
            self.vocabulary.add(element.lower())
            for i in range(len(padded) - 1):
                self.bigrams[padded[i : i + 2]] += 1
                self.total_bigrams += 1
            for i in range(len(padded) - 2):
                self.trigrams[padded[i : i + 3]] += 1
                self.total_trigrams += 1

    def score(self, element: str) -> float:
        """Score an element: higher = more typical of training data.

        Returns log-probability normalized by length. Range roughly [-10, 0].
        More negative = more anomalous.
        """
        if not self.total_bigrams:
            return 0.0

        padded = f"^{element.lower()}$"
        log_prob = 0.0
        n = 0

        for i in range(len(padded) - 1):
            bigram = padded[i : i + 2]
            count = self.bigrams.get(bigram, 0)
            # Laplace smoothing
            prob = (count + 1) / (self.total_bigrams + len(self.bigrams) + 1)
            log_prob += math.log(prob)
            n += 1

        return log_prob / n if n > 0 else 0.0


@dataclass
class SubstrateDetector:
    """Detect non-IE substrate elements in place-name corpora.

    Uses phonotactic modelling to identify elements that don't
    conform to Germanic/IE sound patterns.
    """

    model: PhonotacticModel = field(default_factory=PhonotacticModel)
    threshold: float = -6.0  # Elements below this are candidates
    trained: bool = False

    # Known IE elements for training (Germanic place-name elements)
    KNOWN_IE_ELEMENTS: list[str] = field(
        default_factory=lambda: [
            # Habitative
            "heim",
            "stad",
            "by",
            "torp",
            "tun",
            "rud",
            "seter",
            "bø",
            "gard",
            "hus",
            "land",
            "voll",
            "eng",
            "aker",
            # Topographic
            "berg",
            "fjell",
            "dal",
            "vik",
            "nes",
            "øy",
            "fjord",
            "elv",
            "bekk",
            "foss",
            "vann",
            "sjø",
            "myr",
            "mo",
            "sand",
            "stein",
            "haug",
            "ås",
            "li",
            "brekke",
            "hammer",
            # Directional
            "nord",
            "sør",
            "øst",
            "vest",
            "midt",
            "ytre",
            "indre",
            "øvre",
            "nedre",
            "stor",
            "lille",
            # Religious/cultural
            "hov",
            "horg",
            "ve",
            "lund",
            "kirke",
            "kors",
            # Personal name elements (common in compounds)
            "ulf",
            "bjorn",
            "thor",
            "erik",
            "stein",
            "gunn",
            "arn",
            "finn",
            "hall",
            "sig",
            "rolf",
            "harald",
            # German cognates
            "burg",
            "dorf",
            "feld",
            "wald",
            "bach",
            "brück",
            "kirch",
            "markt",
            "stein",
            "berg",
            "tal",
            "au",
            # English cognates
            "ham",
            "ton",
            "bury",
            "ford",
            "field",
            "wood",
            "church",
            "stead",
            "worth",
            "cester",
            "wick",
        ]
    )

    # Sami-origin indicators
    SAMI_PATTERNS: list[str] = field(
        default_factory=lambda: [
            "njarg",
            "njuon",
            "njar",
            "suol",
            "luok",
            "vuom",
            "jaur",
            "javre",
            "gais",
            "vars",
            "kauto",
            "guov",
            "vuot",
            "gied",
        ]
    )

    # Finnic-origin indicators
    FINNIC_PATTERNS: list[str] = field(
        default_factory=lambda: [
            "lahti",
            "jarvi",
            "joki",
            "koski",
            "niemi",
            "saari",
            "salmi",
            "vuori",
            "maki",
            "ranta",
        ]
    )

    def train(self, additional_elements: list[str] | None = None) -> None:
        """Train the phonotactic model on known IE elements.

        Args:
            additional_elements: Extra IE elements to include in training.
        """
        elements = list(self.KNOWN_IE_ELEMENTS)
        if additional_elements:
            elements.extend(additional_elements)
        self.model.train(elements)
        self.trained = True

    def analyze(self, element: str) -> SubstrateCandidate:
        """Analyze a single element for substrate indicators.

        Args:
            element: The place-name element to analyze.

        Returns:
            SubstrateCandidate with score and reasons.
        """
        if not self.trained:
            self.train()

        score = self.model.score(element)
        reasons: list[str] = []
        possible_origin = ""

        # Check phonotactic anomalies
        lower = element.lower()
        for pattern in _SUBSTRATE_INDICATORS:
            if re.search(pattern, lower):
                reasons.append(f"unusual pattern: {pattern}")

        # Check for non-Germanic phonemes
        non_germanic = set(lower) - _GERMANIC_PHONEMES
        if non_germanic:
            reasons.append(f"non-Germanic chars: {non_germanic}")

        # Check Sami patterns
        for pat in self.SAMI_PATTERNS:
            if pat in lower:
                reasons.append(f"Sami indicator: {pat}")
                possible_origin = "sami"
                break

        # Check Finnic patterns
        if not possible_origin:
            for pat in self.FINNIC_PATTERNS:
                if pat in lower:
                    reasons.append(f"Finnic indicator: {pat}")
                    possible_origin = "finnic"
                    break

        # Determine origin from score
        if not possible_origin and score < self.threshold:
            possible_origin = "pre-ie" if score < self.threshold - 2 else "unknown"

        return SubstrateCandidate(
            element=element,
            score=score,
            reasons=reasons,
            possible_origin=possible_origin,
        )

    def detect_batch(self, elements: list[str]) -> list[SubstrateCandidate]:
        """Analyze a batch of elements, returning only candidates.

        Args:
            elements: List of place-name elements.

        Returns:
            List of SubstrateCandidate objects that are anomalous.
        """
        if not self.trained:
            self.train()

        candidates = []
        for element in elements:
            result = self.analyze(element)
            if result.score < self.threshold or result.reasons:
                candidates.append(result)

        # Sort by score (most anomalous first)
        candidates.sort(key=lambda c: c.score)
        return candidates

    def analyze_corpus(
        self, names: list[str], *, min_length: int = 3
    ) -> dict[str, list[SubstrateCandidate]]:
        """Analyze an entire corpus of place names.

        Segments names into potential elements and checks each.

        Args:
            names: List of place names.
            min_length: Minimum element length to consider.

        Returns:
            Dict mapping names to their substrate candidates.
        """
        if not self.trained:
            self.train()

        results: dict[str, list[SubstrateCandidate]] = {}

        for name in names:
            # Simple segmentation: split on common suffixes
            lower = name.lower()
            # Skip very short names
            if len(lower) < min_length:
                continue

            candidate = self.analyze(lower)
            if candidate.score < self.threshold or candidate.reasons:
                results[name] = [candidate]

        return results
