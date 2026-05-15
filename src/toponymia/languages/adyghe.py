"""Adyghe (Circassian) language module for toponymic analysis.

Adyghe (адыгабзэ, ady) is a Northwest Caucasian language of the Circassian
branch, spoken in the Circassia region (Russia: Adygea, Kabardino-Balkaria,
Karachay-Cherkessia) and by a large diaspora (post-1864 exile). Key toponymic
elements: pse/ps (water), mez (forest), qo (valley), -habl (village),
-ko (son of). Major substrate in Black Sea coast names.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AdygheModule(BaseLanguageModule):
    """Language module for Adyghe (Circassian) toponyms."""

    language_code = "ady"
    language_name = "Adyghe"
    family = "Northwest Caucasian"
    branch = "Abkhaz-Adyghe > Circassian"
    period = "Modern (1800 CE–present)"
    script = "Cyrl"

    prefixes = [
        "Pshy-",
        "Psə-",
        "Mez-",
    ]

    suffixes = [
        "-habl",
        "-ko",
        "-qo",
        "-ape",
        "-shch",
        "-yable",
        "-ps",
    ]

    stems = [
        "pse",
        "mez",
        "qo",
        "wunae",
        "bgy",
        "oshkh",
        "chyg",
        "shkhwa",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "pshy": "river, flowing water (prefix)",
            "psə": "water (prefix form)",
            "mez": "forest",
            "habl": "village, settlement",
            "ko": "son of (patronymic)",
            "qo": "valley, ravine",
            "ape": "cliff, precipice",
            "shch": "head, top (peak)",
            "yable": "apple (orchard place)",
            "ps": "water (suffix form)",
            "pse": "water, river",
            "wunae": "house, home",
            "bgy": "many, much",
            "oshkh": "mountain peak",
            "chyg": "tree",
            "shkhwa": "stone, rock",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Adyghe toponym into morphological components."""
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
        """Classify whether a name form belongs to Adyghe."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Adyghe suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 2:
                evidence.append(f"Adyghe prefix {prefix}-")
                score += 0.25
                break

        circassian_clusters = ["psh", "shch", "bzh", "tsh", "schw", "qw"]
        for cl in circassian_clusters:
            if cl in form_lower:
                evidence.append(f"Circassian consonant cluster '{cl}'")
                score += 0.2
                break

        known_stems = ["maykop", "psekup", "tuaps", "shaps", "adyg"]
        for stem in known_stems:
            if stem in form_lower:
                evidence.append(f"Known Circassian toponym stem '{stem}'")
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
            "pse": ("pse/ps", "water, river", ["Kabardian psy", "Ubykh ps"]),
            "mez": ("mez", "forest", ["Kabardian maz"]),
            "qo": ("qo", "valley, ravine", ["Kabardian qwə"]),
            "habl": ("-ḥabl", "village, settlement", []),
            "ko": ("-qo", "son of (patronymic)", []),
            "oshkh": ("wašxə", "mountain peak", ["Kabardian wašxə"]),
            "shkhwa": ("šxwə", "stone, rock", []),
            "ps": ("pse", "water (suffix form)", ["Kabardian psy"]),
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
                        sources=["Shagirov, Etymological Dictionary of Adyghe"],
                    )
                )
        return candidates
