"""Lower Sorbian language module for toponymic analysis.

Lower Sorbian (dolnoserbšćina) is a critically endangered West Slavic
language spoken in Brandenburg, Germany, in the region of Lower Lusatia.
Its toponymy features -ow, -yn, -ice suffixes and German-Sorbian dual
naming (Cottbus/Chóśebuz, Lübben/Lubin). The language shows distinct
phonological differences from Upper Sorbian, reflected in toponymic
forms. Many Brandenburg place names are of Sorbian origin.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LowerSorbianModule(BaseLanguageModule):
    """Language module for Lower Sorbian toponyms."""

    language_code = "dsb"
    language_name = "Lower Sorbian"
    family = "Indo-European"
    branch = "Slavic > West Slavic > Sorbian"
    period = "Modern (1200 CE–present)"
    script = "Latn"

    prefixes = [
        "Nowy-",
        "Stary-",
        "Wjeliki-",
        "Mały-",
        "Górny-",
        "Dólny-",
        "Pod-",
        "Nad-",
        "Pśi-",
        "Za-",
    ]

    suffixes = [
        "-ow",
        "-yn",
        "-ice",
        "-ow",
        "-in",
        "-awa",
        "-nica",
        "-any",
        "-ojce",
        "-nik",
    ]

    stems = [
        "grod",
        "góra",
        "wóda",
        "las",
        "pólo",
        "dub",
        "lipa",
        "rěka",
        "kamjeń",
        "brjaza",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "nowy": "new",
            "stary": "old",
            "wjeliki": "great",
            "mały": "small",
            "górny": "upper",
            "dólny": "lower",
            "pod": "below",
            "nad": "above",
            "pśi": "near",
            "za": "beyond",
            "ow": "possessive (masc.)",
            "yn": "possessive suffix",
            "ice": "settlement suffix",
            "in": "possessive suffix",
            "awa": "place / river suffix",
            "nica": "river / place dim.",
            "any": "inhabitants of",
            "grod": "castle",
            "góra": "mountain",
            "wóda": "water",
            "las": "forest",
            "pólo": "field",
            "dub": "oak",
            "lipa": "linden tree",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Lower Sorbian toponym into morphological components."""
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
        """Classify whether a name form belongs to Lower Sorbian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Lower Sorbian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Lower Sorbian prefix {prefix}-")
                score += 0.25
                break

        sorbian_markers = ["ś", "ź", "ó", "pś", "ŕ"]
        for marker in sorbian_markers:
            if marker in form_lower:
                evidence.append(f"Lower Sorbian grapheme '{marker}'")
                score += 0.25
                break

        if "šc" in form_lower or "ójc" in form_lower:
            evidence.append("Distinctive Lower Sorbian cluster")
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
            "grod": ("*gordъ", "castle, fortification", ["HSb. hrod", "Cz. hrad"]),
            "góra": ("*gora", "mountain", ["HSb. hora", "Pl. góra"]),
            "wóda": ("*voda", "water", ["HSb. woda", "Pl. woda"]),
            "las": ("*lěsъ", "forest", ["Pl. las", "Cz. les"]),
            "dub": ("*dǫbъ", "oak", ["HSb. dub", "Pl. dąb"]),
            "lipa": ("*lipa", "linden tree", ["HSb. lipa", "Pl. lipa"]),
            "pólo": ("*polje", "field", ["HSb. polo", "Pl. pole"]),
            "brjaza": ("*berza", "birch", ["HSb. brěza", "Pl. brzoza"]),
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
