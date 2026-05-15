"""Crimean Gothic language module.

Crimean Gothic was an East Germanic language spoken in Crimea from the
3rd to possibly 18th century CE—the last survival of any East Germanic
language. Known primarily from a 16th-century word list recorded by
Ogier Ghiselin de Busbecq. Possible place-name traces in Crimean
peninsula toponymy.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CrimeanGothicModule(BaseLanguageModule):
    """Language module for Crimean Gothic toponyms."""

    language_code = "gct"
    language_name = "Crimean Gothic"
    family = "Indo-European"
    branch = "Germanic > East Germanic"
    period = "3rd-18th century CE (?)"
    script = "Latn"

    # Very limited data from Busbecq's word list and possible survivals
    suffixes = [
        "-burg",  # fortification
        "-berg",  # mountain
        "-stein",  # stone
        "-wald",  # forest
        "-dor",  # Busbecq: door/gate
    ]

    prefixes = [
        "Goth-",  # ethnic marker
        "Man-",  # Mangup (Gothic capital?)
        "Dor-",  # Doros/Dori (fortification)
        "Ther-",  # Busbecq: thria = three(?)
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Crimean Gothic toponym."""
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
        """Classify whether a name form is likely Crimean Gothic."""
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

        # Busbecq word list correspondences
        busbecq_words = ["iel", "mine", "schuos", "stul", "handa", "broe"]
        for word in busbecq_words:
            if word in form_lower:
                evidence.append(f"Busbecq word-list element '{word}'")
                score += 0.2
                break

        # Gothic ethnic marker
        if "goth" in form_lower or "got" in form_lower:
            evidence.append("Gothic ethnonym")
            score += 0.2

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="late-antique-to-early-modern" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "burg": ("burg", "fortification", ["Gothic baurgs", "OHG burg"]),
            "berg": ("berg", "mountain", ["Gothic *bairgs", "OHG berg"]),
            "stein": ("stains", "stone", ["Gothic stains", "OHG stein"]),
            "wald": ("wald", "forest, rule", ["Gothic waldan", "OHG wald"]),
            "dor": ("daur", "door, gate", ["Gothic daur", "OE dor"]),
            "man": ("manna", "man; Mangup?", ["Gothic manna"]),
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
                        sound_changes=["Gothic ai > CrGo. ie (Busbecq)"],
                        sources=["Busbecq 1562", "Stearns 1978"],
                    )
                )

        return candidates
