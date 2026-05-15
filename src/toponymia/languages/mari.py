"""Mari (марий йылме) language module for toponymic analysis.

Mari is a Uralic language spoken in the Mari El republic on the middle
Volga, Russia (~350 000 speakers). Called "Cheremis" in older literature.
Important substrate layer in the Volga–Kama region.

Toponymic hallmarks:
- Suffixes: -er (lake), -enger (river/stream), -ola (village/settlement)
- Compound place names with landscape generics
- Vowel ö and ü from Uralic heritage
- Turkic (Chuvash/Tatar) loanwords in toponymy

Key reference: Galkin 1991 "Marijskaja toponimika"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "er": "lake",
    "enger": "river/stream",
    "ola": "village/settlement",
    "korem": "ravine",
    "kuruk": "hill/mountain",
    "oto": "grove/sacred grove",
    "nur": "field",
    "pamash": "spring/source",
    "iksa": "bay/backwater",
    "vüd": "water",
    "shüdö": "swamp",
    "kuп": "long (meadow)",
    "lап": "lowland/plain",
    "mardezh": "wind (in names)",
    "sürem": "river (archaic)",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "sheme": "black",
    "osh": "white",
    "yoshkar": "red",
    "kugu": "big",
    "izhi": "small",
    "kuzhe": "long",
    "kükshö": "high",
    "ülyl": "upper",
    "ülнö": "lower",
    "maske": "bear",
    "pire": "wolf",
    "kuze": "spruce",
    "kuе": "birch",
    "pünchö": "pine",
    "kü": "stone",
}

_MARI_MARKERS = {"enger", "ola", "korem", "kuruk", "pamash", "oto", "iksa"}


class MariModule(BaseLanguageModule):
    """Language module for Mari (марий йылме) toponyms."""

    language_code = "mhr"
    language_name = "Mari"
    family = "Uralic"
    branch = "Mari"
    period = "Modern Mari (1500–present)"
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
        elif fl.endswith("ola") and len(fl) > 4:
            results.append(
                SegmentationResult(
                    component=form[:-3], position=0, morph_type="stem", confidence=0.5
                )
            )
            results.append(
                SegmentationResult(
                    component=form[-3:],
                    position=1,
                    morph_type="suffix",
                    lemma="ola",
                    meaning="village/settlement",
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
                evidence.append(f"Mari generic -{el}")
                if el in _MARI_MARKERS:
                    score += 0.15
                    evidence.append(f"Distinctly Mari element -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Mari modifier {mod}-")
                break

        if any(v in fl for v in ("ö", "ü")):
            score += 0.1
            evidence.append("Uralic vowel ö/ü")

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
                        sources=["Galkin 1991"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Galkin 1991"],
                    )
                )
        return candidates
