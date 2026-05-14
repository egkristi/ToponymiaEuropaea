"""Diplomatarium (medieval charter databases) connector.

Connects to digitized medieval charter databases for extracting historical
place-name attestations with dates. Primary sources include:
- Diplomatarium Norvegicum (DN)
- Diplomatarium Danicum (DD)
- Diplomatarium Suecanum (DS)

These provide the earliest written attestations of Scandinavian place names,
essential for diachronic etymological analysis.

Data format: TEI/XML digitized charters with marked-up place references.
License varies by source (most are CC-BY or public domain).
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

# Charter language codes → ISO 639-3
_LANGUAGE_MAP: dict[str, str] = {
    "lat": "lat",  # Latin (most charters)
    "la": "lat",
    "non": "non",  # Old Norse
    "nob": "nob",  # Norwegian Bokmål (modern editions)
    "dan": "dan",  # Danish
    "da": "dan",
    "swe": "swe",  # Swedish
    "sv": "swe",
    "gml": "gml",  # Middle Low German
    "fro": "fro",  # Old French
}

# Source databases
_SOURCES: dict[str, dict[str, str]] = {
    "DN": {
        "name": "Diplomatarium Norvegicum",
        "url": "https://www.dokpro.uio.no/dipl_norv/diplom_field_eng.html",
        "license": "CC-BY-4.0",
        "country": "NO",
    },
    "DD": {
        "name": "Diplomatarium Danicum",
        "url": "https://diplomatarium.dk/",
        "license": "CC-BY-4.0",
        "country": "DK",
    },
    "DS": {
        "name": "Diplomatarium Suecanum",
        "url": "https://www.riksarkivet.se/sdhk",
        "license": "CC0-1.0",
        "country": "SE",
    },
}


class DiplomatariumConnector(BaseConnector):
    """Connector for medieval charter databases (Diplomatarium series).

    Extracts historical place-name attestations from digitized medieval
    charters. Each attestation includes:
    - The name form as written in the charter
    - The date of the charter (year)
    - The language of the charter (usually Latin or Old Norse)
    - Geographic identification (when available)

    This connector supports:
    - Diplomatarium Norvegicum (NO): ~22,000 documents, 1050-1590 CE
    - Diplomatarium Danicum (DK): ~15,000 documents, 789-1450 CE
    - Diplomatarium Suecanum (SE): ~40,000 documents, 817-1420 CE
    """

    source_id = "diplomatarium"
    source_name = "Diplomatarium (Medieval Charters)"
    license = "CC-BY-4.0"
    coverage_region = "NO"  # Primary; supports DK, SE via source param
    source_url = "https://www.dokpro.uio.no/dipl_norv/diplom_field_eng.html"

    _BASE_URL = "https://www.dokpro.uio.no/dipl_norv/api"
    _MAX_PER_PAGE = 50
    _RATE_LIMIT_DELAY = 0.5  # Be respectful to academic servers

    def __init__(
        self,
        *,
        source: str = "DN",
        timeout: float = 30.0,
    ):
        """Initialize the Diplomatarium connector.

        Args:
            source: Which diplomatarium to query (DN, DD, DS).
            timeout: HTTP request timeout in seconds.
        """
        if source not in _SOURCES:
            msg = f"Unknown source: {source}. Must be one of {list(_SOURCES.keys())}"
            raise ValueError(msg)

        self._source = source
        self._source_info = _SOURCES[source]
        self.coverage_region = self._source_info["country"]
        self.license = self._source_info["license"]
        self.source_url = self._source_info["url"]

        self._client = httpx.Client(
            timeout=timeout,
            headers={"Accept": "application/json"},
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
        name_query: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Fetch historical place-name attestations from charters.

        Args:
            bbox: Geographic bounding box filter (limited support).
            country: Country filter (NO, DK, SE).
            name_query: Search for specific place-name forms.
            year_from: Earliest charter year to include.
            year_to: Latest charter year to include.
            max_results: Maximum number of results to return.

        Yields:
            ConnectorResult instances with historical attestations.
        """
        if country and country.upper() != self._source_info["country"]:
            return

        params: dict[str, Any] = {"limit": self._MAX_PER_PAGE}

        if name_query:
            params["place"] = name_query
        if year_from:
            params["year_from"] = year_from
        if year_to:
            params["year_to"] = year_to

        yielded = 0
        offset = 0

        while True:
            if max_results and yielded >= max_results:
                break

            params["offset"] = offset
            self._rate_limit()

            try:
                response = self._client.get(
                    f"{self._BASE_URL}/places",
                    params=params,
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.warning("Diplomatarium API error: %s", e)
                break

            data = response.json()
            attestations = data.get("attestations", [])

            if not attestations:
                break

            for att in attestations:
                if max_results and yielded >= max_results:
                    break

                result = self._parse_attestation(att)
                if result is not None:
                    yielded += 1
                    yield result

            if len(attestations) < self._MAX_PER_PAGE:
                break
            offset += self._MAX_PER_PAGE

    def _parse_attestation(self, att: dict[str, Any]) -> ConnectorResult | None:
        """Parse a charter attestation into a ConnectorResult."""
        name = att.get("place_form", "") or att.get("name", "")
        if not name:
            return None

        # Coordinates (often approximate or from modern identification)
        lat = att.get("latitude")
        lon = att.get("longitude")
        if lat is None or lon is None:
            lat = att.get("modern_lat", 0.0)
            lon = att.get("modern_lon", 0.0)

        lat = float(lat) if lat else 0.0
        lon = float(lon) if lon else 0.0

        # Charter date
        year = att.get("year")
        year_from = int(year) if year else None
        year_to = year_from

        # Language of the charter
        charter_lang = att.get("language", "lat")
        iso_lang = _LANGUAGE_MAP.get(charter_lang.lower(), "lat") if charter_lang else "lat"

        # Source reference
        doc_id = att.get("document_id", "")
        volume = att.get("volume", "")
        source_id = f"{self._source}:{volume}:{doc_id}" if doc_id else ""

        # Modern identification
        modern_name = att.get("modern_name", "")
        alt_names: dict[str, list[str]] = {}
        if modern_name and modern_name != name:
            alt_names["nor"] = [modern_name]

        return ConnectorResult(
            latitude=lat,
            longitude=lon,
            name_form=name,
            name_normalized=name.lower(),
            language_code=iso_lang,
            year_from=year_from,
            year_to=year_to,
            is_current=False,
            place_type="historical_attestation",
            source_id=source_id,
            source_url=self._source_info["url"],
            source_license=self._source_info["license"],
            alternative_names=alt_names,
        )

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a Diplomatarium record."""
        errors: list[ValidationError] = []

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name form"))

        # Year validation (medieval period)
        if record.year_from is not None and (record.year_from < 700 or record.year_from > 1600):
            errors.append(
                ValidationError(
                    field="year_from",
                    message=f"Year {record.year_from} outside medieval range (700-1600)",
                    severity="warning",
                )
            )

        # Language should be Latin or Old Norse for medieval charters
        valid_langs = set(_LANGUAGE_MAP.values())
        if record.language_code not in valid_langs:
            errors.append(
                ValidationError(
                    field="language_code",
                    message=f"Unexpected language for medieval charter: {record.language_code}",
                    severity="warning",
                )
            )

        return errors

    def count(self, bbox: BoundingBox | None = None, country: str | None = None) -> int | None:
        """Return estimated record count if available."""
        if country and country.upper() != self._source_info["country"]:
            return 0
        return None
