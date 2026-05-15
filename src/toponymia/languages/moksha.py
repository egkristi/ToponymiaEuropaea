"""Moksha (мокшень кяль) language module for toponymic analysis.

Moksha is a Uralic/Mordvinic language spoken in the western part of the
Republic of Mordovia, Russia (~250 000 speakers). Sister language to Erzya.
The Moksha river name is the ethnonym of the language itself.

Toponymic hallmarks:
- Suffixes: -ley (river), -vir (forest), -nar (field)
- Reduced vowels in unstressed syllables (unlike Erzya)
- Distinctive consonant clusters: шт, нд, лт
- Moksha-specific vocabulary diverging from Erzya

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
    "vir": "forest",
    "nar": "field/steppe",
    "panda": "hill/slope",
    "luga": "meadow",
    "kud": "house/settlement",
    "osh": "town/fortress",
    "ved": "water",
    "latka": "ravine/hollow",
    "vel": "village",
    "shi": "river (archaic)",
    "buf": "place",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "ravzha": "black (of water)",
    "aksha": "white",
    "yakstere": "red",
    "poksh": "big",
    "ёmla": "small",
    "kelma": "cold",
    "lemda": "warm",
    "kal": "fish",
    "ofta": "bear",
    "virgas": "wolf",
    "kuz": "spruce",
    "kelу": "birch",
    "poi": "aspen",
    "pizemja": "holy/green",
    "kev": "stone",
}

_MOKSHA_MARKERS = {"nar", "panda", "kud", "latka", "shi", "poksh"}


class MokshaModule(BaseLanguageModule):
    """Language module for Moksha (мокшень кяль) toponyms."""

    language_code = "mdf"
    language_name = "Moksha"
    family = "Uralic"
    branch = "Mordvinic"
    period = "Modern Moksha (1500–present)"
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
                evidence.append(f"Moksha generic -{el}")
                if el in _MOKSHA_MARKERS:
                    score += 0.15
                    evidence.append(f"Distinctly Moksha element -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Moksha modifier {mod}-")
                break

        # Moksha reduced vowels / consonant clusters
        if any(seq in fl for seq in ("sht", "nd", "lt", "rk")):
            score += 0.1
            evidence.append("Moksha consonant cluster")

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
                        cognates=["Erzya " + cl],
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
