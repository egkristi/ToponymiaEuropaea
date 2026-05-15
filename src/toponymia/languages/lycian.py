"""Lycian language module for toponymic analysis.

Lycian (xlc) is an Anatolian/IE language spoken in SW Turkey (5th–3rd c. BCE).
Better attested than Lydian (~200 inscriptions), with its own alphabet derived
from Greek. Known from Xanthos, Letoon, and other Lycian sites.

Toponymic hallmarks:
- Suffixes: -ñni (locative?), -aza (place), -da (locative)
- Xanthos (Arñna in Lycian), Tlōs, Pinara, Patara
- Lycian A (main) and Lycian B (Milyan) varieties
- Important for Anatolian historical geography

Key references: Melchert 2004 "A Dictionary of the Lycian Language",
Neumann 2007 "Glossar des Lykischen"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "nni": "locative / belonging to",
    "aza": "place suffix",
    "da": "locative",
    "ñni": "locative / adjectival",
    "zza": "place suffix",
    "aha": "possessive / place",
    "esi": "ethnic / people of",
    "ije": "adjectival",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "xanthos": ("arñna", "Xanthos (= Arñna in Lycian)"),
    "arnna": ("arñna", "Arñna (= Xanthos)"),
    "tlos": ("tlawa", "Tlōs (= Tlawa)"),
    "pinara": ("pinale", "Pinara (= Pinale, 'round')"),
    "patara": ("pttara", "Patara"),
    "limyra": ("zemuri", "Limyra (= Zemuri)"),
    "myra": ("myra", "Myra"),
    "oinoanda": ("wiñbate", "Oinoanda (= Wiñbate?)"),
    "letoon": ("letoon", "Letoon (sanctuary)"),
    "telmessos": ("telebehi", "Telmessos"),
    "kadyanda": ("kadyanda", "Kadyanda"),
    "olympos": ("olympos", "Olympos (Lycia)"),
}

_PHONOLOGICAL_MARKERS = {"ñ", "ẽ", "ã", "θ"}


class LycianModule(BaseLanguageModule):
    """Language module for Lycian (xlc) toponyms."""

    language_code = "xlc"
    language_name = "Lycian"
    family = "Indo-European"
    branch = "Anatolian"
    period = "5th–3rd c. BCE"
    script = "Lyci"

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
                    confidence=0.55,
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
            evidence.append(f"Known Lycian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Lycian suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.15
                evidence.append(f"Lycian phonological marker '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="lycian" if score > 0.4 else None,
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
                        sources=["Melchert 2004", "Neumann 2007"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.5,
                        cognates=[],
                        sources=["Melchert 2004"],
                    )
                )
        return candidates
