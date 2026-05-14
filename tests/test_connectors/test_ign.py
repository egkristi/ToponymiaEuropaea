"""Tests for the IGN (France) connector."""

from unittest.mock import MagicMock, patch

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.ign import (
    _FEATURE_TYPES,
    _LANGUAGE_MAP,
    IGNConnector,
)


def test_ign_connector_metadata():
    """Test connector class-level metadata."""
    connector = IGNConnector()
    assert connector.source_id == "ign"
    assert connector.source_name == "IGN BD NYME"
    assert connector.license == "Etalab-2.0"
    assert connector.coverage_region == "FR"
    assert "geopf" in connector.source_url


def test_ign_validation_valid_record():
    """Test validation of a valid French record."""
    connector = IGNConnector()
    record = ConnectorResult(
        latitude=48.8566,
        longitude=2.3522,
        name_form="Paris",
        name_normalized="paris",
        language_code="fra",
        source_id="ign:75056",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_ign_validation_outside_france():
    """Test validation catches coordinates outside France."""
    connector = IGNConnector()
    record = ConnectorResult(
        latitude=59.9139,  # Oslo
        longitude=10.7522,
        name_form="Oslo",
        name_normalized="oslo",
        language_code="fra",
        source_id="ign:99999",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)
    assert any(e.field == "longitude" for e in errors)


def test_ign_validation_empty_name():
    """Test validation catches empty name."""
    connector = IGNConnector()
    record = ConnectorResult(
        latitude=46.0,
        longitude=2.0,
        name_form="",
        name_normalized="",
        language_code="fra",
        source_id="ign:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_ign_validation_unknown_language():
    """Test validation warns on unrecognized language code."""
    connector = IGNConnector()
    record = ConnectorResult(
        latitude=46.0,
        longitude=2.0,
        name_form="Test",
        name_normalized="test",
        language_code="zzz",
        source_id="ign:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "language_code" for e in errors)


def test_ign_language_map():
    """Test that language map covers expected codes."""
    assert "fra" in _LANGUAGE_MAP
    assert "bre" in _LANGUAGE_MAP
    assert "oci" in _LANGUAGE_MAP
    assert "cat" in _LANGUAGE_MAP
    assert "eus" in _LANGUAGE_MAP
    assert "cos" in _LANGUAGE_MAP


def test_ign_feature_types():
    """Test that feature types include common French place features."""
    assert "Commune" in _FEATURE_TYPES
    assert "Cours d'eau" in _FEATURE_TYPES
    assert "Sommet" in _FEATURE_TYPES
    assert "Forêt" in _FEATURE_TYPES


def test_ign_parse_feature():
    """Test parsing a GeoJSON feature."""
    connector = IGNConnector()

    feature = {
        "geometry": {"type": "Point", "coordinates": [2.3522, 48.8566]},
        "properties": {
            "id": "75056",
            "label": "Paris",
            "type": "Commune",
            "context": "75, Île-de-France",
        },
    }

    result = connector._parse_feature(feature)
    assert result is not None
    assert result.name_form == "Paris"
    assert result.language_code == "fra"
    assert result.latitude == 48.8566
    assert result.longitude == 2.3522
    assert result.place_type == "municipality"


def test_ign_parse_feature_no_coords():
    """Test that features without coordinates return None."""
    connector = IGNConnector()
    feature = {
        "geometry": {"type": "Point", "coordinates": []},
        "properties": {"label": "NoCoords"},
    }
    result = connector._parse_feature(feature)
    assert result is None


def test_ign_parse_feature_no_name():
    """Test that features without names return None."""
    connector = IGNConnector()
    feature = {
        "geometry": {"type": "Point", "coordinates": [2.0, 46.0]},
        "properties": {"label": ""},
    }
    result = connector._parse_feature(feature)
    assert result is None


@patch("toponymia.connectors.ign.httpx.Client")
def test_ign_fetch_results(mock_client_class: MagicMock) -> None:
    """Test that fetch returns parsed results."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    response = MagicMock()
    response.json.return_value = {
        "features": [
            {
                "geometry": {"type": "Point", "coordinates": [2.3522, 48.8566]},
                "properties": {
                    "id": "75056",
                    "label": "Paris",
                    "type": "Commune",
                    "context": "75, Île-de-France",
                },
            },
            {
                "geometry": {"type": "Point", "coordinates": [4.8357, 45.7640]},
                "properties": {
                    "id": "69123",
                    "label": "Lyon",
                    "type": "Commune",
                    "context": "69, Auvergne-Rhône-Alpes",
                },
            },
        ]
    }
    response.raise_for_status = MagicMock()
    mock_client.get.return_value = response

    connector = IGNConnector()
    connector._client = mock_client
    results = list(connector.fetch(name_query="Paris", max_results=10))
    assert len(results) == 2
    assert results[0].name_form == "Paris"
    assert results[1].name_form == "Lyon"


@patch("toponymia.connectors.ign.httpx.Client")
def test_ign_fetch_country_filter(mock_client_class: MagicMock) -> None:
    """Test that fetch with non-FR country returns nothing."""
    connector = IGNConnector()
    results = list(connector.fetch(country="GB"))
    assert len(results) == 0


def test_ign_count_non_fr():
    """Test that count returns 0 for non-French countries."""
    connector = IGNConnector()
    assert connector.count(country="GB") == 0
