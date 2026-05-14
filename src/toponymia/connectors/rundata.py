"""Rundata (Scandinavian Runic Inscription Database) connector.

Connects to the Scandinavian Runic Text Database (Samnordisk runtextdatabas)
which catalogues all known runic inscriptions from Scandinavia and beyond.
Contains ~6,500 inscriptions with:
- Transliterated runic text
- Normalized Old Norse text
- Geographic coordinates of findspot
- Dating (period estimates)
- Place-name mentions within inscriptions

API: The database is available via the Rundata application and
web interface at Uppsala University.

License: CC-BY-4.0 (academic research use)
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

# Rundata language/script codes
_LANGUAGE_MAP: dict[str, str] = {
    "non": "non",  # Old Norse
    "on": "non",
    "run": "non",  # Runic (treated as Old Norse)
    "swe": "swe",  # Swedish (modern labels)
    "sv": "swe",
    "dan": "dan",  # Danish
    "da": "dan",
    "nor": "nor",  # Norwegian
    "no": "nor",
}

# Inscription period estimates → approximate year ranges
_PERIOD_DATES: dict[str, tuple[int, int]] = {
    "Viking Age": (800, 1100),
    "Medieval": (1100, 1400),
    "Migration Period": (400, 550),
    "Vendel Period": (550, 800),
    "Late Viking Age": (1000, 1100),
    "Early Viking Age": (800, 900),
    "Older": (150, 400),
    "Younger": (1400, 1600),
}

# Signum prefixes → country
_SIGNUM_COUNTRY: dict[str, str] = {
    "U": "SE",  # Uppland
    "Sö": "SE",  # Södermanland
    "Ög": "SE",  # Östergötland
    "Vg": "SE",  # Västergötland
    "Sm": "SE",  # Småland
    "Gs": "SE",  # Gästrikland
    "Vs": "SE",  # Västmanland
    "N": "NO",  # Norway
    "DR": "DK",  # Denmark
    "G": "SE",  # Gotland
    "Öl": "SE",  # Öland
}


class RundataConnector(BaseConnector):
    """Connector for Scandinavian Runic Text Database (Rundata/SRDB).

    Extracts place-name references from runic inscriptions, providing
    the earliest known attestations of many Scandinavian place names
    (often 800-1100 CE). Each record includes:
    - The runic text (transliterated)
    - Old Norse normalized form
    - Findspot coordinates
    - Period dating
    - Referenced place names within the inscription
    """

    source_id = "rundata"
    source_name = "Samnordisk runtextdatabas (Rundata)"
    license = "CC-BY-4.0"
    coverage_region = "SE"  # Primary; supports NO, DK
    source_url = "https://www.nordiska.uu.se/forskn/samnord.htm"

    _BASE_URL = "https://app.uu.se/rundata/api"
    _MAX_PER_PAGE = 50
    _RATE_LIMIT_DELAY = 0.5

    def __init__(self, *, timeout: float = 30.0):
        """Initialize the Rundata connector.

        Args:
            timeout: HTTP request timeout in seconds.
        """
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
        signum: str | None = None,
        name_query: str | None = None,
        period: str | None = None,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Fetch runic inscription records with place-name references.

        Args:
            bbox: Geographic bounding box filter.
            country: Country filter (SE, NO, DK).
            signum: Inscription signum filter (e.g., "U" for Uppland).
            name_query: Search within inscription text.
            period: Period filter (e.g., "Viking Age").
            max_results: Maximum number of results to return.

        Yields:
            ConnectorResult instances for place-name attestations.
        """
        params: dict[str, Any] = {"limit": self._MAX_PER_PAGE}

        if country:
            params["country"] = country.upper()
        if signum:
            params["signum_prefix"] = signum
        if name_query:
            params["text"] = name_query
        if period:
            params["period"] = period

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
                    f"{self._BASE_URL}/inscriptions",
                    params=params,
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.warning("Rundata API error: %s", e)
                break

            data = response.json()
            inscriptions = data.get("inscriptions", [])

            if not inscriptions:
                break

            for insc in inscriptions:
                if max_results and yielded >= max_results:
                    break

                results = self._parse_inscription(insc)
                for result in results:
                    if max_results and yielded >= max_results:
                        break
                    yielded += 1
                    yield result

            if len(inscriptions) < self._MAX_PER_PAGE:
                break
            offset += self._MAX_PER_PAGE

    def _parse_inscription(self, insc: dict[str, Any]) -> list[ConnectorResult]:
        """Parse a runic inscription into ConnectorResult(s).

        An inscription may reference multiple place names.
        """
        results: list[ConnectorResult] = []

        # Findspot coordinates
        lat = insc.get("latitude")
        lon = insc.get("longitude")
        if lat is None or lon is None:
            return results

        lat = float(lat)
        lon = float(lon)

        signum = insc.get("signum", "")
        period_name = insc.get("period", "")
        year_from, year_to = _PERIOD_DATES.get(period_name, (800, 1100))

        # Place names mentioned in the inscription
        place_refs = insc.get("place_names", [])
        if not place_refs:
            # Use findspot as a single record
            findspot = insc.get("findspot", "")
            if findspot:
                place_refs = [{"name": findspot, "type": "findspot"}]

        for ref in place_refs:
            name = ref.get("name", "") if isinstance(ref, dict) else str(ref)
            if not name:
                continue

            # Normalized Old Norse form
            normalized: str = (
                ref.get("normalized", name) or name if isinstance(ref, dict) else str(name)
            )

            results.append(
                ConnectorResult(
                    latitude=lat,
                    longitude=lon,
                    name_form=name,
                    name_normalized=normalized.lower(),
                    language_code="non",
                    year_from=year_from,
                    year_to=year_to,
                    is_current=False,
                    place_type="runic_attestation",
                    source_id=f"rundata:{signum}" if signum else "",
                    source_url=self.source_url,
                    source_license="CC-BY-4.0",
                )
            )

        return results

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a Rundata record."""
        errors: list[ValidationError] = []

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name form"))

        # Scandinavia bounding box
        if record.latitude != 0.0 or record.longitude != 0.0:
            if not (54.0 <= record.latitude <= 72.0):
                errors.append(
                    ValidationError(
                        field="latitude",
                        message=f"Latitude {record.latitude} outside Scandinavia (54-72°N)",
                    )
                )
            if not (4.0 <= record.longitude <= 32.0):
                errors.append(
                    ValidationError(
                        field="longitude",
                        message=f"Longitude {record.longitude} outside Scandinavia (4-32°E)",
                    )
                )

        # Year validation (runic period)
        if record.year_from is not None and (record.year_from < 100 or record.year_from > 1600):
            errors.append(
                ValidationError(
                    field="year_from",
                    message=f"Year {record.year_from} outside runic range (100-1600)",
                    severity="warning",
                )
            )

        return errors

    def count(self, bbox: BoundingBox | None = None, country: str | None = None) -> int | None:
        """Return estimated record count if available."""
        return None
