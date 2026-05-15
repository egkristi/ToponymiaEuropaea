"""Venetic language module for toponymic analysis.

Venetic (xve) is an IE language (Italic? separate branch?) spoken in NE Italy
(6th–1st c. BCE). ~300 inscriptions, mostly votive, in a North Italic alphabet.
Important substrate in Veneto place-names.

Toponymic hallmarks:
- Suffixes: -este (place, cf. Ateste), -ium/-ina (place)
- Patavium (Padova), Ateste (Este), Opitergium (Oderzo), Vicetia (Vicenza)
- Close to Italic but with unique features
- Substrate in modern Veneto/Friuli place-names

Key references: Lejeune 1974 "Manuel de la langue vénète",
Untermann 1961 "Die venetischen Personennamen"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "este": "place / settlement (< *es-te 'is there'?)",
    "ium": "place / settlement",
    "ina": "place / adjectival",
    "etia": "territory",
    "avium": "place of waters?",
    "ona": "river / place",
    "ergium": "fortress? (< *bherg-)",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "patavium": ("patavium", "Patavium (Padova, < *pat- 'broad'?)"),
    "ateste": ("ateste", "Ateste (Este, < river *ates-)"),
    "opitergium": ("opitergium", "Opitergium (Oderzo, 'market town')"),
    "vicetia": ("vicetia", "Vicetia (Vicenza)"),
    "tarvisium": ("tarvisium", "Tarvisium (Treviso)"),
    "altinum": ("altinum", "Altinum (Altino, < *alt- 'height')"),
    "feltria": ("feltria", "Feltria (Feltre)"),
    "acelum": ("acelum", "Acelum (Asolo)"),
    "bellunum": ("bellunum", "Bellunum (Belluno)"),
    "verona": ("verona", "Verona (Venetic or Celtic?)"),
    "mantua": ("mantua", "Mantua (disputed: Venetic or Etruscan?)"),
}

_PHONOLOGICAL_MARKERS = {"vh", "xt", "kv"}


class VeneticModule(BaseLanguageModule):
    """Language module for Venetic (xve) toponyms."""

    language_code = "xve"
    language_name = "Venetic"
    family = "Indo-European"
    branch = "Italic? (or separate IE branch)"
    period = "6th–1st c. BCE"
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
                    confidence=0.55,
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
            evidence.append(f"Known Venetic toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Venetic suffix -{sfx}")
                break

        for marker in _PHONOLOGICAL_MARKERS:
            if marker in fl:
                score += 0.1
                evidence.append(f"Venetic phonological marker '{marker}'")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="venetic" if score > 0.4 else None,
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
                        sound_changes=[],
                        sources=["Lejeune 1974", "Untermann 1961"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.5,
                        cognates=[],
                        sources=["Lejeune 1974"],
                    )
                )
        return candidates
