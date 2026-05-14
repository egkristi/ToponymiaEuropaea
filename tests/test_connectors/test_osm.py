"""Tests for the OpenStreetMap connector."""

from unittest.mock import patch

import httpx
import pytest

from toponymia.connectors.base import BoundingBox, ConnectorResult
from toponymia.connectors.osm import OSMConnector


def test_osm_connector_metadata():
    """Test connector class-level metadata."""
    connector = OSMConnector()
    assert connector.source_id == "osm"
    assert connector.source_name == "OpenStreetMap"
    assert connector.license == "ODbL-1.0"
    assert connector.coverage_region == "global"


def test_osm_validation_valid_record():
    """Test validation of a valid record."""
    connector = OSMConnector()
    record = ConnectorResult(
        latitude=59.9139,
        longitude=10.7522,
        name_form="Oslo",
        name_normalized="Oslo",
        language_code="und",
        source_id="node/123456",
        osm_id=123456,
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_osm_validation_empty_name():
    """Test validation catches empty name."""
    connector = OSMConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="",
        name_normalized="",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_osm_validation_invalid_latitude():
    """Test validation catches invalid latitude."""
    connector = OSMConnector()
    record = ConnectorResult(
        latitude=91.0,
        longitude=10.0,
        name_form="Test",
        name_normalized="test",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)


def test_osm_validation_invalid_longitude():
    """Test validation catches invalid longitude."""
    connector = OSMConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=181.0,
        name_form="Test",
        name_normalized="test",
    )
    errors = connector.validate(record)
    assert any(e.field == "longitude" for e in errors)


def test_osm_fetch_requires_bbox():
    """Test that fetch raises ValueError without bbox."""
    connector = OSMConnector()
    with pytest.raises(ValueError, match="bounding box"):
        list(connector.fetch(bbox=None))


def test_osm_fetch_parses_node_elements():
    """Test that fetch correctly parses OSM node elements."""
    mock_response_data = {
        "elements": [
            {
                "type": "node",
                "id": 12345,
                "lat": 60.3913,
                "lon": 5.3221,
                "tags": {
                    "name": "Bergen",
                    "place": "city",
                    "name:en": "Bergen",
                    "name:de": "Bergen",
                    "old_name": "Bjørgvin",
                },
            }
        ]
    }

    connector = OSMConnector()
    bbox = BoundingBox(min_lon=5.0, min_lat=60.0, max_lon=6.0, max_lat=61.0)

    with patch.object(connector, "_execute_overpass", return_value=mock_response_data["elements"]):
        results = list(connector.fetch(bbox=bbox))

    assert len(results) == 1
    result = results[0]
    assert result.name_form == "Bergen"
    assert result.latitude == 60.3913
    assert result.longitude == 5.3221
    assert result.place_type == "osm.city"
    assert result.source_id == "node/12345"
    assert result.osm_id == 12345
    assert "en" in result.alternative_names
    assert "Bergen" in result.alternative_names["en"]
    assert "historical" in result.alternative_names
    assert "Bjørgvin" in result.alternative_names["historical"]


def test_osm_fetch_parses_way_elements_with_center():
    """Test that fetch uses center coordinates for way elements."""
    mock_elements = [
        {
            "type": "way",
            "id": 67890,
            "center": {"lat": 63.4305, "lon": 10.3951},
            "tags": {
                "name": "Trondheim",
                "place": "city",
            },
        }
    ]

    connector = OSMConnector()
    bbox = BoundingBox(min_lon=10.0, min_lat=63.0, max_lon=11.0, max_lat=64.0)

    with patch.object(connector, "_execute_overpass", return_value=mock_elements):
        results = list(connector.fetch(bbox=bbox))

    assert len(results) == 1
    assert results[0].name_form == "Trondheim"
    assert results[0].latitude == 63.4305
    assert results[0].longitude == 10.3951
    assert results[0].source_id == "way/67890"


def test_osm_fetch_skips_elements_without_name():
    """Test that elements without a name tag are skipped."""
    mock_elements = [
        {
            "type": "node",
            "id": 11111,
            "lat": 60.0,
            "lon": 10.0,
            "tags": {"place": "hamlet"},
        }
    ]

    connector = OSMConnector()
    bbox = BoundingBox(min_lon=9.0, min_lat=59.0, max_lon=11.0, max_lat=61.0)

    with patch.object(connector, "_execute_overpass", return_value=mock_elements):
        results = list(connector.fetch(bbox=bbox))

    assert len(results) == 0


def test_osm_fetch_skips_elements_without_coordinates():
    """Test that way/relation elements without center are skipped."""
    mock_elements = [
        {
            "type": "way",
            "id": 22222,
            "tags": {"name": "NoCoords", "place": "village"},
        }
    ]

    connector = OSMConnector()
    bbox = BoundingBox(min_lon=9.0, min_lat=59.0, max_lon=11.0, max_lat=61.0)

    with patch.object(connector, "_execute_overpass", return_value=mock_elements):
        results = list(connector.fetch(bbox=bbox))

    assert len(results) == 0


def test_osm_execute_overpass_handles_http_error():
    """Test that HTTP errors are handled gracefully."""
    connector = OSMConnector()

    mock_request = httpx.Request("POST", "https://overpass-api.de/api/interpreter")
    mock_response = httpx.Response(500, request=mock_request)
    error = httpx.HTTPStatusError("Server Error", request=mock_request, response=mock_response)

    with patch("httpx.post", side_effect=error):
        result = connector._execute_overpass("test query")

    assert result == []


def test_osm_execute_overpass_handles_network_error():
    """Test that network errors are handled gracefully."""
    connector = OSMConnector()

    with patch("httpx.post", side_effect=httpx.ConnectError("Connection failed")):
        result = connector._execute_overpass("test query")

    assert result == []
