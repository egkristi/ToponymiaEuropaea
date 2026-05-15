"""Udmurt (удмурт кыл) language module for toponymic analysis.

Udmurt is a Uralic/Permic language spoken in the Udmurt Republic on the
Kama river, Russia (~340 000 speakers). Permic branch with Komi.
Substrate in the Kama river region and surrounding areas.

Toponymic hallmarks:
- Suffixes: -kar (fortress/town), -gurt (village), -šur (river/stream)
- Compound names with landscape generics
- Rich hydronymic vocabulary: šur (river), ty (lake), vu (water)
- Shared Permic features with Komi

Key reference: Atamanov 1988 "Udmurtskaja onomastika"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "kar": "fortress/town",
    "gurt": "village/settlement",
    "šur": "river/stream",
    "ty": "lake",
    "vu": "water",
    "nür": "swamp/marsh",
    "gop": "lowland/hollow",
    "muvyr": "hill",
    "jag": "pine forest",
    "nüles": "forest",
    "lud": "field/meadow",
    "dor": "edge/shore",
    "šaj": "cemetery/ancient site",
    "vožo": "sacred place",
    "bus": "mist/steppe",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "sjöd": "black",
    "tödji": "white",
    "gord": "red",
    "badʒym": "big",
    "pokchi": "small",
    "kuz": "long",
    "džuži": "high",
    "ulys": "lower",
    "vylyś": "upper",
    "gondir": "bear",
    "kion": "wolf",
    "kyz": "spruce",
    "pužym": "pine",
    "kiz": "birch",
    "viz": "holy/blue-green",
    "iz": "stone",
}

_UDMURT_MARKERS = {"gurt", "šur", "kar", "nür", "jag", "nüles", "šaj", "vožo"}


class UdmurtModule(BaseLanguageModule):
    """Language module for Udmurt (удмурт кыл) toponyms."""

    language_code = "udm"
    language_name = "Udmurt"
    family = "Uralic"
    branch = "Permic"
    period = "Modern Udmurt (1500–present)"
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
        elif fl.endswith("gurt") and len(fl) > 5:
            results.append(
                SegmentationResult(
                    component=form[:-4], position=0, morph_type="stem", confidence=0.5
                )
            )
            results.append(
                SegmentationResult(
                    component=form[-4:],
                    position=1,
                    morph_type="suffix",
                    lemma="gurt",
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
                evidence.append(f"Udmurt generic -{el}")
                if el in _UDMURT_MARKERS:
                    score += 0.15
                    evidence.append(f"Distinctly Udmurt/Permic element -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Udmurt modifier {mod}-")
                break

        # Udmurt-specific graphemes in Latin transcription
        if any(c in fl for c in ("š", "ž", "č", "ď", "ź")):
            score += 0.1
            evidence.append("Udmurt sibilant/affricate (š/ž/č)")

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
                        cognates=["Komi " + cl],
                        sources=["Atamanov 1988"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Atamanov 1988"],
                    )
                )
        return candidates
