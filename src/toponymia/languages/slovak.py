"""Slovak language module for toponymic analysis.

Slovak (slovenčina) is a West Slavic language spoken in Slovakia. Its
toponymy shares roots with Czech but features distinctive -ovce endings
and Tatra/Carpathian mountain appellatives. The landscape of the High
Tatras, Danube lowlands, and mining towns (Banská-) creates a rich
layering of settlement names reflecting German (Zipser), Hungarian,
and Vlach pastoral influences.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SlovakModule(BaseLanguageModule):
    """Language module for Slovak toponyms."""

    language_code = "slk"
    language_name = "Slovak"
    family = "Indo-European"
    branch = "Slavic > West Slavic"
    period = "Modern (1400 CE–present)"
    script = "Latn"

    prefixes = [
        "Nový-",
        "Nová-",
        "Veľký-",
        "Veľká-",
        "Banská-",
        "Dolný-",
        "Horný-",
        "Pod-",
        "Nad-",
        "Stará-",
    ]

    suffixes = [
        "-ov",
        "-ovce",
        "-any",
        "-ová",
        "-ín",
        "-ec",
        "-ice",
        "-ovo",
        "-ík",
        "-ka",
    ]

    stems = [
        "hrad",
        "hora",
        "vrch",
        "potok",
        "bystrica",
        "lúka",
        "dolina",
        "breza",
        "dub",
        "lipa",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "nový": "new",
            "nová": "new (fem.)",
            "veľký": "great",
            "veľká": "great (fem.)",
            "banská": "mining (fem.)",
            "dolný": "lower",
            "horný": "upper",
            "pod": "below",
            "nad": "above",
            "stará": "old (fem.)",
            "ov": "possessive (masc.)",
            "ovce": "settlement of people",
            "any": "inhabitants",
            "ová": "possessive (fem.)",
            "ín": "possessive suffix",
            "hrad": "castle",
            "hora": "mountain",
            "vrch": "hill, peak",
            "potok": "stream",
            "bystrica": "swift stream",
            "dolina": "valley",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Slovak toponym into morphological components."""
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
        """Classify whether a name form belongs to Slovak."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Slovak suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Slovak prefix {prefix}-")
                score += 0.25
                break

        slovak_markers = ["ľ", "ŕ", "ĺ", "ô", "ä"]
        for marker in slovak_markers:
            if marker in form_lower:
                evidence.append(f"Slovak-specific grapheme '{marker}'")
                score += 0.25
                break

        if "ovce" in form_lower:
            evidence.append("Distinctive Slovak -ovce ending")
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
            "hrad": ("*gordъ", "fortified place", ["Cz. hrad", "Pl. gród"]),
            "hora": ("*gora", "mountain", ["Cz. hora", "Pl. góra"]),
            "bystrica": ("*bystrъ", "swift (stream)", ["Cz. bystřice", "Pl. bystrzyca"]),
            "vrch": ("*vьrxъ", "peak, top", ["Cz. vrch", "Ru. verx"]),
            "dolina": ("*dolina", "valley", ["Cz. dolina", "Pl. dolina"]),
            "potok": ("*potokъ", "stream", ["Cz. potok", "Pl. potok"]),
            "lipa": ("*lipa", "linden tree", ["Cz. lípa", "De. Leipzig"]),
            "banská": ("*banja", "mine (< Lat. balneum)", ["Hu. bánya"]),
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
                        sources=["Stanislav, Slovenský juh v stredoveku"],
                    )
                )
        return candidates
