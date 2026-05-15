"""Upper Sorbian language module for toponymic analysis.

Upper Sorbian (hornjoserbšćina) is a West Slavic minority language spoken
in Saxony, Germany, in the region of Upper Lusatia around Bautzen/Budyšin.
Its toponymy features -ow, -icy, -in suffixes and exists in parallel with
German forms (Bautzen/Budyšin, Dresden/Drježdźany). Many German place
names in Saxony are actually Germanized Sorbian originals, reflecting the
medieval Slavic settlement of the region.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class UpperSorbianModule(BaseLanguageModule):
    """Language module for Upper Sorbian toponyms."""

    language_code = "hsb"
    language_name = "Upper Sorbian"
    family = "Indo-European"
    branch = "Slavic > West Slavic > Sorbian"
    period = "Modern (1200 CE–present)"
    script = "Latn"

    prefixes = [
        "Nowy-",
        "Stary-",
        "Wulki-",
        "Mały-",
        "Horni-",
        "Delni-",
        "Pod-",
        "Nad-",
        "Při-",
        "Za-",
    ]

    suffixes = [
        "-ow",
        "-icy",
        "-in",
        "-ow",
        "-ec",
        "-ica",
        "-ow",
        "-any",
        "-iny",
        "-nik",
    ]

    stems = [
        "hrod",
        "hora",
        "woda",
        "les",
        "polo",
        "dub",
        "lipa",
        "rěka",
        "kamjeń",
        "brěza",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "nowy": "new",
            "stary": "old",
            "wulki": "great",
            "mały": "small",
            "horni": "upper",
            "delni": "lower",
            "pod": "below",
            "nad": "above",
            "při": "near",
            "za": "beyond",
            "ow": "possessive (masc.)",
            "icy": "inhabitants",
            "in": "possessive suffix",
            "ec": "diminutive",
            "ica": "diminutive / river",
            "any": "inhabitants of",
            "hrod": "castle",
            "hora": "mountain",
            "woda": "water",
            "les": "forest",
            "polo": "field",
            "dub": "oak",
            "lipa": "linden tree",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Upper Sorbian toponym into morphological components."""
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
        """Classify whether a name form belongs to Upper Sorbian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Upper Sorbian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Upper Sorbian prefix {prefix}-")
                score += 0.25
                break

        sorbian_markers = ["ć", "dź", "ě", "ó", "ř"]
        for marker in sorbian_markers:
            if marker in form_lower:
                evidence.append(f"Upper Sorbian grapheme '{marker}'")
                score += 0.25
                break

        if "wj" in form_lower or "šć" in form_lower:
            evidence.append("Distinctive Upper Sorbian cluster")
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
            "hrod": ("*gordъ", "castle, fortification", ["Cz. hrad", "Pl. gród"]),
            "hora": ("*gora", "mountain", ["Cz. hora", "Pl. góra"]),
            "woda": ("*voda", "water", ["Cz. voda", "Pl. woda"]),
            "les": ("*lěsъ", "forest", ["Cz. les", "Pl. las"]),
            "dub": ("*dǫbъ", "oak", ["Cz. dub", "Pl. dąb"]),
            "lipa": ("*lipa", "linden tree", ["Cz. lípa", "De. Leipzig"]),
            "polo": ("*polje", "field", ["Cz. pole", "Pl. pole"]),
            "brěza": ("*berza", "birch", ["Cz. bříza", "Pl. brzoza"]),
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
                        sources=["Eichler, Slawische Ortsnamen zwischen Saale und Neiße"],
                    )
                )
        return candidates
