"""Faliscan language module for toponymic analysis.

Faliscan (xfa) is an Italic (Latino-Faliscan) language spoken in a small
area of central Italy around Falerii (modern Civita Castellana) and its
territory (Ager Faliscus). It is the closest known relative of Latin,
sharing the Latino-Faliscan branch of the Italic family. Very small corpus
(~400 inscriptions, mostly short).

Toponymic hallmarks:
- Limited but distinctive: Falerii (Civita Castellana), Capena, Narce
- Phonology close to Latin: f- preserved where Sabellic has h-
- Substrate confined to small area between Rome and southern Etruria

Key references: Giacomelli 1963 "La lingua falisca", Bakkum 2009
               "The Latin Dialect of the Ager Faliscus"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "erii": "place suffix (< *-eri-io-)",
    "ium": "place / territory suffix",
    "ina": "adjectival / feminine place",
    "anum": "place / estate suffix",
    "iscus": "ethnic / adjectival",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "falerii": ("falerii", "Civita Castellana (Faliscan capital)"),
    "capena": ("capena", "Capena (on Faliscan/Etruscan border)"),
    "narce": ("narce", "Narce (Faliscan settlement)"),
    "nepet": ("nepet", "Nepi (< Faliscan/Etruscan *nepet)"),
    "sutrium": ("sutrium", "Sutri (border town)"),
    "fescennium": ("fescennium", "Fescennia (< *fescenn- ?)"),
    "corchiano": ("corchiano", "modern name, Faliscan area"),
    "vignanello": ("vignanello", "Faliscan territory"),
}

# Faliscan territory markers
_FALISCAN_AREA_MARKERS = {"fal", "falis", "capena", "narce", "nepet"}


class FaliscanModule(BaseLanguageModule):
    """Language module for Faliscan (xfa) toponyms."""

    language_code = "xfa"
    language_name = "Faliscan"
    family = "Indo-European"
    branch = "Italic > Latino-Faliscan"
    period = "7th–3rd c. BCE"
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
            evidence.append(f"Known Faliscan toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.25
                evidence.append(f"Italic suffix -{sfx}")
                break

        # Check for Faliscan-area name elements
        for marker in _FALISCAN_AREA_MARKERS:
            if marker in fl:
                score += 0.2
                evidence.append(f"Faliscan territory marker: {marker}")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="faliscan" if score > 0.4 else None,
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
                        cognates=["cf. Latin"],
                        sources=["Giacomelli 1963", "Bakkum 2009"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.55,
                        cognates=["cf. Latin cognate"],
                        sources=["Bakkum 2009"],
                    )
                )
        return candidates
