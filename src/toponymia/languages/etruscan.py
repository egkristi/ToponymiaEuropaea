"""Etruscan language module for toponymic analysis.

Etruscan (ett) is a language isolate spoken in pre-Roman Italy (900–100 BCE).
NOT Indo-European. The Etruscan civilisation dominated Etruria (modern Tuscany,
Umbria, Lazio) and left a massive toponymic substrate in central Italy.

Toponymic hallmarks:
- Suffixes: -na, -ni, -enna, -ina, -anu, -arna
- Gentilicial/family suffixes: -na, -ni (from clan names)
- City names: Perusia (Perugia), Arretium (Arezzo), Clevsin (Chiusi),
  Velzna (Orvieto/Volsinii), Curtun (Cortona), Tarchna (Tarquinia)
- Not IE: no ablaut, agglutinative morphology

Key references: Bonfante & Bonfante 2002, Rix 1991 "Etruskische Texte"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "na": "belonging to / adjectival",
    "ni": "gentilicial / belonging to",
    "enna": "place/origin suffix",
    "ina": "diminutive / place",
    "anu": "locative / place",
    "arna": "locative / place",
    "le": "diminutive",
    "alu": "agent/place",
    "ura": "nominal derivation",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "tarchna": ("tarchna", "Tarquinia (< *tarχ- 'to rule'?)"),
    "velzna": ("velzna", "Volsinii / Orvieto"),
    "clevsin": ("clevsin", "Chiusi (< *clevsina)"),
    "curtun": ("curtun", "Cortona"),
    "perusia": ("perusia", "Perugia"),
    "arretium": ("arretium", "Arezzo"),
    "veii": ("veii", "Veii"),
    "caere": ("caere", "Cerveteri (< *cisra)"),
    "felsina": ("felsina", "Bologna (Etruscan name)"),
    "mantua": ("mantua", "Mantova (< Manthu, Etruscan deity)"),
    "capena": ("capena", "Capena"),
    "spina": ("spina", "Spina (Adriatic port)"),
    "rusellae": ("rusellae", "Roselle"),
    "populonia": ("populonia", "Populonia (< *fufluna)"),
    "clusium": ("clusium", "Chiusi (Latin form < clevsin)"),
}

_PHONOLOGICAL_MARKERS = {"θ", "χ", "φ"}  # aspirated stops in Etruscan transliteration


class EtruscanModule(BaseLanguageModule):
    """Language module for Etruscan (ett) toponyms."""

    language_code = "ett"
    language_name = "Etruscan"
    family = "Language isolate (Tyrsenian?)"
    branch = "Tyrsenian"
    period = "900–100 BCE"
    script = "Latn"

    suffixes = list(_SUFFIXES.keys())
    prefixes: list[str] = []

    def segment(self, form: str) -> list[SegmentationResult]:
        results: list[SegmentationResult] = []
        fl = form.lower()

        # Check known toponyms first
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

        # Try suffix matching (longest first)
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
            evidence.append(f"Known Etruscan toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Etruscan suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.15
                evidence.append(f"Etruscan aspirate '{marker}'")

        # Lack of IE ablaut patterns, presence of vowel clusters
        if any(fl.endswith(s) for s in ("na", "ni", "enna", "ina")) and not any(
            fl.endswith(ie) for ie in ("tina", "nina")
        ):
            score += 0.1
            evidence.append("Typical Etruscan nominal ending")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="etruscan" if score > 0.4 else None,
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
                        confidence=0.75,
                        cognates=[],
                        sound_changes=[],
                        sources=["Bonfante & Bonfante 2002", "Rix 1991"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=[],
                        sources=["Bonfante & Bonfante 2002"],
                    )
                )
        return candidates
