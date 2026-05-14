"""Astronomical orientation perspective.

Analyses whether place names with astronomical/celestial references
correlate with specific orientations (solstice alignments, equinox
sightlines) or elevated positions with wide horizon views.

Elements: sol (sun), måne (moon), stjerne (star), aust/øst (east),
vest (west), nord (north), sør (south).
"""

from __future__ import annotations

import math
from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Astronomical elements → expected orientation/features
_ASTRONOMICAL_ELEMENTS: dict[str, dict[str, Any]] = {
    "sol": {"azimuth_range": (90, 270), "description": "sun-facing exposure"},
    "måne": {"azimuth_range": None, "description": "moon-related"},
    "stjerne": {"description": "star-related, elevated position"},
    "aust": {"azimuth_range": (45, 135), "description": "east-facing"},
    "øst": {"azimuth_range": (45, 135), "description": "east-facing"},
    "vest": {"azimuth_range": (225, 315), "description": "west-facing"},
    "nord": {"azimuth_range": (315, 45), "description": "north-facing"},
    "sør": {"azimuth_range": (135, 225), "description": "south-facing"},
    "middag": {"azimuth_range": (170, 190), "description": "south/noon sun"},
}

# Key solar angles for Scandinavia (latitude ~60°N)
SUMMER_SOLSTICE_SUNRISE_AZ = 37.0  # degrees from north
SUMMER_SOLSTICE_SUNSET_AZ = 323.0
WINTER_SOLSTICE_SUNRISE_AZ = 143.0
WINTER_SOLSTICE_SUNSET_AZ = 217.0
EQUINOX_SUNRISE_AZ = 90.0
EQUINOX_SUNSET_AZ = 270.0


class AstronomicalPerspective(BasePerspective):
    """Astronomical orientation analysis.

    Tests whether place names with directional or celestial references
    correspond to actual orientations or elevated positions with
    specific horizon features.
    """

    perspective_id = "astronomical"
    name = "Astronomical Orientation Perspective"
    description = "Solstice/equinox alignment and celestial reference analysis"
    required_data = ["dem_terrain", "databank"]

    def __init__(self, *, reference_latitude: float = 60.0):
        """Initialize astronomical perspective.

        Args:
            reference_latitude: Reference latitude for solar angle calculations.
        """
        self._ref_lat = reference_latitude

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract astronomical/orientation features for a place."""
        return {
            "place_id": str(place_id),
            "aspect_deg": None,
            "horizon_profile": None,
            "summer_solstice_visible": None,
            "winter_solstice_visible": None,
            "elevation_prominence": None,
            "sky_view_factor": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate astronomical hypotheses for a place."""
        hypotheses: list[Hypothesis] = []

        for element, info in _ASTRONOMICAL_ELEMENTS.items():
            azimuth_range = info.get("azimuth_range")
            if azimuth_range:
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' face "
                            f"{info['description']} (azimuth {azimuth_range}°)"
                        ),
                        null_hypothesis=(f"No directional preference for '{element}' names"),
                        test_family="circular_mean",
                        parameters={
                            "element": element,
                            "expected_azimuth_range": azimuth_range,
                        },
                        source=self.perspective_id,
                    )
                )

        # Solstice alignment hypothesis
        hypotheses.append(
            Hypothesis(
                claim=(
                    "Solar place names align with solstice sight lines more than expected by chance"
                ),
                null_hypothesis="No solstice alignment preference for solar names",
                test_family="rayleigh",
                parameters={
                    "solstice_azimuths": [
                        SUMMER_SOLSTICE_SUNRISE_AZ,
                        SUMMER_SOLSTICE_SUNSET_AZ,
                        WINTER_SOLSTICE_SUNRISE_AZ,
                        WINTER_SOLSTICE_SUNSET_AZ,
                    ],
                    "reference_latitude": self._ref_lat,
                },
                source=self.perspective_id,
            )
        )

        return hypotheses

    @staticmethod
    def solar_azimuth_at_latitude(lat_deg: float, declination_deg: float) -> float:
        """Calculate sunrise azimuth for a given latitude and solar declination.

        Args:
            lat_deg: Observer latitude in degrees.
            declination_deg: Solar declination in degrees.

        Returns:
            Sunrise azimuth in degrees from north.
        """
        lat_rad = math.radians(lat_deg)
        dec_rad = math.radians(declination_deg)
        cos_az = math.sin(dec_rad) / math.cos(lat_rad)
        cos_az = max(-1.0, min(1.0, cos_az))
        return math.degrees(math.acos(cos_az))
