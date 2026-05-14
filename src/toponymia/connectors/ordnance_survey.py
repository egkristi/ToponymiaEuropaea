"""Ordnance Survey (United Kingdom) connector.

Connects to the UK's authoritative geographic data maintained by
Ordnance Survey. The OS Open Names dataset contains approximately
2.6 million named features across England, Scotland, and Wales.

API documentation: https://osdatahub.os.uk/docs/names/overview
Data license: OGL (Open Government Licence v3.0)

Note: The OS Names API requires registration for an API key via
the OS Data Hub. This connector implements the standard interface
for the OS Names API and the OS Open Names CSV dataset.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from typing import Any

import httpx

from toponymia.connectors.base import (
    BaseConnector,
    BoundingBox,
    ConnectorResult,
    ValidationError,
)

logger = logging.getLogger(__name__)

# OS language codes → ISO 639-3
_LANGUAGE_MAP: dict[str, str] = {
    "eng": "eng",  # English
    "en": "eng",
    "cym": "cym",  # Welsh
    "cy": "cym",
    "gla": "gla",  # Scottish Gaelic
    "gd": "gla",
    "sco": "sco",  # Scots
    "cor": "cor",  # Cornish
    "gle": "gle",  # Irish (Northern Ireland — OS NI)
}

# OS feature type mapping
_FEATURE_TYPES: dict[str, str] = {
    "populatedPlace": "settlement",
    "transportNetwork": "transport",
    "water": "water_body",
    "landform": "landform",
    "woodland": "forest",
    "other": "other",
    "City": "city",
    "Town": "town",
    "Village": "village",
    "Hamlet": "hamlet",
    "Suburban Area": "suburb",
    "Bay": "bay",
    "Hill or Mountain": "mountain",
    "Valley": "valley",
    "Island": "island",
    "Lake": "lake",
    "River": "river",
    "Cape": "cape",
    "Woodland": "forest",
}


class OrdnanceSurveyConnector(BaseConnector):
    """Connector for Ordnance Survey Names API (UK national mapping).

    This connector queries the OS Data Hub Names API which provides
    authoritative UK place names including:
    - English place names across England, Scotland, Wales
    - Welsh-language names (bilingual in Wales)
    - Scottish Gaelic names
    - Coordinates (British National Grid, served as WGS84 via API)
    - Feature type classifications (populated places, landforms, water)
    """

    source_id = "ordnance_survey"
    source_name = "Ordnance Survey Open Names"
    license = "OGL-3.0"
    coverage_region = "GB"
    source_url = "https://api.os.uk/search/names/v1/"

    _BASE_URL = "https://api.os.uk/search/names/v1"
    _MAX_PER_PAGE = 100
    _RATE_LIMIT_DELAY = 0.2  # seconds between requests

    def __init__(self, *, api_key: str = "", timeout: float = 30.0):
        """Initialize the Ordnance Survey connector.

        Args:
            api_key: API key for OS Data Hub (required for production use).
            timeout: HTTP request timeout in seconds.
        """
        self._api_key = api_key
        headers: dict[str, str] = {"Accept": "application/json"}
        if api_key:
            headers["key"] = api_key
        self._client = httpx.Client(timeout=timeout, headers=headers)
        self._last_request_time = 0.0

    def _rate_limit(self) -> None:
        """Enforce rate limiting between API requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._RATE_LIMIT_DELAY:
            time.sleep(self._RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    def fetch(
        self,
        bbox: BoundingBox | None = None,
        country: str | None = None,
        *,
        name_query: str | None = None,
        feature_type: str | None = None,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Fetch place names from Ordnance Survey.

        Args:
            bbox: Geographic bounding box filter.
            country: Country filter (only 'GB' is valid).
            name_query: Text search query for place names.
            feature_type: Filter by OS feature type.
            max_results: Maximum number of results to return.

        Yields:
            ConnectorResult instances.
        """
        if country and country.upper() not in ("GB", "UK"):
            return

        params: dict[str, Any] = {"maxresults": self._MAX_PER_PAGE}

        if self._api_key:
            params["key"] = self._api_key
        if name_query:
            params["query"] = name_query
        if feature_type:
            params["fq"] = f"LOCAL_TYPE:{feature_type}"

        if bbox:
            params["bounds"] = f"{bbox.min_lon},{bbox.min_lat},{bbox.max_lon},{bbox.max_lat}"

        yielded = 0
        offset = 0

        while True:
            if max_results and yielded >= max_results:
                break

            params["offset"] = offset
            self._rate_limit()

            try:
                response = self._client.get(
                    f"{self._BASE_URL}/find",
                    params=params,
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.warning("OS Names API error: %s", e)
                break

            data = response.json()
            results_list = data.get("results", [])

            if not results_list:
                break

            for item in results_list:
                if max_results and yielded >= max_results:
                    break

                gazetteer_entry = item.get("GAZETTEER_ENTRY", {})
                result = self._parse_entry(gazetteer_entry)
                if result is not None:
                    yielded += 1
                    yield result

            if len(results_list) < self._MAX_PER_PAGE:
                break
            offset += self._MAX_PER_PAGE

    def _parse_entry(self, entry: dict[str, Any]) -> ConnectorResult | None:
        """Parse a gazetteer entry into a ConnectorResult."""
        name = entry.get("NAME1", "")
        if not name:
            return None

        # Coordinates (API returns WGS84)
        lat = entry.get("GEOMETRY_Y")
        lon = entry.get("GEOMETRY_X")
        if lat is None or lon is None:
            return None

        lat = float(lat)
        lon = float(lon)

        # Language detection
        language = entry.get("LANGUAGE", "eng")
        iso_lang = _LANGUAGE_MAP.get(language.lower(), "eng") if language else "eng"

        # Feature type
        local_type = entry.get("LOCAL_TYPE", "")
        place_type = _FEATURE_TYPES.get(local_type, local_type.lower())

        # Source ID
        source_id = str(entry.get("ID", ""))

        # Alternative names (NAME2 is often the Welsh equivalent)
        alt_names: dict[str, list[str]] = {}
        name2 = entry.get("NAME2", "")
        if name2 and name2 != name:
            alt_lang = "cym" if iso_lang == "eng" else "eng"
            alt_names[alt_lang] = [name2]

        # County/region
        county = entry.get("COUNTY_UNITARY", "") or entry.get("REGION", "")

        return ConnectorResult(
            latitude=lat,
            longitude=lon,
            name_form=name,
            name_normalized=name.lower(),
            language_code=iso_lang,
            place_type=place_type if place_type else None,
            source_id=f"os:{source_id}" if source_id else "",
            source_url="https://osdatahub.os.uk/downloads/open/OpenNames" if source_id else None,
            source_license="OGL-3.0",
            alternative_names=alt_names,
            is_current=True,
            accessed_at=county,
        )

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate an Ordnance Survey record."""
        errors: list[ValidationError] = []

        # UK bounding box (approximate, including offshore islands)
        if not (49.0 <= record.latitude <= 61.0):
            errors.append(
                ValidationError(
                    field="latitude",
                    message=f"Latitude {record.latitude} outside UK (49-61°N)",
                )
            )
        if not (-8.5 <= record.longitude <= 2.0):
            errors.append(
                ValidationError(
                    field="longitude",
                    message=f"Longitude {record.longitude} outside UK (-8.5 to 2°E)",
                )
            )

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name"))

        if record.language_code not in _LANGUAGE_MAP.values():
            errors.append(
                ValidationError(
                    field="language_code",
                    message=f"Unknown language: {record.language_code}",
                    severity="warning",
                )
            )

        return errors

    def count(self, bbox: BoundingBox | None = None, country: str | None = None) -> int | None:
        """Return estimated record count if available."""
        if country and country.upper() not in ("GB", "UK"):
            return 0
        # OS API does not cheaply expose total count
        return None
