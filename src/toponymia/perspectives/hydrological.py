"""Hydrological perspective.

Analyses correlation between water-related place-name elements
(å, elv, bekk, sjø, vatn, fjord, sund, etc.) and actual hydrological
features (rivers, lakes, fjords, coastline proximity).

Tests whether hydro-toponyms are located near the water features
their names describe, and whether specific name elements distinguish
between different water body types.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Hydrological elements → expected features
_HYDRO_ELEMENTS: dict[str, dict[str, Any]] = {
    "å": {"type": "river", "max_distance_m": 200},
    "elv": {"type": "river", "max_distance_m": 500},
    "bekk": {"type": "stream", "max_distance_m": 100},
    "sjø": {"type": "lake", "max_distance_m": 500},
    "vatn": {"type": "lake", "max_distance_m": 500},
    "tjern": {"type": "pond", "max_distance_m": 200},
    "fjord": {"type": "fjord", "max_distance_m": 1000},
    "vik": {"type": "bay", "max_distance_m": 500},
    "sund": {"type": "strait", "max_distance_m": 500},
    "nes": {"type": "peninsula", "max_distance_m": 300},
    "holme": {"type": "island", "max_distance_m": 100},
    "øy": {"type": "island", "max_distance_m": 100},
    "foss": {"type": "waterfall", "max_distance_m": 300},
    "stryk": {"type": "rapids", "max_distance_m": 200},
}


class HydrologicalPerspective(BasePerspective):
    """Hydrological analysis of place names.

    Tests whether water-related toponymic elements correlate with
    proximity to the specific type of water feature they describe.
    """

    perspective_id = "hydrological"
    name = "Hydrological Perspective"
    description = "River/lake/fjord proximity analysis for water-related toponyms"
    required_data = ["osm", "dem_terrain", "databank"]

    def __init__(self, *, max_analysis_radius_m: float = 2000.0):
        """Initialize hydrological perspective.

        Args:
            max_analysis_radius_m: Maximum search radius for water features.
        """
        self._max_radius = max_analysis_radius_m

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract hydrological features for a place.

        Returns distances to nearest water features by type.
        """
        return {
            "place_id": str(place_id),
            "nearest_river_m": None,
            "nearest_lake_m": None,
            "nearest_coast_m": None,
            "nearest_fjord_m": None,
            "watershed_area_km2": None,
            "stream_order": None,
            "water_body_type": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate hydrological hypotheses for a place."""
        hypotheses: list[Hypothesis] = []

        for element, expected in _HYDRO_ELEMENTS.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' are within "
                        f"{expected['max_distance_m']}m of a {expected['type']}"
                    ),
                    null_hypothesis=(
                        f"No spatial association between '{element}' "
                        f"and {expected['type']} features"
                    ),
                    test_family="binomial",
                    parameters={
                        "element": element,
                        "water_type": expected["type"],
                        "threshold_m": expected["max_distance_m"],
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses
