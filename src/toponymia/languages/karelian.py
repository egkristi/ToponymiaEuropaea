"""Karelian (karjala) language module for toponymic analysis.

Karelian is a Uralic/Finnic language spoken in the Republic of Karelia
(Russia) and parts of eastern Finland. Close to Finnish but a separate
language with distinct phonological features (e.g. voiced stops, lack of
certain vowel-harmony patterns found in standard Finnish).

Toponymic hallmarks:
- Compound structure: modifier + landscape generic (järvi, joki, lambi)
- Habitative -la suffix (shared with Finnish)
- Voiced plosives b, d, g in positions where Finnish has p, t, k
- Sibilant ś (palatalised s) in some dialects

Key reference: Nissilä 1975 "Suomen Karjalan nimistö"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "järvi": "lake",
    "joki": "river",
    "lambi": "pond",
    "koski": "rapids",
    "lahti": "bay",
    "salmi": "strait",
    "suo": "swamp",
    "mägi": "hill",
    "vuara": "fell/mountain",
    "niemi": "cape",
    "selgy": "open water/ridge",
    "saari": "island",
    "randu": "shore",
    "oja": "ditch/brook",
    "korbi": "deep forest",
    "kangas": "heath",
    "peldo": "field",
    "kylä": "village",
    "linnu": "fortress",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "musta": "black",
    "valgei": "white",
    "ruskei": "brown/red",
    "sini": "blue",
    "suuri": "big",
    "pieni": "small",
    "pitkä": "long",
    "pohjois": "north",
    "etelä": "south",
    "ylä": "upper",
    "ala": "lower",
    "kondie": "bear",
    "hukka": "wolf",
    "kuuzi": "spruce",
    "koivu": "birch",
    "pedäi": "pine",
    "pyhä": "holy",
}

_KARELIAN_MARKERS = {"lambi", "vuara", "selgy", "randu", "korbi", "peldo"}


class KarelianModule(BaseLanguageModule):
    """Language module for Karelian (karjala) toponyms."""

    language_code = "krl"
    language_name = "Karelian"
    family = "Uralic"
    branch = "Finnic"
    period = "Modern Karelian (1500–present)"
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
        elif fl.endswith("la") and len(fl) > 3:
            results.append(
                SegmentationResult(
                    component=form[:-2], position=0, morph_type="stem", confidence=0.5
                )
            )
            results.append(
                SegmentationResult(
                    component=form[-2:],
                    position=1,
                    morph_type="suffix",
                    lemma="la",
                    meaning="place of / habitation",
                    confidence=0.6,
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
                evidence.append(f"Karelian/Finnic generic -{el}")
                if el in _KARELIAN_MARKERS:
                    score += 0.15
                    evidence.append(f"Distinctly Karelian form -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Karelian modifier {mod}-")
                break

        # Voiced plosives where Finnish has voiceless
        if any(c in fl for c in ("b", "d", "g")):
            score += 0.1
            evidence.append("Voiced plosive (Karelian phonology)")

        if fl.endswith("la") and len(fl) > 3:
            score += 0.1
            evidence.append("-la habitative suffix")

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
                        cognates=[f"Finnish {cl}"],
                        sources=["Nissilä 1975"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        cognates=[f"Finnish {cl}"],
                        sources=["Nissilä 1975"],
                    )
                )
            elif cl in ("la", "lä"):
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning="place of / habitation",
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=["Finnish -la", "Veps -l"],
                        sources=["Nissilä 1975"],
                    )
                )
        return candidates
