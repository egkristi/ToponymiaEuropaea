"""Old Saxon language module.

Old Saxon (Old Low German) was spoken in northern Germany from the
8th to 12th century CE. It is the ancestor of Middle Low German and
modern Low German/Plattdeutsch. Major text: the Heliand. Important
for north German toponymy with distinct forms from Old High German.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldSaxonModule(BaseLanguageModule):
    """Language module for Old Saxon toponyms."""

    language_code = "osx"
    language_name = "Old Saxon"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Ingvaeonic"
    period = "8th-12th century CE"
    script = "Latn"

    suffixes = [
        "-hūs",  # house
        "-burg",  # fortification
        "-feld",  # field
        "-stedi",  # place, stead
        "-beke",  # brook
        "-dorp",  # village
        "-borstel",  # farmstead (< bur-stall)
        "-holt",  # wood, grove
        "-büttel",  # dwelling (< bōdal)
        "-horn",  # corner, promontory
        "-heim",  # home
        "-wik",  # settlement, trading place
        "-loh",  # grove, clearing
        "-mar",  # lake, pool
        "-sted",  # place
        "-torp",  # outlying farm
        "-wede",  # ford, crossing
    ]

    prefixes = [
        "Nort-",  # north
        "Sūth-",  # south
        "Ōst-",  # east
        "West-",  # west
        "Nig-",  # new
        "Old-",  # old
        "Grōt-",  # great
        "Lütt-",  # little
        "Wit-",  # white
        "Swart-",  # black
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Saxon toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix.lower()):
                matched_suffix = suffix
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            if stem:
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="compound_modifier",
                        confidence=0.6,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Old Saxon."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.4
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.3
                break

        # Old Saxon vs OHG distinguishing features (no High German shift)
        if any(x in form_lower for x in ["beke", "dorp", "borstel", "büttel"]):
            evidence.append("Ingvaeonic/Low German form (no consonant shift)")
            score += 0.2

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="old-saxon" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "hūs": ("hūs", "house", ["OE hūs", "ON hús", "OHG hūs"]),
            "burg": ("burg", "fortification", ["OE burh", "ON borg"]),
            "feld": ("feld", "open field", ["OE feld", "OHG feld"]),
            "stedi": ("stedi", "place, stead", ["OE stede", "ON staðr"]),
            "beke": ("beki", "brook, stream", ["OE bece", "MLG bēke"]),
            "dorp": ("thorp", "village", ["OE þorp", "ON þorp"]),
            "borstel": ("bur-stall", "farmstead", ["OE burh-steall"]),
            "holt": ("holt", "wood, grove", ["OE holt", "ON holt"]),
            "büttel": ("bōdal", "dwelling, estate", ["ON ból"]),
            "wik": ("wīk", "trading place", ["OE wīc", "Lat. vicus"]),
            "loh": ("lōh", "grove, clearing", ["OE lēah", "OHG lōh"]),
            "torp": ("thorp", "outlying farm", ["OE þorp", "ON þorp"]),
        }

        candidates: list[EtymologyCandidate] = []
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in meanings:
                lemma, meaning, cognates = meanings[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=cognates,
                        sound_changes=["No High German consonant shift"],
                        sources=["Heliand", "Gallée 1903"],
                    )
                )

        return candidates
