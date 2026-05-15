"""Chuvash (чӑваш чӗлхи) language module for toponymic analysis.

Chuvash is the only surviving member of the Oghur branch of Turkic,
descended from Volga Bulgar. Spoken in the Chuvash Republic on the
middle Volga, Russia (~1 million speakers). Unique r-Turkic / l-Turkic:
where Common Turkic has z, Chuvash has r; where CT has ş, Chuvash has l.

Toponymic hallmarks:
- Suffixes: -kassi (village/hamlet), -šur (river), -çyrma (ravine/stream)
- r/l-Turkic correspondences (e.g. CT *köz "eye" > Chuvash *kur)
- Vowel reduction in unstressed syllables
- Distinctive letter ӑ (reduced a) and ӗ (reduced e)

Key reference: Kornilov 1986 "Toponimija Chuvashii"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "kassi": "village/hamlet",
    "šur": "river/stream",
    "çyrma": "ravine/stream",
    "tu": "mountain/hill",
    "kül": "lake",
    "šyv": "water",
    "vărman": "forest",
    "uj": "field/steppe",
    "çul": "stone",
    "hula": "town/city",
    "yal": "village (larger)",
    "çăl": "spring/source",
    "sara": "swamp",
    "varri": "ravine",
    "pus": "head/source",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "hura": "black",
    "šură": "white",
    "hĕrlĕ": "red",
    "măn": "big",
    "pĕçĕk": "small",
    "vărăm": "long",
    "çüllĕ": "high",
    "anатри": "lower",
    "çĕлĕке": "upper",
    "upa": "bear",
    "kaškar": "wolf",
    "çul": "stone",
    "timĕr": "iron",
    "ылтăн": "gold",
    "çĕнĕ": "new",
    "кивĕ": "old",
}

_CHUVASH_MARKERS = {"kassi", "çyrma", "šyv", "vărman", "çăl", "hura", "šură"}


class ChuvashModule(BaseLanguageModule):
    """Language module for Chuvash (чӑваш чӗлхи) toponyms."""

    language_code = "chv"
    language_name = "Chuvash"
    family = "Turkic"
    branch = "Oghur (r-Turkic / Volga Bulgar)"
    period = "Modern Chuvash (1500–present)"
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
        elif fl.endswith("kassi") and len(fl) > 6:
            results.append(
                SegmentationResult(
                    component=form[:-5], position=0, morph_type="stem", confidence=0.5
                )
            )
            results.append(
                SegmentationResult(
                    component=form[-5:],
                    position=1,
                    morph_type="suffix",
                    lemma="kassi",
                    meaning="village/hamlet",
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
                evidence.append(f"Chuvash generic -{el}")
                if el in _CHUVASH_MARKERS:
                    score += 0.15
                    evidence.append(f"Distinctly Chuvash/Oghur element -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Chuvash modifier {mod}-")
                break

        # Chuvash reduced vowels ă/ĕ
        if "ă" in fl or "ĕ" in fl:
            score += 0.15
            evidence.append("Chuvash reduced vowels (ă/ĕ)")

        # ç is distinctive for Chuvash
        if "ç" in fl:
            score += 0.1
            evidence.append("Chuvash ç consonant")

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
                        sound_changes=[
                            "Common Turkic *z > Chuvash r",
                            "Common Turkic *ş > Chuvash l",
                        ],
                        sources=["Kornilov 1986"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Kornilov 1986"],
                    )
                )
        return candidates
