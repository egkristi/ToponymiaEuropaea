"""Polabian language module.

Polabian was a West Slavic language spoken in northeastern Germany by
the Elbe Slavs (Wends), extinct by the 18th century. It left massive
substrate in eastern German toponymy: Berlin, Dresden, Leipzig all
derive from Slavic. Characteristic Germanized suffixes include -itz,
-ow, and -in.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PolabianModule(BaseLanguageModule):
    """Language module for Polabian toponyms."""

    language_code = "pox"
    language_name = "Polabian"
    family = "Indo-European"
    branch = "Slavic > West Slavic > Lechitic"
    period = "Extinct by 18th century CE"
    script = "Latn"

    suffixes = [
        "-itz",  # Germanized < Slavic -ica/-ice
        "-ow",  # Germanized < Slavic -ov/-ovo
        "-in",  # Germanized < Slavic -in/-ino
        "-witz",  # Germanized < Slavic -vice
        "-zig",  # Germanized < Slavic -sko (Leipzig < *Lipьsko)
        "-ow",  # possessive (< -ov)
        "-au",  # Germanized < Slavic -ov/-ava
    ]

    prefixes = [
        "Wend-",  # ethnic: Wends
        "Sorb-",  # ethnic: Sorbs
        "Dres-",  # cf. Dresden < *Drežďany
        "Lip-",  # linden (cf. Leipzig)
    ]

    stems = [
        "berlin",  # Berlin < *brl- 'swamp'
        "dresden",  # Dresden < *Drežďany 'forest people'
        "leipzig",  # Leipzig < *Lipьsko 'linden place'
        "rostock",  # Rostock < *Rastok 'river fork'
        "schwerin",  # Schwerin < *Zvěrinъ 'animal place'
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Polabian toponym."""
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
                        confidence=0.6,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.6,
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
        """Classify whether a name form is likely Polabian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Germanized Slavic suffix -{suffix}")
                score += 0.35
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.25
                break

        # Wend/Sorbian ethnic markers
        if "wend" in form_lower or "sorb" in form_lower or "wind" in form_lower:
            evidence.append("Slavic ethnic marker")
            score += 0.2

        # Polabian-specific vowel shifts visible in Germanized forms
        polabian_markers = ["itz", "witz", "zig", "ow"]
        count = sum(1 for m in polabian_markers if m in form_lower)
        if count > 0:
            evidence.append("Germanized Slavic phonology")
            score += 0.15

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="medieval-slavic" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "itz": ("-ica/-ice", "place suffix (diminutive)", ["Czech -ice", "Polish -ica"]),
            "ow": ("-ov", "possessive (of X)", ["Czech -ov", "Polish -ów"]),
            "in": ("-in", "possessive (of X)", ["Czech -ín", "Polish -in"]),
            "witz": ("-vice", "place of (patronymic)", ["Czech -vice", "Polish -wice"]),
            "zig": ("-sko", "adjectival place", ["Czech -sko", "Polish -sko"]),
            "lip": ("lipa", "linden tree", ["Czech lípa", "Polish lipa"]),
            "dres": ("drežďane", "forest people", ["Czech Drážďany"]),
            "rost": ("rastok", "river fork, expansion", ["Czech rozток"]),
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
                        sound_changes=["Slavic *ě > Polabian ai/oi"],
                        sources=["Trautmann 1948-1950", "Fischer 1976"],
                    )
                )

        return candidates
