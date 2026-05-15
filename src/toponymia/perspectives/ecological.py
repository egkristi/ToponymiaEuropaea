"""Ecological/Biological perspective (Perspective D).

Analyses place names containing flora and fauna elements and tests whether
they correlate with actual species distributions. Uses historical and modern
biodiversity data to validate toponymic evidence of past ecosystems.

Example hypotheses:
- Places with "bjørk-/birk-" correlate with birch pollen zones
- Places with "ulv-/varg-" map to historical wolf range boundaries
- Places with "eik-/ek-" cluster in deciduous forest zones
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Flora elements — tree and plant species in place names
_FLORA_ELEMENTS: dict[str, dict[str, Any]] = {
    # Trees
    "bjørk": {"species": "Betula", "type": "tree", "meaning": "birch"},
    "birk": {"species": "Betula", "type": "tree", "meaning": "birch"},
    "eik": {"species": "Quercus", "type": "tree", "meaning": "oak"},
    "ek": {"species": "Quercus", "type": "tree", "meaning": "oak"},
    "ask": {"species": "Fraxinus", "type": "tree", "meaning": "ash"},
    "alm": {"species": "Ulmus", "type": "tree", "meaning": "elm"},
    "lind": {"species": "Tilia", "type": "tree", "meaning": "lime/linden"},
    "furu": {"species": "Pinus", "type": "tree", "meaning": "pine"},
    "gran": {"species": "Picea", "type": "tree", "meaning": "spruce"},
    "hassel": {"species": "Corylus", "type": "tree", "meaning": "hazel"},
    "or": {"species": "Alnus", "type": "tree", "meaning": "alder"},
    "selje": {"species": "Salix", "type": "tree", "meaning": "willow"},
    "rogn": {"species": "Sorbus", "type": "tree", "meaning": "rowan"},
    "bøk": {"species": "Fagus", "type": "tree", "meaning": "beech"},
    "lønn": {"species": "Acer", "type": "tree", "meaning": "maple"},
    "apall": {"species": "Malus", "type": "tree", "meaning": "apple tree"},
    # Plants and vegetation types
    "lyng": {"species": "Calluna/Erica", "type": "plant", "meaning": "heather"},
    "mose": {"species": "Bryophyta", "type": "plant", "meaning": "moss/bog"},
    "siv": {"species": "Juncus", "type": "plant", "meaning": "rush"},
    "starr": {"species": "Carex", "type": "plant", "meaning": "sedge"},
    "lin": {"species": "Linum", "type": "crop", "meaning": "flax"},
    "humle": {"species": "Humulus", "type": "crop", "meaning": "hops"},
}

# Fauna elements — animal species in place names
_FAUNA_ELEMENTS: dict[str, dict[str, Any]] = {
    # Mammals
    "ulv": {"species": "Canis lupus", "type": "predator", "meaning": "wolf"},
    "varg": {"species": "Canis lupus", "type": "predator", "meaning": "wolf"},
    "bjørn": {"species": "Ursus arctos", "type": "predator", "meaning": "bear"},
    "rev": {"species": "Vulpes vulpes", "type": "predator", "meaning": "fox"},
    "gaupe": {"species": "Lynx lynx", "type": "predator", "meaning": "lynx"},
    "elg": {"species": "Alces alces", "type": "ungulate", "meaning": "moose/elk"},
    "hjort": {"species": "Cervus elaphus", "type": "ungulate", "meaning": "red deer"},
    "rein": {"species": "Rangifer tarandus", "type": "ungulate", "meaning": "reindeer"},
    "bever": {"species": "Castor fiber", "type": "rodent", "meaning": "beaver"},
    "oter": {"species": "Lutra lutra", "type": "mustelid", "meaning": "otter"},
    "sel": {"species": "Phocidae", "type": "marine", "meaning": "seal"},
    "hval": {"species": "Cetacea", "type": "marine", "meaning": "whale"},
    # Birds
    "ørn": {"species": "Aquila/Haliaeetus", "type": "bird", "meaning": "eagle"},
    "hauk": {"species": "Accipiter", "type": "bird", "meaning": "hawk"},
    "svane": {"species": "Cygnus", "type": "bird", "meaning": "swan"},
    "gås": {"species": "Anser", "type": "bird", "meaning": "goose"},
    "rype": {"species": "Lagopus", "type": "bird", "meaning": "ptarmigan"},
    "ugle": {"species": "Strigidae", "type": "bird", "meaning": "owl"},
    "kråke": {"species": "Corvus cornix", "type": "bird", "meaning": "crow"},
    "ramn": {"species": "Corvus corax", "type": "bird", "meaning": "raven"},
    # Fish
    "laks": {"species": "Salmo salar", "type": "fish", "meaning": "salmon"},
    "ørret": {"species": "Salmo trutta", "type": "fish", "meaning": "trout"},
    "sild": {"species": "Clupea harengus", "type": "fish", "meaning": "herring"},
    "torsk": {"species": "Gadus morhua", "type": "fish", "meaning": "cod"},
}


class EcologicalPerspective(BasePerspective):
    """Ecological/biological analysis of place names.

    Tests whether flora and fauna elements in place names correlate with
    actual species distributions, both historical and modern. Provides
    evidence for past ecosystem conditions encoded in the landscape.
    """

    perspective_id = "ecological"
    name = "Ecological/Biological"
    description = "Flora/fauna name elements vs. species distribution data"
    required_data = ["databank", "biodiversity"]

    def __init__(self, *, include_historical: bool = True):
        """Initialize ecological perspective.

        Args:
            include_historical: Whether to include historical range data.
        """
        self._include_historical = include_historical
        self._flora = _FLORA_ELEMENTS
        self._fauna = _FAUNA_ELEMENTS

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract ecological features for a place.

        Returns species associations, vegetation zone, and biodiversity metrics.
        """
        return {
            "place_id": str(place_id),
            "flora_element": None,
            "fauna_element": None,
            "vegetation_zone": None,
            "species_present_now": None,
            "species_present_historically": None,
            "elevation_zone": None,
            "biome": None,
            "pollen_zone_match": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate ecological hypotheses.

        For each species element, generates a hypothesis that the name
        correlates with the species' actual distribution.
        """
        hypotheses: list[Hypothesis] = []

        for element, info in self._flora.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' ({info['meaning']}) are within the "
                        f"natural range of {info['species']}"
                    ),
                    null_hypothesis=(
                        f"No correlation between '{element}' names and "
                        f"{info['species']} distribution"
                    ),
                    test_family="point_in_polygon",
                    parameters={
                        "element": element,
                        "species": info["species"],
                        "type": info["type"],
                        "include_historical": self._include_historical,
                    },
                    source=self.perspective_id,
                )
            )

        for element, info in self._fauna.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' ({info['meaning']}) are within the "
                        f"historical range of {info['species']}"
                    ),
                    null_hypothesis=(
                        f"No correlation between '{element}' names and "
                        f"{info['species']} historical range"
                    ),
                    test_family="point_in_polygon",
                    parameters={
                        "element": element,
                        "species": info["species"],
                        "type": info["type"],
                        "include_historical": self._include_historical,
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses

    def classify_element(self, element: str) -> dict[str, Any] | None:
        """Classify a name element as flora or fauna.

        Args:
            element: Name element to classify.

        Returns:
            Classification dict or None if not recognized.
        """
        lower = element.lower()
        if lower in self._flora:
            return {"category": "flora", **self._flora[lower]}
        if lower in self._fauna:
            return {"category": "fauna", **self._fauna[lower]}
        return None
