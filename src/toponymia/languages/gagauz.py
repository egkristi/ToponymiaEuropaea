"""Gagauz (gagauz dili) language module for toponymic analysis.

Gagauz is a Turkic/Oghuz language spoken by the Gagauz people in Moldova
(Gagauzia ATU) and parts of Ukraine (~150 000 speakers). The Gagauz are
Orthodox Christian Turks — a rare combination that produced a distinctive
Balkan Turkic toponymic layer.

Toponymic hallmarks:
- Suffixes: -köy (village), -tepe (hill), -su (water), -bair (hill)
- Oghuz Turkic vocabulary close to Turkish
- Slavic/Romanian loanwords in place-names
- Latin script (since 1996; Cyrillic before)

Key reference: Gagauz Yeri toponimleri (1998)
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
    "tepe": "hill/mound",
    "su": "water/river",
    "bair": "hill/slope",
    "göl": "lake",
    "dere": "valley/stream",
    "çeşme": "spring/fountain",
    "orman": "forest",
    "tarla": "field",
    "yol": "road",
    "köprü": "bridge",
    "saray": "palace",
    "kale": "fortress",
    "bağ": "vineyard",
    "ada": "island",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "kara": "black",
    "ak": "white",
    "kızıl": "red",
    "büük": "big",
    "küçük": "small",
    "uzun": "long",
    "üüsek": "high",
    "aşaa": "lower",
    "yukaru": "upper",
    "ayı": "bear",
    "kurt": "wolf",
    "taş": "stone",
    "demir": "iron",
    "altın": "gold",
    "eni": "new",
    "eski": "old",
}

_GAGAUZ_MARKERS = {"bair", "büük", "üüsek", "aşaa"}


class GagauzModule(BaseLanguageModule):
    """Language module for Gagauz (gagauz dili) toponyms."""

    language_code = "gag"
    language_name = "Gagauz"
    family = "Turkic"
    branch = "Oghuz"
    period = "Modern Gagauz (1500–present)"
    script = "Latn"

    suffixes = list(_GENERIC_ELEMENTS.keys())
    prefixes = list(_MODIFIER_ELEMENTS.keys())

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        # Turkic names often have modifier-first structure
        # Check for hyphenated forms first
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
                evidence.append(f"Turkic/Gagauz generic -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Gagauz modifier {mod}-")
                break

        if any(w in fl for w in _GAGAUZ_MARKERS):
            score += 0.15
            evidence.append("Gagauz-specific form (distinct from Turkish)")

        # Gagauz/Turkic vowel harmony
        if any(c in fl for c in ("ö", "ü")):
            score += 0.05
            evidence.append("Turkic front rounded vowels")

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
                        sources=["Gagauz Yeri toponimleri 1998"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        cognates=["Turkish " + cl],
                        sources=["Gagauz Yeri toponimleri 1998"],
                    )
                )
        return candidates
