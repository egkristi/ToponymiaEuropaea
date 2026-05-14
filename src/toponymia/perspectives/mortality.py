"""Mortality/catastrophe perspective.

Analyses correlation between hazard-related place-name elements
and actual hazard zones (avalanche, flood, landslide, rockfall).

Elements: ras (landslide), flaum/flom (flood), snø/skred (avalanche),
stein (rockfall), drukn (drowning), ulykke (accident).

Tests whether danger toponyms function as inherited environmental
knowledge, marking areas with genuine hazard risk.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Hazard-related elements → expected risk
_HAZARD_ELEMENTS: dict[str, dict[str, Any]] = {
    "ras": {
        "hazard": "landslide",
        "risk_indicator": "slope_instability",
        "min_slope_deg": 25.0,
    },
    "skred": {
        "hazard": "avalanche/landslide",
        "risk_indicator": "avalanche_path",
        "min_slope_deg": 28.0,
    },
    "flaum": {
        "hazard": "flood",
        "risk_indicator": "flood_zone",
        "max_elevation_above_river_m": 10.0,
    },
    "flom": {
        "hazard": "flood",
        "risk_indicator": "flood_zone",
        "max_elevation_above_river_m": 10.0,
    },
    "stein": {
        "hazard": "rockfall",
        "risk_indicator": "cliff_proximity",
        "min_slope_deg": 40.0,
    },
    "ur": {
        "hazard": "rockfall/scree",
        "risk_indicator": "scree_slope",
        "min_slope_deg": 30.0,
    },
    "kvikk": {
        "hazard": "quickclay",
        "risk_indicator": "marine_clay",
        "geology": "marine_clay",
    },
    "drukn": {
        "hazard": "drowning",
        "risk_indicator": "deep_water_proximity",
        "max_distance_water_m": 100.0,
    },
    "straum": {
        "hazard": "strong_current",
        "risk_indicator": "tidal_current",
        "max_distance_water_m": 200.0,
    },
    "malstraum": {
        "hazard": "whirlpool/maelstrom",
        "risk_indicator": "tidal_current",
        "max_distance_water_m": 500.0,
    },
}


class MortalityPerspective(BasePerspective):
    """Mortality/catastrophe hazard correlation analysis.

    Tests whether hazard-related place names are located in
    areas with genuine geophysical risk, suggesting they
    encode inherited environmental knowledge.
    """

    perspective_id = "mortality"
    name = "Mortality/Catastrophe Perspective"
    description = "Hazard map correlation with danger-related toponyms"
    required_data = ["dem_terrain", "geology", "hazard_maps", "databank"]

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract hazard-relevant features for a place."""
        return {
            "place_id": str(place_id),
            "slope_deg": None,
            "in_flood_zone": None,
            "in_avalanche_zone": None,
            "in_landslide_zone": None,
            "distance_cliff_m": None,
            "distance_water_m": None,
            "geology_type": None,
            "historical_events": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate hazard correlation hypotheses."""
        hypotheses: list[Hypothesis] = []

        for element, info in _HAZARD_ELEMENTS.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' are in zones with elevated "
                        f"{info['hazard']} risk ({info['risk_indicator']})"
                    ),
                    null_hypothesis=(
                        f"No correlation between '{element}' and actual "
                        f"{info['hazard']} hazard zones"
                    ),
                    test_family="fisher_exact",
                    parameters={
                        "element": element,
                        "hazard_type": info["hazard"],
                        "risk_indicator": info["risk_indicator"],
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses
