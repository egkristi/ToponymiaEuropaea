"""Friulian language module for toponymic analysis.

Friulian (furlan) is a Rhaeto-Romance language spoken in the Friuli
region of northeastern Italy. Its toponymy shows layers of Celtic
(Carnic), Latin, Slavic, and Germanic contact, reflecting its position
at the crossroads of Romance, Slavic, and Germanic language areas.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class FriulianModule(BaseLanguageModule):
    """Language module for Friulian toponyms."""

    language_code = "fur"
    language_name = "Friulian"
    family = "Indo-European"
    branch = "Romance > Western > Rhaeto-Romance"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "San-",
        "Mont-",
        "Cjamp-",
        "Prat-",
        "Rivi-",
        "Plai-",
        "Cjase-",
        "Braide-",
        "Ronc-",
        "Grave-",
    ]

    suffixes = [
        "-ùt",
        "-ât",
        "-ade",
        "-ise",
        "-ans",
        "-ins",
        "-acco",
        "-uzzo",
        "-uzze",
        "-êt",
        "-ûl",
        "-igne",
    ]

    stems = [
        "aghe",
        "clap",
        "mont",
        "cjamp",
        "prat",
        "bosc",
        "grave",
        "ronc",
        "braide",
        "plai",
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
            "san": "saint",
            "mont": "mountain",
            "cjamp": "field",
            "prat": "meadow",
            "rivi": "stream",
            "plai": "slope",
            "cjase": "house",
            "braide": "enclosed cultivated land",
            "ronc": "cleared land",
            "grave": "gravel riverbed",
            "ùt": "diminutive",
            "ât": "past participle/collective",
            "ade": "place characterized by",
            "ise": "place of",
            "ans": "settlement suffix (< -anum)",
            "ins": "settlement suffix",
            "acco": "pejorative/augmentative",
            "uzzo": "diminutive",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Friulian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Friulian suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Friulian prefix {prefix}-")
                score += 0.25
                break
        # Friulian orthographic markers
        if "cj" in form_lower or "gj" in form_lower:
            evidence.append("Friulian palatalized consonant (cj/gj)")
            score += 0.3
        # Circumflex accent (long vowels)
        if "â" in form_lower or "ê" in form_lower or "ô" in form_lower or "û" in form_lower:
            evidence.append("Friulian long vowel (circumflex)")
            score += 0.2
        # Slavic contact layer (-igne, -acco from Slavic -nik, -ac)
        if form_lower.endswith(("igne", "icco")):
            evidence.append("Slavic contact suffix")
            score += 0.15
        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "mont": ("montem", "mountain", ["It. monte", "Roh. munt"]),
            "cjamp": ("campum", "field", ["It. campo", "Roh. champ"]),
            "prat": ("pratum", "meadow", ["It. prato", "Roh. pra"]),
            "clap": ("*klappam", "stone (pre-Roman)", ["Roh. crap"]),
            "aghe": ("aquam", "water", ["It. acqua", "Roh. aua"]),
            "ronc": ("*runcare", "cleared land", ["It. ronco"]),
            "braide": ("*braida", "enclosed field (Lombard)", ["It. braida"]),
            "grave": ("gravam", "gravel, pebble river bed", ["It. ghiaia"]),
            "plai": ("plagam", "slope, hillside", ["Roh. plai"]),
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
                        sources=["DESF", "Pirona"],
                    )
                )
        return candidates
