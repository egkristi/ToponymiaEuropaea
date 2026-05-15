"""Semigallian language module.

Semigallian was a Baltic language spoken in southern Latvia and northern
Lithuania (Zemgale region), extinct by the 15th century. It was closely
related to Lithuanian and left substrate traces in central Latvian
place-names. The ethnonym element -gala means 'end/edge'.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SemigallianModule(BaseLanguageModule):
    """Language module for Semigallian toponyms."""

    language_code = "xzm"
    language_name = "Semigallian"
    family = "Indo-European"
    branch = "Baltic > Eastern Baltic (transitional)"
    period = "Extinct by 15th century CE"
    script = "Latn"

    suffixes = [
        "-gala",  # end, edge (cf. Zemgale)
        "-pils",  # castle
        "-upe",  # river
        "-kalns",  # hill
        "-ciems",  # village
        "-muiža",  # manor/estate
    ]

    prefixes = [
        "Zem-",  # ethnic: Zemgale / low land
        "Mež-",  # forest
        "Saul-",  # sun
        "Sil-",  # heath/pine forest
    ]

    stems = [
        "jelgav",  # Jelgava (seat of Semigallia)
        "dobel",  # Dobele
        "tērvete",  # Tērvete (Semigallian hillfort)
        "bauska",  # Bauska
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Semigallian toponym."""
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
        """Classify whether a name form is likely Semigallian."""
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

        # Key Semigallian element
        if "gal" in form_lower:
            evidence.append("element -gal- ('end/edge')")
            score += 0.25

        # Zemgale ethnic marker
        if "zem" in form_lower or "semigal" in form_lower:
            evidence.append("Semigallian ethnonym")
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
            "gala": ("galas", "end, edge", ["Lithuanian galas", "Latvian gals"]),
            "pils": ("pilis", "castle, hillfort", ["Lithuanian pilis", "Latvian pils"]),
            "upe": ("upė", "river", ["Lithuanian upė", "Latvian upe"]),
            "kalns": ("kalnas", "hill", ["Lithuanian kalnas"]),
            "zem": ("žemė", "land, low ground", ["Lithuanian žemė", "Latvian zeme"]),
            "saul": ("saulė", "sun", ["Lithuanian saulė", "Latvian saule"]),
            "sil": ("šilas", "heath, pine forest", ["Lithuanian šilas"]),
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
                        sound_changes=["Baltic *ē > Semigallian ie (partial)"],
                        sources=["Būga 1958", "Karulis 1992"],
                    )
                )

        return candidates
