"""Multi-source coordinate resolution pipeline.

Resolves coordinate conflicts when multiple sources provide different
coordinates for the same place. Uses a priority hierarchy based on
source authority (national mapping authority > gazetteers > community sources).

See docs/decisions/003-coordinate-resolution.md for the full strategy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, StrEnum


class CoordinateStatus(StrEnum):
    """Status of a resolved coordinate."""

    RESOLVED = "resolved"
    SINGLE_SOURCE = "single_source"
    CONFLICT = "coordinate_conflict"
    MODERATE_DIVERGENCE = "moderate_divergence"


class SourcePriority(int, Enum):
    """Source priority for coordinate resolution (lower = higher priority)."""

    NATIONAL_AUTHORITY = 1  # Kartverket, Lantmäteriet, MML, OS, IGN
    NATIONAL_GAZETTEER = 2  # SSR, SNIG
    GEONAMES = 3
    OSM = 4
    WIKIDATA = 5
    UNKNOWN = 99


# Map source IDs to priorities
SOURCE_PRIORITY_MAP: dict[str, SourcePriority] = {
    "kartverket": SourcePriority.NATIONAL_AUTHORITY,
    "lantmateriet": SourcePriority.NATIONAL_AUTHORITY,
    "mml": SourcePriority.NATIONAL_AUTHORITY,
    "ordnance_survey": SourcePriority.NATIONAL_AUTHORITY,
    "ign": SourcePriority.NATIONAL_AUTHORITY,
    "ssr": SourcePriority.NATIONAL_GAZETTEER,
    "geonames": SourcePriority.GEONAMES,
    "osm": SourcePriority.OSM,
    "wikidata": SourcePriority.WIKIDATA,
}

# Thresholds in metres
MINOR_THRESHOLD_M = 100.0
MAJOR_THRESHOLD_M = 1000.0


@dataclass
class CoordinateSource:
    """A coordinate from a specific source."""

    latitude: float
    longitude: float
    source_id: str
    priority: SourcePriority = SourcePriority.UNKNOWN


@dataclass
class ResolutionResult:
    """Result of resolving coordinates from multiple sources."""

    latitude: float
    longitude: float
    source_id: str
    status: CoordinateStatus
    max_divergence_m: float = 0.0
    provenance: dict[str, list[float]] = field(default_factory=dict)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in metres between two WGS84 coordinate pairs.

    Uses the Haversine formula for spherical Earth approximation.
    Accurate to ~0.3% for distances under 1000km.
    """
    r = 6_371_000  # Earth radius in metres

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c


def get_source_priority(source_id: str) -> SourcePriority:
    """Look up the priority for a source ID."""
    # Normalize source_id for lookup
    normalized = source_id.lower().replace("-", "_").replace(" ", "_")
    return SOURCE_PRIORITY_MAP.get(normalized, SourcePriority.UNKNOWN)


def resolve_coordinates(sources: list[CoordinateSource]) -> ResolutionResult:
    """Resolve coordinates from multiple sources using priority hierarchy.

    Args:
        sources: List of coordinate sources for the same place.

    Returns:
        ResolutionResult with chosen coordinate and provenance.
    """
    if not sources:
        msg = "At least one coordinate source is required"
        raise ValueError(msg)

    if len(sources) == 1:
        s = sources[0]
        return ResolutionResult(
            latitude=s.latitude,
            longitude=s.longitude,
            source_id=s.source_id,
            status=CoordinateStatus.SINGLE_SOURCE,
            provenance={s.source_id: [s.latitude, s.longitude]},
        )

    # Sort by priority (lower number = higher priority)
    sorted_sources = sorted(sources, key=lambda s: s.priority.value)
    best = sorted_sources[0]

    # Calculate max divergence
    max_dist = 0.0
    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            dist = haversine_distance(
                sources[i].latitude,
                sources[i].longitude,
                sources[j].latitude,
                sources[j].longitude,
            )
            max_dist = max(max_dist, dist)

    # Determine status
    if max_dist > MAJOR_THRESHOLD_M:
        status = CoordinateStatus.CONFLICT
    elif max_dist > MINOR_THRESHOLD_M:
        status = CoordinateStatus.MODERATE_DIVERGENCE
    else:
        status = CoordinateStatus.RESOLVED

    # Build provenance
    provenance = {s.source_id: [s.latitude, s.longitude] for s in sources}

    return ResolutionResult(
        latitude=best.latitude,
        longitude=best.longitude,
        source_id=best.source_id,
        status=status,
        max_divergence_m=max_dist,
        provenance=provenance,
    )


def detect_conflicts(
    records: list[dict],
    *,
    group_field: str = "_phonetic_key",
    threshold_m: float = MAJOR_THRESHOLD_M,
) -> list[dict]:
    """Detect coordinate conflicts across grouped records.

    Groups records by the specified field and checks for coordinate
    divergence within each group.

    Args:
        records: List of databank records (dicts with latitude/longitude).
        group_field: Field to group records by.
        threshold_m: Distance threshold for conflict detection.

    Returns:
        List of conflict reports (group key, max distance, sources).
    """
    # Group by field
    groups: dict[str, list[dict]] = {}
    for rec in records:
        key = rec.get(group_field, "")
        if key:
            groups.setdefault(key, []).append(rec)

    conflicts = []
    for key, group in groups.items():
        if len(group) < 2:
            continue

        max_dist = 0.0
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                dist = haversine_distance(
                    group[i]["latitude"],
                    group[i]["longitude"],
                    group[j]["latitude"],
                    group[j]["longitude"],
                )
                max_dist = max(max_dist, dist)

        if max_dist > threshold_m:
            conflicts.append(
                {
                    "group_key": key,
                    "max_divergence_m": round(max_dist, 1),
                    "record_count": len(group),
                    "sources": [r.get("source_id", "unknown") for r in group],
                }
            )

    return conflicts
