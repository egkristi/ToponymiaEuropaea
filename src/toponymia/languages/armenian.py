"""Armenian language module for toponymic analysis.

Armenian (Հայերdelays, hye) is an Indo-European language forming its own
branch, spoken primarily in Armenia and diaspora communities. Armenian
toponymy features: -avan (town), -van (place), -bert/-berd (fortress),
-kert (built city), -stan (land). Historical presence in Eastern Anatolia
and the Caucasus with place names spanning millennia (Yerevan, Vanadzor,
Gyumri). Uses a unique alphabet invented by Mesrop Mashtots in 405 CE.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ArmenianModule(BaseLanguageModule):
    """Language module for Armenian toponyms."""

    language_code = "hye"
    language_name = "Armenian"
    family = "Indo-European"
    branch = "Armenian (isolate branch)"
    period = "Modern (1700 CE–present)"
    script = "Armn"

    prefixes = [
        "Nor-",
        "Hin-",
        "Mets-",
        "Pokr-",
        "Verin-",
        "Nerkin-",
    ]

    suffixes = [
        "-avan",
        "-van",
        "-bert",
        "-berd",
        "-kert",
        "-stan",
        "-shen",
        "-ashen",
        "-adzor",
        "-asar",
        "-avan",
        "-ik",
        "-uk",
    ]

    stems = [
        "kar",
        "dzor",
        "sar",
        "jur",
        "lich",
        "sevan",
        "ararat",
        "masis",
        "hrazdan",
        "araks",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "nor": "new",
            "hin": "old, ancient",
            "mets": "great, large",
            "pokr": "small, little",
            "verin": "upper",
            "nerkin": "lower",
            "avan": "town, settlement",
            "van": "place, town",
            "bert": "fortress",
            "berd": "fortress",
            "kert": "built (city)",
            "stan": "land, place",
            "shen": "village, built place",
            "ashen": "built settlement",
            "adzor": "gorge, valley",
            "asar": "hill, mound",
            "kar": "stone",
            "dzor": "gorge, ravine",
            "sar": "mountain",
            "jur": "water",
            "lich": "lake",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Armenian toponym into morphological components."""
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
                        confidence=0.75,
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
        """Classify whether a name form belongs to Armenian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Armenian suffix -{suffix}")
                score += 0.35
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Armenian prefix {prefix}-")
                score += 0.25
                break

        armenian_markers = ["dz", "ts", "sh", "zh"]
        for marker in armenian_markers:
            if marker in form_lower:
                evidence.append(f"Armenian phonetic element '{marker}'")
                score += 0.2
                break

        armenian_stems = ["yere", "gyu", "vana", "ararat", "sevan"]
        for stem in armenian_stems:
            if stem in form_lower:
                evidence.append(f"Armenian toponymic stem '{stem}'")
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
            "avan": ("awan", "town, settlement", ["MArm. awan"]),
            "bert": ("*bhergh-", "fortress, height", ["Pers. bord"]),
            "berd": ("*bhergh-", "fortress", ["Pers. bord", "Geo. -peti"]),
            "kert": ("kert", "built (< kartel 'to build')", ["MArm. kert"]),
            "stan": ("*stāna-", "land, place (Iranian loan)", ["Pers. -stān"]),
            "dzor": ("jor", "gorge, ravine", ["MArm. jor"]),
            "sar": ("sar", "mountain", ["MArm. sar", "Pers. sar 'head'"]),
            "kar": ("k'ar", "stone", ["MArm. k'ar"]),
            "jur": ("ǰur", "water", ["MArm. ǰur"]),
            "shen": ("šēn", "village (< šinել 'to build')", ["MArm. šēn"]),
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
                        sources=["Acharyan, Armenian Etymological Dictionary"],
                    )
                )
        return candidates
