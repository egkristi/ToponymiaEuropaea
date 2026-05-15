"""Curonian language module.

Curonian was a Western Baltic language spoken in western Latvia (Courland/
Kurzeme) and parts of Lithuania, extinct by the 16th century. It shows
mixed Baltic-Finnic traits and left significant substrate in Latvian
coastal place-names, especially hydronyms.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CuronianModule(BaseLanguageModule):
    """Language module for Curonian toponyms."""

    language_code = "xcu"
    language_name = "Curonian"
    family = "Indo-European"
    branch = "Baltic > Western Baltic"
    period = "Extinct by 16th century CE"
    script = "Latn"

    suffixes = [
        "-upe",  # river
        "-ezers",  # lake (Baltic-Finnic influence)
        "-ava",  # water/river
        "-gals",  # end, edge
        "-pils",  # castle
        "-ciems",  # village
        "-kalns",  # hill
    ]

    prefixes = [
        "Kur-",  # ethnic: Curonians
        "Pil-",  # castle
        "Vēj-",  # wind
        "Jūr-",  # sea
    ]

    stems = [
        "vent",  # Venta river
        "abavas",  # Abava river
        "liep",  # linden tree
        "mežs",  # forest
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Curonian toponym."""
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
        """Classify whether a name form is likely Curonian."""
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

        # Baltic hydronymic markers
        hydro_markers = ["up", "ez", "av"]
        for marker in hydro_markers:
            if marker in form_lower:
                evidence.append(f"hydronymic element '{marker}'")
                score += 0.2
                break

        # Curonian ethnic marker
        if "kur" in form_lower or "cour" in form_lower:
            evidence.append("Curonian ethnonym")
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
            "upe": ("upė", "river", ["Lithuanian upė", "Latvian upe"]),
            "ezers": ("ezers", "lake", ["Latvian ezers", "cf. Finnish järvi"]),
            "ava": ("ava", "water, river", ["Baltic *auā-", "Lithuanian ãužava"]),
            "gals": ("galas", "end, edge", ["Lithuanian galas"]),
            "pils": ("pilis", "castle", ["Lithuanian pilis", "Latvian pils"]),
            "kalns": ("kalnas", "hill, mountain", ["Lithuanian kalnas"]),
            "vent": ("ventā", "Venta river", ["Baltic *vent- 'wind/wet'"]),
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
                        sound_changes=["W.Baltic *ā > Curonian ō (partial)"],
                        sources=["Būga 1958", "Endzelīns 1943"],
                    )
                )

        return candidates
