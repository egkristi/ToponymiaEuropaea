"""Laz language module for toponymic analysis.

Laz (Lazuri, lzz) is a Kartvelian (South Caucasian) language spoken along
the Black Sea coast of NE Turkey and W Georgia. Related to Mingrelian (together
forming the Zan branch). Key toponymic patterns: suffixes -i (locative),
-sh (adjectival), -pe (place); elements mta (mountain), tskali/skali (water),
qva (stone). Important substrate in Turkish Black Sea coast toponymy.
~20,000–50,000 speakers, endangered.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LazModule(BaseLanguageModule):
    """Language module for Laz toponyms."""

    language_code = "lzz"
    language_name = "Laz"
    family = "Kartvelian"
    branch = "South Caucasian (Kartvelian) > Zan"
    period = "Modern (1800 CE–present)"
    script = "Latn"

    prefixes = [
        "O-",
        "Me-",
        "Na-",
    ]

    suffixes = [
        "-i",
        "-sh",
        "-pe",
        "-oba",
        "-uri",
        "-oni",
        "-eti",
        "-nt",
    ]

    stems = [
        "mta",
        "skali",
        "qva",
        "didi",
        "tsikhe",
        "xe",
        "ocha",
        "mzgha",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "o": "place of (circumfix prefix)",
            "me": "place where (prefix)",
            "na": "former place (prefix)",
            "i": "locative (at, place)",
            "sh": "adjectival suffix",
            "pe": "place, settlement",
            "oba": "festival / communal place",
            "uri": "adjectival (belonging to)",
            "oni": "place, locality",
            "eti": "land of",
            "nt": "place (settlement suffix)",
            "mta": "mountain",
            "skali": "water (variant of tskali)",
            "qva": "stone, rock",
            "didi": "great, large",
            "tsikhe": "fortress",
            "xe": "river, stream",
            "ocha": "house, dwelling",
            "mzgha": "coast, shore",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Laz toponym into morphological components."""
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
        """Classify whether a name form belongs to Laz."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix) and len(suffix) > 1:
                evidence.append(f"Laz suffix -{suffix}")
                score += 0.25
                break

        laz_clusters = ["tsk", "skh", "ndz", "nts", "mzg"]
        for cl in laz_clusters:
            if cl in form_lower:
                evidence.append(f"Laz consonant cluster '{cl}'")
                score += 0.2
                break

        known_stems = ["ardeş", "arhav", "viçe", "atina", "xopa", "pazar"]
        for stem in known_stems:
            if stem in form_lower:
                evidence.append(f"Known Laz toponym stem '{stem}'")
                score += 0.35
                break

        if form_lower.endswith(("pe", "nt")):
            evidence.append("Laz settlement suffix")
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
            "mta": ("mta", "mountain", ["Georgian mt'a", "Mingrelian nta"]),
            "skali": ("skali/tskali", "water, stream", ["Georgian c'q'ali"]),
            "qva": ("qva", "stone, rock", ["Georgian qva", "Mingrelian qva"]),
            "pe": ("-pe", "place, settlement", ["Mingrelian -pe"]),
            "xe": ("xe", "river, stream", []),
            "tsikhe": ("cixe", "fortress", ["Georgian c'ixe"]),
            "ocha": ("ocha", "house, dwelling", ["Mingrelian ocha"]),
            "sh": ("-sh", "adjectival (belonging to)", ["Mingrelian -sh"]),
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
                        sources=["Klimov, Etymological Dictionary of Kartvelian Languages"],
                    )
                )
        return candidates
