"""Ancient/Classical Greek language module for toponymic analysis.

Ancient Greek (grc) is the Hellenic language from the 8th c. BCE to 4th c. CE,
covering Archaic, Classical, and Hellenistic periods. Distinct from Byzantine
Greek (covered in byzantine_greek.py).

Toponymic hallmarks:
- Suffixes: -polis (city), -aia/-ea (region), -nthos (pre-Greek substrate),
  -ssos/-ssos (pre-Greek substrate), -eia, -ia, -on
- Massive toponymic legacy: Athēnai, Korinthos, Thēbai, Megalopolis
- Pre-Greek substrate in -nthos, -ssos = non-Indo-European!
- Compound toponyms: Hiero-solyma, Mega-lo-polis, Nea-polis

Key references: Beekes 2010 "Etymological Dictionary of Greek",
Chantraine 1968 "Dictionnaire étymologique de la langue grecque"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "polis": "city",
    "aia": "region / territory",
    "ea": "region / territory",
    "nthos": "pre-Greek substrate",
    "ssos": "pre-Greek substrate",
    "ntha": "pre-Greek substrate",
    "ssa": "pre-Greek substrate",
    "eia": "place/quality",
    "ia": "territory / abstract",
    "on": "neuter place",
    "os": "masculine nominative",
    "ai": "plural nominative",
    "oi": "plural nominative",
    "ousa": "participle (island name)",
}

_PREFIXES: dict[str, str] = {
    "nea": "new",
    "mega": "great",
    "hiero": "sacred",
    "kalli": "beautiful",
    "leuko": "white",
    "melano": "black",
    "chryso": "golden",
    "hepta": "seven",
    "penta": "five",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "athenai": ("athēnai", "Athens (< goddess Athena)"),
    "korinthos": ("korinthos", "Corinth (pre-Greek -nthos)"),
    "thebai": ("thēbai", "Thebes (pre-Greek origin)"),
    "sparta": ("spartē", "Sparta (< spartē 'sown land')"),
    "megalopolis": ("megalopolis", "Great City"),
    "neapolis": ("neapolis", "New City (> Napoli)"),
    "thermopylai": ("thermopylai", "Hot Gates"),
    "delphi": ("delphoi", "Delphi (< delphys 'womb')"),
    "olympia": ("olympia", "Olympia (< olympos 'mountain')"),
    "pylos": ("pylos", "Pylos (pre-Greek)"),
    "knossos": ("knōsos", "Knossos (pre-Greek -ssos)"),
    "halikarnassos": ("halikarnassos", "Halicarnassus (pre-Greek)"),
    "parnassos": ("parnassos", "Parnassus (pre-Greek -ssos)"),
}

_SUBSTRATE_MARKERS = {"nth", "ss", "mn", "gd"}


class AncientGreekModule(BaseLanguageModule):
    """Language module for Ancient Greek (grc) toponyms."""

    language_code = "grc"
    language_name = "Ancient Greek"
    family = "Indo-European"
    branch = "Hellenic"
    period = "8th c. BCE – 4th c. CE"
    script = "Grek"

    suffixes = list(_SUFFIXES.keys())
    prefixes = list(_PREFIXES.keys())

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
                    confidence=0.85,
                )
            )
            return results

        # Prefix check
        pos = 0
        for pfx, meaning in sorted(_PREFIXES.items(), key=lambda x: -len(x[0])):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 2:
                results.append(
                    SegmentationResult(
                        component=form[: len(pfx)],
                        position=pos,
                        morph_type="prefix",
                        lemma=pfx,
                        meaning=meaning,
                        confidence=0.65,
                    )
                )
                form = form[len(pfx) :]
                fl = fl[len(pfx) :]
                pos += 1
                break

        # Suffix check
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
                    position=pos,
                    morph_type="stem",
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=sfx_part,
                    position=pos + 1,
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
                    position=pos,
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
            evidence.append(f"Known Ancient Greek toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Greek suffix -{sfx}")
                break

        for pfx in _PREFIXES:
            if fl.startswith(pfx):
                score += 0.2
                evidence.append(f"Greek prefix {pfx}-")
                break

        for marker in _SUBSTRATE_MARKERS:
            if marker in fl:
                score += 0.15
                evidence.append(f"Pre-Greek substrate cluster '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="ancient-greek" if score > 0.4 else None,
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
                        confidence=0.8,
                        cognates=[],
                        sound_changes=[],
                        sources=["Beekes 2010", "Chantraine 1968"],
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
                        sources=["Beekes 2010"],
                    )
                )
            elif cl in _PREFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_PREFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.65,
                        cognates=[],
                        sources=["Chantraine 1968"],
                    )
                )
        return candidates
