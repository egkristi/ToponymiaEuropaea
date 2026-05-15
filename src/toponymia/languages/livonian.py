"""Livonian (līvõ kēļ) language module for toponymic analysis.

Livonian is a Uralic/Finnic language historically spoken on the coast of
Courland (Kurzeme) in Latvia. Critically endangered (<10 native speakers).
Important as a Finnic substrate in Latvian coastal place-names.

Toponymic hallmarks:
- Suffixes: -rõnda (shore), -jõg (river), -mō (land)
- Loss of final syllables (more extreme than Veps)
- Latvian-influenced orthography (ā, ē, ī, ō, ū, ȭ, ǭ)
- Stød-like broken tone marking (ˀ) in some transcriptions

Key reference: Vääri 1966 "Livische Ortsnamen"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "rõnda": "shore/coast",
    "jõg": "river",
    "mō": "land/country",
    "jōra": "lake",
    "nīem": "cape/peninsula",
    "sōr": "island",
    "kil": "village",
    "kānga": "heath",
    "mäg": "hill",
    "rand": "beach/shore",
    "loul": "town/settlement",
    "jālga": "foot (of hill)",
    "pǟ": "head/end",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "mustā": "black",
    "vālda": "white",
    "sūr": "big",
    "piški": "small",
    "pitkā": "long",
    "īlma": "upper/sky",
    "alā": "lower",
    "pūoj": "tree",
    "akkā": "old woman",
    "kiv": "stone",
    "tūļ": "wind",
    "pǟva": "sun/day",
}

_LIVONIAN_CHARS = {"õ", "ō", "ȭ", "ǭ"}


class LivonianModule(BaseLanguageModule):
    """Language module for Livonian (līvõ kēļ) toponyms."""

    language_code = "liv"
    language_name = "Livonian"
    family = "Uralic"
    branch = "Finnic"
    period = "Modern Livonian (1500–present)"
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
                score += 0.4
                evidence.append(f"Livonian generic -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Livonian modifier {mod}-")
                break

        if any(c in fl for c in _LIVONIAN_CHARS):
            score += 0.2
            evidence.append("Livonian-specific orthography (õ/ō/ȭ/ǭ)")

        if any(v in fl for v in ("ā", "ē", "ī", "ū")):
            score += 0.1
            evidence.append("Long vowel macrons (Livonian/Latvian orthography)")

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
                        cognates=["Finnish " + cl, "Estonian " + cl],
                        sources=["Vääri 1966"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Vääri 1966"],
                    )
                )
        return candidates
