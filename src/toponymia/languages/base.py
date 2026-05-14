"""Base interface for language-specific modules.

Each language module encapsulates the linguistic knowledge needed to:
1. Segment place names into morphological components
2. Classify name forms as belonging to this language (with confidence)
3. Generate etymological candidates

Language modules are the primary extension point for adding new languages
to the framework. A new language requires ONLY implementing this interface—
no changes to core code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SegmentationResult:
    """Result of morphological segmentation."""

    component: str
    position: int
    morph_type: str  # prefix, stem, suffix, compound_head, compound_modifier, infix, genitive
    lemma: str | None = None
    meaning: str | None = None
    meaning_uri: str | None = None
    confidence: float = 0.5


@dataclass
class LanguageClassification:
    """Confidence that a name (or component) belongs to this language."""

    language_code: str
    confidence: float  # 0.0 to 1.0
    evidence: list[str] = field(default_factory=list)
    period_estimate: str | None = None  # e.g., "proto-germanic", "old-norse", "medieval"


@dataclass
class EtymologyCandidate:
    """A proposed etymology for a name or component."""

    lemma: str
    meaning: str
    language_code: str
    confidence: float
    cognates: list[str] = field(default_factory=list)
    sound_changes: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)


class BaseLanguageModule(ABC):
    """Abstract base class for language-specific analysis modules.

    To add a new language:
    1. Create a new module in src/toponymia/languages/
    2. Subclass BaseLanguageModule
    3. Implement all abstract methods
    4. Define the class-level metadata

    The module will automatically be discoverable by the pipeline.
    """

    # Class-level metadata (override in subclass)
    language_code: str = ""       # ISO 639-3
    language_name: str = ""
    family: str = ""              # e.g., "Indo-European"
    branch: str = ""              # e.g., "Germanic > North Germanic"
    period: str = ""              # e.g., "Old Norse (700-1350)"
    script: str = "Latn"          # ISO 15924

    # Known toponymic elements (populate in subclass)
    prefixes: list[str] = []
    suffixes: list[str] = []
    stems: list[str] = []

    @abstractmethod
    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a place name into morphological components.

        Should return multiple possible segmentations ranked by confidence.

        Args:
            form: The normalized name form to segment.

        Returns:
            List of SegmentationResult, ordered by position.
        """
        ...

    @abstractmethod
    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to this language.

        Args:
            form: Normalized name form.

        Returns:
            LanguageClassification with confidence score.
        """
        ...

    @abstractmethod
    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components.

        Args:
            components: Previously segmented morphological components.

        Returns:
            List of EtymologyCandidate ranked by confidence.
        """
        ...

    def normalize(self, form: str) -> str:
        """Normalize a name form for this language.

        Default implementation: lowercase and strip whitespace.
        Override for language-specific normalization (e.g., handling ð/þ, ä/ae).
        """
        return form.lower().strip()

    def is_known_element(self, component: str) -> bool:
        """Check if a component is a known toponymic element in this language."""
        component_lower = component.lower()
        return (
            component_lower in [s.lower() for s in self.suffixes]
            or component_lower in [p.lower() for p in self.prefixes]
            or component_lower in [s.lower() for s in self.stems]
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} lang={self.language_code!r} ({self.language_name})>"
