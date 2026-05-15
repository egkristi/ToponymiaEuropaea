"""Wikidata etymology extraction pipeline (P138: named after).

Extracts etymology relationships for European place names using
Wikidata's P138 property and maps them to databank records.

See issue #19.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "ToponymiaEuropaea/0.1 (research; https://github.com/egkristi/ToponymiaEuropaea)"

# SPARQL query for etymology extraction with P138
_ETYMOLOGY_SPARQL = """
SELECT ?place ?placeLabel ?coord ?namedAfter ?namedAfterLabel
       ?namedAfterDescription ?country
WHERE {{
  ?place wdt:P31/wdt:P279* wd:Q486972 .  # instance of human settlement
  ?place wdt:P17 wd:{country_qid} .       # country
  ?place wdt:P138 ?namedAfter .            # named after (P138)
  ?place wdt:P625 ?coord .                 # coordinates
  OPTIONAL {{ ?place wdt:P17 ?country . }}
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,{lang}" .
  }}
}}
LIMIT {limit}
OFFSET {offset}
"""

# Country QIDs for Nordic + key European countries
COUNTRY_QIDS: dict[str, str] = {
    "NO": "Q20",
    "SE": "Q34",
    "DK": "Q35",
    "FI": "Q33",
    "IS": "Q189",
    "GB": "Q145",
    "IE": "Q27",
    "DE": "Q183",
    "FR": "Q142",
    "ES": "Q29",
    "IT": "Q38",
    "PL": "Q36",
    "NL": "Q55",
    "PT": "Q45",
    "AT": "Q40",
    "CH": "Q39",
    "BE": "Q31",
    "CZ": "Q213",
}

# Language codes for label resolution
COUNTRY_LANGS: dict[str, str] = {
    "NO": "no,nn,nb",
    "SE": "sv",
    "DK": "da",
    "FI": "fi,sv",
    "IS": "is",
    "GB": "en",
    "IE": "en,ga",
    "DE": "de",
    "FR": "fr",
    "ES": "es,ca,eu,gl",
    "IT": "it",
    "PL": "pl",
    "NL": "nl",
    "PT": "pt",
    "AT": "de",
    "CH": "de,fr,it,rm",
    "BE": "nl,fr,de",
    "CZ": "cs",
}


@dataclass
class EtymologyRecord:
    """A place name with its etymology from Wikidata."""

    place_qid: str
    place_name: str
    lat: float
    lon: float
    named_after_qid: str
    named_after_label: str
    named_after_description: str = ""
    country_code: str = ""
    source: str = "wikidata"
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSONL output."""
        return {
            "place_qid": self.place_qid,
            "place_name": self.place_name,
            "lat": self.lat,
            "lon": self.lon,
            "named_after_qid": self.named_after_qid,
            "named_after_label": self.named_after_label,
            "named_after_description": self.named_after_description,
            "country_code": self.country_code,
            "source": self.source,
            **self.extra,
        }


def execute_sparql(query: str, *, endpoint: str | None = None) -> list[dict]:
    """Execute a SPARQL query against Wikidata.

    Args:
        query: SPARQL query string.
        endpoint: SPARQL endpoint URL (default: Wikidata).

    Returns:
        List of result bindings.
    """
    url = endpoint or WIKIDATA_SPARQL_ENDPOINT
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": USER_AGENT,
    }

    response = httpx.get(
        url,
        params={"query": query},
        headers=headers,
        timeout=120.0,
    )
    response.raise_for_status()
    data = response.json()
    return list(data.get("results", {}).get("bindings", []))


def extract_etymologies(
    country_code: str,
    *,
    limit: int = 5000,
    rate_limit: float = 2.0,
    endpoint: str | None = None,
) -> list[EtymologyRecord]:
    """Extract etymology records for all settlements in a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code.
        limit: Maximum results per batch.
        rate_limit: Seconds between API calls.
        endpoint: Optional SPARQL endpoint override.

    Returns:
        List of EtymologyRecord objects.
    """
    country_qid = COUNTRY_QIDS.get(country_code.upper())
    if not country_qid:
        logger.warning(f"No QID mapping for country: {country_code}")
        return []

    lang = COUNTRY_LANGS.get(country_code.upper(), "en")
    records: list[EtymologyRecord] = []
    offset = 0

    while True:
        query = _ETYMOLOGY_SPARQL.format(
            country_qid=country_qid,
            lang=lang,
            limit=limit,
            offset=offset,
        )

        try:
            results = execute_sparql(query, endpoint=endpoint)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limited, waiting 60s...")
                time.sleep(60)
                continue
            logger.error(f"SPARQL error: {e}")
            break
        except httpx.TimeoutException:
            logger.error(f"Query timed out at offset {offset}")
            break

        if not results:
            break

        for binding in results:
            record = _parse_etymology_binding(binding, country_code)
            if record:
                records.append(record)

        logger.info(
            f"  {country_code}: fetched {len(results)} results "
            f"(offset={offset}, total={len(records)})"
        )

        if len(results) < limit:
            break

        offset += limit
        time.sleep(rate_limit)

    return records


