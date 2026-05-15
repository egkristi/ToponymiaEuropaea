"""Corsican language module for toponymic analysis.

Corsican is a Romance language spoken on the island of Corsica (France)
and northern Sardinia. It occupies a transitional position between
Italian (Tuscan) and Sardinian, with Genoese superstrate influence
from centuries of Ligurian rule.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CorsicanModule(BaseLanguageModule):
    """Language module for Corsican toponyms."""

    language_code = "cos"
    language_name = "Corsican"
    family = "Indo-European"
    branch = "Romance > Italo-Dalmatian"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Sant-",
        "San-",
        "Monte-",
        "Punta-",
        "Campo-",
        "Pietra-",
        "Bocca-",
        "Capo-",
        "Foci-",
        "Ponte-",
    ]

    suffixes = [
        "-one",
        "-inu",
        "-acciu",
        "-eto",
        "-ata",
        "-inu",
        "-ella",
        "-iccia",
        "-aia",
        "-olu",
        "-ucciu",
        "-osa",
        "-acci",
    ]

    stems = [
        "monte",
        "petra",
        "campo",
        "bocca",
        "foci",
        "punta",
        "calanca",
        "pozzu",
        "fiumu",
        "torre",
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
            "sant": "saint",
            "san": "saint",
            "monte": "mountain",
            "punta": "peak, point",
            "campo": "field",
            "pietra": "stone",
            "bocca": "mountain pass (mouth)",
            "capo": "cape, headland",
            "foci": "river mouth",
            "ponte": "bridge",
            "one": "augmentative",
            "inu": "diminutive",
            "acciu": "pejorative/augmentative",
            "eto": "grove, place with",
            "ata": "place characterized by",
            "ella": "diminutive",
            "iccia": "diminutive/pejorative",
            "aia": "place of activity",
            "olu": "diminutive",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Corsican."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Corsican suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Corsican prefix {prefix}-")
                score += 0.25
                break
        # Corsican phonological markers
        if "ghj" in form_lower or "chj" in form_lower:
            evidence.append("Corsican palatalized velar (ghj/chj)")
            score += 0.3
        # Final -u characteristic of Corsican
        if form_lower.endswith("u") and not form_lower.endswith("iu"):
            evidence.append("Corsican final -u")
            score += 0.15
        # Double consonants (Italic feature)
        import re

        if re.search(r"([bcdfglmnprstvz])\1", form_lower):
            evidence.append("Geminate consonant")
            score += 0.1
        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "monte": ("montem", "mountain", ["It. monte", "Srd. monte"]),
            "bocca": ("bucca", "mouth, mountain pass", ["It. bocca", "Fr. bouche"]),
            "punta": ("puncta", "point, peak", ["It. punta", "Sp. punta"]),
            "campo": ("campus", "field", ["It. campo", "Fr. champ"]),
            "pietra": ("petra", "stone", ["It. pietra", "Fr. pierre"]),
            "ponte": ("pontem", "bridge", ["It. ponte", "Fr. pont"]),
            "foci": ("foce", "river mouth", ["It. foce"]),
            "capo": ("caput", "head, cape", ["It. capo", "Fr. chef"]),
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
                        sources=["Ferracci 2000", "ALEIC"],
                    )
                )
        return candidates
