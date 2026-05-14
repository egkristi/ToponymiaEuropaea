"""Tests for the GeoNames connector."""

from toponymia.connectors.base import BoundingBox, ConnectorResult
from toponymia.connectors.geonames import GeoNamesConnector


def test_geonames_connector_metadata():
    """Test connector class-level metadata."""
    connector = GeoNamesConnector()
    assert connector.source_id == "geonames"
    assert connector.license == "CC-BY-4.0"
    assert connector.coverage_region == "global"


def test_geonames_validation_valid_record():
    """Test validation of a valid record."""
    connector = GeoNamesConnector()
    record = ConnectorResult(
        latitude=59.9139,
        longitude=10.7522,
        name_form="Oslo",
        name_normalized="Oslo",
        language_code="und",
        source_id="3143244",
        geonames_id=3143244,
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_geonames_validation_invalid_latitude():
    """Test validation catches invalid latitude."""
    connector = GeoNamesConnector()
    record = ConnectorResult(
        latitude=91.0,  # Invalid
        longitude=10.0,
        name_form="Test",
        name_normalized="test",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)


def test_geonames_validation_empty_name():
    """Test validation catches empty name."""
    connector = GeoNamesConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="",
        name_normalized="",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_bounding_box_contains():
    """Test bounding box containment check."""
    bbox = BoundingBox(min_lon=5.0, min_lat=58.0, max_lon=15.0, max_lat=65.0)
    assert bbox.contains(10.0, 60.0)
    assert not bbox.contains(20.0, 60.0)
    assert not bbox.contains(10.0, 70.0)
