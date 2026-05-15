"""Czech language module for toponymic analysis.

Czech (čeština) is a West Slavic language spoken in the Czech Republic.
Its toponymy features distinctive háček diacritics (č, š, ž, ř) and the
unique phoneme /ř/. Place names reflect medieval Slavic settlement patterns
with characteristic suffixes (-ov, -ice, -ín) and descriptive prefixes
(Nový, Velký, Pod-, Nad-). The landscape includes Bohemian basin names
and Moravian highland appellatives.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CzechModule(BaseLanguageModule):
    """Language module for Czech toponyms."""

    language_code = "ces"
    language_name = "Czech"
    family = "Indo-European"
    branch = "Slavic > West Slavic"
    period = "Modern (1400 CE–present)"
    script = "Latn"

    prefixes = [
        "Nový-",
        "Nová-",
        "Velký-",
        "Velká-",
        "Pod-",
        "Nad-",
        "Hora-",
        "Dolní-",
        "Horní-",
        "Malá-",
    ]

    suffixes = [
        "-ov",
        "-ova",
        "-ice",
        "-ín",
        "-any",
        "-sko",
        "-ovec",
        "-ík",
        "-ná",
        "-ov",
        "-ec",
        "-ky",
    ]

    stems = [
        "hrad",
        "hora",
        "lhota",
        "brod",
        "most",
        "les",
        "pole",
        "voda",
        "bílý",
        "černý",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "nový": "new",
            "nová": "new (fem.)",
            "velký": "great, large",
            "velká": "great (fem.)",
            "pod": "below, under",
            "nad": "above, over",
            "hora": "mountain",
            "dolní": "lower",
            "horní": "upper",
            "malá": "small (fem.)",
            "ov": "possessive (masc.)",
            "ova": "possessive (fem.)",
            "ice": "settlement suffix",
            "ín": "possessive suffix",
            "any": "inhabitants of",
            "sko": "region, land",
            "hrad": "castle, fortification",
            "brod": "ford",
            "most": "bridge",
            "les": "forest",
            "pole": "field",
            "voda": "water",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Czech toponym into morphological components."""
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
        """Classify whether a name form belongs to Czech."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Czech suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Czech prefix {prefix}-")
                score += 0.25
                break

        czech_markers = ["ř", "ů", "ě"]
        for marker in czech_markers:
            if marker in form_lower:
                evidence.append(f"Czech-specific grapheme '{marker}'")
                score += 0.25
                break

        if any(c in form_lower for c in ["č", "š", "ž"]):
            evidence.append("Háček diacritics present")
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
            "hrad": ("*gordъ", "fortified place", ["Pl. gród", "Ru. gorod"]),
            "hora": ("*gora", "mountain", ["Pl. góra", "Ru. gora"]),
            "brod": ("*brodъ", "ford", ["Pl. bród", "De. Furt"]),
            "most": ("*mostъ", "bridge", ["Pl. most", "Ru. most"]),
            "les": ("*lěsъ", "forest", ["Pl. las", "Ru. les"]),
            "pole": ("*polje", "field", ["Pl. pole", "Ru. pole"]),
            "voda": ("*voda", "water", ["Pl. woda", "Ru. voda"]),
            "nový": ("*novъ", "new", ["Pl. nowy", "Ru. novyj"]),
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
                        sources=["Profous, Místní jména v Čechách"],
                    )
                )
        return candidates
