"""Tests for the Toponymia Europaea REST API."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio

from toponymia.api.app import app

SAMPLE_PLACES: list[dict[str, Any]] = [
    {
        "name_form": "Oslo",
        "name_normalized": "oslo",
        "latitude": 59.9139,
        "longitude": 10.7522,
        "source_id": "3143244",
        "language_code": "nor",
        "country_code": "NO",
        "place_type": "P.PPLC",
        "is_current": True,
        "alternative_names": {"und": ["Christiania", "Kristiania"]},
        "elevation": 12.0,
        "source_url": "https://www.geonames.org/3143244",
        "_sha256": "aaa111",
        "_h3_r7": "870194e65ffffff",
        "_h3_r9": "890194e6537ffff",
        "_h3_r11": "8b0194e6536cfff",
        "_phonetic_key": "oslo",
    },
    {
        "name_form": "Bergen",
        "name_normalized": "bergen",
        "latitude": 60.3913,
        "longitude": 5.3221,
        "source_id": "3161732",
        "language_code": "nor",
        "country_code": "NO",
        "place_type": "P.PPL",
        "is_current": True,
        "alternative_names": {},
        "elevation": 14.0,
        "source_url": "https://www.geonames.org/3161732",
        "_sha256": "bbb222",
        "_h3_r7": "870194c01ffffff",
        "_h3_r9": "890194c0103ffff",
        "_h3_r11": "8b0194c0102dfff",
        "_phonetic_key": "bergen",
    },
    {
        "name_form": "København",
        "name_normalized": "kobenhavn",
        "latitude": 55.6761,
        "longitude": 12.5683,
        "source_id": "2618425",
        "language_code": "dan",
        "country_code": "DK",
        "place_type": "P.PPLC",
        "is_current": True,
        "alternative_names": {"und": ["Copenhagen"]},
        "elevation": 10.0,
        "source_url": "https://www.geonames.org/2618425",
        "_sha256": "ccc333",
        "_h3_r7": "870196566ffffff",
        "_h3_r9": "890196566b7ffff",
        "_h3_r11": "8b0196566b4dfff",
        "_phonetic_key": "kobenhavn",
    },
    {
        "name_form": "Stockholm",
        "name_normalized": "stockholm",
        "latitude": 59.3293,
        "longitude": 18.0686,
        "source_id": "2673730",
        "language_code": "swe",
        "country_code": "SE",
        "place_type": "P.PPLC",
        "is_current": True,
        "alternative_names": {},
        "elevation": 28.0,
        "source_url": "https://www.geonames.org/2673730",
        "_sha256": "ddd444",
        "_h3_r7": "87019639effffff",
        "_h3_r9": "89019639eb3ffff",
        "_h3_r11": "8b019639eb2cfff",
        "_phonetic_key": "stockholm",
    },
    {
        "name_form": "Oslofjorden",
        "name_normalized": "oslofjorden",
        "latitude": 59.6,
        "longitude": 10.6,
        "source_id": "3143242",
        "language_code": "nor",
        "country_code": "NO",
        "place_type": "H.FJD",
        "is_current": True,
        "alternative_names": {},
        "elevation": None,
        "source_url": "https://www.geonames.org/3143242",
        "_sha256": "eee555",
        "_h3_r7": "870194e64ffffff",
        "_h3_r9": "890194e6403ffff",
        "_h3_r11": "8b0194e6402dfff",
        "_phonetic_key": "oslofjorden",
    },
]

SAMPLE_SOURCES: list[dict[str, Any]] = [
    {
        "dataset_id": "geonames",
        "name": "GeoNames Geographical Database",
        "url": "https://www.geonames.org/",
        "license": "CC-BY-4.0",
        "coverage": "global",
        "record_count_approx": None,
        "notes": "Free geographical database",
    },
    {
        "dataset_id": "kartverket_ssr",
        "name": "Kartverket SSR",
        "url": "https://www.kartverket.no/",
        "license": "CC-BY-4.0",
        "coverage": "NO",
        "record_count_approx": 1000000,
        "notes": "Norwegian national place name registry",
    },
]


def _mock_get_places() -> list[dict[str, Any]]:
    return SAMPLE_PLACES


def _mock_get_sources() -> list[dict[str, Any]]:
    return SAMPLE_SOURCES


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Create an httpx async test client with mocked databank."""
    transport = httpx.ASGITransport(app=app)
    with (
        patch("toponymia.api.app.get_places", side_effect=_mock_get_places),
        patch("toponymia.api.app.get_sources", side_effect=_mock_get_sources),
    ):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.mark.asyncio
