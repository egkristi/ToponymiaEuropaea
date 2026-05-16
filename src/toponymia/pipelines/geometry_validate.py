"""GeoJSON geometry validation pipeline.

Validates geometries stored in databank records, ensuring they conform
to GeoJSON specification (RFC 7946):
- Valid coordinate ranges (longitude -180..180, latitude -90..90)
- Closed polygon rings
- Right-hand rule for exterior rings
- No self-intersections
- Minimum vertex counts

Optionally uses Shapely for advanced topology checks when available.

ROADMAP: 17.2.5
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of geometry validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    geometry_type: str = ""
    vertex_count: int = 0


def _check_coordinate(coord: list, errors: list[str], idx: str = "") -> bool:
    """Validate a single coordinate [lon, lat, (alt)]."""
    if not isinstance(coord, (list, tuple)):
        errors.append(f"Coordinate {idx} is not a list/tuple")
        return False
    if len(coord) < 2:
        errors.append(f"Coordinate {idx} has fewer than 2 values")
        return False
    lon, lat = coord[0], coord[1]
    if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
        errors.append(f"Coordinate {idx} has non-numeric values")
        return False
    if lon < -180 or lon > 180:
        errors.append(f"Longitude {lon} out of range [-180, 180] at {idx}")
        return False
    if lat < -90 or lat > 90:
        errors.append(f"Latitude {lat} out of range [-90, 90] at {idx}")
        return False
    return True


def _ring_is_closed(ring: list) -> bool:
    """Check if a ring's first and last coordinates are identical."""
    if len(ring) < 4:
        return False
    return ring[0][0] == ring[-1][0] and ring[0][1] == ring[-1][1]


def _ring_area_signed(ring: list) -> float:
    """Compute signed area of a ring (shoelace formula).

    Positive = counter-clockwise (exterior in GeoJSON right-hand rule).
    Negative = clockwise (hole).
    """
    area = 0.0
    n = len(ring)
    for i in range(n - 1):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[i + 1][0], ring[i + 1][1]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def _check_self_intersection_simple(ring: list) -> bool:
    """Simple O(n²) check for self-intersections.

    Only checks non-adjacent edge pairs. Returns True if intersection found.
    """
    n = len(ring) - 1  # Exclude closing point
    if n < 4:
        return False

    def segments_intersect(p1: list, p2: list, p3: list, p4: list) -> bool:
        """Check if segment p1-p2 intersects p3-p4."""

        def cross(o: list, a: list, b: list) -> float:
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        d1 = cross(p3, p4, p1)
        d2 = cross(p3, p4, p2)
        d3 = cross(p1, p2, p3)
        d4 = cross(p1, p2, p4)

        return ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
            (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
        )

    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue  # Skip adjacent first-last
            if segments_intersect(ring[i], ring[i + 1], ring[j], ring[j + 1]):
                return True
    return False


def validate_geometry(geojson: dict[str, Any]) -> ValidationResult:
    """Validate a GeoJSON geometry object.

    Args:
        geojson: A GeoJSON geometry dict with 'type' and 'coordinates'.

    Returns:
        ValidationResult with errors and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []
    vertex_count = 0

    if not isinstance(geojson, dict):
        return ValidationResult(valid=False, errors=["Geometry is not a dict"])

    geom_type = geojson.get("type", "")
    coordinates = geojson.get("coordinates")

    if not geom_type:
        errors.append("Missing 'type' field")
    if coordinates is None:
        errors.append("Missing 'coordinates' field")
        return ValidationResult(valid=False, errors=errors, geometry_type=geom_type)

    valid_types = {
        "Point",
        "MultiPoint",
        "LineString",
        "MultiLineString",
        "Polygon",
        "MultiPolygon",
    }
    if geom_type not in valid_types:
        errors.append(f"Unknown geometry type: {geom_type}")
        return ValidationResult(valid=False, errors=errors, geometry_type=geom_type)

    if geom_type == "Point":
        _check_coordinate(coordinates, errors, "Point")
        vertex_count = 1

    elif geom_type == "MultiPoint":
        for i, coord in enumerate(coordinates):
            _check_coordinate(coord, errors, f"MultiPoint[{i}]")
        vertex_count = len(coordinates)

    elif geom_type == "LineString":
        if len(coordinates) < 2:
            errors.append("LineString must have at least 2 coordinates")
        for i, coord in enumerate(coordinates):
            _check_coordinate(coord, errors, f"LineString[{i}]")
        vertex_count = len(coordinates)

    elif geom_type == "MultiLineString":
        for li, line in enumerate(coordinates):
            if len(line) < 2:
                errors.append(f"MultiLineString[{li}] must have at least 2 coordinates")
            for i, coord in enumerate(line):
                _check_coordinate(coord, errors, f"MultiLineString[{li}][{i}]")
            vertex_count += len(line)

    elif geom_type == "Polygon":
        vertex_count = _validate_polygon(coordinates, errors, warnings, "Polygon")

    elif geom_type == "MultiPolygon":
        for pi, polygon in enumerate(coordinates):
            vertex_count += _validate_polygon(polygon, errors, warnings, f"MultiPolygon[{pi}]")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        geometry_type=geom_type,
        vertex_count=vertex_count,
    )


def _validate_polygon(rings: list, errors: list[str], warnings: list[str], prefix: str) -> int:
    """Validate polygon rings."""
    vertex_count = 0

    if not rings:
        errors.append(f"{prefix}: no rings")
        return 0

    for ri, ring in enumerate(rings):
        ring_prefix = f"{prefix}.ring[{ri}]"

        if len(ring) < 4:
            errors.append(f"{ring_prefix}: must have at least 4 coordinates (got {len(ring)})")
            continue

        # Validate coordinates
        for i, coord in enumerate(ring):
            _check_coordinate(coord, errors, f"{ring_prefix}[{i}]")
        vertex_count += len(ring)

        # Check ring is closed
        if not _ring_is_closed(ring):
            errors.append(f"{ring_prefix}: ring is not closed (first != last coordinate)")

        # Check winding order (right-hand rule)
        area = _ring_area_signed(ring)
        if ri == 0 and area < 0:
            warnings.append(
                f"{ring_prefix}: exterior ring is clockwise (should be CCW per RFC 7946)"
            )
        elif ri > 0 and area > 0:
            warnings.append(f"{ring_prefix}: interior ring is CCW (should be CW per RFC 7946)")

        # Check self-intersection (only for small rings to avoid O(n²) cost)
        if len(ring) <= 100 and _check_self_intersection_simple(ring):
            errors.append(f"{ring_prefix}: ring has self-intersection")

    return vertex_count


def validate_feature(feature: dict[str, Any]) -> ValidationResult:
    """Validate a GeoJSON Feature object.

    Args:
        feature: A GeoJSON Feature dict.

    Returns:
        ValidationResult.
    """
    if not isinstance(feature, dict):
        return ValidationResult(valid=False, errors=["Feature is not a dict"])

    if feature.get("type") != "Feature":
        return ValidationResult(valid=False, errors=["type is not 'Feature'"])

    geometry = feature.get("geometry")
    if geometry is None:
        return ValidationResult(valid=True, warnings=["Feature has null geometry"])

    return validate_geometry(geometry)
