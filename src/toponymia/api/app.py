"""FastAPI REST API for the Toponymia Europaea databank."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

DATABANK_PATH: Path | None = None

_places: list[dict[str, Any]] = []
_sources: list[dict[str, Any]] = []
_loaded: bool = False


class PlaceRecord(BaseModel):
    """A single place record from the databank."""

    name_form: str
    name_normalized: str | None = None
    latitude: float
    longitude: float
    source_id: str
    language_code: str | None = None
    place_type: str | None = None
    is_current: bool = True
    alternative_names: dict[str, list[str]] | None = None
    elevation: float | None = None
    source_url: str | None = None
    _sha256: str = ""
    _h3_r7: str | None = None
    _h3_r9: str | None = None
    _h3_r11: str | None = None
    _phonetic_key: str | None = None


class SourceRecord(BaseModel):
    """A data source entry."""

    dataset_id: str
    name: str
    url: str | None = None
    license: str | None = None
    coverage: str | None = None
    record_count_approx: int | None = None
    notes: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    places_loaded: int
    sources_loaded: int


class StatsResponse(BaseModel):
    """Databank statistics."""

    total_places: int
    by_country: dict[str, int]
    by_source: dict[str, int]


class GeoJSONFeature(BaseModel):
    """A GeoJSON Feature."""

    type: str = "Feature"
    geometry: dict[str, Any]
    properties: dict[str, Any]


class GeoJSONCollection(BaseModel):
    """A GeoJSON FeatureCollection."""

    type: str = "FeatureCollection"
    features: list[GeoJSONFeature]


def _resolve_databank_path() -> Path:
    """Resolve the databank root directory."""
    import os

    env_path = os.environ.get("TOPONYMIA_DATABANK_PATH")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent.parent.parent.parent / "databank"


def load_databank() -> None:
    """Load all JSONL place files and sources from the databank."""
    global _places, _sources, _loaded  # noqa: PLW0603
    if _loaded:
        return

    databank = DATABANK_PATH or _resolve_databank_path()
    places_dir = databank / "places"
    sources_file = databank / "sources.jsonl"

    _places = []
    if places_dir.is_dir():
        for country_dir in sorted(places_dir.iterdir()):
            if not country_dir.is_dir():
                continue
            country_code = country_dir.name
            for jsonl_file in sorted(country_dir.glob("*.jsonl")):
                with jsonl_file.open(encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()  # noqa: PLW2901
                        if not line:
                            continue
                        record = json.loads(line)
                        record.setdefault("country_code", country_code)
                        _places.append(record)

    _sources = []
    if sources_file.is_file():
        with sources_file.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()  # noqa: PLW2901
                if not line:
                    continue
                _sources.append(json.loads(line))

    _loaded = True


def get_places() -> list[dict[str, Any]]:
    """Return the loaded places list, loading lazily if needed."""
    load_databank()
    return _places


def get_sources() -> list[dict[str, Any]]:
    """Return the loaded sources list, loading lazily if needed."""
    load_databank()
    return _sources


def _filter_places(
    places: list[dict[str, Any]],
    *,
    country: str | None = None,
    source_id: str | None = None,
    name: str | None = None,
) -> list[dict[str, Any]]:
    """Filter places by country, source, and name substring."""
    result = places
    if country:
        result = [p for p in result if p.get("country_code", "").upper() == country.upper()]
    if source_id:
        result = [p for p in result if p.get("source_id") == source_id]
    if name:
        name_lower = name.lower()
        result = [
            p
            for p in result
            if name_lower in p.get("name_form", "").lower()
            or name_lower in (p.get("name_normalized") or "").lower()
        ]
    return result


def _place_to_geojson(place: dict[str, Any]) -> dict[str, Any]:
    """Convert a place record to a GeoJSON Feature dict."""
    properties = {k: v for k, v in place.items() if k not in ("latitude", "longitude")}
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [place["longitude"], place["latitude"]],
        },
        "properties": properties,
    }


CSV_COLUMNS = [
    "name_form",
    "name_normalized",
    "latitude",
    "longitude",
    "source_id",
    "language_code",
    "country_code",
    "place_type",
    "is_current",
    "elevation",
    "source_url",
    "_sha256",
]


app = FastAPI(
    title="Toponymia Europaea API",
    version="0.1.0",
    description="REST API for the Toponymia Europaea place-name databank",
)

# Mount static web files if the web/ directory exists
_web_dir = Path(__file__).resolve().parent.parent.parent.parent / "web"
if _web_dir.is_dir():
    app.mount("/web", StaticFiles(directory=str(_web_dir), html=True), name="web")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        places_loaded=len(get_places()),
        sources_loaded=len(get_sources()),
    )


@app.get("/api/v1/places")
async def list_places(
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
    country: str | None = Query(default=None),
    source_id: str | None = Query(default=None),
    name: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    """List places with pagination and optional filters."""
    filtered = _filter_places(get_places(), country=country, source_id=source_id, name=name)
    return filtered[offset : offset + limit]


@app.get("/api/v1/places/{sha256}")
async def get_place_by_sha256(sha256: str) -> dict[str, Any]:
    """Get a single place by its _sha256 hash."""
    for place in get_places():
        if place.get("_sha256") == sha256:
            return place
    raise HTTPException(status_code=404, detail="Place not found")


@app.get("/api/v1/sources")
async def list_sources() -> list[dict[str, Any]]:
    """List all data sources."""
    return get_sources()


@app.get("/api/v1/search")
async def search_places(
    q: str = Query(description="Search query (case-insensitive substring)"),
    limit: int = Query(default=100, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
) -> list[dict[str, Any]]:
    """Search places by name pattern (case-insensitive substring)."""
    filtered = _filter_places(get_places(), name=q)
    return filtered[offset : offset + limit]


@app.get("/api/v1/export/geojson")
async def export_geojson(
    country: str | None = Query(default=None),
    source_id: str | None = Query(default=None),
    name: str | None = Query(default=None),
) -> dict[str, Any]:
    """Export places as a GeoJSON FeatureCollection."""
    filtered = _filter_places(get_places(), country=country, source_id=source_id, name=name)
    features = [_place_to_geojson(p) for p in filtered]
    return {"type": "FeatureCollection", "features": features}


@app.get("/api/v1/export/csv")
async def export_csv(
    country: str | None = Query(default=None),
    source_id: str | None = Query(default=None),
    name: str | None = Query(default=None),
) -> Response:
    """Export places as CSV."""
    filtered = _filter_places(get_places(), country=country, source_id=source_id, name=name)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(filtered)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=places.csv"},
    )


@app.get("/api/v1/stats", response_model=StatsResponse)
async def stats() -> StatsResponse:
    """Return databank statistics."""
    places = get_places()
    by_country: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for p in places:
        cc = p.get("country_code", "unknown")
        by_country[cc] = by_country.get(cc, 0) + 1
        ds = p.get("source_id", "unknown")
        by_source[ds] = by_source.get(ds, 0) + 1
    return StatsResponse(
        total_places=len(places),
        by_country=by_country,
        by_source=by_source,
    )