def _parse_etymology_binding(
    binding: dict[str, Any],
    country_code: str,
) -> EtymologyRecord | None:
    """Parse a SPARQL binding into an EtymologyRecord."""
    # Parse coordinates from WKT Point
    coord_value = binding.get("coord", {}).get("value", "")
    if not coord_value:
        return None

    try:
        coords = coord_value.replace("Point(", "").replace(")", "").split()
        lon, lat = float(coords[0]), float(coords[1])
    except (ValueError, IndexError):
        return None

    place_uri = binding.get("place", {}).get("value", "")
    place_qid = place_uri.split("/")[-1] if place_uri else ""
    place_name = binding.get("placeLabel", {}).get("value", "")

    named_after_uri = binding.get("namedAfter", {}).get("value", "")
    named_after_qid = named_after_uri.split("/")[-1] if named_after_uri else ""
    named_after_label = binding.get("namedAfterLabel", {}).get("value", "")
    named_after_desc = binding.get("namedAfterDescription", {}).get("value", "")

    if not place_name or not named_after_qid:
        return None

    # Skip if label resolves to QID (no human-readable label)
    if place_name == place_qid or named_after_label == named_after_qid:
        return None

    return EtymologyRecord(
        place_qid=place_qid,
        place_name=place_name,
        lat=lat,
        lon=lon,
        named_after_qid=named_after_qid,
        named_after_label=named_after_label,
        named_after_description=named_after_desc,
        country_code=country_code.upper(),
    )


def match_to_databank(
    etymology_records: list[EtymologyRecord],
    databank_path: Path | None = None,
    *,
    distance_threshold_m: float = 1000.0,
) -> list[dict[str, Any]]:
    """Match etymology records to existing databank places.

    Matches are based on name similarity and coordinate proximity.

    Args:
        etymology_records: Records from Wikidata extraction.
        databank_path: Path to the databank directory.
        distance_threshold_m: Maximum distance in meters for coordinate match.

    Returns:
        List of matched records with etymology enrichment.
    """
    from toponymia.pipelines.coordinates import haversine_distance

    if databank_path is None:
        databank_path = Path(__file__).parent.parent.parent.parent / "databank"

    # Load databank records
    places_dir = databank_path / "places"
    if not places_dir.exists():
        return []

    databank_records: list[dict] = []
    for jsonl_file in places_dir.rglob("*.jsonl"):
        with jsonl_file.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    databank_records.append(json.loads(line))

    # Index by name (lowercase) for quick lookup
    name_index: dict[str, list[dict]] = {}
    for rec in databank_records:
        name = rec.get("name", "").lower()
        if name:
            name_index.setdefault(name, []).append(rec)

    matched: list[dict[str, Any]] = []
    for etym in etymology_records:
        candidates = name_index.get(etym.place_name.lower(), [])

        for candidate in candidates:
            c_lat = candidate.get("lat")
            c_lon = candidate.get("lon")
            if c_lat is None or c_lon is None:
                continue

            dist = haversine_distance(etym.lat, etym.lon, c_lat, c_lon)
            if dist <= distance_threshold_m:
                enriched = {
                    **candidate,
                    "_etymology_qid": etym.named_after_qid,
                    "_etymology_label": etym.named_after_label,
                    "_etymology_description": etym.named_after_description,
                    "_etymology_source": "wikidata",
                    "_wikidata_qid": etym.place_qid,
                }
                matched.append(enriched)
                break  # Only match first candidate within threshold

    return matched


def export_etymologies(
    records: list[EtymologyRecord],
    output_path: Path,
) -> int:
    """Export etymology records to JSONL file.

    Args:
        records: Etymology records to export.
        output_path: Output JSONL file path.

    Returns:
        Number of records written.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
    return len(records)
