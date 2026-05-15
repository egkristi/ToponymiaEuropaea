"""Manx language module for toponymic analysis.

Manx (Gaelg) is a Goidelic Celtic language of the Isle of Man, revived in
the 20th century after the last native speaker died in 1974. Manx toponymy
shows a unique mixture of Gaelic and Norse elements, reflecting Norse rule
from the 9th–13th centuries. Key prefixes: Balla- (farmstead), Kirk-
(church, from ON kirkja), Lax- (salmon, from ON lax). The Norse overlay
on a Celtic substrate creates distinctive compound names.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ManxModule(BaseLanguageModule):
    """Language module for Manx toponyms."""

    language_code = "glv"
    language_name = "Manx"
    family = "Indo-European"
    branch = "Celtic > Goidelic"
    period = "Medieval–Modern (1000 CE–present, revived 1930s)"
    script = "Latn"

    prefixes = [
        "Balla-",
        "Bally-",
        "Kirk-",
        "Lax-",
        "Knock-",
        "Snaefell-",
        "Creg-",
        "Kione-",
        "Cashtal-",
        "Cronk-",
    ]

    suffixes = [
        "-ey",
        "-by",
        "-wick",
        "-dale",
        "-ness",
        "-agh",
        "-ee",
    ]

    stems = [
        "balla",
        "cronk",
        "creg",
        "glion",
        "lhergy",
        "slieau",
        "ushtey",
        "mooar",
        "beg",
        "doo",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "balla": "farmstead, place",
            "bally": "farmstead (anglicized)",
            "kirk": "church (< ON kirkja)",
            "lax": "salmon (< ON lax)",
            "knock": "hill (< cnoc)",
            "creg": "rock, crag",
            "kione": "head, end",
            "cashtal": "castle",
            "cronk": "hill",
            "ey": "island (< ON ey)",
            "by": "farmstead (< ON bý)",
            "wick": "bay (< ON vík)",
            "dale": "valley (< ON dalr)",
            "ness": "headland (< ON nes)",
            "agh": "place (adjectival)",
            "glion": "valley, glen",
            "lhergy": "slope",
            "slieau": "mountain",
            "ushtey": "water",
            "mooar": "large",
            "beg": "small",
            "doo": "black",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Manx toponym into morphological components."""
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
                        confidence=0.75,
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
        """Classify whether a name form belongs to Manx."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Manx prefix {prefix}-")
                score += 0.35
                break

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Norse-Manx suffix -{suffix}")
                score += 0.25
                break

        manx_elements = ["cronk", "creg", "glion", "slieau", "lhergy"]
        for elem in manx_elements:
            if elem in form_lower:
                evidence.append(f"Manx Gaelic element '{elem}'")
                score += 0.3
                break

        if "lh" in form_lower or "gh" in form_lower:
            evidence.append("Manx orthographic feature")
            score += 0.15

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "balla": ("*baile", "farmstead, place", ["Ir. baile", "ScGael. baile"]),
            "kirk": ("*kirkja", "church (ON loan)", ["ON kirkja", "Sco. kirk"]),
            "lax": ("*lax", "salmon (ON loan)", ["ON lax", "Nw. laks"]),
            "cronk": ("*cnoc", "hill", ["Ir. cnoc", "ScGael. cnoc"]),
            "creg": ("*creag", "rock", ["Ir. creag", "ScGael. creag"]),
            "glion": ("*gleann", "valley", ["Ir. gleann", "ScGael. gleann"]),
            "slieau": ("*sliabh", "mountain", ["Ir. sliabh", "ScGael. sliabh"]),
            "ey": ("*ey", "island (ON)", ["ON ey", "Nw. øy"]),
            "by": ("*bý", "farmstead (ON)", ["ON býr", "Da. by"]),
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
                        sources=["Kneen, Place-Names of the Isle of Man"],
                    )
                )
        return candidates
