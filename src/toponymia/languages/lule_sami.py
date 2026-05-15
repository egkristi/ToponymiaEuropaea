"""Lule Sámi language module for toponymic analysis.

Lule Sámi (julevsámegiella) is the second-largest Sámi language with
~2000 speakers in the Nordland/Troms region of Norway and Norrbotten
county in Sweden (Jokkmokk, Gällivare, Tysfjord/Hamarøy area).

Key differences from Northern Sámi:
- Different vowel system (á, å, ä, i, u, o vs N.Sámi á, i, u, o, a)
- Consonant gradation patterns differ
- Different generic elements for landscape features
- -jávrre (lake) vs N.Sámi -jávri
- -jåhkå (river) vs N.Sámi -johka
- -várre (mountain) vs N.Sámi -várri
- -vágge (valley) vs N.Sámi -vákki

Geographic coverage:
- Tysfjord/Divtasvuodna (Norway) — core Lule Sámi area
- Hamarøy, Fauske, Bodø surroundings (Norway)
- Jokkmokk/Jåhkåmåhkke (Sweden) — traditional center
- Gällivare/Jellivare area (Sweden)

Toponymic significance:
- Many Norwegian/Swedish names in Nordland/Norrbotten are
  Norwegianized/Swedified Lule Sámi names
- Divtasvuodna (Tysfjord) = 'deepwater fjord'
- Jåhkåmåhkke (Jokkmokk) = 'river bend'
- Bådåddjo (Bodø) — possibly Sámi origin (debated)

Key references:
- Grundström 1946-54 "Lulesamisches Wörterbuch"
- Spiik 1989 "Lulesamisk grammatik"
- Qvigstad 1935-44 "De lappiske stedsnavn"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LuleSamiModule(BaseLanguageModule):
    """Language module for Lule Sámi toponyms."""

    language_code = "smj"  # ISO 639-3
    language_name = "Lule Sámi"
    family = "Uralic"
    branch = "Sámi > Western Sámi > Lule Sámi"
    period = "Continuous; modern orthography from 1983"
    script = "Latn"

    prefixes = [
        "Stuor-",  # big (cf. N.Sámi Stuorra-)
        "Unna-",  # small
        "Badje-",  # upper
        "Vuolle-",  # lower
        "Gaska-",  # middle
        "Nuortta-",  # east
        "Oarjje-",  # west
        "Dávvera-",  # north
        "Lulle-",  # south
        "Tjáhppe-",  # black
        "Vielgat-",  # white
        "Ruopsat-",  # red
        "Guhkes-",  # long
        "Ådå-",  # new
        "Boares-",  # old
        "Suojna-",  # hay/grass
        "Guolle-",  # fish
        "Guovtja-",  # bear
    ]

    suffixes = [
        "-jávrre",  # lake (cf. N.Sámi jávri)
        "-jåhkå",  # river (cf. N.Sámi johka)
        "-várre",  # mountain (cf. N.Sámi várri)
        "-vágge",  # valley (cf. N.Sámi vákki)
        "-njárgga",  # headland (cf. N.Sámi njárga)
        "-suolo",  # island (cf. N.Sámi suolu)
        "-vuobme",  # forest (cf. N.Sámi vuopmi)
        "-vuodna",  # fjord (cf. N.Sámi vuotna)
        "-luokta",  # bay (same as N.Sámi)
        "-gádde",  # shore (cf. N.Sámi gáddi)
        "-tjåhkkå",  # peak (cf. N.Sámi čohkka)
        "-duoddar",  # tundra (cf. N.Sámi duottar)
        "-báktte",  # cliff (cf. N.Sámi bákti)
        "-ájvve",  # canyon (cf. N.Sámi ávži)
        "-åjvve",  # head, top
        "-ædno",  # big river (cf. N.Sámi eatnu)
        "-giergge",  # rock (cf. N.Sámi geađgi)
        "-njuoratjåhkå",  # waterfall + river
        "-tjakttja",  # water
    ]

    stems = [
        "jávrre",
        "jåhkå",
        "várre",
        "vágge",
        "njárgga",
        "suolo",
        "vuobme",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Lule Sámi toponym into morphological components."""
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
            "jávrre": "lake",
            "jåhkå": "river",
            "várre": "mountain, fell",
            "vágge": "valley",
            "njárgga": "headland, peninsula",
            "suolo": "island",
            "vuobme": "forest",
            "vuodna": "fjord",
            "luokta": "bay, inlet",
            "gádde": "shore, bank",
            "tjåhkkå": "peak, summit",
            "duoddar": "tundra plateau",
            "báktte": "cliff",
            "ájvve": "canyon, gorge",
            "åjvve": "mountain top, head",
            "ædno": "large river",
            "giergge": "rock, stone",
            "tjakttja": "water",
        }
        return meanings.get(element.lower(), "landscape feature")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Lule Sámi."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Lule Sámi generic element -{suffix}")
                score += 0.5
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Lule Sámi modifier {prefix}-")
                score += 0.3
                break

        # Lule Sámi orthographic markers (å, ä distinctive vs Northern)
        lule_chars = ["å", "ä", "á", "tj", "dj"]
        for char in lule_chars:
            if char in form_lower:
                evidence.append(f"Lule Sámi orthographic feature '{char}'")
                score += 0.15
                break

        # Lule Sámi specific: -åhkå, -ájvve patterns
        if "åhkå" in form_lower or "ájvve" in form_lower:
            evidence.append("Distinctly Lule Sámi phonological pattern")
            score += 0.25

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="lule-sami" if score > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Lule Sámi components."""
        candidates: list[EtymologyCandidate] = []

        lexicon = {
            "jávrre": ("jávrre", "lake", ["N.Sámi jávri", "Inari Sámi jävri"]),
            "jåhkå": ("jåhkå", "river", ["N.Sámi johka", "Finnish joki"]),
            "várre": ("várre", "mountain, fell", ["N.Sámi várri", "Finnish vaara"]),
            "vágge": ("vágge", "valley", ["N.Sámi vákki"]),
            "njárgga": ("njárgga", "headland", ["N.Sámi njárga", "Finnish niemi"]),
            "suolo": ("suolo", "island", ["N.Sámi suolu", "Finnish saari"]),
            "vuobme": ("vuobme", "forest", ["N.Sámi vuopmi"]),
            "vuodna": ("vuodna", "fjord", ["N.Sámi vuotna", "Finnish vuono"]),
            "luokta": ("luokta", "bay", ["N.Sámi luokta", "Finnish lahti"]),
            "gádde": ("gádde", "shore", ["N.Sámi gáddi"]),
            "duoddar": ("duoddar", "tundra plateau", ["N.Sámi duottar"]),
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
                        confidence=0.7,
                        cognates=cognates,
                        sources=["Grundström 1946-54", "Qvigstad 1935-44"],
                    )
                )

        return candidates
