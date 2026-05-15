"""Temporal Cycles & Ritual Calendar perspective (Perspective T).

Analyses place names encoding seasonal activities, festival sites, market days,
and agricultural calendar events. Tests whether temporal names correlate with
climate data, elevation, and known historical fair/assembly schedules.

Example hypotheses:
- Places with "vår-" cluster at lower elevations (earlier spring)
- Places with "jul-/yule-" correlate with solstice-aligned sites
- Places with "seter-/alm-" show elevation consistent with summer transhumance
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Temporal/calendar elements in place names
_TEMPORAL_ELEMENTS: dict[str, dict[str, Any]] = {
    # Seasonal names
    "vår": {"season": "spring", "type": "seasonal", "meaning": "spring"},
    "sommar": {"season": "summer", "type": "seasonal", "meaning": "summer"},
    "høst": {"season": "autumn", "type": "seasonal", "meaning": "autumn/harvest"},
    "vinter": {"season": "winter", "type": "seasonal", "meaning": "winter"},
    # Transhumance/seasonal migration
    "seter": {"season": "summer", "type": "transhumance", "meaning": "summer pasture"},
    "støl": {"season": "summer", "type": "transhumance", "meaning": "mountain dairy"},
    "alm": {"season": "summer", "type": "transhumance", "meaning": "alpine meadow"},
    "voll": {"season": "summer", "type": "transhumance", "meaning": "grazing field"},
    "fjøs": {"season": "winter", "type": "transhumance", "meaning": "cattle shed (winter)"},
    # Festival/ritual sites
    "jul": {"season": "winter_solstice", "type": "festival", "meaning": "yule/midwinter"},
    "jonsok": {"season": "summer_solstice", "type": "festival", "meaning": "midsummer"},
    "mikkels": {"season": "autumn_equinox", "type": "festival", "meaning": "Michaelmas"},
    "olsok": {"season": "summer", "type": "festival", "meaning": "St Olaf's Day (Jul 29)"},
    "valborg": {"season": "spring", "type": "festival", "meaning": "Walpurgis (Apr 30)"},
    # Market/fair timing
    "marked": {"season": None, "type": "market", "meaning": "market"},
    "stevne": {"season": None, "type": "market", "meaning": "gathering/fair"},
    "messe": {"season": None, "type": "market", "meaning": "mass/fair"},
    # Agricultural calendar
    "slått": {"season": "summer", "type": "agricultural", "meaning": "hay-making"},
    "brenne": {"season": "spring", "type": "agricultural", "meaning": "burning (land clearing)"},
    "svedje": {"season": "spring", "type": "agricultural", "meaning": "slash-and-burn"},
    "plog": {"season": "spring", "type": "agricultural", "meaning": "plowing"},
    "sæd": {"season": "spring", "type": "agricultural", "meaning": "sowing/seed"},
    "skurd": {"season": "autumn", "type": "agricultural", "meaning": "harvest/reaping"},
}


class TemporalPerspective(BasePerspective):
    """Temporal cycles and ritual calendar analysis.

    Tests whether seasonal, festival, and agricultural calendar elements
    in place names correlate with actual climate conditions, elevation
    patterns, and known historical calendar traditions.
    """

    perspective_id = "temporal"
    name = "Temporal Cycles & Calendar"
    description = "Seasonal names vs. climate, transhumance, and festival sites"
    required_data = ["databank", "climate", "dem_terrain"]

    def __init__(self, *, include_climate: bool = True):
        """Initialize temporal perspective.

        Args:
            include_climate: Whether to include climate correlation tests.
        """
        self._include_climate = include_climate
        self._temporal_elements = _TEMPORAL_ELEMENTS

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract temporal features for a place.

        Returns seasonal classification, elevation, growing season
        length, and proximity to known festival/market sites.
        """
        return {
            "place_id": str(place_id),
            "temporal_element": None,
            "season": None,
            "activity_type": None,
            "elevation_m": None,
            "growing_season_days": None,
            "frost_free_days": None,
            "snow_cover_days": None,
            "nearest_known_fair_m": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate temporal hypotheses.

        Tests whether temporal names correlate with actual seasonal
        conditions at named locations.
        """
        hypotheses: list[Hypothesis] = []

        for element, info in self._temporal_elements.items():
            if info["type"] == "seasonal":
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' ({info['meaning']}) show climate "
                            f"conditions consistent with early/late {info['season']}"
                        ),
                        null_hypothesis=(
                            f"No correlation between '{element}' names and "
                            f"{info['season']} climate metrics"
                        ),
                        test_family="mann_whitney_u",
                        parameters={
                            "element": element,
                            "season": info["season"],
                            "type": info["type"],
                            "metric": "growing_season_days",
                        },
                        source=self.perspective_id,
                    )
                )
            elif info["type"] == "transhumance":
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' ({info['meaning']}) are at higher "
                            f"elevations than average settlements"
                        ),
                        null_hypothesis=(
                            f"No elevation difference between '{element}' names "
                            f"and general settlement distribution"
                        ),
                        test_family="mann_whitney_u",
                        parameters={
                            "element": element,
                            "season": info["season"],
                            "type": info["type"],
                            "metric": "elevation_m",
                        },
                        source=self.perspective_id,
                    )
                )
            elif info["type"] == "festival":
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' ({info['meaning']}) show spatial "
                            f"clustering consistent with ritual gathering sites"
                        ),
                        null_hypothesis=(
                            f"'{element}' names are randomly distributed "
                            f"with respect to spatial clustering"
                        ),
                        test_family="ripleys_k",
                        parameters={
                            "element": element,
                            "season": info["season"],
                            "type": info["type"],
                        },
                        source=self.perspective_id,
                    )
                )
            else:
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' ({info['meaning']}) correlate with "
                            f"conditions suitable for {info['type']} activities"
                        ),
                        null_hypothesis=(
                            f"No environmental correlation for '{element}' ({info['type']}) names"
                        ),
                        test_family="correspondence",
                        parameters={
                            "element": element,
                            "season": info["season"],
                            "type": info["type"],
                        },
                        source=self.perspective_id,
                    )
                )

        return hypotheses

    def classify_element(self, element: str) -> dict[str, Any] | None:
        """Classify a name element as temporal/calendar-related.

        Args:
            element: Name element to classify.

        Returns:
            Classification dict or None if not recognized.
        """
        lower = element.lower()
        if lower in self._temporal_elements:
            return self._temporal_elements[lower]
        return None
