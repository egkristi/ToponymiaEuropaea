"""Terrain correspondence perspective.

Links place names with topographic elements (berg, dal, ås, nes, vik, etc.)
to actual terrain features derived from DEM data. Tests whether toponymic
elements correlate with the terrain characteristics they describe.

Example hypotheses:
- Places with "berg" have significantly higher elevation than surroundings
- Places with "dal" are in valleys (negative curvature)
- Places with "nes" are on peninsulas (high terrain ruggedness at coast)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Topographic element → expected terrain signature
_TERRAIN_ELEMENTS: dict[str, dict[str, Any]] = {
    "berg": {"min_elevation_diff": 50.0, "min_slope": 10.0},
    "fjell": {"min_elevation_diff": 200.0, "min_slope": 5.0},
    "dal": {"max_curvature": -0.01, "max_slope": 5.0},
    "ås": {"min_elevation_diff": 20.0, "aspect_range": (0, 360)},
    "nes": {"ruggedness_min": 0.3, "coastal": True},
    "vik": {"curvature_min": 0.01, "coastal": True},
    "haug": {"min_elevation_diff": 5.0, "max_elevation_diff": 50.0},
    "flat": {"max_slope": 2.0, "max_elevation_diff": 5.0},
    "bratt": {"min_slope": 20.0},
    "li": {"min_slope": 8.0, "max_slope": 30.0},
}


@dataclass
class TerrainFeatures:
    """Terrain features extracted for a place."""

    elevation_m: float = 0.0
    slope_deg: float = 0.0
    aspect_deg: float = 0.0
    curvature: float = 0.0
    ruggedness: float = 0.0
    elevation_diff_500m: float = 0.0  # Max elev diff within 500m radius
    is_coastal: bool = False
    terrain_class: str = "unknown"


class TerrainPerspective(BasePerspective):
    """Terrain correspondence analysis.

    Analyses whether topographic place-name elements correspond to
    actual terrain features. Uses DEM data to extract terrain
    characteristics at place locations and tests for correlation
    with etymological elements.
    """

    perspective_id = "terrain"
    name = "Terrain Correspondence"
    description = "Links topographic name elements to DEM terrain features"
    required_data = ["dem_terrain", "databank"]

    def __init__(self, *, radius_m: float = 500.0):
        """Initialize terrain perspective.

        Args:
            radius_m: Analysis radius in meters around each place.
        """
        self._radius_m = radius_m
        self._terrain_elements = _TERRAIN_ELEMENTS

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract terrain features for a place.

        Returns elevation, slope, aspect, curvature, ruggedness,
        and terrain classification.
        """
        # In production: query DEM connector + spatial analysis
        return {
            "place_id": str(place_id),
            "elevation_m": None,
            "slope_deg": None,
            "aspect_deg": None,
            "curvature": None,
            "ruggedness": None,
            "elevation_diff_500m": None,
            "is_coastal": None,
            "terrain_class": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate terrain correspondence hypotheses.

        For each topographic element found in a place name, generates
        a hypothesis that the terrain matches the element's meaning.
        """
        hypotheses: list[Hypothesis] = []

        # In production: look up name elements for this place
        # For now, generate template hypotheses for all elements
        for element, expected in self._terrain_elements.items():
            hypotheses.append(
                Hypothesis(
                    claim=(f"Places with element '{element}' have terrain matching {expected}"),
                    null_hypothesis=(f"No correlation between '{element}' and terrain features"),
                    test_family="mann_whitney_u",
                    parameters={
                        "element": element,
                        "expected_terrain": expected,
                        "radius_m": self._radius_m,
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses

    def classify_terrain_match(self, element: str, features: TerrainFeatures) -> tuple[bool, float]:
        """Check if terrain features match expected signature for an element.

        Args:
            element: Topographic name element (e.g., "berg", "dal").
            features: Extracted terrain features.

        Returns:
            Tuple of (matches, confidence_score).
        """
        if element not in self._terrain_elements:
            return False, 0.0

        expected = self._terrain_elements[element]
        score = 0.0
        checks = 0

        if "min_elevation_diff" in expected:
            checks += 1
            if features.elevation_diff_500m >= expected["min_elevation_diff"]:
                score += 1.0

        if "max_elevation_diff" in expected:
            checks += 1
            if features.elevation_diff_500m <= expected["max_elevation_diff"]:
                score += 1.0

        if "min_slope" in expected:
            checks += 1
            if features.slope_deg >= expected["min_slope"]:
                score += 1.0

        if "max_slope" in expected:
            checks += 1
            if features.slope_deg <= expected["max_slope"]:
                score += 1.0

        if "coastal" in expected and expected["coastal"]:
            checks += 1
            if features.is_coastal:
                score += 1.0

        if checks == 0:
            return False, 0.0

        confidence = score / checks
        return confidence >= 0.5, confidence
