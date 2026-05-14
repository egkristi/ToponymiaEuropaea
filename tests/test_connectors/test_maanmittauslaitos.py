"""Tests for the Maanmittauslaitos Paikannimet connector."""

from unittest.mock import MagicMock, patch

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.maanmittauslaitos import (
    _FEATURE_TYPES,
    _LANGUAGE_MAP,
    MaanmittauslaitosConnector,
)


def test_mml_connector_metadata():
    """Test connector class-level metadata."""
    connector = MaanmittauslaitosConnector()
    assert connector.source_id == "maanmittauslaitos"
    assert connector.source_name == "Maanmittauslaitos Paikannimet"
    assert connector.license == "CC-BY-4.0"
    assert connector.coverage_region == "FI"
    assert "maanmittauslaitos" in connector.source_url


def test_mml_validation_valid_record():
    """Test validation of a valid Finnish record."""
    connector = MaanmittauslaitosConnector()
    record = ConnectorResult(
        latitude=60.1699,
        longitude=24.9384,
        name_form="Helsinki",
        name_normalized="helsinki",
        language_code="fin",
        source_id="mml:12345",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_mml_validation_outside_finland():
    """Test validation catches coordinates outside Finland."""
    connector = MaanmittauslaitosConnector()
    record = ConnectorResult(
        latitude=48.8566,  # Paris
        longitude=2.3522,
        name_form="Paris",
        name_normalized="paris",
        language_code="fin",
        source_id="mml:99999",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)
    assert any(e.field == "longitude" for e in errors)


def test_mml_validation_empty_name():
    """Test validation catches empty name."""
    connector = MaanmittauslaitosConnector()
    record = ConnectorResult(
        latitude=61.0,
        longitude=24.0,
        name_form="",
        name_normalized="",
        language_code="fin",
        source_id="mml:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_mml_validation_unknown_language():
    """Test validation warns on unrecognized language code."""
    connector = MaanmittauslaitosConnector()
    record = ConnectorResult(
        latitude=61.0,
        longitude=24.0,
        name_form="Test",
        name_normalized="test",
        language_code="zzz",
        source_id="mml:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "language_code" for e in errors)


def test_mml_language_map():
    """Test that language map covers expected codes."""
    assert "fin" in _LANGUAGE_MAP
    assert "swe" in _LANGUAGE_MAP
    assert "sme" in _LANGUAGE_MAP
    assert "smn" in _LANGUAGE_MAP
    assert "sms" in _LANGUAGE_MAP


def test_mml_feature_types():
    """Test that feature types include common Finnish place features."""
    assert "Järvi" in _FEATURE_TYPES
    assert "Joki" in _FEATURE_TYPES
    assert "Kylä" in _FEATURE_TYPES
    assert "Tunturi" in _FEATURE_TYPES
    assert "Saari" in _FEATURE_TYPES


def test_mml_parse_feature():
    """Test parsing a GeoJSON feature."""
    connector = MaanmittauslaitosConnector()

    feature = {
        "id": "place-12345",
        "geometry": {"type": "Point", "coordinates": [24.9384, 60.1699]},
        "properties": {
            "placeId": "12345",
            "spelling": "Helsinki",
            "language": "fin",
            "placeType": "Asutus",
            "municipality": "Helsinki",
            "alternativeSpellings": [
                {"spelling": "Helsingfors", "language": "swe"},
            ],
        },
    }

    result = connector._parse_feature(feature)
    assert result is not None
    assert result.name_form == "Helsinki"
    assert result.language_code == "fin"
    assert result.latitude == 60.1699
    assert result.longitude == 24.9384
    assert result.place_type == "settlement"
    assert "swe" in result.alternative_names
    assert "Helsingfors" in result.alternative_names["swe"]


def test_mml_parse_feature_no_coords():
    """Test that features without coordinates return None."""
    connector = MaanmittauslaitosConnector()

    feature = {
        "geometry": {"type": "Point", "coordinates": []},
        "properties": {"spelling": "NoCoords", "language": "fin"},
    }

    result = connector._parse_feature(feature)
    assert result is None


def test_mml_parse_feature_no_name():
    """Test that features without names return None."""
    connector = MaanmittauslaitosConnector()

    feature = {
        "geometry": {"type": "Point", "coordinates": [24.0, 61.0]},
        "properties": {"spelling": "", "language": "fin"},
    }

    result = connector._parse_feature(feature)
    assert result is None


@patch("toponymia.connectors.maanmittauslaitos.httpx.Client")
def test_mml_fetch_pagination(mock_client_class: MagicMock) -> None:
    """Test that fetch handles pagination correctly."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    page1_response = MagicMock()
    page1_response.json.return_value = {
        "features": [
            {
                "id": "p1",
                "geometry": {"type": "Point", "coordinates": [24.0, 61.0]},
                "properties": {
                    "placeId": "1",
                    "spelling": "Turku",
                    "language": "fin",
                },
            },
            {
                "id": "p2",
                "geometry": {"type": "Point", "coordinates": [24.1, 61.1]},
                "properties": {
                    "placeId": "2",
                    "spelling": "Tampere",
                    "language": "fin",
                },
            },
        ]
    }
    page1_response.raise_for_status = MagicMock()

    page2_response = MagicMock()
    page2_response.json.return_value = {"features": []}
    page2_response.raise_for_status = MagicMock()

    mock_client.get.side_effect = [page1_response, page2_response]

    connector = MaanmittauslaitosConnector()
    connector._client = mock_client
    results = list(connector.fetch(max_results=10))
    assert len(results) == 2
    assert results[0].name_form == "Turku"
    assert results[1].name_form == "Tampere"


@patch("toponymia.connectors.maanmittauslaitos.httpx.Client")
def test_mml_fetch_country_filter(mock_client_class: MagicMock) -> None:
    """Test that fetch with non-FI country returns nothing."""
    connector = MaanmittauslaitosConnector()
    results = list(connector.fetch(country="NO"))
    assert len(results) == 0


def test_mml_count_non_fi():
    """Test that count returns 0 for non-Finnish countries."""
    connector = MaanmittauslaitosConnector()
    assert connector.count(country="NO") == 0
