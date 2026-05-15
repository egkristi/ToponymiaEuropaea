"""Bulgarian language module for toponymic analysis.

Bulgarian (български) is a South Slavic language unique for its lack of
a case system and use of a definite article suffix. Its toponymy features
-ovo/-evo possessive endings, -grad compounds, and -ene/-ane inhabitant
plurals. A Thracian substrate layer is visible in hydronyms, while the
Ottoman period left Turkish-origin names (especially in the south). Major
examples: Sofia (< *serdica, Thracian), Plovdiv (< Philippopolis/Pulpudeva).
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class BulgarianModule(BaseLanguageModule):
    """Language module for Bulgarian toponyms."""

    language_code = "bul"
    language_name = "Bulgarian"
    family = "Indo-European"
    branch = "Slavic > South Slavic > Eastern"
    period = "Modern (900 CE–present)"
    script = "Latn"

    prefixes = [
        "Novo-",
        "Staro-",
        "Gorno-",
        "Dolno-",
        "Bjalo-",
        "Črno-",
        "Veliko-",
        "Malo-",
        "Sveti-",
        "Zlatni-",
    ]

    suffixes = [
        "-ovo",
        "-evo",
        "-grad",
        "-ene",
        "-ane",
        "-ica",
        "-ište",
        "-nik",
        "-ec",
        "-ino",
    ]

    stems = [
        "grad",
        "selo",
        "pole",
        "gora",
        "reka",
        "dol",
        "voda",
        "kamen",
        "drvo",
        "zem",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "novo": "new",
            "staro": "old",
            "gorno": "upper",
            "dolno": "lower",
            "bjalo": "white",
            "črno": "black",
            "veliko": "great",
            "malo": "small",
            "sveti": "saint",
            "zlatni": "golden",
            "ovo": "possessive (masc.)",
            "evo": "possessive (palatal)",
            "grad": "city",
            "ene": "inhabitants (pl.)",
            "ane": "inhabitants (pl.)",
            "ica": "diminutive / river",
            "ište": "place of",
            "nik": "agent noun",
            "selo": "village",
            "pole": "field",
            "gora": "mountain, forest",
            "reka": "river",
            "dol": "valley",
            "voda": "water",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Bulgarian toponym into morphological components."""
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

        # Check for -grad compound
        if form_lower.endswith("grad") and len(form_lower) > 4:
            modifier = form[: len(form) - 4]
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
        """Classify whether a name form belongs to Bulgarian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Bulgarian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Bulgarian prefix {prefix}-")
                score += 0.25
                break

        bulgarian_markers = ["ъ", "ь", "щ", "ж"]
        for marker in bulgarian_markers:
            if marker in form_lower:
                evidence.append(f"Bulgarian grapheme '{marker}'")
                score += 0.25
                break

        if form_lower.endswith(("ene", "ane")):
            evidence.append("Bulgarian inhabitant plural suffix")
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
            "grad": ("*gordъ", "city", ["Sr. grad", "Mk. grad"]),
            "selo": ("*selo", "village", ["Sr. selo", "Mk. selo"]),
            "pole": ("*polje", "field", ["Sr. polje", "Mk. pole"]),
            "gora": ("*gora", "mountain", ["Sr. gora", "Mk. gora"]),
            "reka": ("*rěka", "river", ["Sr. reka", "Mk. reka"]),
            "dol": ("*dolъ", "valley", ["Sr. dol", "Mk. dol"]),
            "voda": ("*voda", "water", ["Sr. voda", "Ru. voda"]),
            "novo": ("*novъ", "new", ["Sr. novo", "Ru. novyj"]),
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
                        sources=["Duridanov, Ezikът na trakite"],
                    )
                )
        return candidates
