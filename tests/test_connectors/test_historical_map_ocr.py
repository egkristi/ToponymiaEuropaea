"""Tests for the Historical Map OCR connector."""

from pathlib import Path

import pytest

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.historical_map_ocr import (
    OCR_ENGINES,
    HistoricalMapOCRConnector,
    MapMetadata,
    OCRDetection,
)


def test_historical_map_ocr_metadata():
    """Test connector class-level metadata."""
    connector = HistoricalMapOCRConnector()
    assert connector.source_id == "historical_map_ocr"
    assert connector.source_name == "Historical Map OCR Pipeline"
    assert connector.coverage_region == "NO"


def test_historical_map_ocr_invalid_engine():
    """Test that invalid OCR engine raises ValueError."""
    with pytest.raises(ValueError, match="Unknown OCR engine"):
        HistoricalMapOCRConnector(ocr_engine="invalid")


def test_historical_map_ocr_engines():
    """Test supported OCR engines."""
    assert "tesseract" in OCR_ENGINES
    assert "easyocr" in OCR_ENGINES
    assert "kraken" in OCR_ENGINES


def test_historical_map_ocr_add_map():
    """Test adding maps for processing."""
    connector = HistoricalMapOCRConnector()
    meta = MapMetadata(filepath=Path("tests/fixtures/test.tif"), year=1850)
    connector.add_map(meta)
    assert len(connector._maps) == 1


def test_historical_map_ocr_validation_valid():
    """Test validation of a valid OCR record."""
    connector = HistoricalMapOCRConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="Bergen",
        name_normalized="bergen",
        language_code="nor",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_historical_map_ocr_validation_empty_name():
    """Test validation catches empty name."""
    connector = HistoricalMapOCRConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="",
        name_normalized="",
        language_code="nor",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_historical_map_ocr_validation_short_name():
    """Test validation warns on very short names (OCR noise)."""
    connector = HistoricalMapOCRConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="X",
        name_normalized="x",
        language_code="nor",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" and "too short" in e.message for e in errors)


def test_historical_map_ocr_validation_numeric():
    """Test validation warns on all-digit strings."""
    connector = HistoricalMapOCRConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="1234",
        name_normalized="1234",
        language_code="nor",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" and "digits" in e.message for e in errors)


def test_historical_map_ocr_pixel_to_geo():
    """Test pixel-to-geo transformation with control points."""
    connector = HistoricalMapOCRConnector()
    meta = MapMetadata(
        filepath=Path("tests/fixtures/test.tif"),
        control_points=[
            (0.0, 0.0, 10.0, 60.0),
            (100.0, 0.0, 11.0, 60.0),
            (0.0, 100.0, 10.0, 59.0),
        ],
    )
    lon, lat = connector._pixel_to_geo(50.0, 50.0, meta)
    assert 10.0 <= lon <= 11.0
    assert 59.0 <= lat <= 60.0


def test_historical_map_ocr_pixel_to_geo_no_control_points():
    """Test that missing control points returns (0, 0)."""
    connector = HistoricalMapOCRConnector()
    meta = MapMetadata(filepath=Path("tests/fixtures/test.tif"))
    lon, lat = connector._pixel_to_geo(50.0, 50.0, meta)
    assert lon == 0.0
    assert lat == 0.0


def test_historical_map_ocr_detection_to_result():
    """Test converting OCR detection to ConnectorResult."""
    connector = HistoricalMapOCRConnector()
    meta = MapMetadata(
        filepath=Path("tests/fixtures/map1850.tif"),
        year=1850,
        control_points=[
            (0.0, 0.0, 10.0, 60.0),
            (100.0, 0.0, 11.0, 60.0),
            (0.0, 100.0, 10.0, 59.0),
        ],
    )
    detection = OCRDetection(
        text="Bergen",
        confidence=0.95,
        pixel_x=50.0,
        pixel_y=25.0,
        width=80.0,
        height=15.0,
    )
    result = connector._detection_to_result(detection, meta)
    assert result is not None
    assert result.name_form == "Bergen"
    assert result.year_from == 1850
    assert result.is_current is False


def test_historical_map_ocr_fetch_nonexistent_map():
    """Test that fetching from nonexistent map yields nothing."""
    connector = HistoricalMapOCRConnector()
    meta = MapMetadata(filepath=Path("/nonexistent/map.tif"))
    connector.add_map(meta)
    results = list(connector.fetch())
    assert len(results) == 0


def test_historical_map_ocr_count():
    """Test that count returns None."""
    connector = HistoricalMapOCRConnector()
    assert connector.count() is None
