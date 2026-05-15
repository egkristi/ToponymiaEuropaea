"""Asturian language module for toponymic analysis.

Asturian (asturianu/bable) is an Astur-Leonese Romance language spoken
in Asturias, NW Spain. Its toponymy preserves a strong Celtic (Astures)
substrate alongside Latin settlement patterns, with features shared
with Galician-Portuguese in the western dialect zone.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AsturianModule(BaseLanguageModule):
    """Language module for Asturian toponyms."""

    language_code = "ast"
    language_name = "Asturian"
    family = "Indo-European"
    branch = "Romance > Western > Ibero-Romance > Astur-Leonese"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Val-",
        "Vega-",
        "Peña-",
        "Llanu-",
        "Cuetu-",
        "Ríu-",
        "San-",
        "Brañ-",
        "Monte-",
        "Fonte-",
    ]

    suffixes = [
        "-ñu",
        "-ín",
        "-eiro",
        "-ón",
        "-iellu",
        "-anu",
        "-eda",
        "-oso",
        "-ango",
        "-iegu",
        "-iego",
        "-és",
    ]

    stems = [
        "peña",
        "cuetu",
        "vega",
        "brañ",
        "llanu",
        "ríu",
        "fonte",
        "monte",
        "picu",
        "prau",
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
            "val": "valley",
            "vega": "fertile lowland, meadow",
            "peña": "rock, cliff",
            "llanu": "plain, flat area",
            "cuetu": "hill, peak",
            "ríu": "river",
            "san": "saint",
            "brañ": "summer pasture",
            "monte": "mountain, woodland",
            "fonte": "spring, fountain",
            "ñu": "diminutive (< -iño)",
            "ín": "diminutive",
            "eiro": "place of, agent (< -arium)",
            "ón": "augmentative",
            "iellu": "diminutive (< -ellum)",
            "anu": "place of (< -anum)",
            "eda": "grove, collective",
            "oso": "full of",
            "ango": "pre-Roman element",
            "iegu": "pertaining to",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Asturian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Asturian suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Asturian prefix {prefix}-")
                score += 0.25
                break
        # Asturian palatalized lateral ll- initial
        if form_lower.startswith("ll"):
            evidence.append("Asturian initial ll- (palatalized L-)")
            score += 0.3
        # -ñ- characteristic
        if "ñ" in form_lower:
            evidence.append("Asturian palatal nasal ñ")
            score += 0.15
        # Metaphonic -u (masculine marker)
        if form_lower.endswith("u"):
            evidence.append("Asturian masculine -u")
            score += 0.1
        # Celtic substrate markers
        celtic_elements = ["brañ", "ango", "amb"]
        for elem in celtic_elements:
            if elem in form_lower:
                evidence.append(f"Celtic substrate element '{elem}'")
                score += 0.2
                break
        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "vega": ("*vaica", "fertile lowland (Celtic)", ["Sp. vega", "Gl. veiga"]),
            "peña": ("pinnam", "rock, cliff", ["Sp. peña", "Pt. penha"]),
            "brañ": ("*varenna", "summer pasture (Celtic)", ["Gl. braña"]),
            "cuetu": ("*cottum", "hill (pre-Roman)", []),
            "fonte": ("fontem", "spring", ["Sp. fuente", "Pt. fonte"]),
            "llanu": ("planum", "plain", ["Sp. llano", "Pt. chão"]),
            "monte": ("montem", "mountain", ["Sp. monte", "Pt. monte"]),
            "ríu": ("rivum", "river", ["Sp. río", "Pt. rio"]),
            "picu": ("*pikkum", "peak (pre-Roman)", ["Sp. pico"]),
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
                        sources=["DELLA", "García Arias"],
                    )
                )
        return candidates
