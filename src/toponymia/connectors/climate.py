"""Climate data connector.

Connects to historical and modern climate data sources for correlation
analysis between climate patterns and place-name distributions.

Primary data sources:
- CRU TS (Climatic Research Unit Time Series, University of East Anglia)
  Monthly gridded climate data 1901-present, 0.5° resolution
- PAGES2k: Paleoclimate proxy reconstructions (last 2000 years)
- E-OBS: European high-resolution gridded climate data (0.1°)

Climate variables: temperature, precipitation, growing season length,
snow cover duration, frost frequency — all relevant to place-name
elements referencing weather/climate (e.g., "Kalvåg" = cold bay).
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

# Climate data sources
_CLIMATE_SOURCES: dict[str, dict[str, str]] = {
    "cru_ts": {
        "name": "CRU TS (Climatic Research Unit)",
        "url": "https://crudata.uea.ac.uk/cru/data/hrg/",
        "license": "Open Government Licence",
        "resolution": "0.5deg",
        "temporal": "1901-present",
    },
    "pages2k": {
        "name": "PAGES2k Consortium",
        "url": "https://pastglobalchanges.org/science/wg/2k-network",
        "license": "CC-BY-4.0",
        "resolution": "proxy-based",
        "temporal": "0-2000 CE",
    },
    "eobs": {
        "name": "E-OBS (Copernicus/ECAD)",
        "url": "https://www.ecad.eu/download/ensembles/download.php",
        "license": "Copernicus-OL",
        "resolution": "0.1deg",
        "temporal": "1950-present",
    },
}

# Climate variables
CLIMATE_VARIABLES = (
    "tmp",  # Mean temperature (°C)
    "tmn",  # Min temperature (°C)
    "tmx",  # Max temperature (°C)
    "pre",  # Precipitation (mm/month)
    "frs",  # Frost days (days/month)
    "cld",  # Cloud cover (%)
    "wet",  # Wet days (days/month)
)


@dataclass
class ClimateRecord:
    """Climate data for a location and time period."""

    latitude: float
    longitude: float
    year: int
    month: int | None = None
    temperature_mean: float | None = None
    temperature_min: float | None = None
    temperature_max: float | None = None
    precipitation_mm: float | None = None
    frost_days: float | None = None
    snow_cover_days: float | None = None
    growing_season_days: float | None = None


class ClimateConnector(BaseConnector):
    """Connector for historical and modern climate data.

    Provides climate context for place-name analysis, enabling
    correlation studies between climate-referencing toponyms and
    actual climate conditions (historical and modern).

    Example analyses:
    - Do "cold" place names (Kalstad, Frostmo) correlate with
      lower actual temperatures?
    - Do "wet" place names (Våtvik, Regnåsen) correlate with
      higher precipitation?
    - How do climate shifts correlate with place-name patterns?
    """

    source_id = "climate"
    source_name = "Climate Data (CRU/PAGES2k/E-OBS)"
    license = "varies"
    coverage_region = "global"
    source_url = "https://crudata.uea.ac.uk/cru/data/hrg/"

    def __init__(
        self,
        *,
        climate_source: str = "cru_ts",
        variable: str = "tmp",
        year_from: int = 1900,
        year_to: int = 2020,
        cache_dir: str | None = None,
    ):
        """Initialize the Climate connector.

        Args:
            climate_source: Data source (cru_ts, pages2k, eobs).
            variable: Climate variable to query.
            year_from: Start year for temporal filter.
            year_to: End year for temporal filter.
            cache_dir: Local cache directory for downloaded data.
        """
        if climate_source not in _CLIMATE_SOURCES:
            msg = (
                f"Unknown climate source: {climate_source}. "
                f"Must be one of {list(_CLIMATE_SOURCES.keys())}"
            )
            raise ValueError(msg)

        if variable not in CLIMATE_VARIABLES:
            msg = f"Unknown variable: {variable}. Must be one of {CLIMATE_VARIABLES}"
            raise ValueError(msg)

        self._source = climate_source
        self._source_info = _CLIMATE_SOURCES[climate_source]
        self._variable = variable
        self._year_from = year_from
        self._year_to = year_to
        self._cache_dir = cache_dir
        self.license = self._source_info["license"]
        self.source_url = self._source_info["url"]

    def fetch(
        self,
        bbox: BoundingBox | None = None,
        country: str | None = None,
        *,
        points: list[tuple[float, float]] | None = None,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Fetch climate data for specified locations or region.

        Args:
            bbox: Geographic bounding box to sample.
            country: Country filter (not directly used).
            points: Specific (lat, lon) points to query.
            max_results: Maximum number of results.

        Yields:
            ConnectorResult with climate data encoded in fields.
        """
        if points:
            yielded = 0
            for lat, lon in points:
                if max_results and yielded >= max_results:
                    break

                climate = self._query_climate(lat, lon)
                if climate is None:
                    continue

                yielded += 1
                yield self._climate_to_result(climate)
        elif bbox:
            yield from self._sample_bbox(bbox, max_results)

    def _query_climate(self, lat: float, lon: float) -> ClimateRecord | None:
        """Query climate data for a specific point.

        In production, reads from cached NetCDF files (CRU/E-OBS)
        or queries a climate data API.
        """
        logger.debug("Querying climate at (%.4f, %.4f)", lat, lon)
        # Integration point for actual climate data access
        # Would use xarray/netCDF4 to read from cached climate grids
        return None

    def _sample_bbox(
        self, bbox: BoundingBox, max_results: int | None = None
    ) -> Iterator[ConnectorResult]:
        """Sample climate data across a bounding box grid."""
        resolution = self._source_info["resolution"]
        if resolution == "0.5deg":
            step = 0.5
        elif resolution == "0.1deg":
            step = 0.1
        else:
            step = 1.0

        yielded = 0
        lat = bbox.min_lat
        while lat <= bbox.max_lat:
            lon = bbox.min_lon
            while lon <= bbox.max_lon:
                if max_results and yielded >= max_results:
                    return

                climate = self._query_climate(lat, lon)
                if climate is not None:
                    yielded += 1
                    yield self._climate_to_result(climate)

                lon += step
            lat += step

    def _climate_to_result(self, climate: ClimateRecord) -> ConnectorResult:
        """Convert climate data to a ConnectorResult."""
        # Encode climate variable as place_type for analysis
        place_type = f"climate:{self._variable}"
        if climate.temperature_mean is not None:
            place_type += f":{climate.temperature_mean:.1f}"

        return ConnectorResult(
            latitude=climate.latitude,
            longitude=climate.longitude,
            name_form="",
            name_normalized="",
            language_code="und",
            year_from=climate.year,
            year_to=climate.year,
            is_current=True,
            place_type=place_type,
            source_id=(
                f"climate:{self._source}:{climate.latitude:.2f},"
                f"{climate.longitude:.2f}:{climate.year}"
            ),
            source_url=self._source_info["url"],
            source_license=self._source_info["license"],
        )

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a climate data record."""
        errors: list[ValidationError] = []

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

        # Year validation
        if record.year_from is not None and record.year_from < 0:
            errors.append(
                ValidationError(
                    field="year_from",
                    message=f"Negative year: {record.year_from}",
                    severity="warning",
                )
            )

        return errors

    def count(self, bbox: BoundingBox | None = None, country: str | None = None) -> int | None:
        """Return estimated count (depends on bbox and resolution)."""
        return None

    def get_climate_for_places(self, places: list[dict[str, Any]]) -> list[ClimateRecord | None]:
        """Get climate data for a list of places.

        Convenience method for enriching existing place records with climate.

        Args:
            places: List of dicts with 'latitude' and 'longitude' keys.

        Returns:
            List of ClimateRecord (or None if unavailable) for each place.
        """
        results: list[ClimateRecord | None] = []
        for place in places:
            lat = place.get("latitude", 0.0)
            lon = place.get("longitude", 0.0)
            results.append(self._query_climate(lat, lon))
        return results
