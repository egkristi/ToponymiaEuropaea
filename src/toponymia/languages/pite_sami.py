"""Pite Sámi language module for toponymic analysis.

Pite Sámi (bidumsámegiella) is critically endangered (~30 speakers) but
has left an extensive toponymic layer in the Arjeplog/Arvidsjaur area of
Norrbotten (Sweden) and parts of Nordland (Norway: Beiarn, Saltdal).

Although speakers are few, Pite Sámi place-names survive in hundreds of
locations because place-names outlive their speakers. This makes the module
essential for interpreting names in the Piteälven/Pite river watershed.

Key differences from Lule Sámi (its closest relative):
- Different vowel quality: Pite å ≠ Lule å
- -jávrrie (lake) vs Lule -jávrre
- -jåhkå (river) — similar to Lule
- -várrie (mountain) vs Lule -várre
- Morphophonological differences in consonant gradation

Geographic coverage:
- Arjeplog/Áhrriebuörrie municipality (Sweden) — core area
- Arvidsjaur/Árviesjávrrie municipality (Sweden)
- Beiarn (Norway) — Norwegian side of traditional territory
- Saltdal (Norway) — border area with Lule Sámi

Key references:
- Lehtiranta 1992 "Yhteissaamelainen sanasto" (common Sámi vocabulary)
- Halász 1893 "Pite-lappisches Wörterbuch"
- Wilbur 2014 "A Grammar of Pite Saami"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PiteSamiModule(BaseLanguageModule):
    """Language module for Pite Sámi toponyms."""

    language_code = "sje"  # ISO 639-3
    language_name = "Pite Sámi"
    family = "Uralic"
    branch = "Sámi > Western Sámi > Pite Sámi"
    period = "Continuous; critically endangered (~30 speakers)"
    script = "Latn"

    prefixes = [
        "Stuorra-",  # big
        "Unna-",  # small
        "Badje-",  # upper
        "Vuolle-",  # lower
        "Gaska-",  # middle
        "Nuortta-",  # east
        "Oarjje-",  # west
        "Guhkie-",  # long
        "Ådå-",  # new
        "Boares-",  # old
        "Tjáhppie-",  # black
        "Vielgat-",  # white
    ]

    suffixes = [
        "-jávrrie",  # lake (Pite Sámi form)
        "-jåhkå",  # river
        "-várrie",  # mountain
        "-vággie",  # valley
        "-njárgga",  # headland
        "-suoloj",  # island
        "-vuobme",  # forest
        "-vuodno",  # fjord
        "-luoktá",  # bay
        "-gáddie",  # shore
        "-tjåhkkå",  # peak
        "-duoddara",  # tundra
        "-bákttie",  # cliff
        "-åjvvie",  # head, top
        "-ædno",  # big river
        "-gierggie",  # rock
    ]

    stems = [
        "jávrrie",
        "jåhkå",
        "várrie",
        "vággie",
        "njárgga",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Pite Sámi toponym into morphological components."""
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
            "jávrrie": "lake",
            "jåhkå": "river",
            "várrie": "mountain, fell",
            "vággie": "valley",
            "njárgga": "headland, peninsula",
            "suoloj": "island",
            "vuobme": "forest",
            "vuodno": "fjord",
            "luoktá": "bay, inlet",
            "gáddie": "shore, bank",
            "tjåhkkå": "peak",
            "duoddara": "tundra plateau",
            "bákttie": "cliff",
            "åjvvie": "mountain top, head",
            "ædno": "large river",
            "gierggie": "rock, stone",
        }
        return meanings.get(element.lower(), "landscape feature")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Pite Sámi."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Pite Sámi generic element -{suffix}")
                score += 0.5
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Pite Sámi modifier {prefix}-")
                score += 0.3
                break

        # Pite Sámi distinctive: double vowels -ie endings
        if form_lower.endswith(("ie", "rie")):
            evidence.append("Pite Sámi -ie/-rie ending pattern")
            score += 0.2

        # Sámi orthographic features
        sami_chars = ["á", "å", "č", "đ", "ŋ", "š", "ŧ"]
        for char in sami_chars:
            if char in form_lower:
                evidence.append(f"Sámi orthographic feature '{char}'")
                score += 0.1
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="pite-sami" if score > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Pite Sámi components."""
        candidates: list[EtymologyCandidate] = []

        lexicon = {
            "jávrrie": ("jávrrie", "lake", ["Lule Sámi jávrre", "N.Sámi jávri"]),
            "jåhkå": ("jåhkå", "river", ["Lule Sámi jåhkå", "N.Sámi johka"]),
            "várrie": ("várrie", "mountain", ["Lule Sámi várre", "N.Sámi várri"]),
            "vággie": ("vággie", "valley", ["Lule Sámi vágge", "N.Sámi vákki"]),
            "njárgga": ("njárgga", "headland", ["N.Sámi njárga"]),
            "vuobme": ("vuobme", "forest", ["N.Sámi vuopmi"]),
            "vuodno": ("vuodno", "fjord", ["N.Sámi vuotna"]),
            "luoktá": ("luoktá", "bay", ["N.Sámi luokta"]),
            "ædno": ("ædno", "large river", ["N.Sámi eatnu"]),
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
                        confidence=0.65,
                        cognates=cognates,
                        sources=["Halász 1893", "Wilbur 2014"],
                    )
                )

        return candidates
