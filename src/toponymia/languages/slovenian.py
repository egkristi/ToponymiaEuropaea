"""Slovenian language module for toponymic analysis.

Slovenian (slovenščina) is a South Slavic language spoken in Slovenia.
Its toponymy reflects Alpine geography with German, Italian, and Hungarian
contact layers. Distinctive suffixes -je, -ica, -ine mark collective and
settlement names. Ljubljana is etymologized from *ljubiti 'to love' or
possibly a pre-Slavic hydronym. The dual grammatical number and rich
dialectal variation create unique toponymic patterns.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SlovenianModule(BaseLanguageModule):
    """Language module for Slovenian toponyms."""

    language_code = "slv"
    language_name = "Slovenian"
    family = "Indo-European"
    branch = "Slavic > South Slavic > Western"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Nov-",
        "Stari-",
        "Veliki-",
        "Mali-",
        "Pod-",
        "Nad-",
        "Med-",
        "Gornji-",
        "Dolnji-",
        "Sv-",
    ]

    suffixes = [
        "-je",
        "-ica",
        "-ine",
        "-ovo",
        "-nik",
        "-ec",
        "-ek",
        "-ščica",
        "-ane",
        "-ci",
    ]

    stems = [
        "grad",
        "gora",
        "dol",
        "log",
        "brdo",
        "polje",
        "reka",
        "most",
        "drevo",
        "vas",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "nov": "new",
            "stari": "old",
            "veliki": "great",
            "mali": "small",
            "pod": "below",
            "nad": "above",
            "med": "between",
            "gornji": "upper",
            "dolnji": "lower",
            "sv": "saint",
            "je": "collective suffix",
            "ica": "diminutive / river suffix",
            "ine": "place of (plural)",
            "ovo": "possessive",
            "nik": "agent / place noun",
            "ec": "diminutive (masc.)",
            "grad": "castle, town",
            "gora": "mountain",
            "dol": "valley",
            "log": "meadow",
            "brdo": "hill",
            "polje": "field",
            "vas": "village",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Slovenian toponym into morphological components."""
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
        """Classify whether a name form belongs to Slovenian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Slovenian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Slovenian prefix {prefix}-")
                score += 0.25
                break

        slovenian_markers = ["šč", "lj", "nj"]
        for marker in slovenian_markers:
            if marker in form_lower:
                evidence.append(f"Slovenian consonant cluster '{marker}'")
                score += 0.2
                break

        if form_lower.endswith(("ščica", "ščina")):
            evidence.append("Distinctive Slovenian derivational suffix")
            score += 0.2

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "grad": ("*gordъ", "fortified place", ["Sr. grad", "Cz. hrad"]),
            "gora": ("*gora", "mountain", ["Sr. gora", "Cz. hora"]),
            "dol": ("*dolъ", "valley", ["Sr. dol", "Cz. důl"]),
            "log": ("*logъ", "meadow, low ground", ["Ru. lug"]),
            "brdo": ("*bьrdo", "hill", ["Sr. brdo", "Cz. brdo"]),
            "polje": ("*polje", "field", ["Sr. polje", "Cz. pole"]),
            "vas": ("*vьsь", "village", ["Ru. ves'"]),
            "ljub": ("*ljubъ", "beloved", ["Sr. ljub", "Ru. ljubov'"]),
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
                        sources=["Snoj, Etimološki slovar slovenskih zemljepisnih imen"],
                    )
                )
        return candidates
