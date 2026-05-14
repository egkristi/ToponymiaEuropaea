"""Morphological segmentation pipeline.

Applies language modules to segment place names into their constituent
morphological components (prefix, stem, suffix, compound elements).

The segmentation pipeline:
1. Takes normalized name forms
2. Applies all registered language modules
3. Ranks segmentation hypotheses by confidence
4. Stores results with full provenance
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from toponymia.languages.base import BaseLanguageModule, LanguageClassification, SegmentationResult

logger = logging.getLogger(__name__)


@dataclass
class SegmentationHypothesis:
    """A complete segmentation hypothesis for a name form."""

    form: str
    language: LanguageClassification
    components: list[SegmentationResult]
    overall_confidence: float = 0.0

    def __post_init__(self):
        if self.components and self.overall_confidence == 0.0:
            # Compute overall confidence as product of component confidences * language confidence
            component_conf = sum(c.confidence for c in self.components) / len(self.components)
            self.overall_confidence = component_conf * self.language.confidence


class SegmentationPipeline:
    """Pipeline stage for morphological segmentation of place names.

    Applies all registered language modules to each name form and
    produces ranked segmentation hypotheses.
    """

    def __init__(self, modules: list[BaseLanguageModule] | None = None):
        self._modules: list[BaseLanguageModule] = modules or []

    def register_module(self, module: BaseLanguageModule) -> None:
        """Register a language module for use in segmentation."""
        self._modules.append(module)
        logger.info(f"Registered language module: {module}")

    def segment(self, form: str, top_k: int = 5) -> list[SegmentationHypothesis]:
        """Segment a name form using all registered language modules.

        Args:
            form: Normalized name form to segment.
            top_k: Maximum number of hypotheses to return.

        Returns:
            List of SegmentationHypothesis ranked by confidence (descending).
        """
        hypotheses: list[SegmentationHypothesis] = []

        for module in self._modules:
            # First classify: does this language module recognize the form?
            classification = module.classify(form)

            # Only attempt segmentation if there's some confidence
            if classification.confidence < 0.1:
                continue

            # Segment
            components = module.segment(form)
            if components:
                hypothesis = SegmentationHypothesis(
                    form=form,
                    language=classification,
                    components=components,
                )
                hypotheses.append(hypothesis)

        # Sort by overall confidence
        hypotheses.sort(key=lambda h: h.overall_confidence, reverse=True)

        return hypotheses[:top_k]

    def segment_batch(
        self, forms: list[str], top_k: int = 5
    ) -> dict[str, list[SegmentationHypothesis]]:
        """Segment a batch of name forms.

        Args:
            forms: List of normalized name forms.
            top_k: Maximum hypotheses per form.

        Returns:
            Dict mapping form -> list of hypotheses.
        """
        return {form: self.segment(form, top_k) for form in forms}
