"""Kartverket Stedsnavn (Norwegian Place Names) connector.

Connects to Norway's authoritative place-name registry maintained by
Kartverket (Norwegian Mapping Authority). The registry contains ~800,000
place names with coordinates, municipality codes, language codes, and
administrative metadata.

API documentation: https://ws.geonorge.no/stedsnavn/v1/
Data license: NLOD 2.0 (Norwegian Licence for Open Government Data)
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator

import httpx

from toponymia.connectors.base import BaseConnector, BoundingBox, ConnectorResult, ValidationError

logger = logging.getLogger(__name__)

# Kartverket language codes → ISO 639-3
_LANGUAGE_MAP = {
    "nor": "nor",  # Norwegian (generic)
    "nob": "nob",  # Norwegian Bokmål
    "nno": "nno",  # Norwegian Nynorsk
    "sme": "sme",  # Northern Sámi
    "smj": "smj",  # Lule Sámi
    "sma": "sma",  # Southern Sámi
    "fkv": "fkv",  # Kven Finnish
    "fin": "fin",  # Finnish
}

# Kartverket name status values
_STATUS_VEDTATT = "vedtatt"  # Official / decided
_STATUS_GODKJENT = "godkjent"  # Approved
_STATUS_SAMLEVEDTAK = "samlevedtak"  # Collective decision
_STATUS_PRIVAT = "privat"  # Private use
_STATUS_HISTORISK = "historisk"  # Historical


class KartverketConnector(BaseConnector):
    """Connector for Kartverket Stedsnavn API (Norwegian national place-name registry).

    This connector queries the Kartverket place-name web service which provides
    authoritative Norwegian place names including:
    - Official names in Norwegian (Bokmål and Nynorsk)
    - Sámi names (Northern, Lule, Southern)
    - Kven/Finnish minority names
    - Coordinates (UTM33 / ETRS89, converted to WGS84)
    - Municipality codes and feature type classifications
    """

    source_id = "kartverket"
    source_name = "Kartverket Stedsnavn"
    license = "NLOD-2.0"
    coverage_region = "NO"
    source_url = "https://ws.geonorge.no/stedsnavn/v1/"

    _BASE_URL = "https://ws.geonorge.no/stedsnavn/v1/sted"
    _SEARCH_URL = "https://ws.geonorge.no/stedsnavn/v1/sok"
    _MAX_PER_PAGE = 100
    _RATE_LIMIT_DELAY = 0.2  # seconds between requests

    def __init__(self, *, timeout: float = 30.0):
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
        municipality: str | None = None,
        name_query: str | None = None,
        language: str | None = None,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Fetch place names from Kartverket.

        Args:
            bbox: Geographic bounding box filter (WGS84).
            country: Ignored (always NO).
            municipality: 4-digit municipality code filter.
            name_query: Text search filter (partial match).
            language: Language code filter (nob/nno/sme/smj/sma/fkv).
            max_results: Maximum number of results to return.

        Yields:
            ConnectorResult for each place name found.
        """
        params: dict[str, str | int] = {
            "treffPerSide": self._MAX_PER_PAGE,
            "side": 1,
        }

        if bbox:
            # Kartverket accepts WGS84 bbox as nord, sor, ost, vest
            params["nord"] = bbox.max_lat
            params["sor"] = bbox.min_lat
            params["ost"] = bbox.max_lon
            params["vest"] = bbox.min_lon

        if municipality:
            params["kommunenummer"] = municipality

        if name_query:
            params["sok"] = name_query

        if language:
            params["spraak"] = language

        total_yielded = 0
        while True:
            self._rate_limit()
            try:
                response = self._client.get(self._SEARCH_URL, params=params)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error("Kartverket API error: %s", e)
                break
            except httpx.RequestError as e:
                logger.error("Kartverket request failed: %s", e)
                break

            data = response.json()
            names = data.get("navn", [])

            if not names:
                break

            for name_entry in names:
                results = self._parse_name_entry(name_entry)
                for result in results:
                    yield result
                    total_yielded += 1
                    if max_results and total_yielded >= max_results:
                        return

            # Check if there are more pages
            metadata = data.get("metadata", {})
            total_pages = metadata.get("totaltAntallSider", 1)
            current_page = metadata.get("side", 1)

            if current_page >= total_pages:
                break

            params["side"] = current_page + 1

    def _parse_name_entry(self, entry: dict) -> list[ConnectorResult]:
        """Parse a single name entry from the API response.

        Each entry may have multiple name forms (different languages/spellings).
        """
        results = []

        # Get representative point coordinates
        representasjonspunkt = entry.get("representasjonspunkt", {})
        lat = representasjonspunkt.get("nord")
        lon = representasjonspunkt.get("ost")

        if lat is None or lon is None:
            # Try alternative coordinate paths
            koordinater = entry.get("koordinater", {})
            lat = koordinater.get("nord", koordinater.get("lat"))
            lon = koordinater.get("ost", koordinater.get("lon"))

        if lat is None or lon is None:
            logger.debug("Skipping entry without coordinates: %s", entry.get("skrivemåte", "?"))
            return results

        # Feature type
        navneobjekttype = entry.get("navneobjekttype", "")

        # Source identifier
        stedsnummer = str(entry.get("stedsnummer", ""))

        # Process each name form (skrivemåte = spelling)
        skrivemaater = entry.get("skrivemåter", entry.get("skrivemater", []))
        if not skrivemaater:
            # Fallback: single name
            skrivemaate = entry.get("skrivemåte", entry.get("skrivemåte_enkel", ""))
            if skrivemaate:
                skrivemaater = [{"langnavn": skrivemaate}]

        for skriv in skrivemaater:
            name_form = skriv.get("langnavn", skriv.get("skrivemåte", ""))
            if not name_form:
                continue

            # Language from skrivemåte
            spraak = skriv.get("språk", skriv.get("spraak", "nor"))
            iso_code = _LANGUAGE_MAP.get(spraak, "nor")

            # Name status
            navnestatus = skriv.get("navnestatus", "")
            is_current = navnestatus in (_STATUS_VEDTATT, _STATUS_GODKJENT, _STATUS_SAMLEVEDTAK)

            result = ConnectorResult(
                latitude=float(lat),
                longitude=float(lon),
                name_form=name_form,
                name_normalized=name_form.lower().strip(),
                language_code=iso_code,
                is_current=is_current,
                place_type=navneobjekttype,
                source_id=f"kartverket:{stedsnummer}",
                source_url=f"https://ws.geonorge.no/stedsnavn/v1/sted/{stedsnummer}",
                source_license="NLOD-2.0",
                alternative_names=self._extract_alternatives(skrivemaater, name_form),
            )

            results.append(result)

        return results

    def _extract_alternatives(
        self, skrivemaater: list[dict], exclude_form: str
    ) -> dict[str, list[str]]:
        """Extract alternative name forms grouped by language."""
        alternatives: dict[str, list[str]] = {}
        for skriv in skrivemaater:
            form = skriv.get("langnavn", skriv.get("skrivemåte", ""))
            if not form or form == exclude_form:
                continue
            spraak = skriv.get("språk", skriv.get("spraak", "nor"))
            iso_code = _LANGUAGE_MAP.get(spraak, "nor")
            alternatives.setdefault(iso_code, []).append(form)
        return alternatives

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a Kartverket record.

        Checks:
        - Coordinates within Norway's bounding box
        - Name form is non-empty
        - Language code is recognized
        """
        errors = []

        # Norway bounding box (approximate)
        if not (57.0 <= record.latitude <= 72.0):
            errors.append(
                ValidationError(
                    field="latitude",
                    message=f"Latitude {record.latitude} outside Norway bounds (57-72°N)",
                )
            )
        if not (4.0 <= record.longitude <= 32.0):
            errors.append(
                ValidationError(
                    field="longitude",
                    message=f"Longitude {record.longitude} outside Norway bounds (4-32°E)",
                )
            )

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name form"))

        if record.language_code not in _LANGUAGE_MAP.values():
            errors.append(
                ValidationError(
                    field="language_code",
                    message=f"Unrecognized language: {record.language_code}",
                    severity="warning",
                )
            )

        return errors

    def count(self, bbox: BoundingBox | None = None, country: str | None = None) -> int | None:
        """Get estimated record count from the API metadata."""
        params: dict[str, str | int] = {"treffPerSide": 1, "side": 1}

        if bbox:
            params["nord"] = bbox.max_lat
            params["sor"] = bbox.min_lat
            params["ost"] = bbox.max_lon
            params["vest"] = bbox.min_lon

        try:
            self._rate_limit()
            response = self._client.get(self._SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("metadata", {}).get("totaltAntallTreff")
        except (httpx.HTTPError, KeyError):
            return None

    def __del__(self) -> None:
        """Close the HTTP client on cleanup."""
        if hasattr(self, "_client"):
            self._client.close()
