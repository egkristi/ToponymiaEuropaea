"""Tests for the Ordnance Survey Names connector."""

from unittest.mock import MagicMock, patch

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.ordnance_survey import (
    _FEATURE_TYPES,
    _LANGUAGE_MAP,
    OrdnanceSurveyConnector,
)


def test_os_connector_metadata():
    """Test connector class-level metadata."""
    connector = OrdnanceSurveyConnector()
    assert connector.source_id == "ordnance_survey"
    assert connector.source_name == "Ordnance Survey Open Names"
    assert connector.license == "OGL-3.0"
    assert connector.coverage_region == "GB"
    assert "os.uk" in connector.source_url


def test_os_validation_valid_record():
    """Test validation of a valid UK record."""
    connector = OrdnanceSurveyConnector()
    record = ConnectorResult(
        latitude=51.5074,
        longitude=-0.1278,
        name_form="London",
        name_normalized="london",
        language_code="eng",
        source_id="os:12345",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_os_validation_outside_uk():
    """Test validation catches coordinates outside UK."""
    connector = OrdnanceSurveyConnector()
    record = ConnectorResult(
        latitude=48.8566,  # Paris
        longitude=2.3522,
        name_form="Paris",
        name_normalized="paris",
        language_code="eng",
        source_id="os:99999",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)
    assert any(e.field == "longitude" for e in errors)


def test_os_validation_empty_name():
    """Test validation catches empty name."""
    connector = OrdnanceSurveyConnector()
    record = ConnectorResult(
        latitude=52.0,
        longitude=-1.0,
        name_form="",
        name_normalized="",
        language_code="eng",
        source_id="os:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_os_validation_unknown_language():
    """Test validation warns on unrecognized language code."""
    connector = OrdnanceSurveyConnector()
    record = ConnectorResult(
        latitude=52.0,
        longitude=-1.0,
        name_form="Test",
        name_normalized="test",
        language_code="zzz",
        source_id="os:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "language_code" for e in errors)


def test_os_language_map():
    """Test that language map covers expected codes."""
    assert "eng" in _LANGUAGE_MAP
    assert "cym" in _LANGUAGE_MAP
    assert "gla" in _LANGUAGE_MAP
    assert "cor" in _LANGUAGE_MAP


def test_os_feature_types():
    """Test that feature types include common UK place features."""
    assert "populatedPlace" in _FEATURE_TYPES
    assert "water" in _FEATURE_TYPES
    assert "Village" in _FEATURE_TYPES


def test_os_parse_entry():
    """Test parsing a gazetteer entry."""
    connector = OrdnanceSurveyConnector()

    entry = {
        "ID": "osgb4000000074559621",
        "NAME1": "Cardiff",
        "NAME2": "Caerdydd",
        "LANGUAGE": "eng",
        "LOCAL_TYPE": "City",
        "GEOMETRY_X": -3.1791,
        "GEOMETRY_Y": 51.4816,
        "COUNTY_UNITARY": "Cardiff",
    }

    result = connector._parse_entry(entry)
    assert result is not None
    assert result.name_form == "Cardiff"
    assert result.language_code == "eng"
    assert result.latitude == 51.4816
    assert result.longitude == -3.1791
    assert result.place_type == "city"
    assert "cym" in result.alternative_names
    assert "Caerdydd" in result.alternative_names["cym"]


def test_os_parse_entry_no_coords():
    """Test that entries without coordinates return None."""
    connector = OrdnanceSurveyConnector()
    entry = {"ID": "1", "NAME1": "NoCoords", "LANGUAGE": "eng"}
    result = connector._parse_entry(entry)
    assert result is None


def test_os_parse_entry_no_name():
    """Test that entries without names return None."""
    connector = OrdnanceSurveyConnector()
    entry = {"ID": "1", "NAME1": "", "GEOMETRY_X": -1.0, "GEOMETRY_Y": 52.0}
    result = connector._parse_entry(entry)
    assert result is None


@patch("toponymia.connectors.ordnance_survey.httpx.Client")
def test_os_fetch_pagination(mock_client_class: MagicMock) -> None:
    """Test that fetch handles pagination correctly."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    page1_response = MagicMock()
    page1_response.json.return_value = {
        "results": [
            {
                "GAZETTEER_ENTRY": {
                    "ID": "1",
                    "NAME1": "Oxford",
                    "LANGUAGE": "eng",
                    "LOCAL_TYPE": "City",
                    "GEOMETRY_X": -1.2577,
                    "GEOMETRY_Y": 51.7520,
                }
            },
        ]
    }
    page1_response.raise_for_status = MagicMock()

    page2_response = MagicMock()
    page2_response.json.return_value = {"results": []}
    page2_response.raise_for_status = MagicMock()

    mock_client.get.side_effect = [page1_response, page2_response]

    connector = OrdnanceSurveyConnector()
    connector._client = mock_client
    results = list(connector.fetch(name_query="Oxford", max_results=10))
    assert len(results) == 1
    assert results[0].name_form == "Oxford"


@patch("toponymia.connectors.ordnance_survey.httpx.Client")
def test_os_fetch_country_filter(mock_client_class: MagicMock) -> None:
    """Test that fetch with non-GB country returns nothing."""
    connector = OrdnanceSurveyConnector()
    results = list(connector.fetch(country="FR"))
    assert len(results) == 0


def test_os_count_non_gb():
    """Test that count returns 0 for non-UK countries."""
    connector = OrdnanceSurveyConnector()
    assert connector.count(country="FR") == 0
