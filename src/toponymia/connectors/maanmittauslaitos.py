"""Maanmittauslaitos (National Land Survey of Finland) connector.

Connects to Finland's authoritative place-name registry maintained by
Maanmittauslaitos (MML). The registry contains approximately 800,000 place
names in Finnish, Swedish, and Sámi languages with coordinates and
feature classifications.

API documentation: https://www.maanmittauslaitos.fi/en/rajapinnat/api-avaimen-ohje
Data license: CC BY 4.0

Note: The MML geographic names API requires an API key. This connector
implements the standard interface for the paikannimet (place names) endpoint.
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

# MML language codes → ISO 639-3
_LANGUAGE_MAP: dict[str, str] = {
    "fin": "fin",  # Finnish
    "fi": "fin",
    "swe": "swe",  # Swedish (Finland-Swedish)
    "sv": "swe",
    "sme": "sme",  # Northern Sámi
    "smn": "smn",  # Inari Sámi
    "sms": "sms",  # Skolt Sámi
    "se": "sme",
}

# Feature type mapping (Finnish → English)
_FEATURE_TYPES: dict[str, str] = {
    "Asutus": "settlement",
    "Kaupunginosa": "city_district",
    "Kylä": "village",
    "Talo": "farmstead",
    "Vesistö": "water_body",
    "Järvi": "lake",
    "Joki": "river",
    "Lampi": "pond",
    "Lahti": "bay",
    "Salmi": "strait",
    "Maasto": "terrain",
    "Tunturi": "fell",
    "Vaara": "hill",
    "Mäki": "hill",
    "Suo": "bog",
    "Saari": "island",
    "Niemi": "cape",
    "Kangas": "heath",
    "Metsä": "forest",
    "Pelto": "field",
}


class MaanmittauslaitosConnector(BaseConnector):
    """Connector for MML Paikannimet API (Finnish national place-name registry).

    This connector queries the Maanmittauslaitos place-name web service which
    provides authoritative Finnish place names including:
    - Official Finnish names
    - Swedish-language names (bilingual municipalities)
    - Sámi-language names (Northern, Inari, Skolt)
    - Coordinates (ETRS-TM35FIN, served as WGS84 via GeoJSON)
    - Municipality codes and feature type classifications
    """

    source_id = "maanmittauslaitos"
    source_name = "Maanmittauslaitos Paikannimet"
    license = "CC-BY-4.0"
    coverage_region = "FI"
    source_url = "https://avoin-paikkatieto.maanmittauslaitos.fi/geographic-names/features/v1/"

    _BASE_URL = "https://avoin-paikkatieto.maanmittauslaitos.fi/geographic-names/features/v1"
    _MAX_PER_PAGE = 100
    _RATE_LIMIT_DELAY = 0.25  # seconds between requests

    def __init__(self, *, api_key: str = "", timeout: float = 30.0):
        """Initialize the Maanmittauslaitos connector.

        Args:
            api_key: API key for MML (required for production use).
            timeout: HTTP request timeout in seconds.
        """
        self._api_key = api_key
        headers: dict[str, str] = {"Accept": "application/json"}
        self._client = httpx.Client(
            timeout=timeout,
            headers=headers,
            auth=(api_key, "") if api_key else None,
        )
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
        """Fetch place names from MML.

        Args:
            bbox: Geographic bounding box filter.
            country: Country filter (only 'FI' is valid).
            municipality: Finnish municipality code filter.
            name_query: Text search query for place names.
            language: Language filter (fin, swe, sme, smn, sms).
            max_results: Maximum number of results to return.

        Yields:
            ConnectorResult instances.
        """
        if country and country.upper() != "FI":
            return

        params: dict[str, Any] = {"limit": self._MAX_PER_PAGE}

        if name_query:
            params["name"] = name_query
        if municipality:
            params["municipality"] = municipality
        if language:
            params["language"] = language

        if bbox:
            params["bbox"] = f"{bbox.min_lon},{bbox.min_lat},{bbox.max_lon},{bbox.max_lat}"

        yielded = 0
        offset = 0

        while True:
            if max_results and yielded >= max_results:
                break

            params["offset"] = offset
            self._rate_limit()

            try:
                response = self._client.get(
                    f"{self._BASE_URL}/collections/placenames/items",
                    params=params,
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.warning("MML API error: %s", e)
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

        name = properties.get("spelling", "") or properties.get("name", "")
        if not name:
            return None

        # Language
        lang_code = properties.get("language", "fin")
        iso_lang = _LANGUAGE_MAP.get(lang_code.lower(), "fin") if lang_code else "fin"

        # Feature type
        feature_type = properties.get("placeType", "")
        place_type = _FEATURE_TYPES.get(feature_type, feature_type.lower())

        # Source ID
        source_id = str(properties.get("placeId", feature.get("id", "")))

        # Municipality
        kunta = properties.get("municipality", "")

        # Alternative names
        alt_names: dict[str, list[str]] = {}
        alternatives = properties.get("alternativeSpellings", [])
        if isinstance(alternatives, list):
            for alt in alternatives:
                if isinstance(alt, dict):
                    alt_lang = _LANGUAGE_MAP.get(alt.get("language", "").lower(), "fin")
                    alt_name = alt.get("spelling", "")
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
            source_url=f"https://avoin-paikkatieto.maanmittauslaitos.fi/geographic-names/features/v1/collections/placenames/items/{source_id}"
            if source_id
            else None,
            source_license="CC-BY-4.0",
            alternative_names=alt_names,
            is_current=True,
            accessed_at=kunta,  # Store municipality for metadata
        )

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a Maanmittauslaitos record."""
        errors: list[ValidationError] = []

        # Finland bounding box (approximate)
        if not (59.5 <= record.latitude <= 70.5):
            errors.append(
                ValidationError(
                    field="latitude",
                    message=f"Latitude {record.latitude} outside Finland (59.5-70.5°N)",
                )
            )
        if not (19.0 <= record.longitude <= 31.7):
            errors.append(
                ValidationError(
                    field="longitude",
                    message=f"Longitude {record.longitude} outside Finland (19-31.7°E)",
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
        if country and country.upper() != "FI":
            return 0

        params: dict[str, Any] = {"limit": 0}
        if bbox:
            params["bbox"] = f"{bbox.min_lon},{bbox.min_lat},{bbox.max_lon},{bbox.max_lat}"

        self._rate_limit()
        try:
            response = self._client.get(
                f"{self._BASE_URL}/collections/placenames/items",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            return int(data.get("numberMatched", 0))
        except (httpx.HTTPError, ValueError, KeyError):
            return None
