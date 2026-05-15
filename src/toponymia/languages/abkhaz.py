"""Abkhaz language module for toponymic analysis.

Abkhaz (Аԥсуа бызшәа, abk) is a Northwest Caucasian (Abkhaz-Adyghe) language
spoken in Abkhazia (Georgia/disputed territory). Noted for extremely complex
phonology (58+ consonants, only 2 vowels). Toponymic patterns: prefix A-
(definite/possessive), suffixes -ra (place of), -ta (locative), -aa (pluralizer).
Key toponyms: Aqwa (Sukhumi), Pitsunda, Gagra.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AbkhazModule(BaseLanguageModule):
    """Language module for Abkhaz toponyms."""

    language_code = "abk"
    language_name = "Abkhaz"
    family = "Northwest Caucasian"
    branch = "Abkhaz-Adyghe > Abkhaz-Abaza"
    period = "Modern (1800 CE–present)"
    script = "Cyrl"

    prefixes = [
        "A-",
        "Aa-",
        "La-",
    ]

    suffixes = [
        "-ra",
        "-ta",
        "-aa",
        "-rta",
        "-kwa",
        "-psh",
        "-tha",
    ]

    stems = [
        "aqw",
        "psa",
        "dzy",
        "rsh",
        "gw",
        "pshy",
        "kyt",
        "amra",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "a": "definite article / possessive prefix",
            "aa": "plural / collective prefix",
            "la": "diminutive prefix",
            "ra": "place of, abstract noun",
            "ta": "locative (in, at)",
            "rta": "place of (compound locative)",
            "kwa": "settlement, village",
            "psh": "water (related)",
            "tha": "god, sacred",
            "aqw": "white / bright (cf. Aqwa = Sukhumi)",
            "psa": "water, river",
            "dzy": "water, spring",
            "rsh": "forest, wooded area",
            "gw": "heart, centre",
            "pshy": "gorge, ravine",
            "kyt": "village, settlement",
            "amra": "sun",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Abkhaz toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 2:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.6,
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
                        confidence=0.65,
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
        """Classify whether a name form belongs to Abkhaz."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Abkhaz suffix -{suffix}")
                score += 0.3
                break

        if form_lower.startswith("a") and len(form_lower) > 3:
            evidence.append("Abkhaz definite prefix a-")
            score += 0.15

        abkhaz_clusters = ["qw", "gw", "dz", "psh", "tsh", "dzh"]
        for cl in abkhaz_clusters:
            if cl in form_lower:
                evidence.append(f"Abkhaz consonant cluster '{cl}'")
                score += 0.2
                break

        known_stems = ["aqw", "gagr", "pitsund", "psou", "bzyb"]
        for stem in known_stems:
            if stem in form_lower:
                evidence.append(f"Known Abkhaz toponym stem '{stem}'")
                score += 0.3
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
            "aqw": ("aqwa", "white, bright", ["Abaza aqwa"]),
            "psa": ("apsa", "water, river", ["Ubykh psa"]),
            "ra": ("-ra", "place of (abstract nominalizer)", []),
            "ta": ("-ta", "locative (in, at)", []),
            "gagr": ("gagra", "possibly 'coast, shore'", []),
            "amra": ("amra", "sun", ["Abaza amra"]),
            "tha": ("antswa/tha", "god, sacred place", ["Adyghe tha"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower().rstrip("-")
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=cognates,
                        sources=["Chirikba, A Dictionary of Common Abkhaz"],
                    )
                )
        return candidates
