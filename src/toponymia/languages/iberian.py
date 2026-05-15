"""Iberian language module for toponymic analysis.

Iberian (xib) is an unclassified language spoken in eastern and southern
Iberia (5th–1st c. BCE). Written in Iberian script. Not Celtic, not Basque
(though debate continues on possible Basque connections). Attested from
inscriptions and coin legends.

Toponymic hallmarks:
- Suffixes: -ili, -iscar, -iltir (city), -ilu, -ars
- City names: Iltirta (Lérida), Arse (Sagunto), Ilturo (Cabrera de Mar)
- Elements: ili/ilu (city), bels (strong?), ars (?)

Key references: Untermann 1990 "Monumenta Linguarum Hispanicarum",
               de Hoz 2010 "Historia lingüística de la Península Ibérica"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "iltir": "city/town",
    "ili": "city/settlement",
    "iscar": "place suffix",
    "ilu": "city (variant)",
    "ars": "unknown (toponym element)",
    "sken": "ethnic/demonym suffix",
    "tar": "unknown (toponym element)",
    "berri": "new? (cf. Basque berri)",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "iltirta": ("iltirta", "Lérida (< iltir 'city')"),
    "arse": ("arse", "Sagunto"),
    "ilturo": ("ilturo", "Cabrera de Mar (< iltir/iltur)"),
    "baitolo": ("baitolo", "Badalona"),
    "saiti": ("saiti", "Xàtiva"),
    "kese": ("kese", "Tarragona (Iberian name)"),
    "undikesken": ("undikesken", "Ampurias area"),
    "laiesken": ("laiesken", "Laietani territory"),
    "iliberri": ("iliberri", "Elvira/Granada (< ili+berri?)"),
}

_IBERIAN_PHONOLOGICAL = {"ś", "ŕ", "ḿ"}  # special Iberian script signs


class IberianModule(BaseLanguageModule):
    """Language module for Iberian (xib) toponyms."""

    language_code = "xib"
    language_name = "Iberian"
    family = "Unclassified"
    branch = "Pre-Roman Iberian"
    period = "5th–1st c. BCE"
    script = "Latn"

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
            evidence.append(f"Known Iberian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.35
                evidence.append(f"Iberian suffix -{sfx}")
                break

        # ili/iltir element anywhere in name
        if ("iltir" in fl or "ili" in fl or "iltur" in fl) and not evidence:
            score += 0.3
            evidence.append("Contains Iberian element ili/iltir (city)")

        for marker in _IBERIAN_PHONOLOGICAL:
            if marker in fl:
                score += 0.1
                evidence.append(f"Iberian phonological marker '{marker}'")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="iberian" if score > 0.4 else None,
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
                        sources=["Untermann 1990", "de Hoz 2010"],
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
                        sources=["Untermann 1990"],
                    )
                )
        return candidates
