"""Maltese language module for toponymic analysis.

Maltese (Malti, mlt) is a Semitic language descended from Siculo-Arabic with
heavy Italian/Sicilian and English superstrate. It is the only Semitic
language written in the Latin script. Maltese toponymy features: Ħal-
(village, < Ar. ḥāl), San/Santa (saint, Italian), Ta'- (of, possessive).
Other elements: -ija (country/place suffix), -in (plural). The dense
settlement of the Maltese islands creates concentrated, layered toponymy.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MalteseModule(BaseLanguageModule):
    """Language module for Maltese toponyms."""

    language_code = "mlt"
    language_name = "Maltese"
    family = "Afro-Asiatic"
    branch = "Semitic > Arabic > Siculo-Arabic"
    period = "Modern (1400 CE–present)"
    script = "Latn"

    prefixes = [
        "Ħal-",
        "Hal-",
        "San-",
        "Santa-",
        "Ta'-",
        "Tal-",
        "Tas-",
        "Il-",
        "L-",
        "Wied-",
    ]

    suffixes = [
        "-ija",
        "-in",
        "-a",
        "-i",
        "-iet",
        "-ija",
        "-na",
        "-li",
    ]

    stems = [
        "qala",
        "mdina",
        "rabat",
        "birgu",
        "wied",
        "blat",
        "għar",
        "żebbuġ",
        "qormi",
        "marsa",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "ħal": "village, settlement (< Ar. ḥāl)",
            "hal": "village (simplified spelling)",
            "san": "saint (masc., < It.)",
            "santa": "saint (fem., < It.)",
            "ta'": "of, belonging to",
            "tal": "of the",
            "tas": "of the",
            "il": "the (definite article)",
            "wied": "valley (< Ar. wādī)",
            "ija": "place/country suffix",
            "in": "plural marker",
            "qala": "bay, inlet",
            "mdina": "city (< Ar. madīna)",
            "rabat": "suburb (< Ar. rabāṭ)",
            "blat": "rock, slab",
            "għar": "cave (< Ar. ghār)",
            "marsa": "harbour (< Ar. marsā)",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Maltese toponym into morphological components."""
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
                        lemma=prefix.lower(),
                        meaning=self._element_meaning(prefix.lower()),
                        confidence=0.8,
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
                        confidence=0.6,
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
        """Classify whether a name form belongs to Maltese."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Maltese prefix {prefix}-")
                score += 0.35
                break

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Maltese suffix -{suffix}")
                score += 0.2
                break

        maltese_chars = ["ħ", "għ", "ż", "ċ"]
        for ch in maltese_chars:
            if ch in form_lower:
                evidence.append(f"Maltese-specific character '{ch}'")
                score += 0.3
                break

        maltese_elements = ["mdina", "rabat", "marsa", "wied", "qala"]
        for elem in maltese_elements:
            if elem in form_lower:
                evidence.append(f"Maltese toponymic element '{elem}'")
                score += 0.25
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
            "ħal": ("ḥāl", "state, condition > village", ["Ar. ḥāl"]),
            "wied": ("wādī", "valley, watercourse", ["Ar. wādī", "Sic. vaddì"]),
            "mdina": ("madīna", "city", ["Ar. madīna", "Heb. medina"]),
            "rabat": ("rabāṭ", "fortified suburb", ["Ar. ribāṭ"]),
            "marsa": ("marsā", "harbour, anchorage", ["Ar. marsā"]),
            "għar": ("ghār", "cave", ["Ar. ghār"]),
            "qala": ("qal'a", "bay, fortress", ["Ar. qal'a"]),
            "blat": ("balāṭ", "rock, flagstone", ["Ar. balāṭ", "Lat. palatium"]),
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
                        sources=["Aquilina, Maltese-English Dictionary"],
                    )
                )
        return candidates
