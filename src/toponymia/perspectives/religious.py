"""Religious/cult site perspective.

Analyses the distribution of theophoric (god-bearing) place-name elements
and their correlation with pre-Christian cult sites, medieval churches,
and sacred landscape features.

Key elements: Tor/Thor, Odin, Frøy/Frey, Njord, Ull, Ty/Tyr,
Hel, Balder, plus cult terms (hov, horg, ve/vi, lund).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Theophoric elements (Norse deity names in place names)
_DEITY_ELEMENTS: dict[str, dict[str, Any]] = {
    "tor": {"deity": "Thor", "function": "thunder/protection", "period": "Viking Age"},
    "odin": {"deity": "Odin", "function": "wisdom/war", "period": "Migration-Viking"},
    "frøy": {"deity": "Freyr", "function": "fertility", "period": "Iron Age"},
    "frey": {"deity": "Freyr", "function": "fertility", "period": "Iron Age"},
    "njord": {"deity": "Njord", "function": "sea/wealth", "period": "Iron Age"},
    "ull": {"deity": "Ull", "function": "hunting/oaths", "period": "Iron Age"},
    "ty": {"deity": "Tyr", "function": "law/war", "period": "Iron Age"},
    "balder": {"deity": "Balder", "function": "light/beauty", "period": "Viking Age"},
    "hel": {"deity": "Hel", "function": "death/underworld", "period": "Iron Age"},
    "frøya": {"deity": "Freyja", "function": "love/war", "period": "Viking Age"},
}

# Cult-site elements
_CULT_ELEMENTS: dict[str, dict[str, Any]] = {
    "hov": {"type": "temple", "function": "worship hall"},
    "horg": {"type": "altar/shrine", "function": "outdoor cult site"},
    "ve": {"type": "sanctuary", "function": "sacred enclosure"},
    "vi": {"type": "sanctuary", "function": "sacred enclosure"},
    "lund": {"type": "grove", "function": "sacred grove"},
}


class ReligiousPerspective(BasePerspective):
    """Religious/cult site distribution analysis.

    Analyses spatial patterns of theophoric elements to understand:
    - Deity cult distributions and their regional variation
    - Co-occurrence of deity names with cult-site terms
    - Transition from pagan to Christian place names
    - Landscape preferences of different deity cults
    """

    perspective_id = "religious"
    name = "Religious/Cult Site Perspective"
    description = "Theophoric element distribution and cult site correlation"
    required_data = ["databank", "archaeological_registry"]

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract religious/cult features for a place."""
        return {
            "place_id": str(place_id),
            "deity_element": None,
            "cult_element": None,
            "nearest_church_m": None,
            "church_age": None,
            "nearest_cult_site_m": None,
            "elevation_relative": None,
            "visibility_score": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate religious/cult hypotheses for a place."""
        hypotheses: list[Hypothesis] = []

        # Deity distribution hypotheses
        for element, info in _DEITY_ELEMENTS.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"'{element}' ({info['deity']}) names cluster "
                        f"near {info['function']}-related landscape features"
                    ),
                    null_hypothesis=(
                        f"'{element}' names are randomly distributed "
                        f"with respect to landscape features"
                    ),
                    test_family="spatial_clustering",
                    parameters={
                        "element": element,
                        "deity": info["deity"],
                        "function": info["function"],
                        "period": info["period"],
                    },
                    source=self.perspective_id,
                )
            )

        # Cult term co-occurrence
        for cult_element, cult_info in _CULT_ELEMENTS.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"'{cult_element}' ({cult_info['type']}) names "
                        f"co-occur with deity elements more than expected"
                    ),
                    null_hypothesis=(f"No association between '{cult_element}' and deity elements"),
                    test_family="chi_squared",
                    parameters={
                        "cult_element": cult_element,
                        "cult_type": cult_info["type"],
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses
