"""Serbian language module for toponymic analysis.

Serbian (српски/srpski) is a South Slavic language using both Cyrillic
and Latin scripts. Its toponymy features characteristic -ovo/-evo
possessive endings, -grad 'city' compounds, and -ac/-ica settlement
suffixes. Belgrade (Beograd = 'white city') exemplifies the descriptive
Slavic compound pattern. Ottoman Turkish and older Illyrian/Thracian
substrate layers are present in the southern regions.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SerbianModule(BaseLanguageModule):
    """Language module for Serbian toponyms."""

    language_code = "srp"
    language_name = "Serbian"
    family = "Indo-European"
    branch = "Slavic > South Slavic > Western"
    period = "Modern (1100 CE–present)"
    script = "Latn"

    prefixes = [
        "Beo-",
        "Novo-",
        "Staro-",
        "Veliko-",
        "Malo-",
        "Gornji-",
        "Donji-",
        "Pod-",
        "Pri-",
        "Beli-",
    ]

    suffixes = [
        "-ovo",
        "-evo",
        "-ac",
        "-ica",
        "-grad",
        "-ane",
        "-ani",
        "-ište",
        "-ovac",
        "-nik",
    ]

    stems = [
        "grad",
        "selo",
        "polje",
        "gora",
        "voda",
        "reka",
        "brod",
        "kamen",
        "dub",
        "beo",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "beo": "white",
            "novo": "new",
            "staro": "old",
            "veliko": "great",
            "malo": "small",
            "gornji": "upper",
            "donji": "lower",
            "pod": "below",
            "pri": "near",
            "beli": "white",
            "ovo": "possessive (masc.)",
            "evo": "possessive (palatal)",
            "ac": "settlement suffix",
            "ica": "diminutive / river",
            "grad": "city, fortification",
            "ane": "inhabitants (plural)",
            "ište": "place of",
            "ovac": "person from",
            "selo": "village",
            "polje": "field",
            "gora": "mountain",
            "reka": "river",
            "brod": "ford",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Serbian toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 1:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="compound_modifier",
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

        # Check for compound with -grad
        if "grad" in form_lower and form_lower.endswith("grad"):
            modifier = form[: len(form) - 4]
            if modifier:
                results.append(
                    SegmentationResult(
                        component=modifier,
                        position=0,
                        morph_type="compound_modifier",
                        confidence=0.6,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[-4:],
                        position=1,
                        morph_type="compound_head",
                        lemma="grad",
                        meaning="city",
                        confidence=0.8,
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
        """Classify whether a name form belongs to Serbian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Serbian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Serbian prefix {prefix}-")
                score += 0.25
                break

        serbian_markers = ["đ", "lj", "nj", "dž"]
        for marker in serbian_markers:
            if marker in form_lower:
                evidence.append(f"Serbian phoneme marker '{marker}'")
                score += 0.2
                break

        if form_lower.endswith("grad"):
            evidence.append("Compound with -grad 'city'")
            score += 0.25

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "grad": ("*gordъ", "city, fortification", ["Cz. hrad", "Ru. gorod"]),
            "beo": ("*bělъ", "white", ["Ru. belyj", "Bg. bjal"]),
            "selo": ("*selo", "village", ["Bg. selo", "Cz. selo"]),
            "polje": ("*polje", "field", ["Sl. polje", "Cz. pole"]),
            "gora": ("*gora", "mountain", ["Sl. gora", "Cz. hora"]),
            "reka": ("*rěka", "river", ["Bg. reka", "Cz. řeka"]),
            "brod": ("*brodъ", "ford", ["Cz. brod", "Pl. bród"]),
            "novo": ("*novъ", "new", ["Cz. nový", "Ru. novyj"]),
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
                        sources=["Skok, Etimologijski rječnik"],
                    )
                )
        return candidates
