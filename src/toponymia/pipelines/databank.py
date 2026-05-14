"""Databank validation utilities.

Validates JSONL data files against the place record JSON Schema.
Supports extensible schemas (additionalProperties: true).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DatabankValidationError:
    """A single validation error in a databank file."""

    file: str
    line: int
    field: str
    message: str


@dataclass
class DatabankValidationResult:
    """Result of validating one or more databank files."""

    total_files: int = 0
    total_records: int = 0
    valid_records: int = 0
    errors: list[DatabankValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def invalid_records(self) -> int:
        return self.total_records - self.valid_records


# Core required fields per schema
_REQUIRED_FIELDS = {"name_form", "latitude", "longitude", "source_id"}


def _load_schema(schema_path: Path | None = None) -> dict[str, Any]:
    """Load the JSON Schema for place records."""
    if schema_path is None:
        schema_path = (
            Path(__file__).parent.parent.parent.parent / "databank" / "schema" / "place.v1.json"
        )

    if not schema_path.exists():
        # Fallback: minimal inline schema
        return {"required": list(_REQUIRED_FIELDS)}

    with schema_path.open() as f:
        schema: dict[str, Any] = json.load(f)
        return schema


def validate_record_against_schema(
    record: dict[str, Any],
    schema: dict[str, Any] | None = None,
) -> list[str]:
    """Validate a single record dict against the schema.

    Returns list of error messages (empty = valid).
    Uses lightweight validation (no jsonschema dependency required).
    """
    errors: list[str] = []

    if schema is None:
        schema = _load_schema()

    # Check required fields
    required = schema.get("required", list(_REQUIRED_FIELDS))
    for field_name in required:
        if field_name not in record or record[field_name] is None:
            errors.append(f"Missing required field: {field_name}")
        elif field_name == "name_form" and not str(record[field_name]).strip():
            errors.append("name_form must not be empty")
        elif field_name == "source_id" and not str(record[field_name]).strip():
            errors.append("source_id must not be empty")

    # Validate coordinate bounds
    if "latitude" in record and record["latitude"] is not None:
        lat = record["latitude"]
        if not isinstance(lat, (int, float)) or lat < -90 or lat > 90:
            errors.append(f"latitude must be between -90 and 90, got {lat}")

    if "longitude" in record and record["longitude"] is not None:
        lon = record["longitude"]
        if not isinstance(lon, (int, float)) or lon < -180 or lon > 180:
            errors.append(f"longitude must be between -180 and 180, got {lon}")

    # Validate language_code format if present
    if "language_code" in record and record["language_code"] is not None:
        code = record["language_code"]
        if not isinstance(code, str) or len(code) != 3 or not code.isalpha() or not code.islower():
            errors.append(f"language_code must be 3 lowercase letters (ISO 639-3), got '{code}'")

    # Validate country_code format if present
    if "country_code" in record and record["country_code"] is not None:
        cc = record["country_code"]
        if not isinstance(cc, str) or len(cc) != 2 or not cc.isalpha() or not cc.isupper():
            errors.append(f"country_code must be 2 uppercase letters (ISO 3166-1), got '{cc}'")

    return errors


def validate_jsonl_file(
    filepath: Path,
    schema: dict[str, Any] | None = None,
) -> DatabankValidationResult:
    """Validate all records in a JSONL file."""
    result = DatabankValidationResult(total_files=1)

    if schema is None:
        schema = _load_schema()

    with filepath.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            result.total_records += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                result.errors.append(
                    DatabankValidationError(
                        file=str(filepath),
                        line=line_num,
                        field="(json)",
                        message=f"Invalid JSON: {e}",
                    )
                )
                continue

            if not isinstance(record, dict):
                result.errors.append(
                    DatabankValidationError(
                        file=str(filepath),
                        line=line_num,
                        field="(type)",
                        message="Record must be a JSON object",
                    )
                )
                continue

            field_errors = validate_record_against_schema(record, schema)
            if field_errors:
                for err_msg in field_errors:
                    # Extract field name from error message
                    field_name = err_msg.split(":")[0] if ":" in err_msg else "(schema)"
                    result.errors.append(
                        DatabankValidationError(
                            file=str(filepath),
                            line=line_num,
                            field=field_name,
                            message=err_msg,
                        )
                    )
            else:
                result.valid_records += 1

    return result


def validate_databank(
    databank_path: Path | None = None,
) -> DatabankValidationResult:
    """Validate the entire databank directory."""
    if databank_path is None:
        databank_path = Path(__file__).parent.parent.parent.parent / "databank"

    places_dir = databank_path / "places"
    schema = _load_schema(databank_path / "schema" / "place.v1.json")

    combined = DatabankValidationResult()

    if not places_dir.exists():
        return combined

    for jsonl_file in sorted(places_dir.rglob("*.jsonl")):
        file_result = validate_jsonl_file(jsonl_file, schema)
        combined.total_files += file_result.total_files
        combined.total_records += file_result.total_records
        combined.valid_records += file_result.valid_records
        combined.errors.extend(file_result.errors)

    return combined
