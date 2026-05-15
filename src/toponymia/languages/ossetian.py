"""Ossetian (ирон ӕвзаг) language module for toponymic analysis.

Ossetian is a NE Iranian language spoken in North and South Ossetia in
the Caucasus (~600 000 speakers). Descended from Alanic, the language
of the Alans, who were themselves descendants of the Sarmatians and
ultimately the Scythians. Key for understanding Scythian-Sarmatian
toponyms across the Pontic steppe and Caucasus.

Toponymic hallmarks:
- Suffixes: -don (water/river), -ком/kom (gorge/valley), -дон/don
- The famous -don element = 'water/river' (cf. Don, Dnieper, Dniester)
- Two dialects: Iron (eastern) and Digor (western)
- Iranian vocabulary with Caucasian substrate

Key reference: Cagaeva 1971 "Toponimija Severnoj Osetii"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_GENERIC_ELEMENTS: dict[str, str] = {
    "don": "water/river",
    "kom": "gorge/valley",
    "dæn": "water (Digor)",
    "sug": "water (archaic)",
    "cad": "lake",
    "suadæn": "spring/source",
    "byn": "foot/base (of mountain)",
    "dwar": "gate/pass",
    "kʼæj": "stone/slab",
    "fæz": "plain/plateau",
    "xwynkʼ": "hill/mound",
    "kaw": "wall/cliff",
    "midæg": "inner/inside",
    "ræbyn": "edge/slope",
    "mæsyg": "tower",
}

_MODIFIER_ELEMENTS: dict[str, str] = {
    "saw": "black",
    "urs": "white",
    "syrx": "red",
    "styr": "big",
    "gycʼyl": "small",
    "darǧ": "long",
    "bærzond": "high",
    "dællag": "lower",
    "wællag": "upper",
    "ars": "bear",
    "bīræǧ": "wolf",
    "dūr": "stone",
    "æfsæn": "iron",
    "syǧzærīn": "gold",
    "næwæg": "new",
    "zærond": "old",
}

_OSSETIAN_MARKERS = {"don", "kom", "dæn", "fæz", "suadæn", "mæsyg", "dwar"}


class OssetianModule(BaseLanguageModule):
    """Language module for Ossetian (ирон ӕвзаг) toponyms."""

    language_code = "oss"
    language_name = "Ossetian"
    family = "Indo-European"
    branch = "Iranian > NE Iranian (Scythian–Sarmatian–Alanic)"
    period = "Modern Ossetian (1500–present)"
    script = "Latn"

    suffixes = list(_GENERIC_ELEMENTS.keys())
    prefixes = list(_MODIFIER_ELEMENTS.keys())

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        # Hyphenated forms (e.g. Nar-don)
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
        elif fl.endswith("don") and len(fl) > 4:
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
                    lemma="don",
                    meaning="water/river",
                    confidence=0.8,
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
                evidence.append(f"Ossetian generic -{el}")
                if el in _OSSETIAN_MARKERS:
                    score += 0.15
                    evidence.append(f"Distinctly Ossetian/Alanic element -{el}")
                break

        for mod in _MODIFIER_ELEMENTS:
            if fl.startswith(mod):
                score += 0.15
                evidence.append(f"Ossetian modifier {mod}-")
                break

        # -don ending is the most famous Ossetian/Alanic marker
        if fl.endswith("don") and len(fl) > 3:
            score += 0.1
            evidence.append("-don 'water/river' (Scythian-Sarmatian-Alanic)")

        # Ossetian-specific graphemes (æ is diagnostic)
        if "æ" in fl:
            score += 0.15
            evidence.append("Ossetian vowel æ")

        # Ejective consonants in Latin transcription (kʼ, pʼ, tʼ, cʼ)
        if any(ej in fl for ej in ("kʼ", "pʼ", "tʼ", "cʼ")):
            score += 0.1
            evidence.append("Ejective consonant (Caucasian areal feature)")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="alanic-sarmatian" if fl.endswith("don") else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            cl = comp.component.lower()
            if cl in _GENERIC_ELEMENTS:
                cognates = []
                sound_changes = []
                if cl == "don":
                    cognates = ["Avestan dānu- 'river'", "Old Persian danuvatiy", "Scythian *dānu-"]
                    sound_changes = ["PIr *dānu- > Alanic *dān > Ossetian don"]
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_GENERIC_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.85,
                        cognates=cognates,
                        sound_changes=sound_changes,
                        sources=["Cagaeva 1971", "Abaev 1958 IESOJ"],
                    )
                )
            elif cl in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_MODIFIER_ELEMENTS[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        sources=["Cagaeva 1971", "Abaev 1958 IESOJ"],
                    )
                )
        return candidates
