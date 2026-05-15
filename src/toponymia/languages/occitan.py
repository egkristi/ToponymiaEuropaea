"""Occitan language module for toponymic analysis.

Occitan (langue d'oc) is a Romance language spoken across southern France,
parts of Italy (Val d'Aran, Piedmont valleys), and Monaco. Its toponymy
is characterized by the distinctive -ac suffix (< Latin -acum) indicating
property, and Gallo-Roman settlement patterns.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OccitanModule(BaseLanguageModule):
    """Language module for Occitan toponyms."""

    language_code = "oci"
    language_name = "Occitan"
    family = "Indo-European"
    branch = "Romance > Western > Gallo-Romance"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Mont-",
        "Pech-",
        "Puech-",
        "Roc-",
        "Font-",
        "Bòsc-",
        "Castel-",
        "Vilà-",
        "Prat-",
        "Sèrra-",
    ]

    suffixes = [
        "-ac",
        "-argue",
        "-ens",
        "-ès",
        "-ana",
        "-anha",
        "-ièra",
        "-on",
        "-ós",
        "-at",
        "-ièch",
        "-enque",
        "-òl",
        "-agues",
    ]

    stems = [
        "aiga",
        "pèira",
        "ròca",
        "prat",
        "camp",
        "bòsc",
        "val",
        "cròs",
        "claus",
        "fon",
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
            "pech": "hill, peak (< Lat. podium)",
            "puech": "hill, peak (< Lat. podium)",
            "roc": "rock",
            "font": "spring, fountain",
            "bòsc": "forest",
            "castel": "castle",
            "vilà": "estate, village",
            "prat": "meadow",
            "sèrra": "mountain ridge",
            "ac": "property of (< Lat. -acum)",
            "argue": "water channel",
            "ens": "belonging to",
            "ès": "inhabitant of",
            "ana": "place, domain",
            "anha": "related to",
            "ièra": "place of",
            "ós": "full of",
            "at": "collective place",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Occitan."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Occitan suffix -{suffix}")
                score += 0.35
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Occitan prefix {prefix}-")
                score += 0.25
                break
        # Occitan orthographic markers
        if "lh" in form_lower or "nh" in form_lower:
            evidence.append("Occitan digraph (lh/nh)")
            score += 0.2
        if "ò" in form_lower or "è" in form_lower:
            evidence.append("Occitan grave accent")
            score += 0.15
        # -ac suffix is highly characteristic
        if form_lower.endswith(("ac", "iac")):
            evidence.append("Gallo-Roman -acum suffix")
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
            "mont": ("mons", "mountain", ["Cat. mont", "Fr. mont"]),
            "pech": ("podium", "elevated place", ["Cat. puig", "Fr. puy"]),
            "puech": ("podium", "elevated place", ["Cat. puig", "Fr. puy"]),
            "font": ("fons", "spring", ["Cat. font", "Fr. fontaine"]),
            "roc": ("rocca", "rock", ["Fr. roche", "Cat. roca"]),
            "ac": ("-acum", "property of (Gaulish personal name + Lat. suffix)", []),
            "castel": ("castellum", "fortified place", ["Fr. château", "Cat. castell"]),
            "prat": ("pratum", "meadow", ["Fr. pré", "Cat. prat"]),
            "val": ("vallis", "valley", ["Fr. val", "Cat. vall"]),
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
                        sources=["TDF", "ALF"],
                    )
                )
        return candidates
