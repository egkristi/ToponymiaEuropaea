"""Tests for the Lantmäteriet Ortnamn connector."""

from unittest.mock import MagicMock, patch

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.lantmateriet import (
    _FEATURE_TYPES,
    _LANGUAGE_MAP,
    LantmaterietConnector,
)


def test_lantmateriet_connector_metadata():
    """Test connector class-level metadata."""
    connector = LantmaterietConnector()
    assert connector.source_id == "lantmateriet"
    assert connector.source_name == "Lantmäteriet Ortnamn"
    assert connector.license == "CC0-1.0"
    assert connector.coverage_region == "SE"
    assert "lantmateriet" in connector.source_url


def test_lantmateriet_validation_valid_record():
    """Test validation of a valid Swedish record."""
    connector = LantmaterietConnector()
    record = ConnectorResult(
        latitude=59.3293,
        longitude=18.0686,
        name_form="Stockholm",
        name_normalized="stockholm",
        language_code="swe",
        source_id="lantmateriet:12345",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_lantmateriet_validation_outside_sweden():
    """Test validation catches coordinates outside Sweden."""
    connector = LantmaterietConnector()
    record = ConnectorResult(
        latitude=48.8566,  # Paris
        longitude=2.3522,
        name_form="Paris",
        name_normalized="paris",
        language_code="swe",
        source_id="lantmateriet:99999",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)
    assert any(e.field == "longitude" for e in errors)


def test_lantmateriet_validation_empty_name():
    """Test validation catches empty name."""
    connector = LantmaterietConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=15.0,
        name_form="",
        name_normalized="",
        language_code="swe",
        source_id="lantmateriet:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_lantmateriet_validation_unknown_language():
    """Test validation warns on unrecognized language code."""
    connector = LantmaterietConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=15.0,
        name_form="Test",
        name_normalized="test",
        language_code="zzz",
        source_id="lantmateriet:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "language_code" for e in errors)


def test_lantmateriet_language_map():
    """Test that language map covers expected codes."""
    assert "swe" in _LANGUAGE_MAP
    assert "fin" in _LANGUAGE_MAP
    assert "sme" in _LANGUAGE_MAP
    assert "smj" in _LANGUAGE_MAP
    assert "sma" in _LANGUAGE_MAP
    assert "fit" in _LANGUAGE_MAP


def test_lantmateriet_feature_types():
    """Test that feature types include common Swedish place features."""
    assert "Bebyggelse" in _FEATURE_TYPES
    assert "Sjö" in _FEATURE_TYPES
    assert "Älv" in _FEATURE_TYPES
    assert "Fjäll" in _FEATURE_TYPES


def test_lantmateriet_parse_feature():
    """Test parsing a GeoJSON feature."""
    connector = LantmaterietConnector()

    feature = {
        "geometry": {"type": "Point", "coordinates": [18.0686, 59.3293]},
        "properties": {
            "id": "12345",
            "namn": "Stockholm",
            "sprak": "swe",
            "namntyp": "Bebyggelse",
            "kommun": "Stockholm",
            "alternativa_namn": [
                {"namn": "Tukholma", "sprak": "fin"},
            ],
        },
    }

    result = connector._parse_feature(feature)
    assert result is not None
    assert result.name_form == "Stockholm"
    assert result.language_code == "swe"
    assert result.latitude == 59.3293
    assert result.longitude == 18.0686
    assert result.place_type == "settlement"
    assert "fin" in result.alternative_names
    assert "Tukholma" in result.alternative_names["fin"]


def test_lantmateriet_parse_feature_no_coords():
    """Test that features without coordinates return None."""
    connector = LantmaterietConnector()

    feature = {
        "geometry": {"type": "Point", "coordinates": []},
        "properties": {"namn": "NoCoords", "sprak": "swe"},
    }

    result = connector._parse_feature(feature)
    assert result is None


def test_lantmateriet_parse_feature_no_name():
    """Test that features without names return None."""
    connector = LantmaterietConnector()

    feature = {
        "geometry": {"type": "Point", "coordinates": [18.0, 59.0]},
        "properties": {"namn": "", "sprak": "swe"},
    }

    result = connector._parse_feature(feature)
    assert result is None


@patch("toponymia.connectors.lantmateriet.httpx.Client")
def test_lantmateriet_fetch_pagination(mock_client_class: MagicMock) -> None:
    """Test that fetch handles pagination correctly."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    page1_response = MagicMock()
    page1_response.json.return_value = {
        "features": [
            {
                "geometry": {"type": "Point", "coordinates": [18.0, 59.0]},
                "properties": {"id": "1", "namn": "Plats1", "sprak": "swe"},
            },
            {
                "geometry": {"type": "Point", "coordinates": [18.1, 59.1]},
                "properties": {"id": "2", "namn": "Plats2", "sprak": "swe"},
            },
        ]
    }
    page1_response.raise_for_status = MagicMock()

    # Second page empty (end of results)
    page2_response = MagicMock()
    page2_response.json.return_value = {"features": []}
    page2_response.raise_for_status = MagicMock()

    mock_client.get.side_effect = [page1_response, page2_response]

    connector = LantmaterietConnector()
    connector._client = mock_client
    results = list(connector.fetch(max_results=10))
    assert len(results) == 2
    assert results[0].name_form == "Plats1"
    assert results[1].name_form == "Plats2"


@patch("toponymia.connectors.lantmateriet.httpx.Client")
def test_lantmateriet_fetch_country_filter(mock_client_class: MagicMock) -> None:
    """Test that fetch with non-SE country returns nothing."""
    connector = LantmaterietConnector()
    results = list(connector.fetch(country="NO"))
    assert len(results) == 0


def test_lantmateriet_count_non_se():
    """Test that count returns 0 for non-Swedish countries."""
    connector = LantmaterietConnector()
    assert connector.count(country="NO") == 0
