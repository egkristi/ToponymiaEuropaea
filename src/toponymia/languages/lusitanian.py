"""Lusitanian language module for toponymic analysis.

Lusitanian (xls) is an Indo-European language of debated affiliation (Celtic?
Italic? separate branch?) spoken in pre-Roman western Iberia. Known from only
5 inscriptions (Cabeço das Fráguas, Lamas de Moledo, Arroyo de la Luz).
Substrate in Portuguese/Galician toponymy.

Toponymic hallmarks:
- Elements: -briga (fortified place, shared with Celtic), -aeco, -oeco
- Deity names as place elements: Endovellicus, Bandua, Reve
- River names with *-ana suffix
- Possible para-Celtic or Italic features

Key references: Prósper 2002 "Lenguas y religiones prerromanas del occidente
               de la Península Ibérica", Untermann 1997, Villar 2000
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "briga": "fortified place / hill-fort",
    "aeco": "adjective / belonging to",
    "oeco": "adjective / belonging to",
    "ana": "river / water (hydronymic)",
    "obriga": "fortified height",
    "aeum": "place / region suffix",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "conimbriga": ("conimbriga", "Coimbra (< *kon- + -imbriga)"),
    "talabriga": ("talabriga", "Aveiro area (< *tala- + -briga)"),
    "langobriga": ("langobriga", "near Porto (< *lango- + -briga)"),
    "mirobriga": ("mirobriga", "Santiago do Cacém (< *miro- + -briga)"),
    "lacobriga": ("lacobriga", "Lagos (< *laco- + -briga)"),
    "eburobrittium": ("eburobrittium", "Óbidos (< *eburo- yew + -brittium)"),
    "olisipo": ("olisipo", "Lisbon (pre-Roman, possibly Lusitanian)"),
    "bracara": ("bracara", "Braga"),
    "cale": ("cale", "Porto area (< *cal- harbour?)"),
}

_LUSITANIAN_DEITIES = {"endovellicus", "bandua", "reve", "trebaruna", "nabia"}


class LusitanianModule(BaseLanguageModule):
    """Language module for Lusitanian (xls) toponyms."""

    language_code = "xls"
    language_name = "Lusitanian"
    family = "Indo-European (branch debated)"
    branch = "Para-Celtic or separate IE branch"
    period = "Pre-Roman (before 1st c. BCE)"
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

        # Check for -briga compound (most common pattern)
        if "briga" in fl and fl.index("briga") > 0:
            split_idx = fl.index("briga")
            stem = form[:split_idx]
            sfx_part = form[split_idx:]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="compound_modifier",
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=sfx_part,
                    position=1,
                    morph_type="compound_head",
                    lemma="briga",
                    meaning="fortified place / hill-fort",
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
            score += 0.65
            evidence.append(f"Known Lusitanian toponym: {fl}")

        if "briga" in fl:
            score += 0.35
            evidence.append("Contains -briga (Celtic/Lusitanian fortress)")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if sfx != "briga" and fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.25
                evidence.append(f"Lusitanian suffix -{sfx}")
                break

        # Check for Lusitanian deity-based toponyms
        for deity in _LUSITANIAN_DEITIES:
            if deity in fl:
                score += 0.2
                evidence.append(f"Lusitanian deity name: {deity}")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="lusitanian" if score > 0.4 else None,
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
                        cognates=["cf. Celtic -briga"],
                        sources=["Prósper 2002", "Villar 2000"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.55,
                        cognates=["cf. Celtiberian -briga"],
                        sources=["Untermann 1997"],
                    )
                )
        return candidates
