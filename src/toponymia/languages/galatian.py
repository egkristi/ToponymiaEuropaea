"""Galatian language module for toponymic analysis.

Galatian (xga) is a Continental Celtic language spoken in central Anatolia
(3rd c. BCE – 4th c. CE). Celtic tribes (Tolistobogii, Tectosages, Trocmi)
migrated to Asia Minor and established themselves around Ankara. Limited
attestation from classical authors and a few inscriptions.

Toponymic hallmarks:
- Celtic compound elements in Anatolian context
- Elements: -briga (fort?), dru- (oak/strong), -nemetum (sacred grove)
- Place-names: Ancyra (Ankara, possibly Celtic *ankura 'bend'?),
  Drunemeton (sacred oak grove), Pessinus, Gordion (pre-Galatian)

Key references: Freeman 2001, Stifter 2003, Delamarre 2003
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "nemetum": "sacred grove",
    "briga": "fortified place",
    "dunum": "fortress",
    "rigo": "king / royal",
    "marus": "great",
}

_PREFIXES: dict[str, str] = {
    "dru": "oak / strong (< *dru-)",
    "gal": "Galatian tribal prefix?",
    "ande": "great / under?",
    "ver": "great / over",
    "vindo": "white / blessed",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "ancyra": ("ancyra", "Ankara (< *ankura 'bend'? debated)"),
    "drunemeton": ("drunemeton", "sacred oak grove (< dru- + nemetum)"),
    "pessinus": ("pessinus", "Pessinus (Phrygian or Galatian?)"),
    "tavium": ("tavium", "Büyüknefes (tribal centre of Trocmi)"),
    "gordion": ("gordion", "Gordion (pre-Galatian, Phrygian)"),
    "blucium": ("blucium", "fortress near Ankara"),
    "eccobriga": ("eccobriga", "< *ekko- + -briga (horse-fort?)"),
    "vindia": ("vindia", "< *vindo- 'white/blessed'"),
}

_GALATIAN_TRIBES = {"tolistobogii", "tectosages", "trocmi"}


class GalatianModule(BaseLanguageModule):
    """Language module for Galatian (xga) toponyms."""

    language_code = "xga"
    language_name = "Galatian"
    family = "Indo-European"
    branch = "Celtic > Continental Celtic"
    period = "3rd c. BCE – 4th c. CE"
    script = "Latn"

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
                    confidence=0.7,
                )
            )
            return results

        matched_suffix = ""
        matched_sfx_meaning = ""
        for sfx, meaning in sorted(_SUFFIXES.items(), key=lambda x: -len(x[0])):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                matched_suffix = sfx
                matched_sfx_meaning = meaning
                break

        matched_prefix = ""
        matched_pfx_meaning = ""
        for pfx, meaning in sorted(_PREFIXES.items(), key=lambda x: -len(x[0])):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 1:
                matched_prefix = pfx
                matched_pfx_meaning = meaning
                break

        if matched_prefix and matched_suffix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    meaning=matched_pfx_meaning,
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    meaning=matched_sfx_meaning,
                    confidence=0.7,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_modifier",
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    meaning=matched_sfx_meaning,
                    confidence=0.65,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    meaning=matched_pfx_meaning,
                    confidence=0.55,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    confidence=0.35,
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
            evidence.append(f"Known Galatian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Celtic suffix -{sfx}")
                break

        for pfx in sorted(_PREFIXES, key=len, reverse=True):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 1:
                score += 0.2
                evidence.append(f"Galatian/Celtic prefix {pfx}-")
                break

        # Tribal name connections
        for tribe in _GALATIAN_TRIBES:
            if tribe in fl:
                score += 0.15
                evidence.append(f"Galatian tribe name: {tribe}")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="galatian" if score > 0.4 else None,
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
                        cognates=["cf. Gaulish cognates"],
                        sources=["Freeman 2001", "Delamarre 2003"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.55,
                        cognates=["cf. Gaulish -dunum/-nemetum"],
                        sources=["Stifter 2003"],
                    )
                )
            elif cl in _PREFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_PREFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.5,
                        cognates=[],
                        sources=["Delamarre 2003"],
                    )
                )
        return candidates
