"""Lantmäteriet (Swedish National Land Survey) connector.

Connects to Sweden's authoritative place-name registry maintained by
Lantmäteriet. The registry contains approximately 1.5 million place names
with coordinates, municipality codes, and feature type classifications.

API documentation: https://www.lantmateriet.se/en/maps-and-geographic-information/open-geodata-api/
Data license: CC0 (Swedish open data)

Note: The actual Lantmäteriet API requires registration. This connector
implements the standard interface and can be used with the open geodata
endpoint or the registered Ortnamn API.
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

# Lantmäteriet language codes → ISO 639-3
_LANGUAGE_MAP: dict[str, str] = {
    "swe": "swe",  # Swedish
    "sv": "swe",  # ISO 639-1
    "fin": "fin",  # Finnish (Tornedalen)
    "fi": "fin",
    "sme": "sme",  # Northern Sámi
    "smj": "smj",  # Lule Sámi
    "sma": "sma",  # Southern Sámi
    "fit": "fit",  # Meänkieli (Tornedalen Finnish)
    "rom": "rom",  # Romani
    "yid": "yid",  # Yiddish
}

# Feature type mapping (Swedish → English)
_FEATURE_TYPES: dict[str, str] = {
    "Bebyggelse": "settlement",
    "Naturområde": "natural_area",
    "Vattenområde": "water_body",
    "Fjäll": "mountain",
    "Ö": "island",
    "Sjö": "lake",
    "Å": "river",
    "Älv": "river",
    "Berg": "mountain",
    "Dal": "valley",
    "Vik": "bay",
    "Udde": "cape",
    "Halvö": "peninsula",
    "Skog": "forest",
    "Hed": "heath",
    "Mosse": "bog",
}


class LantmaterietConnector(BaseConnector):
    """Connector for Lantmäteriet Ortnamn API (Swedish national place-name registry).

    This connector queries the Lantmäteriet place-name web service which provides
    authoritative Swedish place names including:
    - Official Swedish names
    - Minority language names (Finnish, Sámi, Meänkieli)
    - Coordinates (SWEREF 99 TM, served as WGS84 via API)
    - Municipality codes and feature type classifications
    """

    source_id = "lantmateriet"
    source_name = "Lantmäteriet Ortnamn"
    license = "CC0-1.0"
    coverage_region = "SE"
    source_url = "https://api.lantmateriet.se/ortnamn/v2.1/"

    _BASE_URL = "https://api.lantmateriet.se/ortnamn/v2.1"
    _MAX_PER_PAGE = 100
    _RATE_LIMIT_DELAY = 0.25  # seconds between requests

    def __init__(self, *, api_key: str = "", timeout: float = 30.0):
        """Initialize the Lantmäteriet connector.

        Args:
            api_key: API key for Lantmäteriet (required for production use).
            timeout: HTTP request timeout in seconds.
        """
        self._api_key = api_key
        headers: dict[str, str] = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
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
        municipality: str | None = None,
        name_query: str | None = None,
        language: str | None = None,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Fetch place names from Lantmäteriet.

        Args:
            bbox: Geographic bounding box filter.
            country: Country filter (only 'SE' is valid).
            municipality: Swedish municipality code filter.
            name_query: Text search query for place names.
            language: Language filter (swe, fin, sme, smj, sma, fit).
            max_results: Maximum number of results to return.

        Yields:
            ConnectorResult instances.
        """
        if country and country.upper() != "SE":
            return

        params: dict[str, Any] = {"maxHits": self._MAX_PER_PAGE}

        if name_query:
            params["namn"] = name_query
        if municipality:
            params["kommun"] = municipality
        if language:
            params["sprak"] = language

        if bbox:
            params["nord"] = bbox.max_lat
            params["syd"] = bbox.min_lat
            params["ost"] = bbox.max_lon
            params["vast"] = bbox.min_lon

        yielded = 0
        offset = 0

        while True:
            if max_results and yielded >= max_results:
                break

            params["startindex"] = offset
            self._rate_limit()

            try:
                response = self._client.get(
                    f"{self._BASE_URL}/sok",
                    params=params,
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.warning("Lantmäteriet API error: %s", e)
                break

            data = response.json()
            features = data.get("features", [])

            if not features:
                break

            for feature in features:
                if max_results and yielded >= max_results:
                    break

                result = self._parse_feature(feature)
                if result is not None:
                    yielded += 1
                    yield result

            if len(features) < self._MAX_PER_PAGE:
                break
            offset += self._MAX_PER_PAGE

    def _parse_feature(self, feature: dict[str, Any]) -> ConnectorResult | None:
        """Parse a GeoJSON feature into a ConnectorResult."""
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        coords = geometry.get("coordinates", [])
        if len(coords) < 2:
            return None

        lon = float(coords[0])
        lat = float(coords[1])

        name = properties.get("namn", "")
        if not name:
            return None

        # Language
        lang_code = properties.get("sprak", "swe")
        iso_lang = _LANGUAGE_MAP.get(lang_code.lower(), "swe") if lang_code else "swe"

        # Feature type
        feature_type_sv = properties.get("namntyp", "")
        place_type = _FEATURE_TYPES.get(feature_type_sv, feature_type_sv.lower())

        # Source ID
        source_id = str(properties.get("id", ""))

        # Municipality
        kommun = properties.get("kommun", "")

        # Alternative names
        alt_names: dict[str, list[str]] = {}
        alternatives = properties.get("alternativa_namn", [])
        if isinstance(alternatives, list):
            for alt in alternatives:
                if isinstance(alt, dict):
                    alt_lang = _LANGUAGE_MAP.get(alt.get("sprak", "").lower(), "swe")
                    alt_name = alt.get("namn", "")
                    if alt_name:
                        alt_names.setdefault(alt_lang, []).append(alt_name)

        return ConnectorResult(
            latitude=lat,
            longitude=lon,
            name_form=name,
            name_normalized=name.lower(),
            language_code=iso_lang,
            place_type=place_type if place_type else None,
            source_id=source_id,
            source_url=f"https://ortnamn.lantmateriet.se/namn/{source_id}" if source_id else None,
            source_license="CC0-1.0",
            alternative_names=alt_names,
            is_current=True,
            accessed_at=kommun,  # Store municipality in accessed_at for metadata
        )

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a Lantmäteriet record."""
        errors: list[ValidationError] = []

        # Sweden bounding box (approximate)
        if not (55.0 <= record.latitude <= 69.5):
            errors.append(
                ValidationError(
                    field="latitude",
                    message=f"Latitude {record.latitude} outside Sweden (55-69.5°N)",
                )
            )
        if not (10.5 <= record.longitude <= 24.5):
            errors.append(
                ValidationError(
                    field="longitude",
                    message=f"Longitude {record.longitude} outside Sweden (10.5-24.5°E)",
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
        if country and country.upper() != "SE":
            return 0

        params: dict[str, Any] = {"maxHits": 0}
        if bbox:
            params["nord"] = bbox.max_lat
            params["syd"] = bbox.min_lat
            params["ost"] = bbox.max_lon
            params["vast"] = bbox.min_lon

        self._rate_limit()
        try:
            response = self._client.get(f"{self._BASE_URL}/sok", params=params)
            response.raise_for_status()
            data = response.json()
            return int(data.get("totalFeatures", 0))
        except (httpx.HTTPError, ValueError, KeyError):
            return None
