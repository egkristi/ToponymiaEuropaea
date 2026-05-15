"""Veps (vepsän kel') language module for toponymic analysis.

Veps is a Uralic/Finnic language spoken by a small community between
Lakes Onega and Ladoga in NW Russia. Endangered (<6 000 speakers).
Important for understanding Finnic substrate in the region.

Toponymic hallmarks:
- Shortened generic forms: -järv (lake), -jog (river), -mäg (hill)
- Loss of final vowels compared to Finnish/Karelian
- Rich landscape vocabulary reflecting taiga/lakeland environment
- Voiced stops and consonant clusters

Key reference: Mullonen 2002 "Toponimija Prisvir'ja"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "järv": "lake",
    "jog": "river",
    "mäg": "hill",
    "kond": "forest",
    "sur": "big",
    "org": "ravine/valley",
    "neem": "cape",
    "rand": "shore",
    "sar": "island",
    "lam": "pond",
    "oja": "ditch/brook",
    "kosk": "rapids",
    "laht": "bay",
    "salm": "strait",
    "pelд": "field",
    "sel'g": "ridge",
    "küla": "village",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "must": "black",
    "val'l'": "white",
    "rusk": "red/brown",
    "sur'": "big",
    "peń": "small",
    "pit'k": "long",
    "korge": "high",
    "ala": "lower",
    "ülä": "upper",
    "kondi": "bear",
    "händikas": "wolf",
    "kuz'": "spruce",
    "koiv": "birch",
    "pedai": "pine",
    "püha": "holy",
    "kivi": "stone",
}

_VEPS_MARKERS = {"järv", "jog", "mäg", "neem", "sel'g", "lam"}


class VepsModule(BaseLanguageModule):
    """Language module for Veps (vepsän kel') toponyms."""

    language_code = "vep"
    language_name = "Veps"
    family = "Uralic"
    branch = "Finnic"
    period = "Modern Veps (1500–present)"
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
                evidence.append(f"Veps generic -{el}")
                if el in _VEPS_MARKERS:
                    score += 0.15
                    evidence.append(f"Characteristically Veps truncated form -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Veps modifier {mod}-")
                break

        # Final vowel loss (distinguishes Veps from Finnish/Karelian)
        if fl[-1:] in ("v", "g", "k", "d", "m", "n", "l") and not fl.endswith(("en", "an")):
            score += 0.1
            evidence.append("Final consonant (Veps apocope)")

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
                        cognates=[f"Finnish {cl}i"],
                        sources=["Mullonen 2002"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Mullonen 2002"],
                    )
                )
        return candidates
