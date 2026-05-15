"""Hittite language module for toponymic analysis.

Hittite (hit) is the earliest attested Indo-European language, spoken in
central Anatolia (17th–12th c. BCE). Written in cuneiform on clay tablets.
Capital at Hattuša (Boğazkale). The Hittite Empire was a major Bronze Age power.

Toponymic hallmarks:
- Suffixes: -ša/-šša (place), -wanda (< Luwian), -na, -iya
- Cuneiform renderings with Sumerograms/Akkadograms
- Hattuša, Neša (Kaneš), Zippalanda, Tarḫuntašša
- Laryngeal preservation (ḫ = *h₂)

Key references: Puhvel 1984– "Hittite Etymological Dictionary",
Kloekhorst 2008 "Etymological Dictionary of the Hittite Inherited Lexicon"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "ssa": "place suffix (Hattic substrate)",
    "sa": "place suffix",
    "wanda": "place (< Luwian *wanda-)",
    "na": "locative / place",
    "iya": "adjectival / belonging to",
    "anda": "into / locative",
    "sta": "place (< *stā- 'stand')",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "hattusa": ("ḫattuša", "Hattuša (capital, < Hattic ḫatti)"),
    "nesa": ("neša", "Neša / Kaneš (< Hattic?)"),
    "zippalanda": ("zippalanda", "Zippalanda (cult centre)"),
    "tarhuntassa": ("tarḫuntašša", "Tarḫuntašša (city of storm-god)"),
    "samuha": ("šamuḫa", "Šamuḫa (religious centre)"),
    "sapinuwa": ("šapinuwa", "Šapinuwa (< *šap- ?)"),
    "ankuwa": ("ankuwa", "Ankuwa (cult centre)"),
    "kussara": ("kuššara", "Kuššara (early capital)"),
    "arinna": ("arinna", "Arinna (sun-goddess cult)"),
    "hurma": ("ḫurma", "Ḫurma"),
    "katapa": ("katapa", "Katapa"),
    "nerik": ("nerik", "Nerik (storm-god cult)"),
}

_PHONOLOGICAL_MARKERS = {"ḫ", "š", "ḫḫ", "šš"}


class HittiteModule(BaseLanguageModule):
    """Language module for Hittite (hit) toponyms."""

    language_code = "hit"
    language_name = "Hittite"
    family = "Indo-European"
    branch = "Anatolian"
    period = "17th–12th c. BCE"
    script = "Xsux"

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
            evidence.append(f"Known Hittite toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Hittite/Anatolian suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.15
                evidence.append(f"Hittite phonological marker '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="hittite" if score > 0.4 else None,
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
                        sound_changes=["laryngeal preservation ḫ < *h₂"],
                        sources=["Puhvel 1984", "Kloekhorst 2008"],
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
                        sources=["Kloekhorst 2008"],
                    )
                )
        return candidates
