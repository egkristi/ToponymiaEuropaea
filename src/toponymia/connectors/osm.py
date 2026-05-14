"""OpenStreetMap connector for place names.

Extracts place names from OpenStreetMap via the Overpass API,
including multilingual name tags (name:xx) and etymology tags.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator

import httpx

from toponymia.connectors.base import BaseConnector, BoundingBox, ConnectorResult, ValidationError

logger = logging.getLogger(__name__)

_OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"

_OVERPASS_QUERY_TEMPLATE = """
[out:json][timeout:300];
(
  node["name"]["place"]({min_lat},{min_lon},{max_lat},{max_lon});
  way["name"]["place"]({min_lat},{min_lon},{max_lat},{max_lon});
  relation["name"]["place"]({min_lat},{min_lon},{max_lat},{max_lon});
);
out center meta;
"""


class OSMConnector(BaseConnector):
    """Connector for OpenStreetMap place names via Overpass API."""

    source_id = "osm"
    source_name = "OpenStreetMap"
    license = "ODbL-1.0"
    coverage_region = "global"
    source_url = "https://www.openstreetmap.org"

    def __init__(self, endpoint: str = _OVERPASS_ENDPOINT):
        self._endpoint = endpoint
        self._rate_limit_seconds = 10.0

    def fetch(
        self, bbox: BoundingBox | None = None, country: str | None = None
    ) -> Iterator[ConnectorResult]:
        """Fetch place names from OSM within a bounding box."""
        if bbox is None:
            raise ValueError("OSM connector requires a bounding box")

        query = _OVERPASS_QUERY_TEMPLATE.format(
            min_lat=bbox.min_lat,
            min_lon=bbox.min_lon,
            max_lat=bbox.max_lat,
            max_lon=bbox.max_lon,
        )

        elements = self._execute_overpass(query)

        for element in elements:
            record = self._parse_element(element)
            if record is not None:
                yield record

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate an OSM record."""
        errors: list[ValidationError] = []

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name"))

        if not (-90 <= record.latitude <= 90):
            errors.append(
                ValidationError(field="latitude", message=f"Invalid latitude: {record.latitude}")
            )

        if not (-180 <= record.longitude <= 180):
            errors.append(
                ValidationError(field="longitude", message=f"Invalid longitude: {record.longitude}")
            )

        return errors

    def _execute_overpass(self, query: str) -> list[dict]:
        """Execute Overpass API query."""
        try:
            response = httpx.post(
                self._endpoint,
                data={"data": query},
                timeout=300.0,
                headers={"User-Agent": "ToponymiaEuropaea/0.1"},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("elements", [])
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limited by Overpass API, waiting 60s...")
                time.sleep(60)
                return self._execute_overpass(query)
            logger.error(f"Overpass API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Overpass query failed: {e}")
            return []

    def _parse_element(self, element: dict) -> ConnectorResult | None:
        """Parse an OSM element into a ConnectorResult."""
        tags = element.get("tags", {})
        name = tags.get("name", "")
        if not name:
            return None

        # Get coordinates (for ways/relations, use center)
        if element["type"] == "node":
            lat = element.get("lat")
            lon = element.get("lon")
        else:
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is None or lon is None:
            return None

        # Extract multilingual names
        alt_names: dict[str, list[str]] = {}
        for key, value in tags.items():
            if key.startswith("name:") and len(key) > 5:
                lang = key[5:]  # e.g., "name:en" -> "en"
                alt_names.setdefault(lang, []).append(value)

        # Old names
        if "old_name" in tags:
            alt_names.setdefault("historical", []).append(tags["old_name"])

        osm_id = element.get("id")
        place_type = tags.get("place", "")

        return ConnectorResult(
            latitude=lat,
            longitude=lon,
            name_form=name,
            name_normalized=name,
            language_code="und",
            place_type=f"osm.{place_type}" if place_type else None,
            source_id=f"{element['type']}/{osm_id}",
            osm_id=osm_id,
            alternative_names=alt_names,
            source_url=f"https://www.openstreetmap.org/{element['type']}/{osm_id}",
            source_license="ODbL-1.0",
            is_current=True,
        )
