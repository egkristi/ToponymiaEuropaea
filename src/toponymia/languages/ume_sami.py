"""Ume Sámi language module for toponymic analysis.

Ume Sámi (ubmejesámiengiella) is critically endangered (~20 speakers) in
the Ume river (Umeälven) watershed area: Lycksele, Storuman, Sorsele, and
Tärna in Västerbotten (Sweden) and Hattfjelldal/Rana in Norway.

Ume Sámi is transitional between the Western Sámi group (Pite, Lule,
Northern) and the Southern Sámi group. This is reflected in its toponymic
vocabulary which shares features with both groups.

Key linguistic features:
- Vowel system transitional between South and Lule Sámi
- Consonant gradation similar to Pite/Lule
- Unique diphthong developments
- -jávrrie/jävrie (lake) — shows transitional character
- -juhka (river) vs Lule jåhkå and South johke

Geographic coverage:
- Lycksele/Liksjoe municipality (Sweden) — traditional center
- Storuman/Luspen municipality (Sweden)
- Sorsele/Suorsá municipality (Sweden)
- Tärna/Dearnná (Sweden)
- Hattfjelldal (Norway) — border area

Many municipal names in Västerbotten are Swedified Ume Sámi:
- Lycksele < *Liksjoe/Lïkssjuo ('playing place'?)
- Storuman < Stansen + uman (debated)
- Sorsele < Suorsá ('flowing out')

Key references:
- Schlachter 1958 "Wörterbuch des Waldlappendialekts von Malå"
- Larsson 2012 "Umesamisk grammatik"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class UmeSamiModule(BaseLanguageModule):
    """Language module for Ume Sámi toponyms."""

    language_code = "sju"  # ISO 639-3
    language_name = "Ume Sámi"
    family = "Uralic"
    branch = "Sámi > Western Sámi > Ume Sámi"
    period = "Continuous; critically endangered (~20 speakers)"
    script = "Latn"

    prefixes = [
        "Stuorra-",  # big
        "Unna-",  # small
        "Badje-",  # upper
        "Vuolle-",  # lower
        "Gaska-",  # middle
        "Nuorta-",  # east
        "Oarjje-",  # west
        "Guhkie-",  # long
        "Ådå-",  # new
        "Boares-",  # old
    ]

    suffixes = [
        "-jävrie",  # lake (Ume Sámi form)
        "-juhka",  # river (transitional form)
        "-várrie",  # mountain
        "-vággie",  # valley
        "-njárgga",  # headland
        "-suoluo",  # island
        "-vuobme",  # forest
        "-luoktá",  # bay
        "-gáddie",  # shore
        "-tjåhkkå",  # peak
        "-duoddar",  # tundra
        "-bákttie",  # cliff
        "-åjvvie",  # head, mountain top
        "-eatnuo",  # big river
        "-gierggie",  # rock
        "-tjakttje",  # water
    ]

    stems = [
        "jävrie",
        "juhka",
        "várrie",
        "vággie",
        "njárgga",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Ume Sámi toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

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
                        confidence=0.55,
                    )
                )

            results.append(
                SegmentationResult(
                    component=generic_part,
                    position=1 if specific else 0,
                    morph_type="compound_head",
                    lemma=matched_generic,
                    meaning=self._generic_meaning(matched_generic),
                    confidence=0.75,
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
            "jävrie": "lake",
            "juhka": "river",
            "várrie": "mountain, fell",
            "vággie": "valley",
            "njárgga": "headland, peninsula",
            "suoluo": "island",
            "vuobme": "forest",
            "luoktá": "bay, inlet",
            "gáddie": "shore, bank",
            "tjåhkkå": "peak",
            "duoddar": "tundra plateau",
            "bákttie": "cliff",
            "åjvvie": "mountain top, head",
            "eatnuo": "large river",
            "gierggie": "rock, stone",
            "tjakttje": "water",
        }
        return meanings.get(element.lower(), "landscape feature")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Ume Sámi."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Ume Sámi generic element -{suffix}")
                score += 0.5
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Ume Sámi modifier {prefix}-")
                score += 0.3
                break

        # Ume Sámi distinctive: -jävrie, -juhka (transitional forms)
        if "jävrie" in form_lower or "juhka" in form_lower:
            evidence.append("Distinctly Ume Sámi form (transitional)")
            score += 0.3

        # Sámi orthographic features
        sami_chars = ["á", "å", "č", "đ", "ŋ", "š"]
        for char in sami_chars:
            if char in form_lower:
                evidence.append(f"Sámi orthographic feature '{char}'")
                score += 0.1
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="ume-sami" if score > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Ume Sámi components."""
        candidates: list[EtymologyCandidate] = []

        lexicon = {
            "jävrie": ("jävrie", "lake", ["Lule Sámi jávrre", "S.Sámi jaevrie"]),
            "juhka": ("juhka", "river", ["Lule Sámi jåhkå", "S.Sámi johke"]),
            "várrie": ("várrie", "mountain", ["Lule Sámi várre", "S.Sámi vaerie"]),
            "vággie": ("vággie", "valley", ["Lule Sámi vágge"]),
            "njárgga": ("njárgga", "headland", ["N.Sámi njárga"]),
            "vuobme": ("vuobme", "forest", ["N.Sámi vuopmi"]),
            "luoktá": ("luoktá", "bay", ["N.Sámi luokta"]),
            "eatnuo": ("eatnuo", "large river", ["N.Sámi eatnu"]),
        }

        for comp in components:
            key = comp.lemma.lower() if comp.lemma else comp.component.lower()
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=cognates,
                        sources=["Schlachter 1958", "Larsson 2012"],
                    )
                )

        return candidates
