"""Vandalic language module.

Vandalic was an East Germanic language spoken by the Vandals in
North Africa and Hispania during the 5th century. Almost no direct
attestation survives. Possible toponymic traces include the debated
connection of Andalusia < *Vandalusia. Relevant for migration-period
toponymy studies.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class VandalicModule(BaseLanguageModule):
    """Language module for Vandalic toponyms."""

    language_code = "xvn"
    language_name = "Vandalic"
    family = "Indo-European"
    branch = "Germanic > East Germanic"
    period = "3rd-6th century CE"
    script = "Latn"

    # Very limited attestation—mostly reconstructed from names
    suffixes = [
        "-reiks",  # ruler (cf. Gothic -reiks)
        "-gild",  # value, tribute
        "-mund",  # protection
    ]

    prefixes = [
        "Gais-",  # spear
        "Gund-",  # battle
        "Thras-",  # bold
        "Hild-",  # battle
        "Wand-",  # Vandal ethnonym root
        "Frid-",  # peace
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Vandalic toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix.lower()):
                matched_suffix = suffix
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            if stem:
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="compound_modifier",
                        confidence=0.4,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.4,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.2,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Vandalic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.3
                break

        # Vandalic ethnonym connection
        if "vandal" in form_lower or "wandal" in form_lower:
            evidence.append("contains Vandal ethnonym")
            score += 0.4

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="migration-period" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "reiks": ("reiks", "ruler, king", ["Gothic reiks", "OHG rīhhi"]),
            "mund": ("mund", "protection", ["Gothic mundō", "OHG munt"]),
            "gild": ("gild", "value, tribute", ["Gothic gild", "OE gield"]),
            "wand": ("wand-", "Vandal ethnonym (?)", ["Pliny: Vandilii"]),
        }

        candidates: list[EtymologyCandidate] = []
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in meanings:
                lemma, meaning, cognates = meanings[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=cognates,
                        sound_changes=[],
                        sources=["Procopius", "Courtois 1955"],
                    )
                )

        return candidates
