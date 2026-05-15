"""Ancient Ligurian language module for toponymic analysis.

Ancient Ligurian (xlg) is a pre-Indo-European or early Indo-European language
spoken in NW Italy and SE France before the Roman conquest. Major substrate
in Liguria, Piedmont, and Provence. Distinguished from modern Ligurian
(Romance dialect).

Toponymic hallmarks:
- Suffixes: -asco/-asca, -osco/-usco, -inco/-inca, -entia
- River names: elements in -asco, -entum
- Massive substrate in Liguria/Piedmont/Provence/Catalonia
- Place-names: Genua (Genoa), Albintimilium, Dertona (Tortona)

Key references: Lamboglia 1941, De Bernardo Stempel 2000, Petracco Sicardi 1981
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

_SUFFIXES: dict[str, str] = {
    "asco": "place / topographic suffix",
    "asca": "place / topographic suffix (fem.)",
    "osco": "place / topographic suffix",
    "usco": "place / topographic suffix",
    "inco": "diminutive / place suffix",
    "inca": "diminutive / place suffix (fem.)",
    "entia": "river / water suffix",
    "ela": "diminutive suffix",
}

_KNOWN_ELEMENTS: dict[str, tuple[str, str]] = {
    "genua": ("genua", "Genoa (< *genu- 'knee, bend'?)"),
    "albintimilium": ("albintimilium", "Ventimiglia (< *alb- white + *timilium)"),
    "dertona": ("dertona", "Tortona (< *dert- oak?)"),
    "pollentia": ("pollentia", "Pollenzo (< *pol- + -entia)"),
    "segesta": ("segesta", "possibly Ligurian origin"),
    "vercellae": ("vercellae", "Vercelli (< *ver- + -cellae)"),
    "hasta": ("hasta", "Asti (Ligurian substrate)"),
    "taurasia": ("taurasia", "Turin area (< *taur- mountain?)"),
    "nicaea": ("nicaea", "Nice (< *nik- ?)"),
    "massalia": ("massalia", "Marseille (disputed: Ligurian or Phocaean)"),
}

_LIGURIAN_MARKERS = {"sc", "nk", "nt"}  # consonant clusters typical of substrate


class AncientLigurianModule(BaseLanguageModule):
    """Language module for Ancient Ligurian (xlg) toponyms."""

    language_code = "xlg"
    language_name = "Ancient Ligurian"
    family = "Pre-IE or early IE (debated)"
    branch = "NW Mediterranean substrate"
    period = "Before Roman conquest (pre-2nd c. BCE)"
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
            evidence.append(f"Known Ancient Ligurian toponym: {fl}")

        for sfx in sorted(_SUFFIXES, key=len, reverse=True):
            if fl.endswith(sfx) and len(fl) > len(sfx) + 1:
                score += 0.35
                evidence.append(f"Ligurian suffix -{sfx}")
                break

        # -asco/-asca is a very strong Ligurian marker
        if ("asco" in fl or "asca" in fl) and not any(
            "-asco" in e or "-asca" in e for e in evidence
        ):
            score += 0.15
            evidence.append("Contains -asco/-asca (strong Ligurian indicator)")

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="ancient-ligurian" if score > 0.4 else None,
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
                        cognates=[],
                        sources=["Petracco Sicardi 1981", "De Bernardo Stempel 2000"],
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
                        sources=["Lamboglia 1941"],
                    )
                )
        return candidates
