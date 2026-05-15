"""Catalan language module for toponymic analysis.

Catalan is a Western Romance language spoken in Catalonia, Valencia,
the Balearic Islands, Andorra, and parts of southern France. Its
toponymy reflects layers of Iberian, Latin, Visigothic, and Arabic
influence, with distinctive suffixes differentiating it from Spanish
and Occitan.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CatalanModule(BaseLanguageModule):
    """Language module for Catalan toponyms."""

    language_code = "cat"
    language_name = "Catalan"
    family = "Indo-European"
    branch = "Romance > Western > Gallo-Romance"
    period = "Modern (900 CE–present)"
    script = "Latn"

    prefixes = [
        "Mont-",
        "Sant-",
        "Font-",
        "Cas-",
        "Coll-",
        "Puig-",
        "Vall-",
        "Torr-",
        "Vila-",
        "Bell-",
    ]

    suffixes = [
        "-ell",
        "-ella",
        "-ona",
        "-eny",
        "-ès",
        "-ada",
        "-eda",
        "-anya",
        "-ars",
        "-ós",
        "-ot",
        "-era",
        "-enca",
        "-dor",
    ]

    stems = [
        "aigua",
        "roca",
        "pedra",
        "serra",
        "pla",
        "camp",
        "mas",
        "torre",
        "riu",
        "bosc",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()
        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix.lower()) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                results.append(
                    SegmentationResult(
                        component=stem, position=0, morph_type="compound_modifier", confidence=0.6
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(form) - len(suffix) :],
                        position=1,
                        morph_type="compound_head",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.7,
                    )
                )
                return results
        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 1:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.65,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(prefix) :], position=1, morph_type="stem", confidence=0.5
                    )
                )
                return results
        results.append(
            SegmentationResult(component=form, position=0, morph_type="stem", confidence=0.3)
        )
        return results

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "mont": "mountain",
            "sant": "saint",
            "font": "spring, fountain",
            "cas": "house",
            "coll": "hill pass",
            "puig": "peak, hill",
            "vall": "valley",
            "torr": "tower",
            "vila": "town",
            "bell": "beautiful",
            "ell": "diminutive (< Lat. -ellum)",
            "ella": "diminutive feminine",
            "ona": "augmentative",
            "eny": "pertaining to",
            "ès": "inhabitant of",
            "ada": "collective, place of",
            "eda": "grove, place with many",
            "anya": "related to",
            "ars": "place of",
            "ós": "full of",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Catalan."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Catalan suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Catalan prefix {prefix}-")
                score += 0.25
                break
        # Catalan-specific orthography
        catalan_markers = ["ny", "ll", "ig", "tx"]
        for marker in catalan_markers:
            if marker in form_lower:
                evidence.append(f"Catalan orthographic marker '{marker}'")
                score += 0.15
                break
        # L'article salat (Balearic)
        if form_lower.startswith(("s'", "sa ", "es ")):
            evidence.append("Balearic salat article")
            score += 0.3
        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "mont": ("mons", "mountain", ["Sp. monte", "Fr. mont"]),
            "puig": ("podium", "elevated place", ["Oc. puèg", "Fr. puy"]),
            "font": ("fons", "spring", ["Sp. fuente", "It. fonte"]),
            "vila": ("villa", "estate, town", ["Sp. villa", "Fr. ville"]),
            "coll": ("collum", "neck, pass", ["Fr. col"]),
            "vall": ("vallis", "valley", ["Sp. valle", "Fr. val"]),
            "sant": ("sanctus", "holy, saint", ["Sp. san", "Fr. saint"]),
            "bell": ("bellus", "beautiful", ["Sp. bello", "Fr. beau"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=cognates,
                        sources=["DCVB", "Coromines Onomasticon"],
                    )
                )
        return candidates
