"""Wikidata connector for place names with etymology and multilingual labels.

Uses SPARQL queries against the Wikidata Query Service to fetch:
- Place names in all available languages
- Etymology information (P138: named after)
- Geographic coordinates (P625)
- Historical names and alternative spellings
"""

from __future__ import annotations

import contextlib
import logging
import time
from collections.abc import Iterator
from typing import Any

import httpx

from toponymia.config import get_settings
from toponymia.connectors.base import BaseConnector, BoundingBox, ConnectorResult, ValidationError

logger = logging.getLogger(__name__)

# SPARQL query for places within a bounding box with multilingual names
_SPARQL_TEMPLATE = """
SELECT ?place ?placeLabel ?coord ?geonames_id ?osm_id ?namedAfter ?namedAfterLabel
WHERE {{
  SERVICE wikibase:box {{
    ?place wdt:P625 ?coord .
    bd:serviceParam wikibase:cornerWest "Point({min_lon} {min_lat})"^^geo:wktLiteral .
    bd:serviceParam wikibase:cornerEast "Point({max_lon} {max_lat})"^^geo:wktLiteral .
  }}
  OPTIONAL {{ ?place wdt:P1566 ?geonames_id . }}
  OPTIONAL {{ ?place wdt:P402 ?osm_id . }}
  OPTIONAL {{ ?place wdt:P138 ?namedAfter . }}
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,de,fr,es,it,pt,ru,pl,sv,no,da,fi" .
  }}
}}
LIMIT {limit}
OFFSET {offset}
"""


class WikidataConnector(BaseConnector):
    """Connector for Wikidata place name data via SPARQL."""

    source_id = "wikidata"
    source_name = "Wikidata"
    license = "CC0-1.0"
    coverage_region = "global"
    source_url = "https://www.wikidata.org"

    def __init__(self) -> None:
        settings = get_settings()
        self._endpoint = settings.wikidata_endpoint
        self._batch_size = 5000
        self._rate_limit_seconds = 2.0

    def fetch(
        self, bbox: BoundingBox | None = None, country: str | None = None
    ) -> Iterator[ConnectorResult]:
        """Fetch place names from Wikidata within a bounding box.

        Note: Wikidata requires a bounding box for efficient spatial queries.
        If country is specified without bbox, a default bbox for the country is used.
        """
        if bbox is None and country is None:
            raise ValueError("Either bbox or country must be specified for Wikidata queries")

        if bbox is None:
            bbox = self._country_bbox(country)

        offset = 0
        while True:
            query = _SPARQL_TEMPLATE.format(
                min_lon=bbox.min_lon,
                min_lat=bbox.min_lat,
                max_lon=bbox.max_lon,
                max_lat=bbox.max_lat,
                limit=self._batch_size,
                offset=offset,
            )

            results = self._execute_sparql(query)
            if not results:
                break

            for result in results:
                record = self._parse_result(result)
                if record is not None:
                    yield record

            if len(results) < self._batch_size:
                break

            offset += self._batch_size
            time.sleep(self._rate_limit_seconds)

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a Wikidata record."""
        errors: list[ValidationError] = []

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name"))

        if record.wikidata_qid and not record.wikidata_qid.startswith("Q"):
            errors.append(ValidationError(field="wikidata_qid", message="Invalid QID format"))

        return errors

    def _execute_sparql(self, query: str) -> list[dict[str, Any]]:
        """Execute SPARQL query with rate limiting and error handling."""
        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "ToponymiaEuropaea/0.1 (research project; https://github.com/egkristi/ToponymiaEuropaea)",
        }

        try:
            response = httpx.get(
                self._endpoint,
                params={"query": query},
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return list(data.get("results", {}).get("bindings", []))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limited by Wikidata, waiting...")
                time.sleep(60)
                return self._execute_sparql(query)
            logger.error(f"Wikidata SPARQL error: {e}")
            return []
        except Exception as e:
            logger.error(f"Wikidata query failed: {e}")
            return []

    def _parse_result(self, result: dict[str, Any]) -> ConnectorResult | None:
        """Parse a SPARQL result binding into a ConnectorResult."""
        coord_value = result.get("coord", {}).get("value", "")
        if not coord_value:
            return None

        # Parse "Point(lon lat)" WKT
        try:
            coords = coord_value.replace("Point(", "").replace(")", "").split()
            lon, lat = float(coords[0]), float(coords[1])
        except (ValueError, IndexError):
            return None

        place_uri = result.get("place", {}).get("value", "")
        qid = place_uri.split("/")[-1] if place_uri else None

        name = result.get("placeLabel", {}).get("value", "")
        if not name or name == qid:  # Label resolves to QID if no label exists
            return None

        geonames_id = None
        if "geonames_id" in result:
            with contextlib.suppress(ValueError, KeyError):
                geonames_id = int(result["geonames_id"]["value"])

        return ConnectorResult(
            latitude=lat,
            longitude=lon,
            name_form=name,
            name_normalized=name,
            language_code="und",
            source_id=qid or "",
            wikidata_qid=qid,
            geonames_id=geonames_id,
            source_url=place_uri,
            source_license="CC0-1.0",
            is_current=True,
        )

    @staticmethod
    def _country_bbox(country: str | None) -> BoundingBox:
        """Return approximate bounding box for common countries."""
        # Approximate bboxes for common European countries
        bboxes = {
            "NO": BoundingBox(4.0, 57.0, 31.5, 71.5),
            "SE": BoundingBox(10.5, 55.0, 24.5, 69.5),
            "DK": BoundingBox(7.5, 54.5, 15.5, 58.0),
            "FI": BoundingBox(19.0, 59.5, 32.0, 70.5),
            "IS": BoundingBox(-25.0, 63.0, -13.0, 67.0),
            "GB": BoundingBox(-8.5, 49.5, 2.0, 61.0),
            "DE": BoundingBox(5.5, 47.0, 15.5, 55.5),
            "FR": BoundingBox(-5.5, 41.0, 10.0, 51.5),
            "ES": BoundingBox(-10.0, 35.5, 4.5, 44.0),
            "IT": BoundingBox(6.5, 36.0, 19.0, 47.5),
            "PL": BoundingBox(14.0, 49.0, 24.5, 55.0),
            "RU": BoundingBox(27.0, 41.0, 180.0, 82.0),
        }
        if country and country.upper() in bboxes:
            return bboxes[country.upper()]
        # Default: all of Europe
        return BoundingBox(-25.0, 34.0, 45.0, 72.0)
