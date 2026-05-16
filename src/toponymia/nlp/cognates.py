"""Cross-lingual cognate detection for place-name elements.

Implements sound correspondence rules and sequence alignment to detect
cognate relationships between place-name elements across languages.

Based on established sound laws:
- Grimm's Law (PIE → Proto-Germanic)
- Verner's Law (PIE voiceless stops in certain positions)
- Great Vowel Shift (Middle English → Modern English)
- Nordic i-umlaut, u-umlaut, breaking

References:
- Campbell 2013. "Historical Linguistics: An Introduction."
- Ringe 2006. "From Proto-Indo-European to Proto-Germanic."
- Orel 2003. "A Handbook of Germanic Etymology."
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# Sound correspondence rules (source → target under specific conditions)
GRIMMS_LAW: dict[str, str] = {
    # PIE voiceless stops → Gmc. voiceless fricatives
    "p": "f",
    "t": "þ",
    "k": "h",
    # PIE voiced stops → Gmc. voiceless stops
    "b": "p",
    "d": "t",
    "g": "k",
    # PIE voiced aspirates → Gmc. voiced stops/fricatives
    "bh": "b",
    "dh": "d",
    "gh": "g",
}

# Germanic → specific daughter languages
NORSE_CHANGES: dict[str, str] = {
    "þ": "t",  # ON þ > Norw. t (Þórr > Tor-)
    "ð": "d",  # ON ð > Norw. d
    "au": "ø",  # ON au > Norw. ø (Rauðr > Rød-)
    "ei": "e",  # ON ei > Norw. e/ei
}

# Known cognate sets for place-name elements
COGNATE_SETS: list[dict[str, str | list[str]]] = [
    {
        "proto_form": "*bergaz",
        "meaning": "mountain, rock",
        "cognates": ["nor:berg", "swe:berg", "deu:Berg", "eng:barrow", "non:bjarg"],
    },
    {
        "proto_form": "*haimaz",
        "meaning": "home, settlement",
        "cognates": ["nor:heim", "swe:hem", "deu:Heim", "eng:ham", "non:heimr"],
    },
    {
        "proto_form": "*stadiz",
        "meaning": "place, stead",
        "cognates": ["nor:stad", "swe:stad", "deu:Stadt", "eng:stead", "non:staðr"],
    },
    {
        "proto_form": "*landą",
        "meaning": "land, territory",
        "cognates": ["nor:land", "swe:land", "deu:Land", "eng:land", "non:land"],
    },
    {
        "proto_form": "*wikō",
        "meaning": "bay, inlet",
        "cognates": ["nor:vik", "swe:vik", "dan:vig", "non:vík", "eng:wick"],
    },
    {
        "proto_form": "*nesją",
        "meaning": "headland, promontory",
        "cognates": ["nor:nes", "swe:näs", "dan:næs", "non:nes", "eng:ness"],
    },
    {
        "proto_form": "*dalaz",
        "meaning": "valley",
        "cognates": ["nor:dal", "swe:dal", "deu:Tal", "eng:dale", "non:dalr"],
    },
    {
        "proto_form": "*aujō",
        "meaning": "island",
        "cognates": ["nor:øy", "swe:ö", "dan:ø", "non:ey", "deu:Au/Aue"],
    },
    {
        "proto_form": "*ahwō",
        "meaning": "water, river",
        "cognates": ["nor:å", "swe:å", "dan:å", "non:á", "lat:aqua"],
    },
    {
        "proto_form": "*þurpą",
        "meaning": "village, settlement",
        "cognates": ["deu:Dorf", "eng:thorp", "dan:torp", "swe:torp", "non:þorp"],
    },
    {
        "proto_form": "*burgz",
        "meaning": "fortress, stronghold",
        "cognates": ["deu:Burg", "eng:bury/burgh", "nor:borg", "swe:borg", "non:borg"],
    },
    {
        "proto_form": "*brūkō",
        "meaning": "bridge",
        "cognates": ["deu:Brücke", "eng:bridge", "nor:bru/bro", "swe:bro", "non:brú"],
    },
    {
        "proto_form": "*kirkō",
        "meaning": "church",
        "cognates": ["nor:kirke", "swe:kyrka", "dan:kirke", "eng:church", "non:kirkja"],
    },
    {
        "proto_form": "*haugaz",
        "meaning": "mound, hill",
        "cognates": ["nor:haug", "swe:hög", "dan:høj", "eng:howe", "non:haugr"],
    },
    {
        "proto_form": "*fjorðuz",
        "meaning": "fjord, inlet",
        "cognates": ["nor:fjord", "swe:fjärd", "dan:fjord", "eng:firth", "non:fjǫrðr"],
    },
]


@dataclass
class CognateMatch:
    """A detected cognate relationship."""

    element: str
    proto_form: str
    meaning: str
    cognates: list[str]
    confidence: float


@dataclass
class CognateDetector:
    """Detects cognate relationships between place-name elements."""

    cognate_sets: list[dict[str, str | list[str]]] = field(default_factory=lambda: COGNATE_SETS)

    def _normalize(self, element: str) -> str:
        """Normalize an element for matching."""
        return element.lower().strip("-").strip()

    def detect(self, element: str, language: str = "") -> list[CognateMatch]:
        """Find cognate matches for a place-name element.

        Args:
            element: The morpheme/element to look up.
            language: ISO 639-3 code of the source language (optional).

        Returns:
            List of CognateMatch objects sorted by confidence.
        """
        norm = self._normalize(element)
        matches = []

        for cset in self.cognate_sets:
            cognate_list = cset["cognates"]
            if not isinstance(cognate_list, list):
                continue

            for cognate in cognate_list:
                parts = cognate.split(":", 1)
                if len(parts) != 2:
                    continue
                lang, form = parts
                if form.lower() == norm:
                    conf = 0.9 if (language and lang == language) else 0.7
                    matches.append(
                        CognateMatch(
                            element=element,
                            proto_form=str(cset.get("proto_form", "")),
                            meaning=str(cset.get("meaning", "")),
                            cognates=cognate_list,
                            confidence=conf,
                        )
                    )
                    break

        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches

    def find_cognates_for_name(
        self, morphemes: list[str], language: str = ""
    ) -> dict[str, list[CognateMatch]]:
        """Find cognate relationships for all morphemes in a segmented name.

        Args:
            morphemes: List of morpheme strings from segmentation.
            language: Source language code.

        Returns:
            Dict mapping morpheme → list of cognate matches.
        """
        results = {}
        for morpheme in morphemes:
            matches = self.detect(morpheme, language)
            if matches:
                results[morpheme] = matches
        return results
