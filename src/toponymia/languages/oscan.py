"""Oscan language module for toponymic analysis.

Oscan (osc) is an Italic (Sabellic) language spoken in S.Italy (5th–1st c. BCE).
Related to Latin but a separate branch. Spoken by the Samnites, Campanians,
Lucanians, and Bruttians. Major substrate in southern Italian toponymy.

Toponymic hallmarks:
- Suffixes: -anum, -inum, -entia, -nus
- Oscan phonology: p where Latin has qu, f where Latin has initial h
- Place-names: Pompeii, Nola, Capua, Beneventum, Salernum
- Known from extensive inscriptions (Tabula Bantina, Cippus Abellanus)

Key references: Buck 1928 "A Grammar of Oscan and Umbrian",
               Rix 2002 "Sabellische Texte", McDonald 2015
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "anum": "place / estate suffix",
    "inum": "place / estate suffix",
    "entia": "place / abstract suffix",
    "ernum": "place suffix",
    "anus": "adjectival / belonging to",
    "inus": "adjectival / diminutive",
    "tum": "place / result suffix",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "pompeii": ("pompeii", "Pompeii (< Oscan *pompe 'five'? or family name)"),
    "nola": ("nola", "Nola (< Oscan *novla 'new town'?)"),
    "capua": ("capua", "Capua (< Oscan *kapu- ?)"),
    "beneventum": ("beneventum", "Benevento (< Oscan *Maloventum reinterpreted)"),
    "salernum": ("salernum", "Salerno (< *saler- salt?)"),
    "abella": ("abella", "Avella (< Oscan, known from Cippus Abellanus)"),
    "bantia": ("bantia", "Banzi (known from Tabula Bantina)"),
    "herculaneum": ("herculaneum", "Ercolano (Oscan settlement)"),
    "nuceria": ("nuceria", "Nocera (< *noukr-ia 'new foundation'?)"),
    "teanum": ("teanum", "Teano (< Oscan *tean- ?)"),
    "compsa": ("compsa", "Conza della Campania"),
    "aesernia": ("aesernia", "Isernia (< *ais- god/sacred?)"),
    "bovianum": ("bovianum", "Bojano (Samnite capital)"),
    "venusia": ("venusia", "Venosa (< *wen- ?)"),
}

_OSCAN_PHONOLOGY = {
    "p_for_qu": "Oscan p where Latin has qu (e.g. pis vs quis)",
    "f_for_h": "Oscan f- where Latin has h- (e.g. fifo vs hio)",
}


class OscanModule(BaseLanguageModule):
    """Language module for Oscan (osc) toponyms."""

    language_code = "osc"
    language_name = "Oscan"
    family = "Indo-European"
    branch = "Italic > Sabellic"
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
            evidence.append(f"Known Oscan toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Italic suffix -{sfx}")
                break

        # Oscan-specific features
        if fl.endswith(("ii", "ium")):
            score += 0.1
            evidence.append("Italic/Oscan nominal pattern")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="oscan" if score > 0.4 else None,
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
                        cognates=["cf. Latin", "cf. Umbrian"],
                        sources=["Buck 1928", "Rix 2002"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=["cf. Latin cognate"],
                        sources=["Buck 1928"],
                    )
                )
        return candidates
