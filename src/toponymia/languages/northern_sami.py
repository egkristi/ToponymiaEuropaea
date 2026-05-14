"""Northern Sámi language module.

Handles morphological segmentation and classification of Northern Sámi
(davvisámegiella) toponymic elements. Northern Sámi is the most widely
spoken Sámi language (~25,000 speakers) and has a rich toponymic tradition
across northern Norway, Sweden, and Finland.

NOTE: This module has been developed with reference to published academic
literature on Sámi onomastics. Any community consultation requirements
per the project's ethics guidelines should be observed before using
this module for research involving Sámi communities.

Key references:
- Qvigstad, J.K. (1938-1944): De lappiske stedsnavn i Troms og Nordland
- Sammallahti, P. (1998): The Saami Languages
- Aikio, A. (2009): The Saami Loanwords in Finnish and Karelian
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class NorthernSamiModule(BaseLanguageModule):
    """Language module for Northern Sámi toponyms.

    Northern Sámi place names in Fennoscandia typically describe
    landscape features, water bodies, and resource locations. The
    naming tradition reflects a semi-nomadic reindeer herding
    and fishing economy.
    """

    language_code = "sme"  # ISO 639-3 for Northern Sámi
    language_name = "Northern Sámi"
    family = "Uralic"
    branch = "Sámi > Western Sámi"
    period = "Proto-Sámi roots from ~500 CE; modern orthography from 1979"
    script = "Latn"

    # Common Northern Sámi toponymic suffixes / generic elements (last position)
    suffixes = [
        "-jávri",
        "-jávrri",  # lake (most common water body element)
        "-johka",  # river
        "-suolu",  # island
        "-njárga",  # headland, peninsula
        "-várri",  # mountain (fell)
        "-oaivi",  # mountain top, head
        "-vuopmi",  # forest
        "-vuotna",  # fjord
        "-luokta",  # bay, inlet
        "-geađgi",
        "-geađge",  # rock, stone
        "-gáddi",  # shore, bank
        "-njoammil",  # waterfall
        "-coahkka",  # peak, point
        "-duottar",  # tundra plateau
        "-čohkka",  # peak
        "-ávži",  # canyon, gorge
        "-láhku",  # flat area
        "-bákti",  # cliff
        "-mearri",  # sea
        "-suoloj",  # group of islands
        "-jieŋa",  # glacier
        "-eatnu",  # big river
    ]

    # Common Northern Sámi first elements (modifiers)
    prefixes = [
        "Stuor(r)a-",  # big, great
        "Unna-",  # small
        "Badje-",  # upper
        "Vuolle-",  # lower
        "Gaska-",  # middle
        "Davvi-",  # north
        "Lulli-",  # south
        "Nuorta-",  # east
        "Oarje-",  # west
        "Čáhce-",  # water
        "Muoŧŧá-",  # mountain (as modifier)
        "Ruoksat-",  # red
        "Vielgat-",  # white
        "Čáhppat-",  # black
        "Ruoná-",  # green
        "Alimus-",  # uppermost
        "Vuollimus-",  # lowest
        "Guovda-",  # middle
        "Boares-",  # old
        "Ođđa-",  # new
        "Guhkes-",  # long
        "Oanehis-",  # short
        "Govda-",  # wide
        "Gáitsa-",  # narrow
        "Suoidne-",  # grass/hay
        "Guolle-",  # fish
        "Eal(l)i-",  # reindeer herd
        "Goddi-",  # wild reindeer
        "Beavri-",  # beaver
        "Rieban-",  # fox
        "Guovža-",  # bear
        "Sávza-",  # sheep
        "Ákšo-",  # female reindeer
    ]

    stems = [
        "jávri",
        "johka",
        "várri",
        "suolu",
        "njárga",
        "vuopmi",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Northern Sámi toponym into morphological components.

        Sámi place names typically have a structure:
        [modifier] + [generic element (landscape feature)]
        """
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try generic element matching (last element, longest match first)
        sorted_generics = sorted(
            [s.lstrip("-") for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_generic = None
        for generic in sorted_generics:
            if form_lower.endswith(generic.lower()):
                matched_generic = generic
                break

        if matched_generic:
            specific = form[: len(form) - len(matched_generic)]
            generic_part = form[len(form) - len(matched_generic) :]

            if specific:
                results.append(
                    SegmentationResult(
                        component=specific,
                        position=0,
                        morph_type="compound_modifier",
                        meaning="specific/descriptive element",
                        confidence=0.6,
                    )
                )

            results.append(
                SegmentationResult(
                    component=generic_part,
                    position=1 if specific else 0,
                    morph_type="compound_head",
                    lemma=matched_generic,
                    meaning=self._generic_meaning(matched_generic),
                    confidence=0.8,
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

    def _generic_meaning(self, element: str) -> str:
        """Look up meaning of a generic landscape element."""
        meanings = {
            "jávri": "lake",
            "jávrri": "lake",
            "johka": "river",
            "suolu": "island",
            "njárga": "headland, peninsula",
            "várri": "mountain, fell",
            "oaivi": "mountain top, head",
            "vuopmi": "forest",
            "vuotna": "fjord",
            "luokta": "bay, inlet",
            "geađgi": "rock, stone",
            "geađge": "rock, stone",
            "gáddi": "shore, bank",
            "njoammil": "waterfall",
            "coahkka": "peak, point",
            "duottar": "tundra plateau",
            "čohkka": "peak",
            "ávži": "canyon, gorge",
            "láhku": "flat area",
            "bákti": "cliff",
            "mearri": "sea",
            "eatnu": "big river",
            "jieŋa": "glacier",
        }
        return meanings.get(element.lower(), "landscape feature")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Northern Sámi."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Check generic elements (suffixes)
        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Sámi generic element -{suffix}")
                score += 0.5
                break

        # Check specific elements (prefixes/modifiers)
        for prefix in [
            p.rstrip("-").lower().replace("(", "").replace(")", "") for p in self.prefixes
        ]:
            if form_lower.startswith(prefix):
                evidence.append(f"Sámi modifier {prefix}-")
                score += 0.3
                break

        # Check for Sámi orthographic features
        sami_chars = ["á", "č", "đ", "ŋ", "š", "ŧ", "ž"]
        for char in sami_chars:
            if char in form_lower:
                evidence.append(f"Sámi orthographic feature '{char}'")
                score += 0.15
                break  # Only count once

        # Double vowels common in Sámi
        double_vowels = ["ea", "ie", "oa", "uo"]
        for dv in double_vowels:
            if dv in form_lower:
                evidence.append(f"Sámi diphthong '{dv}'")
                score += 0.1
                break

        confidence = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="northern-sami" if confidence > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Northern Sámi components."""
        candidates: list[EtymologyCandidate] = []

        sami_lexicon = {
            "jávri": ("jávri", "lake", ["Lule Sámi jávrre", "Inari Sámi jävri"]),
            "jávrri": ("jávri", "lake", ["Lule Sámi jávrre"]),
            "johka": ("johka", "river", ["Lule Sámi jåhkå", "Finnish joki"]),
            "suolu": ("suolu", "island", ["Finnish saari (Sámi substrate)"]),
            "njárga": ("njárga", "headland, cape", ["Finnish niemi (substrate)"]),
            "várri": ("várri", "mountain, fell", ["Finnish vaara (< Sámi)"]),
            "oaivi": ("oaivi", "head, mountain top", ["Finnish aivo- (substrate)"]),
            "vuopmi": ("vuopmi", "forest, wooded area", []),
            "vuotna": ("vuotna", "fjord, inlet", ["cf. Finnish vuono"]),
            "luokta": ("luokta", "bay, shallow inlet", ["Finnish lahti (substrate)"]),
            "geađgi": ("geađgi", "stone, rock", []),
            "gáddi": ("gáddi", "shore, river bank", []),
            "eatnu": ("eatnu", "large river", ["Finnish eno (< Sámi)"]),
            "duottar": ("duottar", "treeless plateau, tundra", ["Finnish tunturi (< Sámi)"]),
            "čohkka": ("čohkka", "peak, summit", []),
            "bákti": ("bákti", "cliff, rock face", []),
        }

        for comp in components:
            key = comp.lemma.lower() if comp.lemma else comp.component.lower()
            if key in sami_lexicon:
                lemma, meaning, cognates = sami_lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.75,
                        cognates=cognates,
                        sources=["Sammallahti 1998", "Qvigstad 1938-44"],
                    )
                )

        return candidates
