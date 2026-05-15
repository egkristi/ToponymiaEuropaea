"""Medicinal & Healing Landscape perspective (Perspective S).

Analyses place names related to healing waters, medicinal plants, hospitals,
and therapeutic traditions. Tests whether healing-related names correlate
with actual mineral springs, thermal sources, and historical care facilities.

Example hypotheses:
- Places with "bad-/bath-" correlate with actual thermal/mineral springs
- Places with "hellig kilde" (holy well) cluster near geological fault lines
- Places with "spital-/hospital-" show spacing consistent with pilgrim route network
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Healing water elements
_HEALING_WATER_ELEMENTS: dict[str, dict[str, Any]] = {
    "bad": {"type": "thermal", "meaning": "bath", "tradition": "germanic"},
    "bath": {"type": "thermal", "meaning": "bath", "tradition": "english"},
    "spa": {"type": "mineral", "meaning": "mineral spring", "tradition": "walloon"},
    "varm": {"type": "thermal", "meaning": "warm/hot", "tradition": "norse"},
    "heit": {"type": "thermal", "meaning": "hot", "tradition": "norse"},
    "kilde": {"type": "spring", "meaning": "spring/well", "tradition": "norse"},
    "brunn": {"type": "spring", "meaning": "well/spring", "tradition": "germanic"},
    "sur": {"type": "mineral", "meaning": "sour (mineral water)", "tradition": "norse"},
    "salt": {"type": "mineral", "meaning": "salt (saline spring)", "tradition": "germanic"},
    "hellig": {"type": "holy_well", "meaning": "holy/sacred", "tradition": "norse"},
    "therm": {"type": "thermal", "meaning": "hot spring", "tradition": "greek"},
    "aquae": {"type": "thermal", "meaning": "waters (Roman bath)", "tradition": "latin"},
}

# Hospital and care elements
_CARE_ELEMENTS: dict[str, dict[str, Any]] = {
    "hospital": {"type": "hospital", "meaning": "hospital/hospice", "tradition": "latin"},
    "spital": {"type": "hospital", "meaning": "hospital", "tradition": "germanic"},
    "lazarett": {"type": "quarantine", "meaning": "lazaretto/quarantine", "tradition": "italian"},
    "jørgen": {"type": "leper", "meaning": "St. George (leper patron)", "tradition": "norse"},
    "roch": {"type": "plague", "meaning": "St. Roch (plague patron)", "tradition": "french"},
    "apotek": {"type": "pharmacy", "meaning": "pharmacy/apothecary", "tradition": "greek"},
}

# Medicinal plant elements
_MEDICINAL_PLANT_ELEMENTS: dict[str, dict[str, Any]] = {
    "lind": {"species": "Tilia", "use": "fever/sedative", "meaning": "lime/linden"},
    "selje": {"species": "Salix", "use": "pain (salicylic acid)", "meaning": "willow"},
    "humle": {"species": "Humulus", "use": "sedative/digestive", "meaning": "hops"},
    "mjødurt": {"species": "Filipendula", "use": "fever (aspirin)", "meaning": "meadowsweet"},
    "einer": {"species": "Juniperus", "use": "antiseptic/diuretic", "meaning": "juniper"},
    "malurt": {"species": "Artemisia", "use": "digestive/antimalarial", "meaning": "wormwood"},
}


class MedicinalPerspective(BasePerspective):
    """Medicinal and healing landscape analysis.

    Tests whether place names related to healing, thermal waters, and
    medicinal traditions correlate with actual geological features
    (thermal springs, mineral deposits) and historical healthcare infrastructure.
    """

    perspective_id = "medicinal"
    name = "Medicinal & Healing Landscape"
    description = "Healing waters, medicinal plants, and care facilities in toponymy"
    required_data = ["databank", "geological_survey", "thermal_springs"]

    def __init__(self, *, include_plants: bool = True):
        """Initialize medicinal perspective.

        Args:
            include_plants: Whether to include medicinal plant analysis.
        """
        self._include_plants = include_plants
        self._healing_water = _HEALING_WATER_ELEMENTS
        self._care = _CARE_ELEMENTS
        self._plants = _MEDICINAL_PLANT_ELEMENTS

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract medicinal/healing features for a place.

        Returns proximity to thermal springs, mineral water sources,
        historical healthcare sites, and geological features.
        """
        return {
            "place_id": str(place_id),
            "healing_element": None,
            "element_type": None,
            "nearest_thermal_spring_m": None,
            "nearest_mineral_spring_m": None,
            "nearest_hospital_site_m": None,
            "geological_fault_distance_m": None,
            "water_temperature_c": None,
            "mineral_content": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate medicinal/healing hypotheses.

        Tests whether healing-related names correlate with actual
        geological and historical healthcare features.
        """
        hypotheses: list[Hypothesis] = []

        for element, info in self._healing_water.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' ({info['meaning']}) are closer to "
                        f"actual {info['type']} springs than expected by chance"
                    ),
                    null_hypothesis=(
                        f"No correlation between '{element}' names and "
                        f"{info['type']} spring proximity"
                    ),
                    test_family="distance_test",
                    parameters={
                        "element": element,
                        "type": info["type"],
                        "tradition": info["tradition"],
                        "target": "thermal_springs",
                    },
                    source=self.perspective_id,
                )
            )

        for element, info in self._care.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' ({info['meaning']}) show spacing "
                        f"consistent with planned healthcare/pilgrim infrastructure"
                    ),
                    null_hypothesis=(
                        f"'{element}' names are randomly distributed with respect "
                        f"to spacing regularity"
                    ),
                    test_family="regularity_test",
                    parameters={
                        "element": element,
                        "type": info["type"],
                        "tradition": info["tradition"],
                    },
                    source=self.perspective_id,
                )
            )

        if self._include_plants:
            for element, info in self._plants.items():
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' ({info['meaning']}) are within the "
                            f"natural range of {info['species']} ({info['use']})"
                        ),
                        null_hypothesis=(
                            f"No correlation between '{element}' names and "
                            f"{info['species']} distribution"
                        ),
                        test_family="point_in_polygon",
                        parameters={
                            "element": element,
                            "species": info["species"],
                            "medicinal_use": info["use"],
                        },
                        source=self.perspective_id,
                    )
                )

        return hypotheses

    def classify_element(self, element: str) -> dict[str, Any] | None:
        """Classify a name element as medicinal/healing-related.

        Args:
            element: Name element to classify.

        Returns:
            Classification dict with category, or None if not recognized.
        """
        lower = element.lower()
        if lower in self._healing_water:
            return {"category": "healing_water", **self._healing_water[lower]}
        if lower in self._care:
            return {"category": "care_facility", **self._care[lower]}
        if lower in self._plants:
            return {"category": "medicinal_plant", **self._plants[lower]}
        return None
