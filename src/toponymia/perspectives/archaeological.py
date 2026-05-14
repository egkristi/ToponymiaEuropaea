"""Archaeological site perspective.

Analyses correlation between place names and known archaeological sites.
Tests whether certain name elements (e.g., horg, hov, ting, toft)
co-locate with excavated sites of the corresponding type.

Key research questions:
- Do theophoric elements predict cult site locations?
- Do habitation elements (bø, by, tun, toft) predict settlement sites?
- Do industrial elements (smi, kvern) predict production sites?
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Archaeological element categories
_ARCHAEOLOGICAL_ELEMENTS: dict[str, dict[str, Any]] = {
    # Cult/religious sites
    "horg": {"site_type": "cult_site", "period": "Iron Age", "max_distance_m": 500},
    "hov": {"site_type": "cult_site", "period": "Iron Age", "max_distance_m": 500},
    "vi": {"site_type": "cult_site", "period": "Iron Age", "max_distance_m": 500},
    "lund": {"site_type": "sacred_grove", "period": "Iron Age", "max_distance_m": 300},
    # Assembly sites
    "ting": {"site_type": "assembly", "period": "Viking Age", "max_distance_m": 1000},
    # Habitation
    "toft": {"site_type": "settlement", "period": "Medieval", "max_distance_m": 200},
    "tun": {"site_type": "farmstead", "period": "Iron Age", "max_distance_m": 200},
    "bø": {"site_type": "farmstead", "period": "Iron Age", "max_distance_m": 300},
    "by": {"site_type": "settlement", "period": "Viking Age", "max_distance_m": 500},
    # Burial
    "haug": {"site_type": "burial_mound", "period": "Iron Age", "max_distance_m": 200},
    "grav": {"site_type": "grave", "period": "any", "max_distance_m": 300},
    # Production/industry
    "smi": {"site_type": "smithy", "period": "Iron Age", "max_distance_m": 200},
    "kvern": {"site_type": "mill", "period": "Medieval", "max_distance_m": 300},
}


class ArchaeologicalPerspective(BasePerspective):
    """Archaeological site correlation analysis.

    Tests whether place-name elements with archaeological meanings
    predict the presence of corresponding excavated sites.
    """

    perspective_id = "archaeological"
    name = "Archaeological Site Perspective"
    description = "Correlation between name elements and known archaeological sites"
    required_data = ["databank", "archaeological_registry"]

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract archaeological features for a place.

        Returns nearby archaeological sites and their types.
        """
        return {
            "place_id": str(place_id),
            "nearest_site_m": None,
            "nearest_site_type": None,
            "nearest_site_period": None,
            "sites_within_500m": None,
            "site_types_nearby": [],
            "site_density_km2": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate archaeological hypotheses for a place."""
        hypotheses: list[Hypothesis] = []

        for element, expected in _ARCHAEOLOGICAL_ELEMENTS.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' are within "
                        f"{expected['max_distance_m']}m of a "
                        f"{expected['site_type']} from the {expected['period']}"
                    ),
                    null_hypothesis=(
                        f"No spatial association between '{element}' and "
                        f"{expected['site_type']} sites"
                    ),
                    test_family="fisher_exact",
                    parameters={
                        "element": element,
                        "site_type": expected["site_type"],
                        "period": expected["period"],
                        "threshold_m": expected["max_distance_m"],
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses
