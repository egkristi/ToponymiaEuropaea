"""Scots language module for toponymic analysis.

Scots (Braid Scots) is a West Germanic Anglic language spoken in Lowland
Scotland and parts of Ulster. NOT to be confused with Scottish Gaelic (Goidelic
Celtic). Scots toponymy features: -toun (town), -brae (hill), -burn (stream),
-glen (valley), -kirk (church), -brig (bridge). It descends from Northumbrian
Old English with Norse and Gaelic substrate influence.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ScotsModule(BaseLanguageModule):
    """Language module for Scots toponyms."""

    language_code = "sco"
    language_name = "Scots"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Anglic"
    period = "Modern (1400 CE–present)"
    script = "Latn"

    prefixes = [
        "Auld-",
        "New-",
        "Wee-",
        "Lang-",
        "East-",
        "West-",
    ]

    suffixes = [
        "-toun",
        "-ton",
        "-brae",
        "-burn",
        "-glen",
        "-kirk",
        "-brig",
        "-muir",
        "-shaw",
        "-haugh",
        "-gate",
        "-wynd",
        "-rigg",
        "-law",
        "-stane",
    ]

    stems = [
        "brae",
        "burn",
        "glen",
        "kirk",
        "brig",
        "muir",
        "haugh",
        "craig",
        "loch",
        "stane",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "auld": "old",
            "new": "new",
            "wee": "small",
            "lang": "long",
            "toun": "town, farmstead",
            "ton": "town, farmstead",
            "brae": "hillside, slope",
            "burn": "stream",
            "glen": "valley",
            "kirk": "church",
            "brig": "bridge",
            "muir": "moor, heath",
            "shaw": "wood, thicket",
            "haugh": "flat ground by river",
            "gate": "road, street",
            "wynd": "narrow lane",
            "rigg": "ridge",
            "law": "rounded hill",
            "stane": "stone",
            "craig": "rock, crag",
            "loch": "lake",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Scots toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 1:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.7,
                    )
                )
                form = form[len(prefix) :]
                form_lower = form.lower()
                break

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                pos = len(results)
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
                        component=form[len(form) - len(suffix) :],
                        position=pos + 1,
                        morph_type="suffix",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.7,
                    )
                )
                return results

        pos = len(results)
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
        """Classify whether a name form belongs to Scots."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Scots suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Scots prefix {prefix}-")
                score += 0.25
                break

        scots_elements = ["brae", "burn", "kirk", "muir", "haugh", "wynd"]
        for elem in scots_elements:
            if elem in form_lower:
                evidence.append(f"Scots element '{elem}'")
                score += 0.25
                break

        scots_spelling = ["ou", "ae", "ui"]
        for sp in scots_spelling:
            if sp in form_lower:
                evidence.append(f"Scots orthography '{sp}'")
                score += 0.15
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "toun": ("*tūnaz", "enclosure, farmstead", ["OE tūn", "En. town"]),
            "burn": ("*brunnō", "stream, spring", ["OE burna", "De. Brunnen"]),
            "kirk": ("*kirikō", "church (< Gk. kyriakon)", ["ON kirkja", "En. church"]),
            "brae": ("ON brá", "brow, hillside", ["ON brá", "Nw. bra"]),
            "muir": ("OE mōr", "moor, wasteland", ["En. moor", "De. Moor"]),
            "glen": ("Gael. gleann", "valley (Celtic loan)", ["Ir. gleann", "Mx. glion"]),
            "law": ("OE hlāw", "burial mound, hill", ["En. low", "barrow"]),
            "haugh": ("OE healh", "corner of land, meadow", ["En. hale"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=cognates,
                        sources=["Scottish National Dictionary"],
                    )
                )
        return candidates
