"""Phrygian language module for toponymic analysis.

Phrygian (xpg) is an IE language (closest to Greek?) spoken in W/C Anatolia
(8th c. BCE – 5th c. CE). Two phases: Old Phrygian (~8th-4th c. BCE, in
Phrygian alphabet) and Neo-Phrygian (1st-3rd c. CE, in Greek alphabet).

Toponymic hallmarks:
- Suffixes: -ssos (pre-Phrygian substrate), -ion, -anon
- Gordion, Midas City (Yazılıkaya), Pessinus, Dorylaion
- Important Anatolian layer between Hittite period and Hellenistic
- Connection to Thracian/Balkan substrate (Brygian = Phrygian?)

Key references: Brixhe & Lejeune 1984 "Corpus des inscriptions paléo-phrygiennes",
Obrador-Cursach 2020 "The Phrygian Language"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "ssos": "pre-Phrygian substrate (< Anatolian)",
    "ion": "place / settlement",
    "anon": "place / settlement",
    "ssa": "place (Anatolian substrate)",
    "aion": "territory / place",
    "inon": "place suffix",
    "oussa": "place suffix (Greek?)",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "gordion": ("gordion", "Gordion (capital, < king Gordias)"),
    "pessinus": ("pessinus", "Pessinus (cult of Cybele)"),
    "dorylaion": ("dorylaion", "Dorylaion (Eskişehir, 'spear-place'?)"),
    "midaion": ("midaion", "Midaion (< king Midas)"),
    "kelainai": ("kelainai", "Kelainai (Dinar, 'dark place')"),
    "ankyra": ("ankyra", "Ankyra (Ankara, 'anchor'? or Phrygian)"),
    "amorion": ("amorion", "Amorion (Amorium)"),
    "kotiaion": ("kotiaion", "Kotiaion (Kütahya)"),
    "nakoleia": ("nakoleia", "Nakoleia (Seyitgazi area)"),
    "synnada": ("synnada", "Synnada (Şuhut area)"),
    "laodikeia": ("laodikeia", "Laodikeia (Hellenistic rename)"),
}

_PHONOLOGICAL_MARKERS = {"ks", "gd", "pt"}


class PhrygianModule(BaseLanguageModule):
    """Language module for Phrygian (xpg) toponyms."""

    language_code = "xpg"
    language_name = "Phrygian"
    family = "Indo-European"
    branch = "Graeco-Phrygian? (closest to Greek)"
    period = "8th c. BCE – 5th c. CE"
    script = "Grek"

    suffixes = list(_SUFFIXES.keys())
    prefixes: list[str] = []

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        if fl in _KNOWN_ELEMENTS:
            lemma, meaning = _KNOWN_ELEMENTS[fl]
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=lemma,
                    meaning=meaning,
                    confidence=0.8,
                )
            )
            return results

        matched_suffix = ""
        matched_meaning = ""
        for sfx, meaning in sorted(_SUFFIXES.items(), key=lambda x: -len(x[0])):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                matched_suffix = sfx
                matched_meaning = meaning
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            sfx_part = form[len(form) - len(matched_suffix) :]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=sfx_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=matched_meaning,
                    confidence=0.6,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        fl = form.lower()
        score = 0.0
        evidence: list[str] = []

        if fl in _KNOWN_ELEMENTS:
            score += 0.7
            evidence.append(f"Known Phrygian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Phrygian suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.1
                evidence.append(f"Phrygian phonological cluster '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="phrygian" if score > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            cl = comp.component.lower()
            if cl in _KNOWN_ELEMENTS:
                lemma, meaning = _KNOWN_ELEMENTS[cl]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=[],
                        sound_changes=[],
                        sources=["Brixhe & Lejeune 1984", "Obrador-Cursach 2020"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.55,
                        cognates=[],
                        sources=["Obrador-Cursach 2020"],
                    )
                )
        return candidates
