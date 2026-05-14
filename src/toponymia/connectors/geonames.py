"""GeoNames data connector.

Downloads and parses GeoNames dump files (allCountries.txt or per-country).
GeoNames provides ~12 million geographical names globally under CC-BY license.

Data format: TSV with fields defined at
https://download.geonames.org/export/dump/readme.txt
"""

from __future__ import annotations

import csv
import io
import logging
import zipfile
from pathlib import Path
from typing import Iterator

import httpx

from toponymia.config import get_settings
from toponymia.connectors.base import BaseConnector, BoundingBox, ConnectorResult, ValidationError

logger = logging.getLogger(__name__)

# GeoNames TSV column indices
_GEONAME_ID = 0
_NAME = 1
_ASCIINAME = 2
_ALTERNATENAMES = 3
_LATITUDE = 4
_LONGITUDE = 5
_FEATURE_CLASS = 6
_FEATURE_CODE = 7
_COUNTRY_CODE = 8
_CC2 = 9
_ADMIN1 = 10
_ADMIN2 = 11
_ADMIN3 = 12
_ADMIN4 = 13
_POPULATION = 14
_ELEVATION = 15
_DEM = 16
_TIMEZONE = 17
_MODIFICATION_DATE = 18


class GeoNamesConnector(BaseConnector):
    """Connector for GeoNames geographical database."""

    source_id = "geonames"
    source_name = "GeoNames"
    license = "CC-BY-4.0"
    coverage_region = "global"
    source_url = "https://www.geonames.org"

    def __init__(self, cache_dir: Path | None = None):
        settings = get_settings()
        self._base_url = settings.geonames_dump_url
        self._cache_dir = cache_dir or settings.cache_dir / "geonames"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch(self, bbox: BoundingBox | None = None, country: str | None = None) -> Iterator[ConnectorResult]:
        """Fetch GeoNames records, optionally filtered by country or bbox.

        Args:
            bbox: Geographic bounding box filter.
            country: ISO 3166-1 alpha-2 country code (e.g., "NO", "SE", "GB").
        """
        filepath = self._ensure_downloaded(country)

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
            for row in reader:
                if len(row) < 19:
                    continue

                lat = float(row[_LATITUDE])
                lon = float(row[_LONGITUDE])

                if bbox and not bbox.contains(lon, lat):
                    continue

                # Parse elevation (prefer DEM over geonames elevation field)
                elevation = None
                if row[_DEM] and row[_DEM] != "":
                    try:
                        elevation = float(row[_DEM])
                    except ValueError:
                        pass
                if elevation is None and row[_ELEVATION] and row[_ELEVATION] != "":
                    try:
                        elevation = float(row[_ELEVATION])
                    except ValueError:
                        pass

                # Parse alternative names
                alt_names: dict[str, list[str]] = {}
                if row[_ALTERNATENAMES]:
                    for alt in row[_ALTERNATENAMES].split(","):
                        alt = alt.strip()
                        if alt:
                            alt_names.setdefault("und", []).append(alt)

                yield ConnectorResult(
                    latitude=lat,
                    longitude=lon,
                    elevation_m=elevation,
                    name_form=row[_NAME],
                    name_normalized=row[_ASCIINAME] or row[_NAME],
                    language_code="und",  # GeoNames doesn't specify language per main name
                    place_type=f"{row[_FEATURE_CLASS]}.{row[_FEATURE_CODE]}",
                    source_id=row[_GEONAME_ID],
                    geonames_id=int(row[_GEONAME_ID]),
                    alternative_names=alt_names,
                    source_url=f"https://www.geonames.org/{row[_GEONAME_ID]}",
                    source_license="CC-BY-4.0",
                    is_current=True,
                )

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a GeoNames record."""
        errors: list[ValidationError] = []

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name"))

        if not (-90 <= record.latitude <= 90):
            errors.append(ValidationError(field="latitude", message=f"Invalid latitude: {record.latitude}"))

        if not (-180 <= record.longitude <= 180):
            errors.append(ValidationError(field="longitude", message=f"Invalid longitude: {record.longitude}"))

        if record.geonames_id is not None and record.geonames_id <= 0:
            errors.append(ValidationError(field="geonames_id", message="Invalid GeoNames ID"))

        return errors

    def _ensure_downloaded(self, country: str | None) -> Path:
        """Download GeoNames dump if not cached."""
        if country:
            filename = f"{country.upper()}.txt"
            zip_filename = f"{country.upper()}.zip"
        else:
            filename = "allCountries.txt"
            zip_filename = "allCountries.zip"

        filepath = self._cache_dir / filename
        if filepath.exists():
            return filepath

        zip_path = self._cache_dir / zip_filename
        if not zip_path.exists():
            url = f"{self._base_url}/{zip_filename}"
            logger.info(f"Downloading {url}...")
            with httpx.stream("GET", url, follow_redirects=True) as response:
                response.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            logger.info(f"Downloaded {zip_path}")

        # Extract
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extract(filename, self._cache_dir)
        logger.info(f"Extracted {filepath}")

        return filepath
