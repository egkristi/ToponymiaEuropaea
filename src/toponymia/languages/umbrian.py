"""Umbrian language module for toponymic analysis.

Umbrian (xum) is an Italic (Sabellic) language spoken in central Italy
(7th–1st c. BCE). Closely related to Oscan. Best known from the Iguvine
Tablets (Tabulae Iguvinae), a set of bronze tablets from Gubbio describing
ritual procedures. Substrate in Umbria and Marche.

Toponymic hallmarks:
- Suffixes: -inium, -arna, -erna, -illum
- Umbrian phonology: distinct from both Oscan and Latin
- Place-names: Iguvium (Gubbio), Spoletium (Spoleto), Tuder (Todi),
  Interamna (Terni), Asisium (Assisi)
- Known primarily from Iguvine Tablets + scattered inscriptions

Key references: Buck 1928, Rix 2002, Poultney 1959 "The Bronze Tables of Iguvium"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "inium": "place / territory suffix",
    "arna": "locative / place suffix",
    "erna": "locative / place suffix",
    "illum": "diminutive / place",
    "ium": "place / territory",
    "etium": "place suffix",
    "ina": "adjectival / place",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "iguvium": ("iguvium", "Gubbio (< Umbrian Ikuvins)"),
    "spoletium": ("spoletium", "Spoleto (< *spol- ?)"),
    "tuder": ("tuder", "Todi (< *tud- 'community'?)"),
    "interamna": ("interamna", "Terni (< *inter-amna 'between rivers')"),
    "asisium": ("asisium", "Assisi (< Umbrian substrate)"),
    "mevania": ("mevania", "Bevagna (< *medu- mead?)"),
    "ameria": ("ameria", "Amelia (< Umbrian *amer-)"),
    "sentinum": ("sentinum", "Sassoferrato area"),
    "camerinum": ("camerinum", "Camerino (< *kamer- ?)"),
    "fulginium": ("fulginium", "Foligno (< *fulg- ?)"),
    "perusia": ("perusia", "Perugia (Etruscan/Umbrian border)"),
    "hispellum": ("hispellum", "Spello (< *hisp- ?)"),
}


class UmbrianModule(BaseLanguageModule):
    """Language module for Umbrian (xum) toponyms."""

    language_code = "xum"
    language_name = "Umbrian"
    family = "Indo-European"
    branch = "Italic > Sabellic"
    period = "7th–1st c. BCE"
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

        # Check for inter- prefix (interamna pattern)
        if fl.startswith("inter") and len(fl) > 7:
            results.append(
                SegmentationResult(
                    component=form[:5],
                    position=0,
                    morph_type="prefix",
                    lemma="inter",
                    meaning="between",
                    confidence=0.7,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[5:],
                    position=1,
                    morph_type="stem",
                    confidence=0.5,
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
            evidence.append(f"Known Umbrian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Italic/Umbrian suffix -{sfx}")
                break

        # -arna/-erna suffix is particularly Umbrian
        if fl.endswith(("arna", "erna")):
            score += 0.1
            evidence.append("Umbrian locative -arna/-erna pattern")

        # inter- prefix (shared with Latin but Umbrian substrate)
        if fl.startswith("inter"):
            score += 0.1
            evidence.append("inter- prefix (between, Italic shared)")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="umbrian" if score > 0.4 else None,
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
                        cognates=["cf. Oscan", "cf. Latin"],
                        sources=["Buck 1928", "Poultney 1959"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=["cf. Oscan cognate"],
                        sources=["Rix 2002"],
                    )
                )
        return candidates
