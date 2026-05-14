"""IGN (Institut Géographique National, France) connector.

Connects to France's authoritative geographic data maintained by
IGN. The BD NYME (Base de Données des Noms et Lieux) contains
approximately 4 million geographic names across France, DOM-TOM,
and overseas territories.

API documentation: https://geoservices.ign.fr/documentation/donnees/vecteur/bdnyme
Data license: Licence Ouverte 2.0 (Etalab)

Note: IGN provides open data via the Géoplateforme API. Some
endpoints require registration. This connector targets the
open geocoding and search APIs.
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

# IGN language codes → ISO 639-3
_LANGUAGE_MAP: dict[str, str] = {
    "fra": "fra",  # French
    "fr": "fra",
    "bre": "bre",  # Breton
    "br": "bre",
    "oci": "oci",  # Occitan
    "oc": "oci",
    "cat": "cat",  # Catalan
    "ca": "cat",
    "eus": "eus",  # Basque
    "eu": "eus",
    "cos": "cos",  # Corsican
    "co": "cos",
    "als": "gsw",  # Alsatian (Germanic)
    "gsw": "gsw",
}

# IGN feature type mapping (French → English)
_FEATURE_TYPES: dict[str, str] = {
    "Commune": "municipality",
    "Lieu-dit habité": "hamlet",
    "Lieu-dit non habité": "locality",
    "Château": "castle",
    "Cours d'eau": "river",
    "Plan d'eau": "lake",
    "Relief": "landform",
    "Sommet": "peak",
    "Col": "pass",
    "Forêt": "forest",
    "Île": "island",
    "Cap": "cape",
    "Baie": "bay",
    "Plage": "beach",
    "Grotte": "cave",
    "Vallée": "valley",
    "Montagne": "mountain",
    "Plateau": "plateau",
}


class IGNConnector(BaseConnector):
    """Connector for IGN Géoplateforme API (French national mapping).

    This connector queries the IGN geographic search service which provides
    authoritative French place names including:
    - Official French names across metropolitan France
    - Regional language names (Breton, Occitan, Catalan, Basque, Corsican, Alsatian)
    - Coordinates (Lambert-93 / RGF93, served as WGS84 via API)
    - Administrative codes (INSEE) and feature type classifications
    """

    source_id = "ign"
    source_name = "IGN BD NYME"
    license = "Etalab-2.0"
    coverage_region = "FR"
    source_url = "https://data.geopf.fr/geocodage/"

    _BASE_URL = "https://data.geopf.fr/geocodage"
    _MAX_PER_PAGE = 100
    _RATE_LIMIT_DELAY = 0.25  # seconds between requests

    def __init__(self, *, api_key: str = "", timeout: float = 30.0):
        """Initialize the IGN connector.

        Args:
            api_key: API key for IGN (optional for most endpoints).
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
        department: str | None = None,
        name_query: str | None = None,
        feature_type: str | None = None,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Fetch place names from IGN.

        Args:
            bbox: Geographic bounding box filter.
            country: Country filter (only 'FR' is valid).
            department: French department code filter (e.g., '75' for Paris).
            name_query: Text search query for place names.
            feature_type: Filter by IGN feature type.
            max_results: Maximum number of results to return.

        Yields:
            ConnectorResult instances.
        """
        if country and country.upper() != "FR":
            return

        params: dict[str, Any] = {"limit": self._MAX_PER_PAGE}

        if name_query:
            params["q"] = name_query
        if department:
            params["departmentcode"] = department
        if feature_type:
            params["type"] = feature_type

        if bbox:
            params["lon"] = (bbox.min_lon + bbox.max_lon) / 2
            params["lat"] = (bbox.min_lat + bbox.max_lat) / 2

        yielded = 0

        self._rate_limit()

        try:
            response = self._client.get(
                f"{self._BASE_URL}/search",
                params=params,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning("IGN API error: %s", e)
            return

        data = response.json()
        features = data.get("features", [])

        for feature in features:
            if max_results and yielded >= max_results:
                break

            result = self._parse_feature(feature)
            if result is not None:
                yielded += 1
                yield result

    def _parse_feature(self, feature: dict[str, Any]) -> ConnectorResult | None:
        """Parse a GeoJSON feature into a ConnectorResult."""
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        coords = geometry.get("coordinates", [])
        if len(coords) < 2:
            return None

        lon = float(coords[0])
        lat = float(coords[1])

        name = properties.get("label", "") or properties.get("name", "")
        if not name:
            return None

        # Language (IGN defaults to French)
        iso_lang = "fra"

        # Feature type
        feature_type = properties.get("type", "")
        place_type = _FEATURE_TYPES.get(feature_type, feature_type.lower())

        # Source ID (INSEE code or IGN ID)
        source_id = str(properties.get("id", "") or properties.get("citycode", ""))

        # Department/context
        context = properties.get("context", "")

        # Alternative names
        alt_names: dict[str, list[str]] = {}
        old_name = properties.get("oldcityname", "")
        if old_name and old_name != name:
            alt_names["fra"] = [old_name]

        return ConnectorResult(
            latitude=lat,
            longitude=lon,
            name_form=name,
            name_normalized=name.lower(),
            language_code=iso_lang,
            place_type=place_type if place_type else None,
            source_id=f"ign:{source_id}" if source_id else "",
            source_url=f"https://www.geoportail.gouv.fr/carte?c={lon},{lat}&z=14"
            if source_id
            else None,
            source_license="Etalab-2.0",
            alternative_names=alt_names,
            is_current=True,
            accessed_at=context,
        )

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate an IGN record."""
        errors: list[ValidationError] = []

        # France bounding box (metropolitan, approximate)
        if not (41.0 <= record.latitude <= 51.5):
            errors.append(
                ValidationError(
                    field="latitude",
                    message=f"Latitude {record.latitude} outside France (41-51.5°N)",
                )
            )
        if not (-5.5 <= record.longitude <= 10.0):
            errors.append(
                ValidationError(
                    field="longitude",
                    message=f"Longitude {record.longitude} outside France (-5.5 to 10°E)",
                )
            )

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name"))

        valid_langs = set(_LANGUAGE_MAP.values())
        if record.language_code not in valid_langs:
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
        if country and country.upper() != "FR":
            return 0
        # IGN geocoding API does not expose total count cheaply
        return None
