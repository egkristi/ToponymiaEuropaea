"""Rhaetian language module for toponymic analysis.

Rhaetian (xrr) is an unclassified language (possibly Tyrsenian, i.e. related
to Etruscan) spoken in the Alps (5th–1st c. BCE). Known from ~300 short
inscriptions in the Bolzano/Trentino/Veneto area. Substrate in Alpine
place-names of South Tyrol, Trentino, and Graubünden.

Toponymic hallmarks:
- Suffixes: -enna, -ina, -ona, -anu, -ate
- Alpine landscape terms as substrate
- Possible Etruscan-like morphology (-na, -ni suffixes)
- Place-names: Tridentum (Trento), Meran, Brixen (Bressanone)

Key references: Rix 1998, Schumacher 2004, Marchesini 2015
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "enna": "place/locative suffix",
    "ina": "diminutive / place suffix",
    "ona": "locative / augmentative",
    "anu": "adjectival / belonging to",
    "ate": "collective / place",
    "na": "adjectival (cf. Etruscan -na)",
    "ni": "gentilicial (cf. Etruscan -ni)",
    "asco": "place suffix (shared with Ligurian)",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "tridentum": ("tridentum", "Trento (< *tri-dent- 'three-tooth/peak'?)"),
    "meran": ("meran", "Merano (Rhaetian substrate?)"),
    "brixen": ("brixen", "Bressanone (< *brig- hill? or Rhaetian)"),
    "laion": ("laion", "Laion (Rhaetian substrate)"),
    "schenna": ("schenna", "Scena (< -enna suffix)"),
    "bozen": ("bozen", "Bolzano (Rhaetian substrate?)"),
    "matrei": ("matrei", "Matrei (< *matr- ?)"),
    "innichen": ("innichen", "San Candido (< *inn- river + -ichen?)"),
}

_ALPINE_SUBSTRATE_MARKERS = {"sch", "tsch", "pf"}


class RhaetianModule(BaseLanguageModule):
    """Language module for Rhaetian (xrr) toponyms."""

    language_code = "xrr"
    language_name = "Rhaetian"
    family = "Unclassified (Tyrsenian?)"
    branch = "Alpine pre-Roman"
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
                    confidence=0.55,
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
            score += 0.6
            evidence.append(f"Known Rhaetian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Rhaetian suffix -{sfx}")
                break

        for marker in _ALPINE_SUBSTRATE_MARKERS:
            if marker in fl:
                score += 0.1
                evidence.append(f"Alpine substrate cluster '{marker}'")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="rhaetian" if score > 0.4 else None,
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
                        cognates=["cf. Etruscan morphology"],
                        sources=["Rix 1998", "Marchesini 2015"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.5,
                        cognates=["cf. Etruscan -na/-ni"],
                        sources=["Schumacher 2004"],
                    )
                )
        return candidates
