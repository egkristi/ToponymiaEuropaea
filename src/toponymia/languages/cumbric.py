"""Cumbric language module for toponymic analysis.

Cumbric (xcb) is a Brittonic Celtic language spoken in N.England and
S.Scotland (6th–12th c. CE). Closely related to Welsh and Cornish.
The last Brittonic language of the "Old North" (Yr Hen Ogledd).
Key for understanding place-names in Cumbria, Lancashire, Strathclyde,
and parts of S.Scotland.

Toponymic hallmarks:
- Prefixes: Pen- (head/hill), Caer- (fort), Llan- (enclosure/church)
- Elements: pol/pwll (pool), coed (wood), tref (homestead), aber (river mouth)
- Place-names: Penrith, Carlisle (< Caer Luel), Lanark (< llannerch)
- Counting system in "yan tan tethera" shepherds' tallies

Key references: Breeze 2002, Jackson 1953 "Language and History in Early
               Britain", Padel 2013
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_PREFIXES: dict[str, str] = {
    "pen": "head / hill / top",
    "caer": "fort / fortified place",
    "llan": "enclosure / church",
    "aber": "river mouth / confluence",
    "tref": "homestead / settlement",
    "pol": "pool / lake",
    "coed": "wood / forest",
    "cum": "valley (< cwm)",
    "gled": "clearing?",
    "blen": "head of a valley (< blaen)",
    "car": "fort (reduced form of caer)",
    "eccles": "church (< Latin ecclesia via Brittonic)",
}

_SUFFIXES: dict[str, str] = {
    "rith": "ford (< rhyd)",
    "wath": "ford (< gwâth?)",
    "ard": "height / high ground",
    "ock": "diminutive",
    "erch": "glade / clearing (< llannerch)",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "penrith": ("penrith", "Penrith (< pen 'hill' + rhyd 'ford')"),
    "carlisle": ("carlisle", "Carlisle (< Caer Luel 'fort of Luel')"),
    "lanark": ("lanark", "Lanark (< llannerch 'glade')"),
    "cumbria": ("cumbria", "Cumbria (< *Combrogi 'fellow countrymen')"),
    "glasgow": ("glasgow", "Glasgow (< glas cau 'green hollow'?)"),
    "blencathra": ("blencathra", "< blaen + cadair 'summit of the chair'"),
    "pendle": ("pendle", "Pendle (< pen + hill, tautological)"),
    "cardunneth": ("cardunneth", "< caer + *duno- + -eth"),
    "ecclefechan": ("ecclefechan", "< eccles + *bechan 'little church'"),
    "aberfoyle": ("aberfoyle", "< aber 'confluence' + phuill 'pool'"),
    "dunbar": ("dunbar", "< din bar 'summit fort'"),
    "traquair": ("traquair", "< tref + cwaer 'homestead on Quair Water'"),
}


class CumbricModule(BaseLanguageModule):
    """Language module for Cumbric (xcb) toponyms."""

    language_code = "xcb"
    language_name = "Cumbric"
    family = "Indo-European"
    branch = "Celtic > Brittonic"
    period = "6th–12th c. CE"
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
                    confidence=0.8,
                )
            )
            return results

        # Try prefix matching (most common Brittonic pattern)
        matched_prefix = ""
        matched_pfx_meaning = ""
        for pfx, meaning in sorted(_PREFIXES.items(), key=lambda x: -len(x[0])):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 1:
                matched_prefix = pfx
                matched_pfx_meaning = meaning
                break

        matched_suffix = ""
        matched_sfx_meaning = ""
        for sfx, meaning in sorted(_SUFFIXES.items(), key=lambda x: -len(x[0])):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                matched_suffix = sfx
                matched_sfx_meaning = meaning
                break

        if matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="prefix",
                    lemma=matched_prefix,
                    meaning=matched_pfx_meaning,
                    confidence=0.7,
                )
            )
            remainder = form[len(matched_prefix) :]
            if matched_suffix and remainder.lower().endswith(matched_suffix):
                inner = remainder[: len(remainder) - len(matched_suffix)]
                if inner:
                    results.append(
                        SegmentationResult(
                            component=inner,
                            position=1,
                            morph_type="stem",
                            confidence=0.4,
                        )
                    )
                results.append(
                    SegmentationResult(
                        component=remainder[len(remainder) - len(matched_suffix) :],
                        position=2,
                        morph_type="suffix",
                        lemma=matched_suffix,
                        meaning=matched_sfx_meaning,
                        confidence=0.6,
                    )
                )
            else:
                results.append(
                    SegmentationResult(
                        component=remainder,
                        position=1,
                        morph_type="stem",
                        confidence=0.5,
                    )
                )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
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
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    meaning=matched_sfx_meaning,
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
            evidence.append(f"Known Cumbric toponym: {fl}")

        for pfx in sorted(_PREFIXES, key=len, reverse=True):
            if fl.startswith(pfx) and len(fl) > len(pfx) + 1:
                score += 0.4
                evidence.append(f"Brittonic prefix {pfx}- (< Welsh {pfx})")
                break

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.2
                evidence.append(f"Cumbric suffix -{sfx}")
                break

        # Eccles- is a strong Brittonic marker (church < ecclesia)
        if fl.startswith("eccles"):
            score += 0.3
            evidence.append("eccles- element (Brittonic church name)")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="cumbric" if score > 0.4 else None,
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
                        cognates=["cf. Welsh", "cf. Cornish"],
                        sources=["Jackson 1953", "Breeze 2002"],
                    )
                )
            elif cl in _PREFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_PREFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=[f"Welsh {cl}"],
                        sources=["Padel 2013"],
                    )
                )
            elif cl in _SUFFIXES:
                candidates.append(
                    EtymologyCandidate(
                        lemma=cl,
                        meaning=_SUFFIXES[cl],
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=["cf. Welsh cognate"],
                        sources=["Jackson 1953"],
                    )
                )
        return candidates
