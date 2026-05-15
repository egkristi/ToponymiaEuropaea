"""Illyrian language module for toponymic analysis.

Illyrian (xil) is a poorly attested IE language spoken in the western Balkans
(2nd millennium BCE – 2nd c. CE). Known only from personal names, tribal names,
and toponyms in Greek/Latin sources. Albanian may descend from it (debated).

Toponymic hallmarks:
- Suffixes: -ona (place/river), -ista (place), -inium (settlement)
- Epidaurum (Dubrovnik area), Dyrrachium (Durrës), Scodra (Shkodër)
- Centum or satem? Still debated
- Substrate in Albanian, Croatian, Montenegrin place-names

Key references: Krahe 1955 "Die Sprache der Illyrier",
Mayer 1957 "Die illyrischen Sprachreste"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "ona": "place / river",
    "ista": "place / settlement",
    "inium": "settlement",
    "entia": "people / region",
    "etia": "territory",
    "arna": "place (cf. Etruscan)",
    "esta": "place suffix",
    "issa": "island / place",
}

# Deduplicated for matching
_SUFFIX_MAP: dict[str, str] = {
    "inium": "settlement",
    "entia": "people / region",
    "etia": "territory",
    "ista": "place / settlement",
    "issa": "island / place",
    "arna": "place suffix",
    "esta": "place suffix",
    "ona": "place / river",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "epidaurum": ("epidaurum", "Epidaurum (Cavtat, < *epi-daurom ?)"),
    "dyrrachium": ("dyrrachium", "Dyrrachium (Durrës)"),
    "scodra": ("scodra", "Scodra (Shkodër)"),
    "salona": ("salona", "Salona (Solin, < *sal- 'salt')"),
    "narona": ("narona", "Narona (Vid, < river Naro)"),
    "iader": ("iader", "Iader (Zadar)"),
    "epidamnos": ("epidamnos", "Epidamnos (= Dyrrachium)"),
    "doclea": ("doclea", "Doclea (Podgorica area)"),
    "lissus": ("lissus", "Lissus (Lezhë)"),
    "byllis": ("byllis", "Byllis (Illyrian city in Albania)"),
    "apollonia": ("apollonia", "Apollonia (Fier, Greek colony on Illyrian land)"),
    "delminium": ("delminium", "Delminium (Dalmatae capital)"),
}

_PHONOLOGICAL_MARKERS = {"sc", "dl", "gn"}


class IllyrianModule(BaseLanguageModule):
    """Language module for Illyrian (xil) toponyms."""

    language_code = "xil"
    language_name = "Illyrian"
    family = "Indo-European"
    branch = "Uncertain (centum/satem debated)"
    period = "2nd millennium BCE – 2nd c. CE"
    script = "Latn"

    suffixes = list(_SUFFIX_MAP.keys())
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
                    confidence=0.7,
                )
            )
            return results

        matched_suffix = ""
        matched_meaning = ""
        for sfx, meaning in sorted(_SUFFIX_MAP.items(), key=lambda x: -len(x[0])):
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
                    confidence=0.45,
                )
            )
            results.append(
                SegmentationResult(
                    component=sfx_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=matched_meaning,
                    confidence=0.5,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.25,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        fl = form.lower()
        score = 0.0
        evidence: list[str] = []

        if fl in _KNOWN_ELEMENTS:
            score += 0.65
            evidence.append(f"Known Illyrian toponym: {fl}")

        for sfx in sorted(_SUFFIX_MAP, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.25
                evidence.append(f"Illyrian suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.1
                evidence.append(f"Illyrian phonological cluster '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="illyrian" if score > 0.4 else None,
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
                        confidence=0.6,
                        cognates=[],
                        sound_changes=[],
                        sources=["Krahe 1955", "Mayer 1957"],
                    )
                )
            elif cl in _SUFFIX_MAP:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIX_MAP[cl],
                        language_code=self.language_code,
                        confidence=0.45,
                        cognates=[],
                        sources=["Krahe 1955"],
                    )
                )
        return candidates
