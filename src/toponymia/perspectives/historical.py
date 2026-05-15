"""Historical/Diachronic perspective (Perspective B).

Analyses place names in terms of historical settlement periods, migration waves,
and chronological layers. Identifies period-specific naming patterns and tests
whether name formation correlates with known historical events.

Example hypotheses:
- Places with "-by" cluster in areas settled during the Viking Age (800-1050)
- Places with "-rud/-rød" correlate with medieval clearing waves (1100-1350)
- Places with "-torp" show higher density where Black Death depopulation was severe
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Historical period definitions with approximate date ranges
_HISTORICAL_PERIODS: dict[str, dict[str, Any]] = {
    "iron_age": {"start": -500, "end": 800, "label": "Iron Age"},
    "viking_age": {"start": 800, "end": 1050, "label": "Viking Age"},
    "high_medieval": {"start": 1050, "end": 1350, "label": "High Medieval"},
    "black_death": {"start": 1350, "end": 1500, "label": "Post-Black Death"},
    "early_modern": {"start": 1500, "end": 1800, "label": "Early Modern"},
    "modern": {"start": 1800, "end": 2000, "label": "Modern"},
}

# Name elements indicative of specific historical periods
_PERIOD_ELEMENTS: dict[str, dict[str, Any]] = {
    # Iron Age / Pre-Viking (primary farm names, simplex or nature-descriptive)
    "heim": {"period": "iron_age", "type": "habitative", "meaning": "home/settlement"},
    "vin": {"period": "iron_age", "type": "habitative", "meaning": "meadow/pasture"},
    "land": {"period": "iron_age", "type": "habitative", "meaning": "land/territory"},
    "aker": {"period": "iron_age", "type": "agricultural", "meaning": "cultivated field"},
    "eng": {"period": "iron_age", "type": "agricultural", "meaning": "meadow"},
    # Viking Age (expansion, new settlements)
    "by": {"period": "viking_age", "type": "habitative", "meaning": "farmstead/village"},
    "toft": {"period": "viking_age", "type": "habitative", "meaning": "homestead plot"},
    "bø": {"period": "viking_age", "type": "habitative", "meaning": "dwelling/farm"},
    "stad": {"period": "viking_age", "type": "habitative", "meaning": "place/stead"},
    "set": {"period": "viking_age", "type": "habitative", "meaning": "seat/dwelling"},
    # High Medieval (clearing wave, secondary settlement)
    "rud": {"period": "high_medieval", "type": "clearing", "meaning": "cleared land"},
    "rød": {"period": "high_medieval", "type": "clearing", "meaning": "cleared land"},
    "torp": {"period": "high_medieval", "type": "secondary", "meaning": "outlying farm"},
    "tved": {"period": "high_medieval", "type": "clearing", "meaning": "clearing in forest"},
    "sved": {"period": "high_medieval", "type": "clearing", "meaning": "burned clearing"},
    "hult": {"period": "high_medieval", "type": "clearing", "meaning": "small wood/copse"},
    # Post-Black Death (depopulation, farm desertion)
    "ødegård": {"period": "black_death", "type": "deserted", "meaning": "deserted farm"},
    "øde": {"period": "black_death", "type": "deserted", "meaning": "deserted/empty"},
    # Early Modern (newer compound formations)
    "plass": {"period": "early_modern", "type": "habitative", "meaning": "cotter's place"},
    "stue": {"period": "early_modern", "type": "habitative", "meaning": "cottage/house"},
    "bruk": {"period": "early_modern", "type": "economic", "meaning": "works/factory"},
}


class HistoricalPerspective(BasePerspective):
    """Historical/diachronic analysis of place names.

    Analyses settlement chronology through name typology. Different name
    elements are characteristic of different historical periods, enabling
    the dating of settlement patterns through toponymic evidence.
    """

    perspective_id = "historical"
    name = "Historical/Diachronic"
    description = "Settlement wave detection and period-specific naming patterns"
    required_data = ["databank", "attestations"]

    def __init__(self, *, min_attestation_count: int = 1):
        """Initialize historical perspective.

        Args:
            min_attestation_count: Minimum attestation count to consider a name datable.
        """
        self._min_attestation_count = min_attestation_count
        self._period_elements = _PERIOD_ELEMENTS
        self._periods = _HISTORICAL_PERIODS

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract historical features for a place.

        Returns period assignment, earliest attestation, settlement
        type classification, and name stratigraphy.
        """
        return {
            "place_id": str(place_id),
            "assigned_period": None,
            "earliest_attestation_year": None,
            "latest_attestation_year": None,
            "attestation_count": None,
            "name_type": None,
            "settlement_wave": None,
            "is_deserted": None,
            "period_confidence": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate historical hypotheses.

        For each period-indicative element, generates a hypothesis that
        places bearing it cluster in areas with settlement from that period.
        """
        hypotheses: list[Hypothesis] = []

        for element, info in self._period_elements.items():
            period = self._periods[info["period"]]
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' ({info['meaning']}) cluster in areas "
                        f"settled during {period['label']} ({period['start']}–{period['end']})"
                    ),
                    null_hypothesis=(
                        f"No spatial correlation between '{element}' names "
                        f"and {period['label']} settlement areas"
                    ),
                    test_family="spatial_correlation",
                    parameters={
                        "element": element,
                        "period": info["period"],
                        "period_start": period["start"],
                        "period_end": period["end"],
                        "settlement_type": info["type"],
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses

    def assign_period(self, elements: list[str]) -> tuple[str | None, float]:
        """Assign a likely formation period based on name elements.

        Args:
            elements: List of morphological elements found in the name.

        Returns:
            Tuple of (period_id, confidence) or (None, 0.0) if no assignment.
        """
        period_votes: dict[str, float] = {}

        for element in elements:
            if element.lower() in self._period_elements:
                info = self._period_elements[element.lower()]
                period = info["period"]
                # Weight by specificity: clearing elements are more diagnostic
                weight = 1.5 if info["type"] == "clearing" else 1.0
                period_votes[period] = period_votes.get(period, 0.0) + weight

        if not period_votes:
            return None, 0.0

        best_period = max(period_votes, key=period_votes.get)  # type: ignore[arg-type]
        total_weight = sum(period_votes.values())
        confidence = period_votes[best_period] / total_weight if total_weight > 0 else 0.0

        return best_period, confidence
