"""Erzya (эрзянь кель) language module for toponymic analysis.

Erzya is a Uralic/Mordvinic language spoken in the Republic of Mordovia
and surrounding regions of the Middle Volga, Russia (~400 000 speakers).
Important substrate layer in central Russian toponymy.

Toponymic hallmarks:
- Suffixes: -ley/-lej (river/valley), -vir (forest), -gar (suffix of unclear origin)
- Agglutinative morphology with definite/indefinite noun declension
- Rich landscape vocabulary: лей (river), вирь (forest), пандо (hill)
- Palatalised consonants: ль, нь, рь, ть

Key reference: Tsygankin 2005 "Mordovskaja toponimija"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "ley": "river/valley",
    "lej": "river/valley",
    "vir": "forest",
    "gar": "settlement (archaic)",
    "pando": "hill/slope",
    "luga": "meadow",
    "kudo": "house/settlement",
    "osh": "town/fortress",
    "kal": "fish (in hydronyms)",
    "ved": "water",
    "nar": "field/steppe",
    "vele": "village",
    "bue": "place",
    "latko": "ravine/hollow",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "ravo": "black (of water)",
    "ašo": "white",
    "yakstere": "red",
    "poke": "long",
    "nuzjaks": "marshy",
    "ine": "big/great",
    "vežan": "small",
    "kelme": "cold",
    "lembe": "warm",
    "kal": "fish",
    "ovto": "bear",
    "verhaz": "wolf",
    "pize": "holy/green",
    "kuz": "spruce",
    "kilej": "birch",
    "poy": "aspen",
}

_ERZYA_MARKERS = {"ley", "lej", "vir", "pando", "kudo", "vele", "osh", "latko"}


class ErzyaModule(BaseLanguageModule):
    """Language module for Erzya (эрзянь кель) toponyms."""

    language_code = "myv"
    language_name = "Erzya"
    family = "Uralic"
    branch = "Mordvinic"
    period = "Modern Erzya (1500–present)"
    script = "Latn"

    suffixes = list(_GENERIC_ELEMENTS.keys())
    prefixes = list(_MODIFIER_ELEMENTS.keys())

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        best_gen = ""
        best_meaning = ""
        for el, meaning in sorted(_GENERIC_ELEMENTS.items(), key=lambda x: -len(x[0])):
            if fl.endswith(el) and len(fl) > len(el):
                best_gen = el
                best_meaning = meaning
                break

        if best_gen:
            mod = form[: len(form) - len(best_gen)]
            gen = form[len(form) - len(best_gen) :]
            results.append(
                SegmentationResult(
                    component=mod, position=0, morph_type="compound_modifier", confidence=0.6
                )
            )
            results.append(
                SegmentationResult(
                    component=gen,
                    position=1,
                    morph_type="compound_head",
                    lemma=best_gen,
                    meaning=best_meaning,
                    confidence=0.7,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form, position=0, morph_type="stem", lemma=fl, confidence=0.3
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        fl = form.lower()
        score = 0.0
        evidence: list[str] = []

        for el in _GENERIC_ELEMENTS:
            if fl.endswith(el):
                score += 0.35
                evidence.append(f"Erzya generic -{el}")
                if el in _ERZYA_MARKERS:
                    score += 0.15
                    evidence.append(f"Distinctly Mordvinic/Erzya element -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Erzya modifier {mod}-")
                break

        # Erzya palatalisation markers in Latin transcription
        if any(seq in fl for seq in ("lj", "nj", "rj", "tj")):
            score += 0.1
            evidence.append("Palatalised consonant (Erzya phonology)")

        return LanguageClassification(
            language_code=self.language_code, confidence=min(score, 1.0), evidence=evidence
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            cl = comp.component.lower()
            if cl in _GENERIC_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_GENERIC_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.8,
                        cognates=["Moksha " + cl],
                        sources=["Tsygankin 2005"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Tsygankin 2005"],
                    )
                )
        return candidates
