"""Burgundian language module.

Burgundian was an East Germanic language spoken by the Burgundians in
southeastern France during the 5th-6th centuries. Minimal attestation
survives. Place-name substrate is found in Burgundy, Franche-Comté,
and Romandie, particularly in names with -ens, -inge (< *-ingos).
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class BurgundianModule(BaseLanguageModule):
    """Language module for Burgundian toponyms."""

    language_code = "xbu"
    language_name = "Burgundian"
    family = "Indo-European"
    branch = "Germanic > East Germanic"
    period = "5th-6th century CE"
    script = "Latn"

    suffixes = [
        "-ens",  # < *-ingos (patronymic)
        "-inge",  # < *-ingos variant
        "-inge(n)",  # Germanic patronymic
        "-ans",  # < *-ingos (evolved)
        "-ins",  # patronymic variant
        "-ey",  # < *aujō (island/meadow)
        "-oux",  # < *-wald (forest)
        "-olf",  # personal name element (wolf)
        "-gund",  # battle
    ]

    prefixes = [
        "Gun-",  # battle
        "Gond-",  # Romanized Gund-
        "Burg-",  # fortress
        "Sig-",  # victory
        "Ald-",  # old
        "Bert-",  # bright
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Burgundian toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)

        matched_suffix = None
        for suffix in sorted_suffixes:
            clean = suffix.replace("(", "").replace(")", "")
            if form_lower.endswith(clean.lower()):
                matched_suffix = clean
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
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.5,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Burgundian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [
            s.lstrip("-").lower().replace("(", "").replace(")", "") for s in self.suffixes
        ]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.4
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.3
                break

        # Burgundian-region markers
        if (form_lower.endswith(("ens", "inge"))) and not evidence:
            evidence.append("patronymic ending typical of Burgundian zone")
            score += 0.3

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="migration-period" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "ens": ("-ingos", "patronymic: people of", ["Gmc *-ingōz"]),
            "inge": ("-ingos", "patronymic: people of", ["Gmc *-ingōz"]),
            "ans": ("-ingos", "patronymic (evolved)", ["Gmc *-ingōz"]),
            "ey": ("aujō", "island, water-meadow", ["ON ey", "OHG ouwa"]),
            "oux": ("wald", "forest, power", ["OHG wald", "Gothic waldan"]),
            "gund": ("gunþ", "battle", ["Gothic gunþs", "OHG gund"]),
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
                        sound_changes=["Gmc. *-ingōz > Burg. -ens/-inge"],
                        sources=["Lex Burgundionum", "Perrenot 1942"],
                    )
                )

        return candidates
