"""Kashubian language module for toponymic analysis.

Kashubian (kaszëbsczi) is a West Slavic/Pomeranian language spoken in
northeastern Poland in the Gdańsk/Pomerania region. Its toponymy features
-owo, -ino, -ewo endings and reflects Baltic Sea coastal geography. The
language is related to the extinct Pomeranian and Slovincian languages.
Place names preserve archaic Pomeranian features and show both Polish
and German contact layers from historical partitions.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KashubianModule(BaseLanguageModule):
    """Language module for Kashubian toponyms."""

    language_code = "csb"
    language_name = "Kashubian"
    family = "Indo-European"
    branch = "Slavic > West Slavic > Lechitic > Pomeranian"
    period = "Modern (1200 CE–present)"
    script = "Latn"

    prefixes = [
        "Nowi-",
        "Stari-",
        "Wiôldżi-",
        "Mały-",
        "Górny-",
        "Dólny-",
        "Pòd-",
        "Za-",
        "Przë-",
        "Bôłt-",
    ]

    suffixes = [
        "-owo",
        "-ino",
        "-ewo",
        "-ice",
        "-ów",
        "-ëno",
        "-sk",
        "-nia",
        "-owò",
        "-ëce",
    ]

    stems = [
        "gard",
        "góra",
        "wòda",
        "las",
        "pòle",
        "mòrze",
        "rëbë",
        "jezoro",
        "bór",
        "dąb",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "nowi": "new",
            "stari": "old",
            "wiôldżi": "great",
            "mały": "small",
            "górny": "upper",
            "dólny": "lower",
            "pòd": "below",
            "za": "beyond",
            "przë": "near, by",
            "owo": "possessive (neut.)",
            "ino": "possessive",
            "ewo": "possessive variant",
            "ice": "settlement suffix",
            "ów": "possessive (masc.)",
            "ëno": "possessive (Kashubian)",
            "sk": "adjectival / regional",
            "gard": "castle, town",
            "góra": "mountain",
            "wòda": "water",
            "las": "forest",
            "pòle": "field",
            "mòrze": "sea",
            "jezoro": "lake",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Kashubian toponym into morphological components."""
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
        """Classify whether a name form belongs to Kashubian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Kashubian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Kashubian prefix {prefix}-")
                score += 0.25
                break

        kashubian_markers = ["ò", "ë", "ã", "ô", "dż"]
        for marker in kashubian_markers:
            if marker in form_lower:
                evidence.append(f"Kashubian grapheme '{marker}'")
                score += 0.3
                break

        if "szë" in form_lower or "żë" in form_lower:
            evidence.append("Distinctive Kashubian orthography")
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
            "gard": ("*gordъ", "castle, town", ["Pl. gród", "Cz. hrad"]),
            "góra": ("*gora", "mountain", ["Pl. góra", "Cz. hora"]),
            "wòda": ("*voda", "water", ["Pl. woda", "Cz. voda"]),
            "las": ("*lěsъ", "forest", ["Pl. las", "Cz. les"]),
            "pòle": ("*polje", "field", ["Pl. pole", "Cz. pole"]),
            "mòrze": ("*morje", "sea", ["Pl. morze", "Ru. more"]),
            "jezoro": ("*ezero", "lake", ["Pl. jezioro", "Ru. ozero"]),
            "dąb": ("*dǫbъ", "oak", ["Pl. dąb", "Cz. dub"]),
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
                        confidence=0.65,
                        cognates=cognates,
                        sources=["Treder, Nazwy miejscowe Pomorza Gdańskiego"],
                    )
                )
        return candidates
