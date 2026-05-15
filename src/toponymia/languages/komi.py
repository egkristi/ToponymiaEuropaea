"""Komi (коми кыв) language module for toponymic analysis.

Komi is a Uralic/Permic language spoken in the Komi Republic in NE
European Russia (~160 000 speakers). Capital: Syktyvkar. Important for
understanding Finno-Ugric substrate across NE Europe.

Toponymic hallmarks:
- Suffixes: -din (mouth/confluence), -kar (fortress/town), -va (water), -yu (river)
- -va 'water' widely distributed (cf. Moscow < Finno-Ugric *mosk-va?)
- Compound structure with landscape generics
- Shared Permic features with Udmurt

Key reference: Turkin 1986 "Komi toponimija"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "din": "mouth/confluence",
    "kar": "fortress/town",
    "va": "water",
    "yu": "river",
    "ty": "lake",
    "shor": "brook/stream",
    "nür": "swamp/marsh",
    "parma": "dense forest/ridge",
    "yag": "pine forest",
    "ras": "deciduous forest",
    "nol'": "cape/headland",
    "jyl": "top/upper",
    "dor": "edge/shore",
    "grézd": "village (Russian loan adaptation)",
    "vyv": "upper part",
    "ul": "lower part",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "sjöd": "black",
    "ydžyd": "big",
    "ičöt": "small",
    "kuz'": "long",
    "dzhudža": "high",
    "ulys": "lower",
    "vylys": "upper",
    "osh": "bear",
    "kötš": "wolf",
    "koz": "spruce",
    "kydzh": "birch",
    "pöžöm": "pine",
    "iz": "stone",
    "vež": "holy/green",
    "edjyd": "white",
    "gerd": "red",
}

_KOMI_MARKERS = {"din", "va", "yu", "shor", "parma", "yag", "nol'"}


class KomiModule(BaseLanguageModule):
    """Language module for Komi (коми кыв) toponyms."""

    language_code = "kpv"
    language_name = "Komi"
    family = "Uralic"
    branch = "Permic"
    period = "Modern Komi (1500–present)"
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
        elif fl.endswith("va") and len(fl) > 3:
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
                    lemma="va",
                    meaning="water",
                    confidence=0.75,
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
                evidence.append(f"Komi generic -{el}")
                if el in _KOMI_MARKERS:
                    score += 0.15
                    evidence.append(f"Distinctly Komi/Permic element -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Komi modifier {mod}-")
                break

        # Komi-specific graphemes in Latin transcription
        if any(c in fl for c in ("ö", "ž", "š", "č", "dž")):
            score += 0.1
            evidence.append("Komi phonology (ö/ž/š/č)")

        # -va ending is especially characteristic
        if fl.endswith("va") and len(fl) > 3:
            score += 0.1
            evidence.append("-va 'water' suffix (widely Permic/Komi)")

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
                        cognates=["Udmurt " + cl] if cl in ("kar", "ty") else [],
                        sound_changes=["PFU *wete > Komi va"] if cl == "va" else [],
                        sources=["Turkin 1986"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Turkin 1986"],
                    )
                )
        return candidates
