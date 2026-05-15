"""Crimean Tatar (qırımtatar tili) language module for toponymic analysis.

Crimean Tatar is a Turkic language (Kipchak–Oghuz mixed) spoken in Crimea
and the diaspora (~500 000 speakers). Rich Crimean toponymy: Bakhchysarai,
Simferopol, Aqmescit.

Toponymic hallmarks:
- Suffixes: -köy (village), -dağ (mountain), -su (water), -saray (palace)
- Three dialect groups: southern (Oghuz), central (mixed), northern (Kipchak)
- Arabic/Persian overlay on Turkic base in settlement names
- Distinctive vowel system with front/back harmony

Key reference: Bushakov 2003 "Leksyčnyj sklad istoryčnoï toponimiji Krymu"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "köy": "village",
    "dağ": "mountain",
    "su": "water/river",
    "saray": "palace",
    "tepe": "hill",
    "göl": "lake",
    "dere": "valley/stream",
    "çeşme": "spring/fountain",
    "orman": "forest",
    "qale": "fortress",
    "bağça": "garden",
    "yol": "road",
    "köprü": "bridge",
    "liman": "harbour",
    "burun": "cape/nose",
    "boğaz": "strait/pass",
    "ova": "plain",
    "ada": "island",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "qara": "black",
    "aq": "white",
    "qızıl": "red",
    "kök": "blue/green",
    "büyük": "big",
    "küçük": "small",
    "uzun": "long",
    "yüksek": "high",
    "aşağı": "lower",
    "yuqarı": "upper",
    "eski": "old",
    "yañı": "new",
    "taş": "stone",
    "demir": "iron",
    "altın": "gold",
    "balta": "axe",
}

_CRH_MARKERS = {"qara", "aq", "qale", "bağça", "qızıl", "yañı", "yuqarı"}


class CrimeanTatarModule(BaseLanguageModule):
    """Language module for Crimean Tatar (qırımtatar tili) toponyms."""

    language_code = "crh"
    language_name = "Crimean Tatar"
    family = "Turkic"
    branch = "Kipchak–Oghuz"
    period = "Modern Crimean Tatar (1500–present)"
    script = "Latn"

    suffixes = list(_GENERIC_ELEMENTS.keys())
    prefixes = list(_MODIFIER_ELEMENTS.keys())

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        # Hyphenated forms
        if "-" in form:
            parts = form.split("-", 1)
            results.append(
                SegmentationResult(
                    component=parts[0], position=0, morph_type="compound_modifier", confidence=0.6
                )
            )
            lo = parts[1].lower()
            meaning = _GENERIC_ELEMENTS.get(lo)
            results.append(
                SegmentationResult(
                    component=parts[1],
                    position=1,
                    morph_type="compound_head",
                    lemma=lo if meaning else None,
                    meaning=meaning,
                    confidence=0.7 if meaning else 0.4,
                )
            )
            return results

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
            # Check for Turkic modifier-first pattern (e.g. Aq + mescit)
            for mod, mod_meaning in sorted(_MODIFIER_ELEMENTS.items(), key=lambda x: -len(x[0])):
                if fl.startswith(mod) and len(fl) > len(mod):
                    results.append(
                        SegmentationResult(
                            component=form[: len(mod)],
                            position=0,
                            morph_type="compound_modifier",
                            lemma=mod,
                            meaning=mod_meaning,
                            confidence=0.6,
                        )
                    )
                    results.append(
                        SegmentationResult(
                            component=form[len(mod) :],
                            position=1,
                            morph_type="compound_head",
                            confidence=0.4,
                        )
                    )
                    return results
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
            if fl.endswith(el) or ("-" in fl and fl.split("-")[-1] == el):
                score += 0.35
                evidence.append(f"Crimean Tatar generic -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Crimean Tatar modifier {mod}-")
                if mod in _CRH_MARKERS:
                    score += 0.1
                    evidence.append(f"Distinctly Crimean Tatar form {mod}")
                break

        # Crimean Tatar uses q where Turkish uses k
        if "q" in fl:
            score += 0.15
            evidence.append("Crimean Tatar q- (vs. Turkish k-)")

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
                        cognates=["Turkish " + cl],
                        sources=["Bushakov 2003"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        cognates=["Turkish " + cl.replace("q", "k")],
                        sound_changes=["Common Turkic *k > CrTat q (before back vowels)"]
                        if "q" in cl
                        else [],
                        sources=["Bushakov 2003"],
                    )
                )
        return candidates
