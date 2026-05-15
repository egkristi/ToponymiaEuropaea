"""Võro (võro kiil) language module for toponymic analysis.

Võro is a Uralic/Finnic language spoken in SE Estonia (Võrumaa, Setomaa).
Sometimes classified as a South Estonian dialect but retains deep Finnic
archaisms lost in standard Estonian: vowel harmony, the q sound (glottal
stop written as q or ʔ), and archaic vocabulary.

Toponymic hallmarks:
- Suffixes: -maa (land), -järv (lake), -jõgi (river), -mägi (hill)
- Glottal stop in stem-final position (written q): Võroq, Setomaq
- Distinctive vowels: õ, ü

Key reference: Faster & Saar 2020 "Võru kohanimist"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "maa": "land/country",
    "järv": "lake",
    "jõgi": "river",
    "mägi": "hill",
    "oja": "brook/ditch",
    "org": "valley",
    "nulk": "corner/district",
    "külä": "village",
    "liin": "town",
    "saar": "island",
    "niim": "cape",
    "rand": "shore",
    "mõts": "forest",
    "nurm": "field/meadow",
    "suu": "mouth (of river)",
    "põh'a": "north/bottom",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "must": "black",
    "valgõ": "white",
    "verrev": "red",
    "suur": "big",
    "väiku": "small",
    "pikk": "long",
    "korgõ": "high",
    "ala": "lower",
    "üle": "upper/over",
    "kahr": "bear",
    "hunt": "wolf",
    "kuus": "spruce",
    "kõiv": "birch",
    "petäi": "pine",
    "pühä": "holy",
    "kivi": "stone",
    "hõpõ": "silver",
}

_VORO_MARKERS = {"nulk", "mõts", "põh'a", "korgõ", "valgõ", "verrev", "hõpõ"}


class VoroModule(BaseLanguageModule):
    """Language module for Võro (võro kiil) toponyms."""

    language_code = "vro"
    language_name = "Võro"
    family = "Uralic"
    branch = "Finnic (South Estonian)"
    period = "Modern Võro (1500–present)"
    script = "Latn"

    suffixes = list(_GENERIC_ELEMENTS.keys())
    prefixes = list(_MODIFIER_ELEMENTS.keys())

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        # Strip glottal stop marker for matching
        fl_clean = fl.replace("q", "").replace("ʔ", "")

        best_gen = ""
        best_meaning = ""
        for el, meaning in sorted(_GENERIC_ELEMENTS.items(), key=lambda x: -len(x[0])):
            if fl_clean.endswith(el) and len(fl_clean) > len(el):
                best_gen = el
                best_meaning = meaning
                break

        if best_gen:
            cut = len(fl) - len(best_gen)
            if fl.endswith(("q", "ʔ")):
                cut = len(fl) - len(best_gen) - 1
            mod = form[:cut]
            gen = form[cut:]
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
            if fl.endswith(el) or fl.replace("q", "").replace("ʔ", "").endswith(el):
                score += 0.35
                evidence.append(f"Võro/Finnic generic -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Võro modifier {mod}-")
                break

        if "q" in fl or "ʔ" in fl:
            score += 0.2
            evidence.append("Glottal stop marker (q/ʔ) — distinctly Võro")

        if "õ" in fl:
            score += 0.1
            evidence.append("Vowel õ (South Estonian / Võro)")

        if any(w in fl for w in _VORO_MARKERS):
            score += 0.1
            evidence.append("Võro-specific lexical form")

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
                        cognates=["Estonian " + cl, "Finnish " + cl],
                        sources=["Faster & Saar 2020"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Faster & Saar 2020"],
                    )
                )
        return candidates
