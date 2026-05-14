"""Finnish (suomi) language module for toponymic analysis.

Finnish toponymy is characterized by:
- Agglutinative morphology (suffixes stack without fusion)
- Rich case system affecting place names (locative cases)
- Compound structure: modifier + generic element
- Landscape-oriented generic elements (järvi, joki, mäki, etc.)
- Vowel harmony affecting suffix forms (front/back)
- Historical layers: indigenous Finnic, Swedish loans, Sámi substrate

Key reference: Ainiala et al. 2012 "Nimistöntutkimuksen perusteet"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

# Generic landscape elements (second component in compounds)
_GENERIC_ELEMENTS: dict[str, str] = {
    # Water features
    "järvi": "lake",
    "joki": "river",
    "koski": "rapids",
    "lahti": "bay",
    "lampi": "pond",
    "lähde": "spring",
    "salmi": "strait",
    "selkä": "open water/ridge",
    "virta": "stream/current",
    "vesi": "water",
    "suo": "swamp/bog",
    # Terrain features
    "mäki": "hill",
    "vuori": "mountain",
    "vaara": "fell/rounded mountain",
    "tunturi": "fell (above tree line)",
    "kallio": "rock/cliff",
    "harju": "esker/ridge",
    "kangas": "heath/sandy ground",
    "korpi": "deep forest/wilderness",
    "nummi": "heath/moor",
    "pelto": "field",
    "niitty": "meadow",
    "rinne": "slope",
    # Settlement/human
    "kylä": "village",
    "kaupunki": "city",
    "linna": "castle/fortress",
    "kirkko": "church",
    "saari": "island",
    "niemi": "cape/peninsula",
    "ranta": "shore/beach",
    "metsä": "forest",
    # Roads/paths
    "tie": "road",
    "polku": "path",
    "silta": "bridge",
}

# Common modifier elements (first component)
_MODIFIER_ELEMENTS: dict[str, str] = {
    # Colours
    "musta": "black",
    "valko": "white",
    "puna": "red",
    "vihreä": "green",
    "sini": "blue",
    "kelta": "yellow",
    "harmaa": "grey",
    # Size/shape
    "iso": "big",
    "pieni": "small",
    "pitkä": "long",
    "leveä": "wide",
    "kapea": "narrow",
    "syvä": "deep",
    "matala": "shallow",
    "korkea": "high",
    # Cardinal directions
    "pohjois": "north",
    "etelä": "south",
    "itä": "east",
    "länsi": "west",
    "ylä": "upper",
    "ala": "lower",
    "keski": "middle",
    # Nature/animals
    "karhu": "bear",
    "susi": "wolf",
    "hirvi": "moose",
    "kotka": "eagle",
    "hauki": "pike (fish)",
    "kuusi": "spruce",
    "koivu": "birch",
    "mänty": "pine",
    "tammi": "oak",
    "leppä": "alder",
    # Sacred/cultural
    "pyhä": "holy/sacred",
    "hiisi": "sacred grove (later: evil place)",
    "ukko": "old man / thunder god Ukko",
    "kirkon": "church (genitive)",
    "pappi": "priest",
    # Temperature/quality
    "kylmä": "cold",
    "lämmin": "warm",
    "kuiva": "dry",
    "märkä": "wet",
}

# Locative case suffixes common in place names
_LOCATIVE_SUFFIXES: list[str] = [
    "ssa",
    "ssä",  # inessive (in)
    "sta",
    "stä",  # elative (from)
    "lla",
    "llä",  # adessive (at/on)
    "lta",
    "ltä",  # ablative (from surface)
    "lle",  # allative (to surface)
    "nen",  # adjectival (-inen ending)
    "la",
    "lä",  # -la/-lä (place of, very common in Finnish place names)
    "sto",
    "stö",  # collective
]

# Finnish orthographic markers (distinguishing from Swedish/Sámi)
_FINNISH_MARKERS = {
    "ä",
    "ö",
    "y",  # Front vowels (shared with Swedish but different usage)
    "aa",
    "ee",
    "ii",
    "oo",
    "uu",
    "ää",
    "öö",
    "yy",  # Long vowels
}

# Diphthongs typical of Finnish
_FINNISH_DIPHTHONGS = ["ai", "ei", "oi", "ui", "au", "eu", "ou", "äi", "öi", "yi", "ie", "uo", "yö"]


class FinnishModule(BaseLanguageModule):
    """Language module for Finnish (suomi) toponyms.

    Finnish place names are typically compounds: modifier + generic element.
    The agglutinative morphology means suffixes stack predictably.
    """

    language_code = "fin"
    language_name = "Finnish"
    family = "Uralic"
    branch = "Finnic"
    period = "Modern Finnish (1500–present)"
    script = "Latn"

    suffixes = list(_GENERIC_ELEMENTS.keys())
    prefixes = list(_MODIFIER_ELEMENTS.keys())

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Finnish place name into components.

        Finnish compounds: modifier + generic element.
        Also handles -la/-lä habitative suffix and locative cases.
        """
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try to find generic element at end
        best_generic = ""
        best_generic_meaning = ""
        for element, meaning in sorted(_GENERIC_ELEMENTS.items(), key=lambda x: -len(x[0])):
            if form_lower.endswith(element) and len(form_lower) > len(element):
                best_generic = element
                best_generic_meaning = meaning
                break

        if best_generic:
            modifier_part = form[: len(form) - len(best_generic)]
            generic_part = form[len(form) - len(best_generic) :]

            results.append(
                SegmentationResult(
                    component=modifier_part,
                    position=0,
                    morph_type="compound_modifier",
                    lemma=None,
                    confidence=0.6,
                )
            )
            results.append(
                SegmentationResult(
                    component=generic_part,
                    position=1,
                    morph_type="compound_head",
                    lemma=best_generic,
                    meaning=best_generic_meaning,
                    confidence=0.7,
                )
            )
        else:
            # Check for -la/-lä habitative suffix
            if form_lower.endswith(("la", "lä")) and len(form_lower) > 3:
                stem = form[:-2]
                suffix = form[-2:]
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="stem",
                        lemma=None,
                        confidence=0.5,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=suffix,
                        position=1,
                        morph_type="suffix",
                        lemma=suffix.lower(),
                        meaning="place of / habitation",
                        confidence=0.6,
                    )
                )
            else:
                # No clear segmentation
                results.append(
                    SegmentationResult(
                        component=form,
                        position=0,
                        morph_type="stem",
                        lemma=form_lower,
                        confidence=0.3,
                    )
                )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Finnish.

        Uses orthographic features, known elements, and structural patterns.
        """
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Check for Finnish generic elements
        for element in _GENERIC_ELEMENTS:
            if form_lower.endswith(element):
                score += 0.4
                evidence.append(f"Finnish generic element -{element}")
                break

        # Check for Finnish modifier elements
        for modifier in _MODIFIER_ELEMENTS:
            if form_lower.startswith(modifier):
                score += 0.2
                evidence.append(f"Finnish modifier {modifier}-")
                break

        # Check for -la/-lä habitative suffix (very Finnish)
        if (
            form_lower.endswith(("la", "lä"))
            and len(form_lower) > 3
            and any(
                form_lower.endswith((f"{m}la", f"{m}lä"))
                for m in ("ta", "tta", "kka", "ppa", "nta")
            )
        ):
            score += 0.15
            evidence.append("-la/-lä habitative suffix (with consonant cluster)")

        # Finnish diphthongs
        diphthong_count = sum(1 for d in _FINNISH_DIPHTHONGS if d in form_lower)
        if diphthong_count >= 1:
            score += 0.1
            evidence.append(f"Finnish diphthong(s) ({diphthong_count})")

        # Long vowels (doubled vowels)
        long_vowels = sum(
            1 for v in ("aa", "ee", "ii", "oo", "uu", "ää", "öö", "yy") if v in form_lower
        )
        if long_vowels >= 1:
            score += 0.1
            evidence.append(f"Long vowel(s) ({long_vowels})")

        # Finnish-specific letter combinations
        if "ks" in form_lower or "ts" in form_lower:
            score += 0.05
            evidence.append("Finnish consonant cluster (ks/ts)")

        # Vowel harmony check (front/back consistency)
        has_front = any(v in form_lower for v in ("ä", "ö", "y"))
        has_back = any(v in form_lower for v in ("a", "o", "u"))
        # In pure Finnish words, front and back vowels don't mix (except compounds)
        if has_front and not has_back:
            score += 0.05
            evidence.append("Vowel harmony (front)")
        elif has_back and not has_front:
            score += 0.05
            evidence.append("Vowel harmony (back)")

        # Cap at 1.0
        score = min(score, 1.0)

        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []

        for comp in components:
            comp_lower = comp.component.lower()

            # Check generic elements
            if comp_lower in _GENERIC_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp_lower,
                        meaning=_GENERIC_ELEMENTS[comp_lower],
                        language_code=self.language_code,
                        confidence=0.8,
                        sources=["Ainiala et al. 2012"],
                    )
                )
                continue

            # Check modifier elements
            if comp_lower in _MODIFIER_ELEMENTS:
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp_lower,
                        meaning=_MODIFIER_ELEMENTS[comp_lower],
                        language_code=self.language_code,
                        confidence=0.8,
                        sources=["Ainiala et al. 2012"],
                    )
                )
                continue

            # Check for genitive-modified forms of known elements
            # Finnish genitive: -n suffix on modifier
            if comp_lower.endswith("n") and comp_lower[:-1] in _MODIFIER_ELEMENTS:
                base = comp_lower[:-1]
                candidates.append(
                    EtymologyCandidate(
                        lemma=base,
                        meaning=f"{_MODIFIER_ELEMENTS[base]} (genitive)",
                        language_code=self.language_code,
                        confidence=0.7,
                        sound_changes=["genitive -n suffix"],
                        sources=["Ainiala et al. 2012"],
                    )
                )
                continue

            # Habitative -la/-lä suffix
            if comp_lower in ("la", "lä"):
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp_lower,
                        meaning="place of / habitation (habitative suffix)",
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=["Estonian -la", "Karelian -la"],
                        sources=["Ainiala et al. 2012", "Kiviniemi 1990"],
                    )
                )

        return candidates

    def normalize(self, form: str) -> str:
        """Normalize Finnish form preserving ä/ö."""
        return form.lower().strip()