async def test_health(client: httpx.AsyncClient) -> None:
    """Health endpoint returns ok status."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["places_loaded"] == len(SAMPLE_PLACES)
    assert data["sources_loaded"] == len(SAMPLE_SOURCES)


@pytest.mark.asyncio
async def test_list_places_returns_all(client: httpx.AsyncClient) -> None:
    """List places returns all sample records by default."""
    resp = await client.get("/api/v1/places")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(SAMPLE_PLACES)


@pytest.mark.asyncio
async def test_list_places_empty_with_no_match(client: httpx.AsyncClient) -> None:
    """Filtering with a non-existent country returns empty list."""
    resp = await client.get("/api/v1/places", params={"country": "XX"})
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_filter_by_country(client: httpx.AsyncClient) -> None:
    """Filter by country returns only matching records."""
    resp = await client.get("/api/v1/places", params={"country": "NO"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert all(p["country_code"] == "NO" for p in data)


@pytest.mark.asyncio
async def test_filter_by_source(client: httpx.AsyncClient) -> None:
    """Filter by source_id returns only matching records."""
    resp = await client.get("/api/v1/places", params={"source_id": "3143244"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name_form"] == "Oslo"


@pytest.mark.asyncio
async def test_filter_by_name(client: httpx.AsyncClient) -> None:
    """Filter by name substring is case-insensitive."""
    resp = await client.get("/api/v1/places", params={"name": "oslo"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = {p["name_form"] for p in data}
    assert names == {"Oslo", "Oslofjorden"}


@pytest.mark.asyncio
async def test_get_place_by_sha256_found(client: httpx.AsyncClient) -> None:
    """Lookup by sha256 returns the matching record."""
    resp = await client.get("/api/v1/places/aaa111")
    assert resp.status_code == 200
    assert resp.json()["name_form"] == "Oslo"


@pytest.mark.asyncio
async def test_get_place_by_sha256_not_found(client: httpx.AsyncClient) -> None:
    """Lookup by sha256 with unknown hash returns 404."""
    resp = await client.get("/api/v1/places/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_sources(client: httpx.AsyncClient) -> None:
    """Sources endpoint returns all sources."""
    resp = await client.get("/api/v1/sources")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == len(SAMPLE_SOURCES)
    ids = {s["dataset_id"] for s in data}
    assert "geonames" in ids


@pytest.mark.asyncio
async def test_search_places(client: httpx.AsyncClient) -> None:
    """Search endpoint finds places by substring."""
    resp = await client.get("/api/v1/search", params={"q": "berg"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name_form"] == "Bergen"


@pytest.mark.asyncio
async def test_search_case_insensitive(client: httpx.AsyncClient) -> None:
    """Search is case-insensitive."""
    resp = await client.get("/api/v1/search", params={"q": "STOCKHOLM"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name_form"] == "Stockholm"


@pytest.mark.asyncio
async def test_export_geojson(client: httpx.AsyncClient) -> None:
    """GeoJSON export returns valid FeatureCollection."""
    resp = await client.get("/api/v1/export/geojson", params={"country": "NO"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 3
    feature = data["features"][0]
    assert feature["type"] == "Feature"
    assert feature["geometry"]["type"] == "Point"
    assert len(feature["geometry"]["coordinates"]) == 2


@pytest.mark.asyncio
async def test_export_csv(client: httpx.AsyncClient) -> None:
    """CSV export returns valid CSV with headers."""
    resp = await client.get("/api/v1/export/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    lines = resp.text.strip().split("\n")
    assert len(lines) == len(SAMPLE_PLACES) + 1
    header = lines[0]
    assert "name_form" in header
    assert "latitude" in header


@pytest.mark.asyncio
async def test_stats(client: httpx.AsyncClient) -> None:
    """Stats endpoint returns correct counts."""
    resp = await client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_places"] == len(SAMPLE_PLACES)
    assert data["by_country"]["NO"] == 3
    assert data["by_country"]["DK"] == 1
    assert data["by_country"]["SE"] == 1


@pytest.mark.asyncio
async def test_pagination_limit(client: httpx.AsyncClient) -> None:
    """Limit parameter restricts result count."""
    resp = await client.get("/api/v1/places", params={"limit": 2})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_pagination_offset(client: httpx.AsyncClient) -> None:
    """Offset parameter skips leading records."""
    resp = await client.get("/api/v1/places", params={"limit": 2, "offset": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name_form"] == "Stockholm"
    assert data[1]["name_form"] == "Oslofjorden"


@pytest.mark.asyncio
async def test_geojson_coordinates_order(client: httpx.AsyncClient) -> None:
    """GeoJSON coordinates are [longitude, latitude] per spec."""
    resp = await client.get("/api/v1/export/geojson", params={"country": "SE"})
    data = resp.json()
    coords = data["features"][0]["geometry"]["coordinates"]
    assert coords[0] == pytest.approx(18.0686)
    assert coords[1] == pytest.approx(59.3293)
