"""Tests for the Rundata (Scandinavian Runic Text Database) connector."""

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.rundata import (
    _LANGUAGE_MAP,
    _PERIOD_DATES,
    _SIGNUM_COUNTRY,
    RundataConnector,
)


def test_rundata_connector_metadata():
    """Test connector class-level metadata."""
    connector = RundataConnector()
    assert connector.source_id == "rundata"
    assert connector.source_name == "Samnordisk runtextdatabas (Rundata)"
    assert connector.license == "CC-BY-4.0"
    assert connector.coverage_region == "SE"


def test_rundata_validation_valid_record():
    """Test validation of a valid runic inscription record."""
    connector = RundataConnector()
    record = ConnectorResult(
        latitude=59.86,
        longitude=17.63,
        name_form="Ulunda",
        name_normalized="ulunda",
        language_code="non",
        year_from=1000,
        source_id="rundata:U 1163",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_rundata_validation_empty_name():
    """Test validation catches empty name."""
    connector = RundataConnector()
    record = ConnectorResult(
        latitude=59.0,
        longitude=17.0,
        name_form="",
        name_normalized="",
        language_code="non",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_rundata_validation_outside_scandinavia():
    """Test validation catches coordinates outside Scandinavia."""
    connector = RundataConnector()
    record = ConnectorResult(
        latitude=40.0,  # Southern Europe
        longitude=17.0,
        name_form="Test",
        name_normalized="test",
        language_code="non",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)


def test_rundata_validation_year_outside_range():
    """Test validation warns on years outside runic range."""
    connector = RundataConnector()
    record = ConnectorResult(
        latitude=59.0,
        longitude=17.0,
        name_form="Test",
        name_normalized="test",
        language_code="non",
        year_from=1900,  # Too modern for runes
    )
    errors = connector.validate(record)
    assert any(e.field == "year_from" for e in errors)


def test_rundata_period_dates():
    """Test that period dates are properly configured."""
    assert "Viking Age" in _PERIOD_DATES
    assert "Medieval" in _PERIOD_DATES
    assert _PERIOD_DATES["Viking Age"] == (800, 1100)


def test_rundata_signum_country():
    """Test signum → country mapping."""
    assert _SIGNUM_COUNTRY["U"] == "SE"
    assert _SIGNUM_COUNTRY["N"] == "NO"
    assert _SIGNUM_COUNTRY["DR"] == "DK"


def test_rundata_language_map():
    """Test language map includes Old Norse."""
    assert "non" in _LANGUAGE_MAP
    assert _LANGUAGE_MAP["run"] == "non"


def test_rundata_parse_inscription():
    """Test parsing a runic inscription."""
    connector = RundataConnector()

    insc = {
        "signum": "U 1163",
        "latitude": 59.86,
        "longitude": 17.63,
        "period": "Viking Age",
        "place_names": [
            {"name": "Ulunda", "normalized": "Ulundr"},
        ],
    }

    results = connector._parse_inscription(insc)
    assert len(results) == 1
    assert results[0].name_form == "Ulunda"
    assert results[0].name_normalized == "ulundr"
    assert results[0].language_code == "non"
    assert results[0].year_from == 800
    assert results[0].year_to == 1100
    assert results[0].is_current is False
    assert "U 1163" in results[0].source_id


def test_rundata_parse_inscription_findspot():
    """Test parsing inscription with findspot only (no place_names)."""
    connector = RundataConnector()

    insc = {
        "signum": "Sö 179",
        "latitude": 59.0,
        "longitude": 16.5,
        "period": "Medieval",
        "findspot": "Gripsholm",
    }

    results = connector._parse_inscription(insc)
    assert len(results) == 1
    assert results[0].name_form == "Gripsholm"
    assert results[0].year_from == 1100
    assert results[0].year_to == 1400


def test_rundata_parse_inscription_no_coords():
    """Test that inscriptions without coordinates return empty list."""
    connector = RundataConnector()
    insc = {"signum": "U 999", "place_names": [{"name": "Test"}]}
    results = connector._parse_inscription(insc)
    assert len(results) == 0


def test_rundata_parse_multiple_places():
    """Test parsing inscription referencing multiple places."""
    connector = RundataConnector()

    insc = {
        "signum": "U 101",
        "latitude": 59.5,
        "longitude": 17.0,
        "period": "Viking Age",
        "place_names": [
            {"name": "Sigtuna", "normalized": "Sigtúnir"},
            {"name": "Uppsalir", "normalized": "Uppsalir"},
        ],
    }

    results = connector._parse_inscription(insc)
    assert len(results) == 2
    assert results[0].name_form == "Sigtuna"
    assert results[1].name_form == "Uppsalir"
