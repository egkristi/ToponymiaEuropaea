"""Tests for the Diplomatarium (medieval charter) connector."""

from unittest.mock import MagicMock, patch

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.diplomatarium import (
    _LANGUAGE_MAP,
    _SOURCES,
    DiplomatariumConnector,
)


def test_diplomatarium_connector_metadata():
    """Test connector class-level metadata."""
    connector = DiplomatariumConnector(source="DN")
    assert connector.source_id == "diplomatarium"
    assert connector.coverage_region == "NO"
    assert connector.license == "CC-BY-4.0"
    assert "dokpro" in connector.source_url


def test_diplomatarium_source_selection():
    """Test different source selection."""
    dn = DiplomatariumConnector(source="DN")
    assert dn.coverage_region == "NO"

    dd = DiplomatariumConnector(source="DD")
    assert dd.coverage_region == "DK"

    ds = DiplomatariumConnector(source="DS")
    assert ds.coverage_region == "SE"


def test_diplomatarium_invalid_source():
    """Test that invalid source raises ValueError."""
    import pytest

    with pytest.raises(ValueError, match="Unknown source"):
        DiplomatariumConnector(source="XX")


def test_diplomatarium_validation_valid_record():
    """Test validation of a valid charter attestation."""
    connector = DiplomatariumConnector(source="DN")
    record = ConnectorResult(
        latitude=59.9,
        longitude=10.7,
        name_form="Ásló",
        name_normalized="ásló",
        language_code="lat",
        year_from=1225,
        source_id="DN:I:42",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_diplomatarium_validation_empty_name():
    """Test validation catches empty name."""
    connector = DiplomatariumConnector(source="DN")
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="",
        name_normalized="",
        language_code="lat",
        year_from=1300,
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_diplomatarium_validation_year_outside_range():
    """Test validation warns on years outside medieval range."""
    connector = DiplomatariumConnector(source="DN")
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="Test",
        name_normalized="test",
        language_code="lat",
        year_from=1900,  # Too modern
    )
    errors = connector.validate(record)
    assert any(e.field == "year_from" for e in errors)


def test_diplomatarium_validation_unknown_language():
    """Test validation warns on unexpected language."""
    connector = DiplomatariumConnector(source="DN")
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="Test",
        name_normalized="test",
        language_code="jpn",  # Japanese - unexpected for medieval charters
        year_from=1300,
    )
    errors = connector.validate(record)
    assert any(e.field == "language_code" for e in errors)


def test_diplomatarium_language_map():
    """Test that language map covers expected codes."""
    assert "lat" in _LANGUAGE_MAP
    assert "non" in _LANGUAGE_MAP
    assert "gml" in _LANGUAGE_MAP


def test_diplomatarium_sources():
    """Test that all sources are configured."""
    assert "DN" in _SOURCES
    assert "DD" in _SOURCES
    assert "DS" in _SOURCES


def test_diplomatarium_parse_attestation():
    """Test parsing a charter attestation."""
    connector = DiplomatariumConnector(source="DN")

    att = {
        "place_form": "Ásló",
        "latitude": 59.9139,
        "longitude": 10.7522,
        "year": 1225,
        "language": "lat",
        "document_id": "42",
        "volume": "I",
        "modern_name": "Oslo",
    }

    result = connector._parse_attestation(att)
    assert result is not None
    assert result.name_form == "Ásló"
    assert result.latitude == 59.9139
    assert result.year_from == 1225
    assert result.language_code == "lat"
    assert result.is_current is False
    assert "DN:I:42" in result.source_id
    assert "nor" in result.alternative_names
    assert "Oslo" in result.alternative_names["nor"]


def test_diplomatarium_parse_attestation_no_name():
    """Test that entries without names return None."""
    connector = DiplomatariumConnector(source="DN")
    att = {"place_form": "", "latitude": 60.0, "longitude": 10.0}
    result = connector._parse_attestation(att)
    assert result is None


@patch("toponymia.connectors.diplomatarium.httpx.Client")
def test_diplomatarium_fetch_country_filter(mock_client_class: MagicMock) -> None:
    """Test that fetch with wrong country returns nothing."""
    connector = DiplomatariumConnector(source="DN")
    results = list(connector.fetch(country="SE"))
    assert len(results) == 0


def test_diplomatarium_count_wrong_country():
    """Test that count returns 0 for wrong country."""
    connector = DiplomatariumConnector(source="DN")
    assert connector.count(country="SE") == 0
