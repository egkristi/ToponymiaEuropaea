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
from typing import Any

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


@dataclass
class RecordAnalysis:
    """Complete analysis of a databank record across all name forms."""

    place_id: str | None
    name_form: str
    best_hypothesis: SegmentationHypothesis | None
    best_form: str
    all_hypotheses: dict[str, list[SegmentationHypothesis]] = field(default_factory=dict)

    @property
    def is_segmented(self) -> bool:
        """Whether any form produced a compound segmentation."""
        return (
            self.best_hypothesis is not None
            and len(self.best_hypothesis.components) > 1
            and any(c.morph_type == "compound_head" for c in self.best_hypothesis.components)
        )


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

    def segment_record(self, record: dict[str, Any], top_k: int = 5) -> RecordAnalysis:
        """Analyze a full databank record including all attestation forms.

        Segments the current name_form AND all historical attestation forms,
        then picks the best segmentation across all forms. Historical forms
        often yield better segmentation (e.g., Bjǫrgvin > Bergen).

        Args:
            record: A databank record dict with at minimum 'name_form',
                    optionally 'attestations' and 'place_id'.
            top_k: Maximum hypotheses per form.

        Returns:
            RecordAnalysis with the best hypothesis across all forms.
        """
        name_form = record["name_form"]
        place_id = record.get("place_id")
        attestations = record.get("attestations", [])

        # Collect all forms to analyze
        forms_to_analyze = [name_form]
        for att in attestations:
            form = att.get("form")
            if form and form not in forms_to_analyze:
                forms_to_analyze.append(form)

        # Segment all forms
        all_hypotheses: dict[str, list[SegmentationHypothesis]] = {}
        best_hypothesis: SegmentationHypothesis | None = None
        best_form = name_form

        for form in forms_to_analyze:
            hyps = self.segment(form, top_k)
            all_hypotheses[form] = hyps

            if hyps:
                top_hyp = hyps[0]
                # Prefer compound segmentation over stem-only
                has_compound = any(c.morph_type == "compound_head" for c in top_hyp.components)
                if best_hypothesis is None:
                    best_hypothesis = top_hyp
                    best_form = form
                elif has_compound:
                    best_has_compound = any(
                        c.morph_type == "compound_head" for c in best_hypothesis.components
                    )
                    if (
                        not best_has_compound
                        or top_hyp.overall_confidence > best_hypothesis.overall_confidence
                    ):
                        best_hypothesis = top_hyp
                        best_form = form

        return RecordAnalysis(
            place_id=place_id,
            name_form=name_form,
            best_hypothesis=best_hypothesis,
            best_form=best_form,
            all_hypotheses=all_hypotheses,
        )
