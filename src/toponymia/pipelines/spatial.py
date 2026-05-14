"""H3 hierarchical spatial indexing for place records.

Computes H3 hexagonal grid indices at multiple resolutions,
enabling efficient spatial queries, clustering, and aggregation
across millions of place records.

Resolutions used:
- R7  (~5.16 km²): Regional analysis, broad clustering
- R9  (~0.105 km²): Local neighbourhood, deduplication
- R11 (~0.00176 km²): Precise location, sub-settlement level
"""

from __future__ import annotations

from typing import Any

import h3

# Default resolutions for hierarchical indexing
DEFAULT_RESOLUTIONS = (7, 9, 11)


def lat_lng_to_h3(lat: float, lng: float, resolution: int = 9) -> str:
    """Convert latitude/longitude to H3 index at given resolution.

    Args:
        lat: WGS84 latitude in decimal degrees.
        lng: WGS84 longitude in decimal degrees.
        resolution: H3 resolution (0-15). Default 9.

    Returns:
        H3 index as hex string.
    """
    return h3.latlng_to_cell(lat, lng, resolution)


def compute_h3_indices(
    lat: float, lng: float, resolutions: tuple[int, ...] = DEFAULT_RESOLUTIONS
) -> dict[str, str]:
    """Compute H3 indices at multiple resolutions.

    Returns dict with keys like 'h3_r7', 'h3_r9', 'h3_r11'.
    """
    return {f"h3_r{r}": h3.latlng_to_cell(lat, lng, r) for r in resolutions}


def enrich_record_h3(
    record: dict[str, Any], resolutions: tuple[int, ...] = DEFAULT_RESOLUTIONS
) -> dict[str, Any]:
    """Add H3 index fields to a place record.

    Adds _h3_r7, _h3_r9, _h3_r11 fields computed from latitude/longitude.
    Returns the record unchanged if lat/lon are missing.
    """
    lat = record.get("latitude")
    lng = record.get("longitude")

    if lat is None or lng is None:
        return record

    result = dict(record)
    for r in resolutions:
        result[f"_h3_r{r}"] = h3.latlng_to_cell(lat, lng, r)

    return result


def find_neighbours(h3_index: str, ring_size: int = 1) -> list[str]:
    """Find neighbouring H3 cells within k rings.

    Args:
        h3_index: H3 cell index.
        ring_size: Number of rings (1 = immediate neighbours).

    Returns:
        List of H3 indices in the neighbourhood (excluding center).
    """
    return [cell for cell in h3.grid_disk(h3_index, ring_size) if cell != h3_index]


def h3_distance(index1: str, index2: str) -> int:
    """Compute grid distance between two H3 cells.

    Returns the number of cells in the shortest path between them.
    Returns -1 if cells are at different resolutions.
    """
    try:
        return h3.grid_distance(index1, index2)
    except (h3.H3ValueError, h3.H3ResMismatchError, h3.H3GridNavigationError):
        return -1
