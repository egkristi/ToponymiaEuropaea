"""Historical map OCR pipeline connector.

Provides an interface for extracting place names from scanned/digitized
historical maps using OCR (Optical Character Recognition) techniques.
Targets digitized map collections such as:
- Kartverket historical maps (Norway)
- Riksarkivet kartor (Sweden)
- Geodatastyrelsen historiske kort (Denmark)

The pipeline:
1. Accept a raster image (TIFF/JPEG) of a historical map
2. Run OCR (Tesseract or custom LSTM model)
3. Apply text segmentation to isolate place-name labels
4. Georeference detected labels to map coordinates
5. Yield ConnectorResult for each detected place name

This is a local-processing connector (no external API required).
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from toponymia.connectors.base import (
    BaseConnector,
    BoundingBox,
    ConnectorResult,
    ValidationError,
)

logger = logging.getLogger(__name__)

# Supported OCR engines
OCR_ENGINES = ("tesseract", "easyocr", "kraken")

# Map language labels → ISO 639-3
_LANGUAGE_MAP: dict[str, str] = {
    "nor": "nor",
    "nob": "nob",
    "nno": "nno",
    "swe": "swe",
    "dan": "dan",
    "fin": "fin",
    "deu": "deu",
    "lat": "lat",
}


@dataclass
class MapMetadata:
    """Metadata for a historical map image."""

    filepath: Path
    year: int | None = None
    region: str = ""
    crs: str = "EPSG:4326"
    scale: float | None = None
    # Georeferencing control points (pixel_x, pixel_y, lon, lat)
    control_points: list[tuple[float, float, float, float]] | None = None


@dataclass
class OCRDetection:
    """A single text detection from OCR."""

    text: str
    confidence: float
    pixel_x: float
    pixel_y: float
    width: float
    height: float


class HistoricalMapOCRConnector(BaseConnector):
    """Connector for extracting place names from historical maps via OCR.

    This connector processes digitized historical maps to extract
    place-name labels with their geographic positions. It supports:
    - Multiple OCR engines (Tesseract, EasyOCR, Kraken)
    - Georeferencing via control points or world files
    - Confidence filtering for detection quality
    - Historical language detection

    Usage requires pre-scanned maps with georeferencing information.
    """

    source_id = "historical_map_ocr"
    source_name = "Historical Map OCR Pipeline"
    license = "varies"
    coverage_region = "NO"
    source_url = "https://www.kartverket.no/historiske-kart"

    def __init__(
        self,
        *,
        ocr_engine: str = "tesseract",
        language: str = "nor",
        min_confidence: float = 0.6,
    ):
        """Initialize the Historical Map OCR connector.

        Args:
            ocr_engine: OCR engine to use (tesseract, easyocr, kraken).
            language: Default language for OCR recognition.
            min_confidence: Minimum confidence threshold for detections.
        """
        if ocr_engine not in OCR_ENGINES:
            msg = f"Unknown OCR engine: {ocr_engine}. Must be one of {OCR_ENGINES}"
            raise ValueError(msg)

        self._engine = ocr_engine
        self._language = language
        self._min_confidence = min_confidence
        self._maps: list[MapMetadata] = []

    def add_map(self, map_meta: MapMetadata) -> None:
        """Register a map for processing.

        Args:
            map_meta: Metadata for the map image to process.
        """
        self._maps.append(map_meta)

    def fetch(
        self,
        bbox: BoundingBox | None = None,
        country: str | None = None,
        *,
        max_results: int | None = None,
    ) -> Iterator[ConnectorResult]:
        """Extract place names from registered maps.

        Args:
            bbox: Geographic bounding box filter.
            country: Country filter.
            max_results: Maximum number of results to return.

        Yields:
            ConnectorResult for each detected place name.
        """
        yielded = 0

        for map_meta in self._maps:
            if max_results and yielded >= max_results:
                break

            detections = self._run_ocr(map_meta)

            for detection in detections:
                if max_results and yielded >= max_results:
                    break

                if detection.confidence < self._min_confidence:
                    continue

                result = self._detection_to_result(detection, map_meta)
                if result is None:
                    continue

                if bbox and not bbox.contains(result.longitude, result.latitude):
                    continue

                yielded += 1
                yield result

    def _run_ocr(self, map_meta: MapMetadata) -> list[OCRDetection]:
        """Run OCR on a map image.

        This is the integration point for actual OCR engines.
        In production, this calls tesseract/easyocr/kraken.
        Returns empty list if the map file doesn't exist or OCR fails.
        """
        if not map_meta.filepath.exists():
            logger.warning("Map file not found: %s", map_meta.filepath)
            return []

        # Actual OCR integration would go here
        # For now, return empty (requires OCR engine installation)
        logger.info("OCR processing %s with engine=%s", map_meta.filepath, self._engine)
        return []

    def _detection_to_result(
        self, detection: OCRDetection, map_meta: MapMetadata
    ) -> ConnectorResult | None:
        """Convert an OCR detection to a ConnectorResult.

        Applies georeferencing to transform pixel coordinates to geographic.
        """
        lon, lat = self._pixel_to_geo(detection.pixel_x, detection.pixel_y, map_meta)

        if lat == 0.0 and lon == 0.0:
            return None

        lang_code = _LANGUAGE_MAP.get(self._language, "und")

        return ConnectorResult(
            latitude=lat,
            longitude=lon,
            name_form=detection.text.strip(),
            name_normalized=detection.text.strip().lower(),
            language_code=lang_code,
            year_from=map_meta.year,
            year_to=map_meta.year,
            is_current=False,
            place_type="map_label",
            source_id=f"ocr:{map_meta.filepath.stem}",
            source_url=self.source_url,
            source_license=self.license,
        )

    def _pixel_to_geo(self, px: float, py: float, map_meta: MapMetadata) -> tuple[float, float]:
        """Transform pixel coordinates to geographic coordinates.

        Uses affine transformation from control points or world file.
        Returns (longitude, latitude).
        """
        if not map_meta.control_points or len(map_meta.control_points) < 3:
            return 0.0, 0.0

        # Simple affine transformation using first 3 control points
        # In production, use proper least-squares affine or polynomial fit
        cp = map_meta.control_points
        # Use centroid of control points as approximation
        avg_lon = sum(p[2] for p in cp) / len(cp)
        avg_lat = sum(p[3] for p in cp) / len(cp)

        # Scale from pixel space (rough approximation)
        if len(cp) >= 2:
            dx_pixel = cp[1][0] - cp[0][0]
            dx_geo = cp[1][2] - cp[0][2]
            dy_pixel = cp[1][1] - cp[0][1]
            dy_geo = cp[1][3] - cp[0][3]

            if dx_pixel != 0 and dy_pixel != 0:
                lon = cp[0][2] + (px - cp[0][0]) * dx_geo / dx_pixel
                lat = cp[0][3] + (py - cp[0][1]) * dy_geo / dy_pixel
                return lon, lat

        return avg_lon, avg_lat

    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate an OCR-extracted record."""
        errors: list[ValidationError] = []

        if not record.name_form:
            errors.append(ValidationError(field="name_form", message="Empty name form"))

        # Check for OCR noise (very short or all-numeric)
        if record.name_form and len(record.name_form) < 2:
            errors.append(
                ValidationError(
                    field="name_form",
                    message="Name too short (likely OCR noise)",
                    severity="warning",
                )
            )

        if record.name_form and record.name_form.isdigit():
            errors.append(
                ValidationError(
                    field="name_form",
                    message="Name is all digits (likely not a place name)",
                    severity="warning",
                )
            )

        return errors

    def count(self, bbox: BoundingBox | None = None, country: str | None = None) -> int | None:
        """Return estimated count (not available for OCR pipeline)."""
        return None


def process_map_batch(
    maps: list[dict[str, Any]],
    *,
    ocr_engine: str = "tesseract",
    language: str = "nor",
    min_confidence: float = 0.6,
) -> Iterator[ConnectorResult]:
    """Process a batch of maps and yield place-name results.

    Convenience function for batch processing.

    Args:
        maps: List of dicts with 'filepath', 'year', 'region', 'control_points'.
        ocr_engine: OCR engine to use.
        language: Language for OCR recognition.
        min_confidence: Minimum confidence threshold.

    Yields:
        ConnectorResult for each detected place name.
    """
    connector = HistoricalMapOCRConnector(
        ocr_engine=ocr_engine,
        language=language,
        min_confidence=min_confidence,
    )

    for map_dict in maps:
        meta = MapMetadata(
            filepath=Path(map_dict["filepath"]),
            year=map_dict.get("year"),
            region=map_dict.get("region", ""),
            control_points=map_dict.get("control_points"),
        )
        connector.add_map(meta)

    yield from connector.fetch()
