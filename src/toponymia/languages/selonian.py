"""Selonian language module.

Selonian was a Baltic language spoken in southeastern Latvia and
northeastern Lithuania (Sēlija region), extinct by the 15th century.
Very poorly attested, it occupied a transitional position between
Lithuanian and Latvian. Substrate traces persist in the Daugava
river region.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SelonianModule(BaseLanguageModule):
    """Language module for Selonian toponyms."""

    language_code = "sel"
    language_name = "Selonian"
    family = "Indo-European"
    branch = "Baltic > Eastern Baltic (transitional)"
    period = "Extinct by 15th century CE"
    script = "Latn"

    suffixes = [
        "-pils",  # castle
        "-upe",  # river
        "-kalns",  # hill
        "-ava",  # water/river
        "-ēni",  # inhabitants
        "-gals",  # end
    ]

    prefixes = [
        "Sēl-",  # ethnic: Selonians
        "Daug-",  # cf. Daugava
        "Jēk-",  # Jēkabpils area
        "Līv-",  # border with Livonians
    ]

    stems = [
        "sēlpils",  # Sēlpils (Selonian hillfort)
        "daugav",  # Daugava river
        "koknese",  # Koknese (hillfort)
        "aizkraukl",  # Aizkraukle
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Selonian toponym."""
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
        """Classify whether a name form is likely Selonian."""
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

        # Selonian ethnic / regional marker
        if "sēl" in form_lower or "sel" in form_lower:
            evidence.append("Selonian ethnonym")
            score += 0.2

        # Daugava region marker
        if "daug" in form_lower:
            evidence.append("Daugava region hydronym")
            score += 0.2

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="medieval-baltic" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "pils": ("pilis", "castle, hillfort", ["Lithuanian pilis", "Latvian pils"]),
            "upe": ("upė", "river", ["Lithuanian upė", "Latvian upe"]),
            "kalns": ("kalnas", "hill", ["Lithuanian kalnas"]),
            "ava": ("ava", "water, river", ["Baltic *auā-"]),
            "daug": ("daug-", "much, great", ["Lithuanian daug", "Latvian daudz"]),
            "sēl": ("sēl-", "Selonian (ethnonym)", ["Henry of Livonia: Selones"]),
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
                        sound_changes=["Baltic *ei > Selonian ē (?)"],
                        sources=["Būga 1958", "Henry of Livonia"],
                    )
                )

        return candidates
