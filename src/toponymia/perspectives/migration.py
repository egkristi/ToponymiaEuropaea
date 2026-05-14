"""Migration/diaspora perspective.

Analyses place-name distributions to trace migration patterns and
population movements. Tests whether toponymic transfer (replication
of names from origin to destination) can reveal migration routes.

Methods:
- Name-cluster detection (same name appearing in multiple regions)
- Directional diffusion analysis (chronological spread patterns)
- Dialect isogloss correlation (name variants follow dialect boundaries)
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Migration indicator elements
_MIGRATION_ELEMENTS: dict[str, dict[str, Any]] = {
    "ny": {"type": "settlement_transfer", "direction": "outward"},
    "nýr": {"type": "settlement_transfer", "direction": "outward"},
    "gamla": {"type": "origin_marker", "direction": "inward"},
    "store": {"type": "primary_settlement", "direction": "inward"},
    "lille": {"type": "secondary_settlement", "direction": "outward"},
    "øvre": {"type": "expansion_uphill", "direction": "outward"},
    "nedre": {"type": "expansion_downhill", "direction": "outward"},
    "austr": {"type": "directional_expansion", "direction": "east"},
    "nordr": {"type": "directional_expansion", "direction": "north"},
}

# Known migration patterns for validation
_KNOWN_MIGRATIONS: list[dict[str, Any]] = [
    {
        "name": "Viking Age westward expansion",
        "period": (800, 1100),
        "origin": "NO/SE",
        "destination": "IS/FO/GB",
        "markers": ["staðr", "bólstaðr", "setr"],
    },
    {
        "name": "Danish eastward colonization",
        "period": (1100, 1300),
        "origin": "DK",
        "destination": "EE/LV",
        "markers": ["by", "torp", "sted"],
    },
    {
        "name": "Finnish internal migration",
        "period": (1500, 1800),
        "origin": "FI_west",
        "destination": "FI_east",
        "markers": ["la", "lä"],
    },
]


class MigrationPerspective(BasePerspective):
    """Migration/diaspora analysis through toponymic transfer.

    Detects population movements by analysing:
    - Spatial clustering of identical or similar names
    - Chronological ordering of first attestations
    - Correlation with known historical migration routes
    - Dialect-boundary alignment of name variants
    """

    perspective_id = "migration"
    name = "Migration/Diaspora Perspective"
    description = "Origin tracing by name distribution patterns"
    required_data = ["databank", "diplomatarium", "rundata"]

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract migration-relevant features for a place."""
        return {
            "place_id": str(place_id),
            "name_cluster_id": None,
            "cluster_size": None,
            "earliest_attestation_year": None,
            "relative_chronology_rank": None,
            "dialect_zone": None,
            "distance_to_origin_km": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate migration hypotheses for a place."""
        hypotheses: list[Hypothesis] = []

        # Name transfer hypotheses
        for element, info in _MIGRATION_ELEMENTS.items():
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"'{element}' ({info['type']}) names show directional "
                        f"spread consistent with {info['direction']} migration"
                    ),
                    null_hypothesis=(
                        f"'{element}' names are randomly distributed without directional bias"
                    ),
                    test_family="spatial_trend",
                    parameters={
                        "element": element,
                        "migration_type": info["type"],
                        "expected_direction": info["direction"],
                    },
                    source=self.perspective_id,
                )
            )

        # Known migration validation
        for migration in _KNOWN_MIGRATIONS:
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Marker names {migration['markers']} show "
                        f"chronological spread from {migration['origin']} "
                        f"to {migration['destination']}"
                    ),
                    null_hypothesis=(
                        f"No chronological gradient for markers "
                        f"between {migration['origin']} and {migration['destination']}"
                    ),
                    test_family="spearman_correlation",
                    parameters={
                        "migration_name": migration["name"],
                        "markers": migration["markers"],
                        "period": migration["period"],
                        "origin": migration["origin"],
                        "destination": migration["destination"],
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses
