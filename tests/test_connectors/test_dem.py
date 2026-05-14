"""Tests for the DEM/terrain data connector."""

import pytest

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.dem import (
    _DEM_SOURCES,
    _TERRAIN_CLASSES,
    DEMConnector,
    TerrainPoint,
)


def test_dem_connector_metadata():
    """Test connector class-level metadata."""
    connector = DEMConnector()
    assert connector.source_id == "dem_terrain"
    assert connector.source_name == "DEM/Terrain Data"
    assert connector.coverage_region == "global"


def test_dem_invalid_source():
    """Test that invalid DEM source raises ValueError."""
    with pytest.raises(ValueError, match="Unknown DEM source"):
        DEMConnector(dem_source="invalid")


def test_dem_sources():
    """Test that all DEM sources are configured."""
    assert "copernicus" in _DEM_SOURCES
    assert "srtm" in _DEM_SOURCES
    assert "kartverket_dtm" in _DEM_SOURCES


def test_dem_source_selection():
    """Test different DEM source selection."""
    cop = DEMConnector(dem_source="copernicus")
    assert cop.license == "Copernicus-OL"

    srtm = DEMConnector(dem_source="srtm")
    assert srtm.license == "public-domain"

    kv = DEMConnector(dem_source="kartverket_dtm")
    assert kv.license == "CC-BY-4.0"


def test_dem_terrain_classes():
    """Test terrain classification thresholds."""
    assert "flat" in _TERRAIN_CLASSES
    assert "steep" in _TERRAIN_CLASSES
    assert _TERRAIN_CLASSES["flat"] == (0.0, 2.0)


def test_dem_validation_valid():
    """Test validation of valid terrain record."""
    connector = DEMConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        elevation_m=500.0,
        name_form="",
        name_normalized="",
        language_code="und",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_dem_validation_invalid_elevation():
    """Test validation catches impossible elevation."""
    connector = DEMConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        elevation_m=10000.0,  # Above Everest
        name_form="",
        name_normalized="",
    )
    errors = connector.validate(record)
    assert any(e.field == "elevation_m" for e in errors)


def test_dem_validation_invalid_latitude():
    """Test validation catches invalid latitude."""
    connector = DEMConnector()
    record = ConnectorResult(
        latitude=100.0,  # Invalid
        longitude=10.0,
        name_form="",
        name_normalized="",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)


def test_dem_validation_invalid_longitude():
    """Test validation catches invalid longitude."""
    connector = DEMConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=200.0,  # Invalid
        name_form="",
        name_normalized="",
    )
    errors = connector.validate(record)
    assert any(e.field == "longitude" for e in errors)


def test_dem_terrain_to_result():
    """Test converting TerrainPoint to ConnectorResult."""
    connector = DEMConnector()
    terrain = TerrainPoint(
        latitude=60.0,
        longitude=10.0,
        elevation_m=500.0,
        slope_deg=5.0,
        aspect_deg=180.0,
    )
    result = connector._terrain_to_result(terrain)
    assert result.latitude == 60.0
    assert result.longitude == 10.0
    assert result.elevation_m == 500.0
    assert "gentle" in (result.place_type or "")


def test_dem_terrain_to_result_steep():
    """Test terrain classification for steep slope."""
    connector = DEMConnector()
    terrain = TerrainPoint(
        latitude=61.0,
        longitude=7.0,
        elevation_m=1500.0,
        slope_deg=25.0,
    )
    result = connector._terrain_to_result(terrain)
    assert "steep" in (result.place_type or "")


def test_dem_count():
    """Test that count returns None."""
    connector = DEMConnector()
    assert connector.count() is None


def test_dem_get_terrain_for_places():
    """Test batch terrain query returns correct length."""
    connector = DEMConnector()
    places = [
        {"latitude": 60.0, "longitude": 10.0},
        {"latitude": 61.0, "longitude": 11.0},
    ]
    results = connector.get_terrain_for_places(places)
    assert len(results) == 2
    # Both None since no actual DEM data loaded
    assert all(r is None for r in results)
