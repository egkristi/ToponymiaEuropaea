"""DEM/terrain data connector.

Connects to Digital Elevation Model data sources to provide terrain
characteristics for place-name analysis. Terrain features are critical
for understanding topographic place names (berg, dal, ås, nes, etc.).

Primary data sources:
- Copernicus DEM (EU-DEM, 25m resolution for Europe)
- SRTM (Shuttle Radar Topography Mission, 30m global)
- Kartverket DTM (10m resolution for Norway)

Provides: elevation, slope, aspect, curvature, terrain ruggedness index.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from toponymia.connectors.base import (
    BaseConnector,
    BoundingBox,
    ConnectorResult,
    ValidationError,
)

logger = logging.getLogger(__name__)

# DEM data sources
_DEM_SOURCES: dict[str, dict[str, str]] = {
    "copernicus": {
        "name": "Copernicus DEM",
        "url": "https://land.copernicus.eu/imagery-in-situ/eu-dem",
        "license": "Copernicus-OL",
        "resolution": "25m",
    },
    "srtm": {
        "name": "SRTM (NASA)",
        "url": "https://www2.jpl.nasa.gov/srtm/",
        "license": "public-domain",
        "resolution": "30m",
    },
    "kartverket_dtm": {
        "name": "Kartverket DTM",
        "url": "https://hoydedata.no/",
        "license": "CC-BY-4.0",
        "resolution": "10m",
    },
}

# Terrain classification thresholds
_TERRAIN_CLASSES: dict[str, tuple[float, float]] = {
    "flat": (0.0, 2.0),  # slope degrees
    "gentle": (2.0, 8.0),
    "moderate": (8.0, 16.0),
    "steep": (16.0, 30.0),
    "very_steep": (30.0, 90.0),
}


@dataclass
class TerrainPoint:
    """Terrain data for a single point."""

    latitude: float
    longitude: float
    elevation_m: float
    slope_deg: float = 0.0
    aspect_deg: float = 0.0
    curvature: float = 0.0
    terrain_ruggedness: float = 0.0


class DEMConnector(BaseConnector):
    """Connector for Digital Elevation Model / terrain data.

    Provides terrain characteristics for place-name locations, enabling
    correlation analysis between topographic features and place-name
    elements (e.g., "berg" with high elevation, "dal" with valleys).

    Supports multiple DEM data sources with varying resolution.
    """

    source_id = "dem_terrain"
    source_name = "DEM/Terrain Data"
    license = "varies"
    coverage_region = "global"
    source_url = "https://land.copernicus.eu/imagery-in-situ/eu-dem"

    def __init__(
        self,
        *,
        dem_source: str = "copernicus",
        cache_dir: str | None = None,
    ):
        """Initialize the DEM connector.

        Args:
            dem_source: DEM data source (copernicus, srtm, kartverket_dtm).
            cache_dir: Local cache directory for downloaded DEM tiles.
        """
        if dem_source not in _DEM_SOURCES:
            msg = f"Unknown DEM source: {dem_source}. Must be one of {list(_DEM_SOURCES.keys())}"
            raise ValueError(msg)

        self._source = dem_source
        self._source_info = _DEM_SOURCES[dem_source]
        self.license = self._source_info["license"]
        self.source_url = self._source_info["url"]
        self._cache_dir = cache_dir

    def fetch(
        self,
        bbox: BoundingBox | None = None,
        country: str | None = None,
        *,
        points: list[tuple[float, float]] | None = None,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Fetch terrain data for specified locations.

        Args:
            bbox: Geographic bounding box to sample.
            country: Country filter (not directly used for DEM).
            points: Specific (lat, lon) points to query.
            max_results: Maximum number of results.

        Yields:
            ConnectorResult with terrain data in metadata fields.
        """
        if points:
            yielded = 0
            for lat, lon in points:
                if max_results and yielded >= max_results:
                    break

                terrain = self._query_elevation(lat, lon)
                if terrain is None:
                    continue

                yielded += 1
                yield self._terrain_to_result(terrain)
        elif bbox:
            yield from self._sample_bbox(bbox, max_results)

    def _query_elevation(self, lat: float, lon: float) -> TerrainPoint | None:
        """Query elevation and terrain data for a point.

        In production, this reads from local DEM tiles or queries
        an elevation API. Returns None if data unavailable.
        """
        logger.debug("Querying DEM at (%.4f, %.4f)", lat, lon)
        # Integration point for actual DEM data access
        # Would use rasterio/GDAL to read from cached GeoTIFF tiles
        return None

    def _sample_bbox(
        self, bbox: BoundingBox, max_results: int | None = None
    ) -> Iterator[ConnectorResult]:
        """Sample terrain data across a bounding box grid."""
        # Calculate grid spacing based on resolution
        resolution_m = float(self._source_info["resolution"].rstrip("m"))
        # Approximate degrees per meter at mid-latitude
        mid_lat = (bbox.min_lat + bbox.max_lat) / 2
        import math

        deg_per_m_lat = 1.0 / 111320.0
        deg_per_m_lon = 1.0 / (111320.0 * math.cos(math.radians(mid_lat)))

        step_lat = resolution_m * deg_per_m_lat * 10  # Sample every 10 pixels
        step_lon = resolution_m * deg_per_m_lon * 10

        yielded = 0
        lat = bbox.min_lat
        while lat <= bbox.max_lat:
            lon = bbox.min_lon
            while lon <= bbox.max_lon:
                if max_results and yielded >= max_results:
                    return

                terrain = self._query_elevation(lat, lon)
                if terrain is not None:
                    yielded += 1
                    yield self._terrain_to_result(terrain)

                lon += step_lon
            lat += step_lat

    def _terrain_to_result(self, terrain: TerrainPoint) -> ConnectorResult:
        """Convert terrain data to a ConnectorResult."""
        # Classify terrain
        slope_class = "unknown"
        for cls, (low, high) in _TERRAIN_CLASSES.items():
            if low <= terrain.slope_deg < high:
                slope_class = cls
                break

        return ConnectorResult(
            latitude=terrain.latitude,
            longitude=terrain.longitude,
            elevation_m=terrain.elevation_m,
            name_form="",
            name_normalized="",
            language_code="und",
            is_current=True,
            place_type=f"terrain:{slope_class}",
            source_id=f"dem:{self._source}:{terrain.latitude:.4f},{terrain.longitude:.4f}",
            source_url=self._source_info["url"],
            source_license=self._source_info["license"],
        )

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a terrain data record."""
        errors: list[ValidationError] = []

        # Elevation sanity check (Earth's range: -430m to 8849m)
        if record.elevation_m is not None and (
            record.elevation_m < -500 or record.elevation_m > 9000
        ):
            errors.append(
                ValidationError(
                    field="elevation_m",
                    message=f"Elevation {record.elevation_m}m outside Earth range",
                )
            )

        # Coordinate validation
        if not (-90 <= record.latitude <= 90):
            errors.append(
                ValidationError(
                    field="latitude",
                    message=f"Invalid latitude: {record.latitude}",
                )
            )
        if not (-180 <= record.longitude <= 180):
            errors.append(
                ValidationError(
                    field="longitude",
                    message=f"Invalid longitude: {record.longitude}",
                )
            )

        return errors

    def count(self, bbox: BoundingBox | None = None, country: str | None = None) -> int | None:
        """Return estimated count (depends on bbox and resolution)."""
        return None

    def get_terrain_for_places(self, places: list[dict[str, Any]]) -> list[TerrainPoint | None]:
        """Get terrain data for a list of places.

        Convenience method for enriching existing place records with terrain.

        Args:
            places: List of dicts with 'latitude' and 'longitude' keys.

        Returns:
            List of TerrainPoint (or None if unavailable) for each place.
        """
        results: list[TerrainPoint | None] = []
        for place in places:
            lat = place.get("latitude", 0.0)
            lon = place.get("longitude", 0.0)
            results.append(self._query_elevation(lat, lon))
        return results
