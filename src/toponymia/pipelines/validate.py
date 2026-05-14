"""Automated validation rules for the data onboarding pipeline.

Stage 2 validation: ensures records meet minimum quality criteria before
advancing from candidate to verified status.

Rules cover:
- Format validation (encoding, form structure)
- Coordinate bounds checking (valid WGS84)
- Language code validation (ISO 639-3)
- Duplicate detection interface
- Source completeness checks
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from toponymia.connectors.base import ConnectorResult, ValidationError

# ISO 639-3: 3-letter codes. We validate structure, not exhaustive list.
_ISO_639_3_PATTERN = re.compile(r"^[a-z]{3}$")

# WGS84 coordinate bounds
_MIN_LAT = -90.0
_MAX_LAT = 90.0
_MIN_LON = -180.0
_MAX_LON = 180.0

# Maximum reasonable name length (characters)
_MAX_NAME_LENGTH = 500

# Minimum name length (at least one character)
_MIN_NAME_LENGTH = 1

# Characters that indicate encoding corruption
_ENCODING_CORRUPTION_PATTERNS = [
    "\ufffd",  # Unicode replacement character
    "â€",  # UTF-8 decoded as Latin-1
    "Ã¤",  # UTF-8 double-encoding artifacts
    "Ã¸",
    "Ã¥",
    "Ã¶",
    "Ã¼",
    "Ã©",
]

# Control characters (except common whitespace)
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass
class ValidationConfig:
    """Configuration for validation rules."""

    # Coordinate bounds (can be narrowed per-region)
    min_lat: float = _MIN_LAT
    max_lat: float = _MAX_LAT
    min_lon: float = _MIN_LON
    max_lon: float = _MAX_LON

    # Name constraints
    max_name_length: int = _MAX_NAME_LENGTH
    min_name_length: int = _MIN_NAME_LENGTH

    # Whether to enforce source_id presence
    require_source_id: bool = True

    # Whether to enforce language code format
    require_valid_language_code: bool = True

    # Whether to check for encoding issues
    check_encoding: bool = True


def validate_record(
    record: ConnectorResult,
    config: ValidationConfig | None = None,
) -> list[ValidationError]:
    """Run all automated validation rules on a record.

    Returns a list of ValidationError objects (empty if valid).
    """
    config = config or ValidationConfig()
    errors: list[ValidationError] = []

    errors.extend(_validate_coordinates(record, config))
    errors.extend(_validate_name_form(record, config))
    errors.extend(_validate_language_code(record, config))
    errors.extend(_validate_source(record, config))
    errors.extend(_validate_temporal(record))

    return errors


def _validate_coordinates(
    record: ConnectorResult, config: ValidationConfig
) -> list[ValidationError]:
    """Validate geographic coordinates are within bounds."""
    errors: list[ValidationError] = []

    if not (config.min_lat <= record.latitude <= config.max_lat):
        errors.append(
            ValidationError(
                field="latitude",
                message=(
                    f"Latitude {record.latitude} out of bounds [{config.min_lat}, {config.max_lat}]"
                ),
            )
        )

    if not (config.min_lon <= record.longitude <= config.max_lon):
        errors.append(
            ValidationError(
                field="longitude",
                message=(
                    f"Longitude {record.longitude} out of bounds"
                    f" [{config.min_lon}, {config.max_lon}]"
                ),
            )
        )

    # Check for null island (0,0) — almost always an error
    if record.latitude == 0.0 and record.longitude == 0.0:
        errors.append(
            ValidationError(
                field="coordinates",
                message="Coordinates are (0, 0) — likely missing data (Null Island)",
                severity="warning",
            )
        )

    return errors


def _validate_name_form(record: ConnectorResult, config: ValidationConfig) -> list[ValidationError]:
    """Validate the name form for format and encoding issues."""
    errors: list[ValidationError] = []

    form = record.name_form

    # Empty or missing name
    if not form or not form.strip():
        errors.append(
            ValidationError(field="name_form", message="Name form is empty or whitespace-only")
        )
        return errors

    # Length check
    if len(form) < config.min_name_length:
        errors.append(
            ValidationError(
                field="name_form",
                message=f"Name form too short ({len(form)} chars, min {config.min_name_length})",
            )
        )

    if len(form) > config.max_name_length:
        errors.append(
            ValidationError(
                field="name_form",
                message=f"Name form too long ({len(form)} chars, max {config.max_name_length})",
            )
        )

    # Encoding corruption detection
    if config.check_encoding:
        for pattern in _ENCODING_CORRUPTION_PATTERNS:
            if pattern in form:
                errors.append(
                    ValidationError(
                        field="name_form",
                        message=f"Encoding corruption detected: '{pattern}' in name",
                    )
                )
                break

    # Control characters
    if _CONTROL_CHAR_PATTERN.search(form):
        errors.append(
            ValidationError(
                field="name_form",
                message="Name contains control characters",
            )
        )

    # Unicode normalization check (should be NFC)
    if form != unicodedata.normalize("NFC", form):
        errors.append(
            ValidationError(
                field="name_form",
                message="Name is not in Unicode NFC normalized form",
                severity="warning",
            )
        )

    # Pure digits (likely an ID, not a name)
    if form.strip().isdigit():
        errors.append(
            ValidationError(
                field="name_form",
                message="Name form is purely numeric — likely an ID, not a place name",
            )
        )

    return errors


def _validate_language_code(
    record: ConnectorResult, config: ValidationConfig
) -> list[ValidationError]:
    """Validate language code format (ISO 639-3)."""
    errors: list[ValidationError] = []

    if not config.require_valid_language_code:
        return errors

    code = record.language_code

    if not code:
        errors.append(ValidationError(field="language_code", message="Language code is missing"))
        return errors

    # "und" (undetermined) is valid but produces a warning
    if code == "und":
        errors.append(
            ValidationError(
                field="language_code",
                message="Language code is 'und' (undetermined) — should be resolved",
                severity="warning",
            )
        )
        return errors

    # Must be 3 lowercase letters
    if not _ISO_639_3_PATTERN.match(code):
        errors.append(
            ValidationError(
                field="language_code",
                message=(
                    f"Language code '{code}' is not valid ISO 639-3"
                    " format (expected 3 lowercase letters)"
                ),
            )
        )

    return errors


def _validate_source(record: ConnectorResult, config: ValidationConfig) -> list[ValidationError]:
    """Validate source provenance information."""
    errors: list[ValidationError] = []

    if config.require_source_id and not record.source_id:
        errors.append(
            ValidationError(field="source_id", message="Source ID is required but missing")
        )

    return errors


def _validate_temporal(record: ConnectorResult) -> list[ValidationError]:
    """Validate temporal bounds for consistency."""
    errors: list[ValidationError] = []

    if (
        record.year_from is not None
        and record.year_to is not None
        and record.year_from > record.year_to
    ):
        errors.append(
            ValidationError(
                field="year_from",
                message=(f"year_from ({record.year_from}) is after year_to ({record.year_to})"),
            )
        )

    # Sanity check: no dates in the far future
    if record.year_from is not None and record.year_from > 2100:
        errors.append(
            ValidationError(
                field="year_from",
                message=f"year_from ({record.year_from}) is in the far future",
                severity="warning",
            )
        )

    if record.year_to is not None and record.year_to > 2100:
        errors.append(
            ValidationError(
                field="year_to",
                message=f"year_to ({record.year_to}) is in the far future",
                severity="warning",
            )
        )

    return errors


def validate_batch(
    records: list[ConnectorResult],
    config: ValidationConfig | None = None,
) -> dict[int, list[ValidationError]]:
    """Validate a batch of records, returning errors keyed by index.

    Only records with errors are included in the result.
    """
    config = config or ValidationConfig()
    results: dict[int, list[ValidationError]] = {}

    for i, record in enumerate(records):
        errors = validate_record(record, config)
        if errors:
            results[i] = errors

    return results
