"""Galindian language module.

Galindian was a Western Baltic language spoken primarily in the Masuria
region (Prussian Galindians), extinct by the 14th century. A possibly
related eastern group (Galindai/Голядь) is attested near Moscow.
Closely related to Old Prussian.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class GalindianModule(BaseLanguageModule):
    """Language module for Galindian toponyms."""

    language_code = "xgl"
    language_name = "Galindian"
    family = "Indo-European"
    branch = "Baltic > Western Baltic"
    period = "Extinct by 14th century CE"
    script = "Latn"

    suffixes = [
        "-aw",  # lake/water (cf. Old Prussian)
        "-ang",  # meadow (cf. Old Prussian angis)
        "-kaym",  # village (cf. Old Prussian caymis)
        "-garbis",  # mountain
        "-lauks",  # field
        "-wald",  # forest (Germanized)
    ]

    prefixes = [
        "Gal-",  # ethnic: Galindians
        "Naru-",  # narrow (cf. Narew)
        "Sar-",  # guard
    ]

    stems = [
        "galind",  # Galindian ethnonym
        "masur",  # Masuria region
        "sasn",  # hare (cf. Old Prussian sasins)
        "narew",  # Narew river
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Galindian toponym."""
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
        """Classify whether a name form is likely Galindian."""
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

        # Galindian ethnic marker
        if "galind" in form_lower or "goliad" in form_lower:
            evidence.append("Galindian ethnonym")
            score += 0.25

        # Old Prussian cognate features
        prussian_markers = ["kaym", "ang", "garb"]
        for marker in prussian_markers:
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
            "aw": ("aw", "lake, water", ["Old Prussian ape 'river'"]),
            "ang": ("angis", "meadow, snake", ["Old Prussian angis", "Lithuanian angis"]),
            "kaym": ("caymis", "village", ["Old Prussian caymis", "Lithuanian kaimas"]),
            "garbis": ("garbis", "mountain", ["Old Prussian garbis"]),
            "lauks": ("lauks", "field", ["Old Prussian lauks", "Lithuanian laukas"]),
            "gal": ("galas", "end; Galindian ethnonym", ["Lithuanian galas 'end'"]),
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
                        sound_changes=["W.Baltic *ā > Galindian o (?)"],
                        sources=["Ptolemy Geographia", "Gerullis 1922"],
                    )
                )

        return candidates
