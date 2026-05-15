"""Gaulish language module for toponymic analysis.

Gaulish (xcg) is a Continental Celtic language spoken in Gaul (modern France,
Belgium, N.Italy, parts of Switzerland/Germany) from the 6th c. BCE to the
5th c. CE. Massive toponymic legacy—hundreds of French place-names derive
from Gaulish compounds.

Toponymic hallmarks:
- -dunum (fortress): Lugdunum (Lyon), Virodunum (Verdun)
- -magus (field/market): Rotomagus (Rouen), Nemetacum (Arras)
- -briga (hill/fort): shared with other Celtic
- -ritum (ford): Augustoritum (Limoges)
- -ialo (clearing): Argenteuil, Nanteuil
- -lanum/-lano (plain): Mediolanum (Milan)
- Prefixes: ver- (great), nanto- (valley), duro- (fort)

Key references: Delamarre 2003 "Dictionnaire de la langue gauloise",
               Lambert 2003 "La langue gauloise", Billy 1993
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
    "magus": "field / market / plain",
    "briga": "hill / fortified place",
    "ritum": "ford",
    "ialo": "clearing / glade",
    "lanum": "plain / open ground",
    "acum": "estate of (< Celtic -āko-)",
    "ialum": "clearing (variant)",
    "bona": "foundation / settlement",
    "nemetum": "sacred grove",
    "randa": "boundary",
    "vern": "alder tree",
    "ate": "place suffix (< -atis)",
}

_PREFIXES: dict[str, str] = {
    "ver": "great / over",
    "nanto": "valley / stream",
    "duro": "fort / door",
    "novio": "new",
    "condo": "confluence",
    "medio": "middle",
    "lugu": "Lugus (deity) / light",
    "roto": "wheel / fort?",
    "argento": "silver / shining",
    "ebu": "yew tree",
    "vindo": "white / blessed",
    "cambo": "bend / curve",
    "briva": "bridge",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "lugdunum": ("lugdunum", "Lyon (< Lugu- + -dunum 'fort of Lugus')"),
    "mediolanum": ("mediolanum", "Milan (< medio- + -lanum 'middle plain')"),
    "rotomagus": ("rotomagus", "Rouen (< roto- + -magus 'great field')"),
    "augustoritum": ("augustoritum", "Limoges (< Augusto- + -ritum 'ford')"),
    "virodunum": ("virodunum", "Verdun (< viro- 'man' + -dunum 'fort')"),
    "noviodunum": ("noviodunum", "several (< novio- 'new' + -dunum 'fort')"),
    "vindobona": ("vindobona", "Vienna (< vindo- 'white' + -bona)"),
    "cambodunum": ("cambodunum", "Kempten (< cambo- 'bend' + -dunum)"),
    "argentoratum": ("argentoratum", "Strasbourg (< argento- 'silver')"),
    "durocortorum": ("durocortorum", "Reims (< duro- + -cortorum)"),
    "condatomagus": ("condatomagus", "La Graufesenque (< condo- + -magus)"),
    "nemausus": ("nemausus", "Nîmes (< nemo- sacred grove)"),
    "eburodunum": ("eburodunum", "Yverdon (< eburo- 'yew' + -dunum)"),
    "brivodurum": ("brivodurum", "Briare? (< briva- + durum)"),
}


class GaulishModule(BaseLanguageModule):
    """Language module for Gaulish (xcg) toponyms."""

    language_code = "xcg"
    language_name = "Gaulish"
    family = "Indo-European"
    branch = "Celtic > Continental Celtic"
    period = "6th c. BCE – 5th c. CE"
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
                    confidence=0.85,
                )
            )
            return results

        # Try suffix matching (longest first)
        matched_suffix = ""
        matched_sfx_meaning = ""
        for sfx, meaning in sorted(_SUFFIXES.items(), key=lambda x: -len(x[0])):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                matched_suffix = sfx
                matched_sfx_meaning = meaning
                break

        # Try prefix matching
        matched_prefix = ""
        matched_pfx_meaning = ""
        for pfx, meaning in sorted(_PREFIXES.items(), key=lambda x: -len(x[0])):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 2:
                matched_prefix = pfx
                matched_pfx_meaning = meaning
                break

        if matched_prefix and matched_suffix:
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    meaning=matched_pfx_meaning,
                    confidence=0.7,
                )
            )
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="infix",
                        confidence=0.4,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=2,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    meaning=matched_sfx_meaning,
                    confidence=0.75,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
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
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    meaning=matched_sfx_meaning,
                    confidence=0.75,
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
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    confidence=0.4,
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
            score += 0.75
            evidence.append(f"Known Gaulish toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.4
                evidence.append(f"Gaulish suffix -{sfx}")
                break

        for pfx in sorted(_PREFIXES, key=len, reverse=True):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 2:
                score += 0.25
                evidence.append(f"Gaulish prefix {pfx}-")
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="gaulish" if score > 0.4 else None,
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
                        cognates=["cf. Old Irish, Welsh"],
                        sources=["Delamarre 2003", "Lambert 2003"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.75,
                        cognates=["cf. Old Irish dún, Welsh din"],
                        sources=["Delamarre 2003"],
                    )
                )
            elif cl in _PREFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_PREFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=[],
                        sources=["Delamarre 2003", "Billy 1993"],
                    )
                )
        return candidates
