"""Colour-landscape perspective.

Analyses correlation between colour-denoting place-name elements
and actual landscape colour characteristics (vegetation, soil, rock).

Elements: svart/sort (black), hvit/kvit (white), rød/raud (red),
grønn/grøn (green), blå (blue), gul (yellow), grå (grey).

Tests whether colour toponyms correspond to measurable spectral
properties of the landscape (from satellite imagery or geology).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Colour elements → expected landscape features
_COLOUR_ELEMENTS: dict[str, dict[str, Any]] = {
    "svart": {
        "colour": "black",
        "features": ["dark_rock", "peat", "deep_water", "shadow"],
        "ndvi_range": None,
    },
    "sort": {
        "colour": "black",
        "features": ["dark_rock", "peat", "deep_water"],
        "ndvi_range": None,
    },
    "hvit": {
        "colour": "white",
        "features": ["limestone", "quartz", "snow", "birch_bark"],
        "ndvi_range": None,
    },
    "kvit": {
        "colour": "white",
        "features": ["limestone", "quartz", "snow"],
        "ndvi_range": None,
    },
    "rød": {
        "colour": "red",
        "features": ["iron_oxide", "red_sandstone", "autumn_foliage"],
        "ndvi_range": None,
    },
    "raud": {
        "colour": "red",
        "features": ["iron_oxide", "red_sandstone"],
        "ndvi_range": None,
    },
    "grønn": {
        "colour": "green",
        "features": ["lush_vegetation", "meadow"],
        "ndvi_range": (0.4, 0.9),
    },
    "grøn": {
        "colour": "green",
        "features": ["lush_vegetation", "meadow"],
        "ndvi_range": (0.4, 0.9),
    },
    "blå": {
        "colour": "blue",
        "features": ["water", "haze", "distance"],
        "ndvi_range": None,
    },
    "gul": {
        "colour": "yellow",
        "features": ["clay_soil", "sand", "autumn_grass"],
        "ndvi_range": (0.1, 0.3),
    },
    "grå": {
        "colour": "grey",
        "features": ["granite", "gneiss", "overcast_water"],
        "ndvi_range": None,
    },
}


class ColourPerspective(BasePerspective):
    """Colour-landscape correlation analysis.

    Tests whether colour-denoting place-name elements correspond to
    measurable colour/spectral properties of the local landscape.
    """

    perspective_id = "colour"
    name = "Colour-Landscape Perspective"
    description = "Spectral correlation between colour names and landscape"
    required_data = ["dem_terrain", "satellite_imagery", "geology", "databank"]

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract colour/spectral features for a place."""
        return {
            "place_id": str(place_id),
            "dominant_colour_rgb": None,
            "ndvi": None,
            "geology_type": None,
            "soil_type": None,
            "vegetation_class": None,
            "spectral_signature": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate colour-landscape hypotheses for a place."""
        hypotheses: list[Hypothesis] = []

        for element, info in _COLOUR_ELEMENTS.items():
            features_str = ", ".join(info["features"])
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' ({info['colour']}) correlate "
                        f"with landscape features: {features_str}"
                    ),
                    null_hypothesis=(
                        f"No correlation between '{element}' and "
                        f"{info['colour']} landscape features"
                    ),
                    test_family="mann_whitney_u",
                    parameters={
                        "element": element,
                        "colour": info["colour"],
                        "expected_features": info["features"],
                        "ndvi_range": info["ndvi_range"],
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses
