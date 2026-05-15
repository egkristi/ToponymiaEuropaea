"""Mycenaean Greek language module for toponymic analysis.

Mycenaean Greek (gmy) is the earliest attested form of Greek, written in
Linear B syllabic script (16th–12th c. BCE). Known from palace archives at
Pylos, Knossos, Mycenae, Thebes, and Tiryns.

Toponymic hallmarks:
- Linear B syllabic renderings: pa-ki-ja-ne, pu-ro, ko-no-so
- Pre-Greek substrate layer visible underneath
- Labiovelar preservation (*kʷ > Linear B q-series)
- Archaic case endings and place-name formulae

Key references: Ventris & Chadwick 1973 "Documents in Mycenaean Greek",
Aura Jorro 1985–1993 "Diccionario Micénico"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "jo": "adjectival / ethnic",
    "ja": "adjectival feminine",
    "wo": "locative?",
    "to": "place/agent",
    "so": "nominal ending",
    "no": "nominal ending",
    "ne": "locative/dative?",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "pu-ro": ("pulos", "Pylos (< *pulos 'gate')"),
    "ko-no-so": ("knōsos", "Knossos"),
    "mu-ka-na": ("mukanai", "Mycenae"),
    "te-qa": ("thēbai", "Thebes (labiovelar *kʷ > q)"),
    "ti-ri-to": ("tritons", "Tiryns?"),
    "pa-ki-ja-ne": ("sphagianes", "Sphagianes (sanctuary)"),
    "a-mi-ni-so": ("amnisos", "Amnisos (harbour of Knossos)"),
    "da-wo": ("dawon", "Daulis?"),
    "e-re-ta": ("eretai", "rowers (place of rowers?)"),
    "pa-ra-jo": ("pharaios", "Pharai?"),
    "ku-ta-to": ("kytatos", "?"),
    "ra-wa-ra-ta": ("lawaratas", "people's place?"),
}

_PHONOLOGICAL_MARKERS = {"q", "dw", "nw", "gw"}


class MycenaeanModule(BaseLanguageModule):
    """Language module for Mycenaean Greek (gmy) toponyms."""

    language_code = "gmy"
    language_name = "Mycenaean Greek"
    family = "Indo-European"
    branch = "Hellenic > Mycenaean"
    period = "16th–12th c. BCE"
    script = "Linb"

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
                    confidence=0.75,
                )
            )
            return results

        # Linear B names often hyphenated; split on hyphens
        if "-" in fl:
            parts = form.split("-")
            for i, part in enumerate(parts):
                mtype = "stem" if i == 0 else "suffix"
                pl = part.lower()
                meaning = _SUFFIXES.get(pl)
                results.append(
                    SegmentationResult(
                        component=part,
                        position=i,
                        morph_type=mtype,
                        lemma=pl if meaning else None,
                        meaning=meaning,
                        confidence=0.5,
                    )
                )
            return results

        # Suffix matching for non-hyphenated forms
        for sfx, meaning in sorted(_SUFFIXES.items(), key=lambda x: -len(x[0])):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                stem = form[: len(form) - len(sfx)]
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="stem",
                        confidence=0.4,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(form) - len(sfx) :],
                        position=1,
                        morph_type="suffix",
                        lemma=sfx,
                        meaning=meaning,
                        confidence=0.5,
                    )
                )
                return results

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
            score += 0.75
            evidence.append(f"Known Mycenaean toponym: {fl}")

        # Hyphenated Linear B convention
        if "-" in fl:
            score += 0.3
            evidence.append("Linear B syllabic notation (hyphenated)")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx):
                score += 0.2
                evidence.append(f"Mycenaean suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.15
                evidence.append(f"Mycenaean phonological marker '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="mycenaean" if score > 0.4 else None,
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
                        sources=["Ventris & Chadwick 1973", "Aura Jorro 1985"],
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
                        sources=["Ventris & Chadwick 1973"],
                    )
                )
        return candidates
