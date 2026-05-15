"""Inari Sámi language module for toponymic analysis.

Inari Sámi (anarâškielâ) is spoken exclusively in the municipality of
Inari (Aanaar) in Finnish Lapland (~400 speakers). It is the only Sámi
language spoken entirely within Finland.

Inari Sámi belongs to the Eastern Sámi group and differs significantly
from Northern Sámi in phonology and vocabulary. It occupies a transitional
position between Western and Eastern Sámi.

Key differences from Northern Sámi:
- No consonant gradation of the Northern type
- Different vowel system (â, ä, á, e, i, o, u)
- -jävri (lake) vs N.Sámi -jávri
- -juhâ (river) vs N.Sámi -johka
- -väärri (mountain) vs N.Sámi -várri
- Unique lexical items (e.g., njálmm 'mouth' for river confluence)

Geographic coverage:
- Inari/Aanaar municipality only (Finland)
- Ivalo/Avveel area
- Nellim area (border with Skolt Sámi)
- Lake Inari (Aanaarjävri) and surroundings

The entire traditional territory is within one Finnish municipality,
making Inari Sámi place-names a coherent local system.

Key references:
- Itkonen 1986-91 "Inarilappisches Wörterbuch"
- Sammallahti & Morottaja 1993 "Säämi-suomâ säänitkirje"
- Olthuis 2003 "Uđđâ säänih aanaarâškielân"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class InariSamiModule(BaseLanguageModule):
    """Language module for Inari Sámi toponyms."""

    language_code = "smn"  # ISO 639-3
    language_name = "Inari Sámi"
    family = "Uralic"
    branch = "Sámi > Eastern Sámi > Inari Sámi"
    period = "Continuous; ~400 speakers in Inari municipality"
    script = "Latn"

    prefixes = [
        "Styeres-",  # big
        "Ucceeh-",  # small
        "Paaje-",  # upper
        "Vuâlle-",  # lower
        "Koskâ-",  # middle
        "Tave-",  # north
        "Maaddâ-",  # south
        "Nuorttâ-",  # east
        "Viestâr-",  # west
        "Kukkâ-",  # long
        "Uđđâ-",  # new
        "Puáris-",  # old
        "Čáppis-",  # black
        "Viilgâs-",  # white
    ]

    suffixes = [
        "-jävri",  # lake (Inari Sámi form; cf. N.Sámi jávri)
        "-juhâ",  # river (cf. N.Sámi johka)
        "-väärri",  # mountain (cf. N.Sámi várri)
        "-vuáđđi",  # bottom, valley floor
        "-njárgâ",  # headland (cf. N.Sámi njárga)
        "-suálui",  # island (cf. N.Sámi suolu)
        "-vuovdi",  # forest (cf. N.Sámi vuopmi)
        "-luokká",  # bay (cf. N.Sámi luokta)
        "-kááidi",  # shore (cf. N.Sámi gáddi)
        "-čuákku",  # peak (cf. N.Sámi čohkka)
        "-tuodâr",  # tundra (cf. N.Sámi duottar)
        "-pääkti",  # cliff (cf. N.Sámi bákti)
        "-uáivi",  # head, top (cf. N.Sámi oaivi)
        "-eennâm",  # land, ground
        "-čääci",  # water (cf. N.Sámi čáhci)
        "-njálmm",  # mouth (river confluence; Inari-specific usage)
        "-kooskâs",  # rapids
    ]

    stems = [
        "jävri",
        "juhâ",
        "väärri",
        "njárgâ",
        "suálui",
        "vuovdi",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Inari Sámi toponym into morphological components."""
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
            "jävri": "lake",
            "juhâ": "river",
            "väärri": "mountain, fell",
            "vuáđđi": "valley floor, bottom",
            "njárgâ": "headland, peninsula",
            "suálui": "island",
            "vuovdi": "forest",
            "luokká": "bay, inlet",
            "kááidi": "shore, bank",
            "čuákku": "peak, summit",
            "tuodâr": "tundra plateau",
            "pääkti": "cliff",
            "uáivi": "head, mountain top",
            "eennâm": "land, ground",
            "čääci": "water",
            "njálmm": "mouth, river confluence",
            "kooskâs": "rapids",
        }
        return meanings.get(element.lower(), "landscape feature")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Inari Sámi."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Inari Sámi generic element -{suffix}")
                score += 0.5
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Inari Sámi modifier {prefix}-")
                score += 0.3
                break

        # Inari Sámi distinctive: â vowel (most diagnostic)
        if "â" in form_lower:
            evidence.append("Inari Sámi distinctive â vowel")
            score += 0.35

        # Double vowels distinctive to Inari (ää, uu, etc.)
        inari_doubles = ["ää", "uu", "ii", "áá"]
        for dbl in inari_doubles:
            if dbl in form_lower:
                evidence.append(f"Inari Sámi double vowel '{dbl}'")
                score += 0.2
                break

        # Inari-specific vocabulary
        if "aanaar" in form_lower:
            evidence.append("Inari Sámi 'Aanaar' (Inari)")
            score += 0.5

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
            period_estimate="inari-sami" if score > 0.5 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Inari Sámi components."""
        candidates: list[EtymologyCandidate] = []

        lexicon = {
            "jävri": ("jävri", "lake", ["N.Sámi jávri", "Skolt Sámi jäu'rr"]),
            "juhâ": ("juhâ", "river", ["N.Sámi johka", "Skolt Sámi jokk"]),
            "väärri": ("väärri", "mountain", ["N.Sámi várri", "Finnish vaara"]),
            "njárgâ": ("njárgâ", "headland", ["N.Sámi njárga"]),
            "suálui": ("suálui", "island", ["N.Sámi suolu"]),
            "vuovdi": ("vuovdi", "forest", ["N.Sámi vuopmi"]),
            "luokká": ("luokká", "bay", ["N.Sámi luokta"]),
            "čääci": ("čääci", "water", ["N.Sámi čáhci"]),
            "tuodâr": ("tuodâr", "tundra", ["N.Sámi duottar"]),
            "uáivi": ("uáivi", "head, top", ["N.Sámi oaivi"]),
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
                        sources=["Itkonen 1986-91", "Sammallahti & Morottaja 1993"],
                    )
                )

        return candidates
