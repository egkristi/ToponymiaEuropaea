"""Tartessian language module for toponymic analysis.

Tartessian (txr) is a possibly Celtic or unclassified language of SW Iberia
(8th–5th c. BCE). Known from inscriptions in the SW script (Southwestern
script / Tartessian script). Extremely fragmentary. Associated with the
Tartessos civilisation in the Huelva/Algarve/Guadalquivir region.

Toponymic hallmarks:
- Possibly Celtic elements: -briga?, -ipo (settlement?)
- SW Iberia river/settlement names
- Connection to later Lusitanian and Celtiberian debated
- Elements: ipo (settlement?), -oba/-uba (water?), -ipo

Key references: Koch 2009 "Tartessian: Celtic in the South-west",
               Valério 2008, Correa 2005
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "ipo": "settlement/town (debated)",
    "oba": "water/river? (debated)",
    "uba": "water/river? (variant)",
    "igi": "place suffix?",
    "ppo": "toponym suffix",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "tartessos": ("tartessos", "Tartessos (legendary city/region)"),
    "onoba": ("onoba", "Huelva (< *on- + -oba)"),
    "olisipo": ("olisipo", "Lisbon (< *oli- + -ipo)"),
    "ossonoba": ("ossonoba", "Faro (< *osson- + -oba)"),
    "conistorgis": ("conistorgis", "Eastern Algarve settlement"),
    "baesippo": ("baesippo", "Barbate area (< *baes- + -ippo)"),
    "iptuci": ("iptuci", "Prado del Rey (< ipt- + -uci)"),
    "ilipa": ("ilipa", "Alcalá del Río (< il- + -ipa)"),
    "nabrissa": ("nabrissa", "Lebrija"),
}

_SW_SCRIPT_CONTEXTS = {"algarve", "huelva", "guadalquivir", "tartessos"}


class TartessianModule(BaseLanguageModule):
    """Language module for Tartessian (txr) toponyms."""

    language_code = "txr"
    language_name = "Tartessian"
    family = "Unclassified (possibly Celtic)"
    branch = "SW Iberian"
    period = "8th–5th c. BCE"
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
                    confidence=0.7,
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
                    confidence=0.4,
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
            evidence.append(f"Known Tartessian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Tartessian suffix -{sfx}")
                break

        # -ipo/-ippo element (strong Tartessian marker)
        if ("ipo" in fl or "ippo" in fl) and "ipo" not in [e.split()[-1] for e in evidence]:
            score += 0.2
            evidence.append("Contains -ipo/-ippo element (SW Iberian settlement)")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="tartessian" if score > 0.4 else None,
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
                        confidence=0.55,
                        cognates=[],
                        sources=["Koch 2009", "Correa 2005"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.45,
                        cognates=[],
                        sources=["Koch 2009", "Valério 2008"],
                    )
                )
        return candidates
