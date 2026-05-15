"""Dacian language module for toponymic analysis.

Dacian (xdc) is an IE language (related to Thracian?) spoken in Romania/Moldova
(1st millennium BCE – 2nd c. CE). Poorly attested: ~100 plant names (Dioscorides),
personal names, and toponyms. Critical Romanian substrate.

Toponymic hallmarks:
- Suffixes: -dava/-deva (city/fortress, most distinctive!), -upa (water)
- Sarmizegetusa (capital), Apulum (Alba Iulia), Napoca (Cluj)
- ~100 plant names preserved in Dioscorides/Pseudo-Apuleius
- Dacian substrate in modern Romanian place-names

Key references: Russu 1969 "Die Sprache der Thrako-Daker",
Duridanov 1969, Olteanu 2009 (Encyclopaedia Encyclopaedia)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "dava": "city / fortress",
    "deva": "city / fortress (variant)",
    "daba": "settlement (variant?)",
    "upa": "water / river",
    "apa": "water / river",
    "issa": "place suffix",
    "ura": "place / nominal",
    "ava": "territory / water",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "sarmizegetusa": ("sarmizegetusa", "Sarmizegetusa (capital, 'proud fortress'?)"),
    "apulum": ("apulum", "Apulum (Alba Iulia, < *apa 'water')"),
    "napoca": ("napoca", "Napoca (Cluj, < *nap- ?)"),
    "porolissum": ("porolissum", "Porolissum (frontier fort)"),
    "dierna": ("dierna", "Dierna (Orșova, < *dier- 'flow'?)"),
    "sucidava": ("sucidava", "Sucidava (< *suk- ?)"),
    "buridava": ("buridava", "Buridava (< *bur- 'height'?)"),
    "cumidava": ("cumidava", "Cumidava (Rîșnov)"),
    "acidava": ("acidava", "Acidava (< *ak- 'water'?)"),
    "petrodava": ("petrodava", "Petrodava (< *petr- + dava)"),
    "ziridava": ("ziridava", "Ziridava (< *ziri- ?)"),
    "pelendava": ("pelendava", "Pelendava (Craiova area)"),
    "singidava": ("singidava", "Singidava"),
}

_PHONOLOGICAL_MARKERS = {"dz", "zd", "str"}


class DacianModule(BaseLanguageModule):
    """Language module for Dacian (xdc) toponyms."""

    language_code = "xdc"
    language_name = "Dacian"
    family = "Indo-European"
    branch = "Satem (Daco-Thracian?)"
    period = "1st millennium BCE – 2nd c. CE"
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
                    morph_type="compound_modifier",
                    confidence=0.55,
                )
            )
            results.append(
                SegmentationResult(
                    component=sfx_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=matched_meaning,
                    confidence=0.7,
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
            evidence.append(f"Known Dacian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.4
                evidence.append(f"Dacian suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.1
                evidence.append(f"Dacian phonological cluster '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="dacian" if score > 0.4 else None,
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
                        sound_changes=["satem: *k̑ > s"],
                        sources=["Russu 1969", "Duridanov 1969"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.65,
                        cognates=["Thracian -diza", "Dacian -dava"],
                        sources=["Russu 1969"],
                    )
                )
        return candidates
