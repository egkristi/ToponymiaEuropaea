"""Messapian language module for toponymic analysis.

Messapian (cms) is an IE language (related to Illyrian?) spoken in SE Italy/Apulia
(6th–2nd c. BCE). ~600 inscriptions in Greek-derived alphabet.
Important substrate in Puglia/Salento place-names.

Toponymic hallmarks:
- Suffixes: -entum/-untum (place), -uba (settlement?), -ias
- Brundisium (Brindisi), Taras (Taranto), Hydruntum (Otranto)
- Non-Latin substrate in modern Apulian toponymy
- Possible Illyrian connection (cross-Adriatic migration?)

Key references: De Simone 1964 "Die messapischen Inschriften",
Marchesini 2009 "Le lingue frammentarie dell'Italia antica"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "entum": "place / settlement",
    "untum": "place / settlement",
    "uba": "settlement?",
    "ias": "adjectival / ethnic",
    "enna": "place suffix",
    "etia": "territory",
    "orium": "place suffix",
    "isium": "settlement",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "brundisium": ("brundisium", "Brundisium (Brindisi, < *brenta 'deer'?)"),
    "taras": ("taras", "Taras (Taranto)"),
    "hydruntum": ("hydruntum", "Hydruntum (Otranto, < *udra 'water')"),
    "lupiae": ("lupiae", "Lupiae (Lecce)"),
    "gnathia": ("gnathia", "Gnathia / Egnazia"),
    "uria": ("uria", "Uria (Oria)"),
    "caelia": ("caelia", "Caelia (Ceglie)"),
    "manduria": ("manduria", "Manduria (< *mand- ?)"),
    "rudiae": ("rudiae", "Rudiae (birthplace of Ennius)"),
    "basta": ("basta", "Basta (Vaste)"),
    "uzentum": ("uzentum", "Uzentum (Ugento)"),
    "aletium": ("aletium", "Aletium (Alezio)"),
}

_PHONOLOGICAL_MARKERS = {"θ", "ht", "gn"}


class MessapianModule(BaseLanguageModule):
    """Language module for Messapian (cms) toponyms."""

    language_code = "cms"
    language_name = "Messapian"
    family = "Indo-European"
    branch = "Uncertain (Illyrian-related?)"
    period = "6th–2nd c. BCE"
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
                    confidence=0.75,
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
            evidence.append(f"Known Messapian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Messapian suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.1
                evidence.append(f"Messapian phonological marker '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="messapian" if score > 0.4 else None,
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
                        confidence=0.65,
                        cognates=[],
                        sound_changes=[],
                        sources=["De Simone 1964", "Marchesini 2009"],
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
                        sources=["De Simone 1964"],
                    )
                )
        return candidates
