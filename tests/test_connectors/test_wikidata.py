"""Tests for the Wikidata connector."""

from unittest.mock import patch

import httpx
import pytest

from toponymia.connectors.base import BoundingBox, ConnectorResult
from toponymia.connectors.wikidata import WikidataConnector


def _make_connector():
    """Create a WikidataConnector with mocked settings."""
    with patch("toponymia.connectors.wikidata.get_settings") as mock_settings:
        mock_settings.return_value.wikidata_endpoint = "https://query.wikidata.org/sparql"
        return WikidataConnector()


def test_wikidata_connector_metadata():
    """Test connector class-level metadata."""
    connector = _make_connector()
    assert connector.source_id == "wikidata"
    assert connector.source_name == "Wikidata"
    assert connector.license == "CC0-1.0"
    assert connector.coverage_region == "global"


def test_wikidata_validation_valid_record():
    """Test validation of a valid record."""
    connector = _make_connector()
    record = ConnectorResult(
        latitude=59.9139,
        longitude=10.7522,
        name_form="Oslo",
        name_normalized="Oslo",
        language_code="und",
        source_id="Q585",
        wikidata_qid="Q585",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_wikidata_validation_empty_name():
    """Test validation catches empty name."""
    connector = _make_connector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="",
        name_normalized="",
        wikidata_qid="Q123",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_wikidata_validation_invalid_qid():
    """Test validation catches invalid QID format."""
    connector = _make_connector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="Test",
        name_normalized="test",
        wikidata_qid="P123",  # Properties start with P, not Q
    )
    errors = connector.validate(record)
    assert any(e.field == "wikidata_qid" for e in errors)


def test_wikidata_fetch_requires_bbox_or_country():
    """Test that fetch raises ValueError without bbox or country."""
    connector = _make_connector()
    with pytest.raises(ValueError, match="(?i)bbox|country"):
        list(connector.fetch(bbox=None, country=None))


def test_wikidata_fetch_parses_sparql_results():
    """Test that fetch correctly parses SPARQL bindings."""
    mock_bindings = [
        {
            "place": {"value": "http://www.wikidata.org/entity/Q585"},
            "placeLabel": {"value": "Oslo"},
            "coord": {"value": "Point(10.7522 59.9139)"},
            "geonames_id": {"value": "3143244"},
        }
    ]

    connector = _make_connector()
    bbox = BoundingBox(min_lon=10.0, min_lat=59.0, max_lon=11.0, max_lat=60.0)

    with patch.object(connector, "_execute_sparql", return_value=mock_bindings):
        results = list(connector.fetch(bbox=bbox))

    assert len(results) == 1
    result = results[0]
    assert result.name_form == "Oslo"
    assert result.latitude == 59.9139
    assert result.longitude == 10.7522
    assert result.wikidata_qid == "Q585"
    assert result.geonames_id == 3143244
    assert result.source_license == "CC0-1.0"


def test_wikidata_fetch_skips_entries_without_coordinates():
    """Test that entries missing coordinates are skipped."""
    mock_bindings = [
        {
            "place": {"value": "http://www.wikidata.org/entity/Q999"},
            "placeLabel": {"value": "NoCoords"},
            "coord": {"value": ""},
        }
    ]

    connector = _make_connector()
    bbox = BoundingBox(min_lon=10.0, min_lat=59.0, max_lon=11.0, max_lat=60.0)

    with patch.object(connector, "_execute_sparql", return_value=mock_bindings):
        results = list(connector.fetch(bbox=bbox))

    assert len(results) == 0


def test_wikidata_fetch_skips_entries_where_label_is_qid():
    """Test that entries where label resolves to QID are skipped."""
    mock_bindings = [
        {
            "place": {"value": "http://www.wikidata.org/entity/Q99999"},
            "placeLabel": {"value": "Q99999"},  # No label available
            "coord": {"value": "Point(10.0 60.0)"},
        }
    ]

    connector = _make_connector()
    bbox = BoundingBox(min_lon=9.0, min_lat=59.0, max_lon=11.0, max_lat=61.0)

    with patch.object(connector, "_execute_sparql", return_value=mock_bindings):
        results = list(connector.fetch(bbox=bbox))

    assert len(results) == 0


def test_wikidata_fetch_with_country_uses_default_bbox():
    """Test that country code resolves to a default bounding box."""
    connector = _make_connector()

    with patch.object(connector, "_execute_sparql", return_value=[]) as mock_sparql:
        list(connector.fetch(country="NO"))

    # Should have been called (with any query string)
    assert mock_sparql.called


def test_wikidata_fetch_paginates():
    """Test that fetch continues fetching until batch is smaller than batch_size."""
    connector = _make_connector()
    connector._batch_size = 2  # Small batch for testing

    # First call returns full batch (2 items), second returns partial (1 item)
    batch1 = [
        {
            "place": {"value": "http://www.wikidata.org/entity/Q1"},
            "placeLabel": {"value": "Place1"},
            "coord": {"value": "Point(10.0 60.0)"},
        },
        {
            "place": {"value": "http://www.wikidata.org/entity/Q2"},
            "placeLabel": {"value": "Place2"},
            "coord": {"value": "Point(11.0 61.0)"},
        },
    ]
    batch2 = [
        {
            "place": {"value": "http://www.wikidata.org/entity/Q3"},
            "placeLabel": {"value": "Place3"},
            "coord": {"value": "Point(12.0 62.0)"},
        },
    ]

    connector._rate_limit_seconds = 0  # No delay in tests
    bbox = BoundingBox(min_lon=9.0, min_lat=59.0, max_lon=13.0, max_lat=63.0)

    with patch.object(connector, "_execute_sparql", side_effect=[batch1, batch2]):
        results = list(connector.fetch(bbox=bbox))

    assert len(results) == 3


def test_wikidata_execute_sparql_handles_http_error():
    """Test that HTTP errors are handled gracefully."""
    connector = _make_connector()

    mock_request = httpx.Request("GET", "https://query.wikidata.org/sparql")
    mock_response = httpx.Response(500, request=mock_request)
    error = httpx.HTTPStatusError("Server Error", request=mock_request, response=mock_response)

    with patch("httpx.get", side_effect=error):
        result = connector._execute_sparql("test query")

    assert result == []


def test_wikidata_execute_sparql_handles_network_error():
    """Test that network errors are handled gracefully."""
    connector = _make_connector()

    with patch("httpx.get", side_effect=httpx.ConnectError("Connection failed")):
        result = connector._execute_sparql("test query")

    assert result == []


def test_wikidata_country_bbox_known():
    """Test that known countries return valid bounding boxes."""
    bbox = WikidataConnector._country_bbox("NO")
    assert bbox.min_lat < bbox.max_lat
    assert bbox.min_lon < bbox.max_lon


def test_wikidata_country_bbox_unknown_returns_europe():
    """Test that unknown countries return Europe-wide bbox."""
    bbox = WikidataConnector._country_bbox("XX")
    # Default Europe bbox
    assert bbox.min_lon == -25.0
    assert bbox.max_lat == 72.0
