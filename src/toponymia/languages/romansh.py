"""Romansh language module for toponymic analysis.

Romansh is a Rhaeto-Romance language spoken in the Swiss canton of
Graubünden. Its five written varieties (Sursilvan, Sutsilvan, Surmiran,
Puter, Vallader) and the standardized Rumantsch Grischun reflect alpine
geography in their toponymy with distinctive mountain, valley, and
pasture terminology.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class RomanshModule(BaseLanguageModule):
    """Language module for Romansh toponyms."""

    language_code = "roh"
    language_name = "Romansh"
    family = "Indo-European"
    branch = "Romance > Western > Rhaeto-Romance"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Val-",
        "Piz-",
        "Munt-",
        "Crap-",
        "Alp-",
        "Fuorn-",
        "Plan-",
        "God-",
        "Sur-",
        "Suot-",
    ]

    suffixes = [
        "-ín",
        "-un",
        "-eira",
        "-uogn",
        "-ail",
        "-adùra",
        "-èr",
        "-ogna",
        "-isch",
        "-aus",
        "-uors",
        "-als",
    ]

    stems = [
        "val",
        "piz",
        "munt",
        "crap",
        "aua",
        "god",
        "plan",
        "fuorn",
        "champ",
        "selva",
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
            "piz": "peak, summit",
            "munt": "mountain",
            "crap": "rock, boulder",
            "alp": "alpine pasture",
            "fuorn": "oven, lime kiln",
            "plan": "flat area, plain",
            "god": "forest",
            "sur": "above, upper",
            "suot": "below, lower",
            "ín": "diminutive",
            "un": "augmentative",
            "eira": "place of",
            "uogn": "pertaining to",
            "ail": "place",
            "adùra": "collective",
            "èr": "agent/place",
            "ogna": "related to",
            "isch": "adjectival",
            "aus": "water place",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Romansh."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Romansh suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Romansh prefix {prefix}-")
                score += 0.25
                break
        # Romansh orthographic markers
        romansh_clusters = ["tsch", "sch", "gl", "gn"]
        for cluster in romansh_clusters:
            if cluster in form_lower:
                evidence.append(f"Romansh cluster '{cluster}'")
                score += 0.2
                break
        # Characteristic Romansh words in compounds
        if "crap" in form_lower or "piz" in form_lower or "fuorn" in form_lower:
            evidence.append("Romansh lexical element")
            score += 0.25
        # -uogn ending is uniquely Romansh
        if form_lower.endswith("uogn"):
            evidence.append("Distinctive Romansh ending -uogn")
            score += 0.2
        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "val": ("vallem", "valley", ["It. valle", "Fr. val"]),
            "piz": ("*pittsu", "peak (pre-Roman alpine)", ["Ladin piz"]),
            "munt": ("montem", "mountain", ["It. monte", "Fr. mont"]),
            "crap": ("*krappam", "rock (pre-Roman)", ["Ladin crap"]),
            "god": ("*godum", "forest (pre-Roman)", []),
            "alp": ("alpem", "mountain pasture", ["De. Alp", "It. alpe"]),
            "plan": ("planum", "flat ground", ["It. piano", "Fr. plan"]),
            "fuorn": ("furnum", "oven, kiln", ["It. forno", "Fr. four"]),
            "aua": ("aquam", "water", ["It. acqua", "Fr. eau"]),
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
                        sources=["DRG", "RN"],
                    )
                )
        return candidates
