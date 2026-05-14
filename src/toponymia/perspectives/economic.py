"""Economic/trade route perspective.

Analyses correlation between trade-related place-name elements and
historical trade routes, market sites, and economic activity zones.

Elements: kaup (market/trade), torg (market square), hamn (harbour),
leid (route), vad (ford/crossing), bro (bridge), ting (assembly/legal).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Trade/economic elements → expected features
_ECONOMIC_ELEMENTS: dict[str, dict[str, Any]] = {
    "kaup": {
        "type": "market/trade",
        "features": ["trade_route", "harbour", "crossroads"],
        "period": "Viking Age",
    },
    "torg": {
        "type": "market_square",
        "features": ["settlement_center", "crossroads"],
        "period": "Medieval",
    },
    "hamn": {
        "type": "harbour",
        "features": ["sheltered_coast", "deep_water", "trade_route"],
        "period": "any",
    },
    "leid": {
        "type": "route/path",
        "features": ["natural_passage", "low_gradient"],
        "period": "any",
    },
    "vad": {
        "type": "ford/crossing",
        "features": ["river_crossing", "shallow_water"],
        "period": "any",
    },
    "bro": {
        "type": "bridge",
        "features": ["river_crossing", "narrow_point"],
        "period": "Medieval",
    },
    "ferje": {
        "type": "ferry",
        "features": ["water_crossing", "narrow_strait"],
        "period": "Medieval",
    },
    "smi": {
        "type": "smithy",
        "features": ["iron_production", "settlement"],
        "period": "Iron Age",
    },
    "salt": {
        "type": "salt_production",
        "features": ["coastal", "evaporation_site"],
        "period": "Iron Age",
    },
    "kvern": {
        "type": "mill",
        "features": ["waterfall", "stream_power"],
        "period": "Medieval",
    },
    "skog": {
        "type": "forest/timber",
        "features": ["forest_resource", "transport_route"],
        "period": "any",
    },
}


class EconomicPerspective(BasePerspective):
    """Economic/trade route correlation analysis.

    Tests whether trade- and commerce-related place-name elements
    correlate with historical trade routes, market locations, and
    natural resource sites.
    """

    perspective_id = "economic"
    name = "Economic/Trade Route Perspective"
    description = "Trade path correlation with commercial toponyms"
    required_data = ["databank", "osm", "archaeological_registry"]

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract economic/trade features for a place."""
        return {
            "place_id": str(place_id),
            "on_trade_route": None,
            "distance_trade_route_m": None,
            "nearest_harbour_m": None,
            "nearest_crossing_m": None,
            "centrality_index": None,
            "resource_type": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate economic/trade hypotheses for a place."""
        hypotheses: list[Hypothesis] = []

        for element, info in _ECONOMIC_ELEMENTS.items():
            features_str = ", ".join(info["features"])
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' ({info['type']}) correlate with {features_str}"
                    ),
                    null_hypothesis=(
                        f"No spatial association between '{element}' and trade/economic features"
                    ),
                    test_family="fisher_exact",
                    parameters={
                        "element": element,
                        "economic_type": info["type"],
                        "expected_features": info["features"],
                        "period": info["period"],
                    },
                    source=self.perspective_id,
                )
            )

        # Network centrality hypothesis
        hypotheses.append(
            Hypothesis(
                claim=(
                    "Trade-related place names have higher network "
                    "centrality (betweenness) in the historical route network"
                ),
                null_hypothesis=(
                    "Trade-related names are not more central in the route network than other names"
                ),
                test_family="mann_whitney_u",
                parameters={
                    "trade_elements": list(_ECONOMIC_ELEMENTS.keys()),
                    "centrality_metric": "betweenness",
                },
                source=self.perspective_id,
            )
        )

        return hypotheses
