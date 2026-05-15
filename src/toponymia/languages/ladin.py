"""Ladin language module for toponymic analysis.

Ladin is a Rhaeto-Romance language spoken in the Dolomite valleys of
northern Italy (South Tyrol, Trentino, Belluno). Its toponymy is
deeply tied to alpine/Dolomite mountain landscape, with pre-Roman
substrate and centuries of German (Tyrolean) contact influence.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LadinModule(BaseLanguageModule):
    """Language module for Ladin toponyms."""

    language_code = "lld"
    language_name = "Ladin"
    family = "Indo-European"
    branch = "Romance > Western > Rhaeto-Romance"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Col-",
        "Piz-",
        "Crap-",
        "Plan-",
        "Val-",
        "Sas-",
        "Bosc-",
        "Pra-",
        "Ciamp-",
        "Rì-",
    ]

    suffixes = [
        "-ëur",
        "-ëi",
        "-an",
        "-acia",
        "-eda",
        "-iera",
        "-ëla",
        "-ons",
        "-oi",
        "-ënt",
        "-ada",
        "-ùra",
    ]

    stems = [
        "col",
        "piz",
        "crap",
        "sas",
        "val",
        "plan",
        "bosc",
        "pra",
        "ega",
        "ciamp",
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
            "col": "hill, pass",
            "piz": "peak, summit",
            "crap": "rock, boulder",
            "plan": "flat area",
            "val": "valley",
            "sas": "rock, stone",
            "bosc": "forest",
            "pra": "meadow",
            "ciamp": "field",
            "rì": "stream",
            "ëur": "agent/place suffix",
            "ëi": "plural/collective",
            "an": "place of",
            "acia": "augmentative",
            "eda": "grove, collective",
            "iera": "place characterized by",
            "ëla": "diminutive",
            "ons": "collective",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Ladin."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Ladin suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Ladin prefix {prefix}-")
                score += 0.25
                break
        # Ladin diaeresis ë (schwa)
        if "ë" in form_lower:
            evidence.append("Ladin schwa (ë)")
            score += 0.25
        # Dolomite-specific elements
        dolomite_words = ["sas", "crap", "piz", "ciamp"]
        for word in dolomite_words:
            if word in form_lower:
                evidence.append(f"Dolomite lexical element '{word}'")
                score += 0.2
                break
        # -sc- cluster preserved
        if "sc" in form_lower:
            evidence.append("Preserved -sc- cluster")
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
            "col": ("collem", "hill, pass", ["It. colle", "Fr. col"]),
            "piz": ("*pittsu", "peak (pre-Roman)", ["Roh. piz"]),
            "crap": ("*krappam", "rock (pre-Roman)", ["Roh. crap"]),
            "sas": ("saxum", "rock, stone", ["It. sasso"]),
            "val": ("vallem", "valley", ["It. valle", "Roh. val"]),
            "plan": ("planum", "flat area", ["It. piano", "Roh. plan"]),
            "bosc": ("*buskum", "forest (Germanic)", ["It. bosco", "Fr. bois"]),
            "pra": ("pratum", "meadow", ["It. prato", "Roh. pra"]),
            "ciamp": ("campum", "field", ["It. campo", "Fur. cjamp"]),
            "ega": ("aquam", "water", ["It. acqua", "Roh. aua"]),
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
                        sources=["EWD", "Kramer 1989"],
                    )
                )
        return candidates
