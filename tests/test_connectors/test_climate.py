"""Tests for the Climate data connector."""

import pytest

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.climate import (
    _CLIMATE_SOURCES,
    CLIMATE_VARIABLES,
    ClimateConnector,
    ClimateRecord,
)


def test_climate_connector_metadata():
    """Test connector class-level metadata."""
    connector = ClimateConnector()
    assert connector.source_id == "climate"
    assert connector.coverage_region == "global"
    assert "CRU" in connector.source_name


def test_climate_invalid_source():
    """Test that invalid climate source raises ValueError."""
    with pytest.raises(ValueError, match="Unknown climate source"):
        ClimateConnector(climate_source="invalid")


def test_climate_invalid_variable():
    """Test that invalid variable raises ValueError."""
    with pytest.raises(ValueError, match="Unknown variable"):
        ClimateConnector(variable="invalid")


def test_climate_sources():
    """Test that all climate sources are configured."""
    assert "cru_ts" in _CLIMATE_SOURCES
    assert "pages2k" in _CLIMATE_SOURCES
    assert "eobs" in _CLIMATE_SOURCES


def test_climate_variables():
    """Test that key climate variables are defined."""
    assert "tmp" in CLIMATE_VARIABLES
    assert "pre" in CLIMATE_VARIABLES
    assert "frs" in CLIMATE_VARIABLES


def test_climate_source_selection():
    """Test different climate source selection."""
    cru = ClimateConnector(climate_source="cru_ts")
    assert "Open Government" in cru.license

    pages = ClimateConnector(climate_source="pages2k")
    assert pages.license == "CC-BY-4.0"

    eobs = ClimateConnector(climate_source="eobs")
    assert eobs.license == "Copernicus-OL"


def test_climate_validation_valid():
    """Test validation of valid climate record."""
    connector = ClimateConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="",
        name_normalized="",
        language_code="und",
        year_from=1960,
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_climate_validation_invalid_latitude():
    """Test validation catches invalid latitude."""
    connector = ClimateConnector()
    record = ConnectorResult(
        latitude=100.0,  # Invalid
        longitude=10.0,
        name_form="",
        name_normalized="",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)


def test_climate_validation_invalid_longitude():
    """Test validation catches invalid longitude."""
    connector = ClimateConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=200.0,  # Invalid
        name_form="",
        name_normalized="",
    )
    errors = connector.validate(record)
    assert any(e.field == "longitude" for e in errors)


def test_climate_validation_negative_year():
    """Test validation warns on negative year."""
    connector = ClimateConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="",
        name_normalized="",
        year_from=-100,
    )
    errors = connector.validate(record)
    assert any(e.field == "year_from" for e in errors)


def test_climate_to_result():
    """Test converting ClimateRecord to ConnectorResult."""
    connector = ClimateConnector(variable="tmp")
    climate = ClimateRecord(
        latitude=60.0,
        longitude=10.0,
        year=1960,
        temperature_mean=5.2,
    )
    result = connector._climate_to_result(climate)
    assert result.latitude == 60.0
    assert result.longitude == 10.0
    assert result.year_from == 1960
    assert "climate:tmp:5.2" in (result.place_type or "")


def test_climate_count():
    """Test that count returns None."""
    connector = ClimateConnector()
    assert connector.count() is None


def test_climate_get_climate_for_places():
    """Test batch climate query returns correct length."""
    connector = ClimateConnector()
    places = [
        {"latitude": 60.0, "longitude": 10.0},
        {"latitude": 55.0, "longitude": 12.0},
        {"latitude": 63.0, "longitude": 10.0},
    ]
    results = connector.get_climate_for_places(places)
    assert len(results) == 3
    # All None since no actual climate data loaded
    assert all(r is None for r in results)
