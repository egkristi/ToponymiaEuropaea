"""Lepontic language module for toponymic analysis.

Lepontic (xlp) is a Continental Celtic language—the earliest attested Celtic
language—spoken in N.Italy and S.Switzerland (6th–3rd c. BCE). Known from
~140 inscriptions in the Lepontic alphabet (derived from Etruscan).
Substrate in Lombardy, Ticino, and Piedmont.

Toponymic hallmarks:
- Elements: -dunum (fortress), -magus (field)
- Celtic compound structure in Alpine context
- Personal names as settlement bases
- Place-names: Mediolanum (Milan), Como, Bergamo (< *berg- hill?)

Key references: Lejeune 1971, Stifter 2020, Uhlich 2007
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "dunum": "fortress / fortified hill",
    "magus": "field / market",
    "lanum": "plain / open ground",
    "acum": "estate (< -āko-)",
    "ate": "place suffix",
}

_PREFIXES: dict[str, str] = {
    "medio": "middle",
    "brig": "hill / height",
    "novio": "new",
    "vindo": "white / blessed",
    "ebu": "yew tree",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "mediolanum": ("mediolanum", "Milan (< medio- 'middle' + -lanum 'plain')"),
    "comum": ("comum", "Como (< *komu- ?)"),
    "bergomum": ("bergomum", "Bergamo (< *brig- 'hill' + -omum)"),
    "brixia": ("brixia", "Brescia (< *brig- 'hill/height')"),
    "vercellae": ("vercellae", "Vercelli (possibly Lepontic)"),
    "laus": ("laus", "Lodi Vecchio (< *laus- ?)"),
    "novaria": ("novaria", "Novara (< novio- 'new'?)"),
    "victumulae": ("victumulae", "near Vercelli"),
    "clastidium": ("clastidium", "Casteggio"),
}


class LeponticModule(BaseLanguageModule):
    """Language module for Lepontic (xlp) toponyms."""

    language_code = "xlp"
    language_name = "Lepontic"
    family = "Indo-European"
    branch = "Celtic > Continental Celtic"
    period = "6th–3rd c. BCE"
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
                    confidence=0.75,
                )
            )
            return results

        # Try suffix + prefix
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
            if fl.startswith(pfx) and len(fl) > len(pfx) + 2:
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
                    confidence=0.65,
                )
            )
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="infix",
                        confidence=0.35,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=2,
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
                    confidence=0.55,
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
            score += 0.7
            evidence.append(f"Known Lepontic toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.3
                evidence.append(f"Celtic suffix -{sfx}")
                break

        for pfx in sorted(_PREFIXES, key=len, reverse=True):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 2:
                score += 0.2
                evidence.append(f"Lepontic/Celtic prefix {pfx}-")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="lepontic" if score > 0.4 else None,
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
                        cognates=["cf. Gaulish cognates"],
                        sources=["Lejeune 1971", "Stifter 2020"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.65,
                        cognates=["cf. Gaulish -dunum"],
                        sources=["Lejeune 1971"],
                    )
                )
            elif cl in _PREFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_PREFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=[],
                        sources=["Uhlich 2007"],
                    )
                )
        return candidates
