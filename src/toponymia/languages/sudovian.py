"""Sudovian/Yotvingian language module.

Sudovian (also called Yotvingian or Jatvingian) was a Western Baltic
language spoken in the border region of NE Poland, W Lithuania, and
NW Belarus (Suwałki region), extinct by the 17th century. Better
documented than other extinct Western Baltic languages through the
"Sudovian Catechism" and place-name evidence.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SudovianModule(BaseLanguageModule):
    """Language module for Sudovian/Yotvingian toponyms."""

    language_code = "xsv"
    language_name = "Sudovian"
    family = "Indo-European"
    branch = "Baltic > Western Baltic"
    period = "Extinct by 17th century CE"
    script = "Latn"

    suffixes = [
        "-kaym",  # village (cf. Old Prussian)
        "-lauks",  # field
        "-garbis",  # mountain
        "-pelk",  # swamp/marsh
        "-wald",  # forest (Germanized)
        "-ow",  # Slavicized suffix
        "-iszki",  # place of (Lithuanian influence)
    ]

    prefixes = [
        "Sūd-",  # ethnic: Sudovians
        "Jotv-",  # ethnic: Yotvingians
        "Aug-",  # high (cf. Augustów)
        "Nett-",  # Netta river
    ]

    stems = [
        "suwałk",  # Suwałki
        "sudav",  # Sudovian ethnonym
        "jotvingai",  # Yotvingian ethnonym
        "nett",  # Netta river
        "grodno",  # Grodno area
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Sudovian toponym."""
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
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="compound_head",
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
        """Classify whether a name form is likely Sudovian."""
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

        # Sudovian/Yotvingian ethnic markers
        if "sudov" in form_lower or "sūd" in form_lower:
            evidence.append("Sudovian ethnonym")
            score += 0.25
        elif "jotv" in form_lower or "jatv" in form_lower:
            evidence.append("Yotvingian ethnonym")
            score += 0.25

        # W.Baltic characteristic elements
        wb_markers = ["kaym", "pelk", "garb"]
        for marker in wb_markers:
            if marker in form_lower:
                evidence.append(f"W.Baltic element '{marker}'")
                score += 0.2
                break

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
            "kaym": ("caymis", "village", ["Old Prussian caymis", "Lithuanian kaimas"]),
            "lauks": ("lauks", "field", ["Old Prussian lauks", "Lithuanian laukas"]),
            "garbis": ("garbis", "mountain", ["Old Prussian garbis"]),
            "pelk": ("pelkē", "swamp, marsh", ["Old Prussian pelky", "Lithuanian pelkė"]),
            "sūd": ("sūd-", "Sudovian (ethnonym)", ["Sudovian Catechism"]),
            "aug": ("aug-", "high, grow", ["Lithuanian augti 'to grow'"]),
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
                        sound_changes=["W.Baltic *ei > Sudovian ī"],
                        sources=["Sudovian Catechism", "Zinkevičius 1984"],
                    )
                )

        return candidates
