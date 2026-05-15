"""Attestation-specific validation against the attestation.v1 schema.

Validates JSONL attestation records for:
- Required fields (form, language_code, year_from, source)
- Field format and range constraints
- Unicode NFC normalization
- Date plausibility
- Component morph_type values
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ISO_639_3_PATTERN = re.compile(r"^[a-z]{2,3}$")
_ISO_15924_PATTERN = re.compile(r"^[A-Z][a-z]{3}$")
_VALID_MORPH_TYPES = frozenset(
    {"prefix", "stem", "suffix", "compound_head", "compound_modifier", "infix", "genitive"}
)
_VALID_DATE_PRECISIONS = frozenset({"exact", "decade", "quarter_century", "century", "estimated"})
_VALID_COLLECTION_METHODS = frozenset(
    {"manual_transcription", "ocr", "automated_extraction", "field_recording", "database_export"}
)
_MIN_YEAR = -3000
_MAX_YEAR = 2100


@dataclass
class AttestationError:
    """A single validation error for an attestation record."""

    line: int
    field: str
    message: str
    severity: str = "error"


@dataclass
class AttestationValidationReport:
    """Summary of attestation validation results."""

    total_records: int = 0
    valid_records: int = 0
    errors: list[AttestationError] = field(default_factory=list)

    @property
    def invalid_records(self) -> int:
        return self.total_records - self.valid_records

    @property
    def is_valid(self) -> bool:
        return not any(e.severity == "error" for e in self.errors)


def validate_attestation_record(
    record: dict[str, Any], line_number: int = 0
) -> list[AttestationError]:
    """Validate a single attestation record dict."""
    errors: list[AttestationError] = []

    # Required fields
    if not record.get("form"):
        errors.append(
            AttestationError(
                line=line_number,
                field="form",
                message="Required field 'form' is missing or empty",
            )
        )
    elif not isinstance(record["form"], str):
        errors.append(
            AttestationError(
                line=line_number,
                field="form",
                message="Field 'form' must be a string",
            )
        )
    else:
        form = record["form"]
        if form != unicodedata.normalize("NFC", form):
            errors.append(
                AttestationError(
                    line=line_number,
                    field="form",
                    message="Form is not Unicode NFC normalized",
                    severity="warning",
                )
            )

    if not record.get("language_code"):
        errors.append(
            AttestationError(
                line=line_number,
                field="language_code",
                message="Required field 'language_code' is missing or empty",
            )
        )
    elif not _ISO_639_3_PATTERN.match(record["language_code"]):
        errors.append(
            AttestationError(
                line=line_number,
                field="language_code",
                message=(
                    f"Invalid language code '{record['language_code']}'"
                    " (expected 2-3 lowercase letters)"
                ),
            )
        )

    if "year_from" not in record or record["year_from"] is None:
        errors.append(
            AttestationError(
                line=line_number,
                field="year_from",
                message="Required field 'year_from' is missing or null",
            )
        )
    elif not isinstance(record["year_from"], int):
        errors.append(
            AttestationError(
                line=line_number,
                field="year_from",
                message=(
                    "Field 'year_from' must be an integer, got"
                    f" {type(record['year_from']).__name__}"
                ),
            )
        )
    else:
        if record["year_from"] < _MIN_YEAR or record["year_from"] > _MAX_YEAR:
            errors.append(
                AttestationError(
                    line=line_number,
                    field="year_from",
                    message=(
                        f"year_from {record['year_from']} outside range [{_MIN_YEAR}, {_MAX_YEAR}]"
                    ),
                )
            )

    if not record.get("source"):
        errors.append(
            AttestationError(
                line=line_number,
                field="source",
                message="Required field 'source' is missing or empty",
            )
        )

    # Optional field validation
    year_to = record.get("year_to")
    if year_to is not None:
        if not isinstance(year_to, int):
            errors.append(
                AttestationError(
                    line=line_number,
                    field="year_to",
                    message=(
                        f"Field 'year_to' must be an integer or null, got {type(year_to).__name__}"
                    ),
                )
            )
        elif year_to < _MIN_YEAR or year_to > _MAX_YEAR:
            errors.append(
                AttestationError(
                    line=line_number,
                    field="year_to",
                    message=f"year_to {year_to} outside range [{_MIN_YEAR}, {_MAX_YEAR}]",
                )
            )
        elif isinstance(record.get("year_from"), int) and year_to < record["year_from"]:
            errors.append(
                AttestationError(
                    line=line_number,
                    field="year_to",
                    message=f"year_to ({year_to}) is before year_from ({record['year_from']})",
                )
            )

    confidence = record.get("confidence")
    if confidence is not None:
        if not isinstance(confidence, (int, float)):
            errors.append(
                AttestationError(
                    line=line_number,
                    field="confidence",
                    message=f"Confidence must be a number, got {type(confidence).__name__}",
                )
            )
        elif confidence < 0.0 or confidence > 1.0:
            errors.append(
                AttestationError(
                    line=line_number,
                    field="confidence",
                    message=f"Confidence {confidence} outside range [0.0, 1.0]",
                )
            )

    script = record.get("script")
    if script is not None and not _ISO_15924_PATTERN.match(str(script)):
        errors.append(
            AttestationError(
                line=line_number,
                field="script",
                message=f"Invalid script code '{script}' (expected ISO 15924, e.g. 'Latn')",
            )
        )

    date_precision = record.get("date_precision")
    if date_precision is not None and date_precision not in _VALID_DATE_PRECISIONS:
        valid = ", ".join(sorted(_VALID_DATE_PRECISIONS))
        errors.append(
            AttestationError(
                line=line_number,
                field="date_precision",
                message=f"Invalid date_precision '{date_precision}' (expected: {valid})",
            )
        )

    collection_method = record.get("collection_method")
    if collection_method is not None and collection_method not in _VALID_COLLECTION_METHODS:
        errors.append(
            AttestationError(
                line=line_number,
                field="collection_method",
                message=f"Invalid collection_method '{collection_method}'",
            )
        )

    lemma_lang = record.get("lemma_language")
    if lemma_lang is not None and not _ISO_639_3_PATTERN.match(str(lemma_lang)):
        errors.append(
            AttestationError(
                line=line_number,
                field="lemma_language",
                message=f"Invalid lemma_language '{lemma_lang}'",
            )
        )

    # Component validation
    components = record.get("components")
    if components is not None:
        if not isinstance(components, list):
            errors.append(
                AttestationError(
                    line=line_number,
                    field="components",
                    message="Components must be an array",
                )
            )
        else:
            for i, comp in enumerate(components):
                if not isinstance(comp, dict):
                    errors.append(
                        AttestationError(
                            line=line_number,
                            field=f"components[{i}]",
                            message="Each component must be an object",
                        )
                    )
                    continue
                if not comp.get("component"):
                    errors.append(
                        AttestationError(
                            line=line_number,
                            field=f"components[{i}].component",
                            message="Component text is required",
                        )
                    )
                if "position" not in comp:
                    errors.append(
                        AttestationError(
                            line=line_number,
                            field=f"components[{i}].position",
                            message="Component position is required",
                        )
                    )
                morph_type = comp.get("morph_type")
                if not morph_type:
                    errors.append(
                        AttestationError(
                            line=line_number,
                            field=f"components[{i}].morph_type",
                            message="Component morph_type is required",
                        )
                    )
                elif morph_type not in _VALID_MORPH_TYPES:
                    errors.append(
                        AttestationError(
                            line=line_number,
                            field=f"components[{i}].morph_type",
                            message=f"Invalid morph_type '{morph_type}'",
                        )
                    )

    return errors


def validate_attestation_file(path: Path) -> AttestationValidationReport:
    """Validate an entire JSONL file of attestation records."""
    report = AttestationValidationReport()

    with path.open() as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            report.total_records += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                report.errors.append(
                    AttestationError(
                        line=line_number,
                        field="json",
                        message=f"Invalid JSON: {e}",
                    )
                )
                continue

            errors = validate_attestation_record(record, line_number)
            if not any(e.severity == "error" for e in errors):
                report.valid_records += 1
            report.errors.extend(errors)

    return report
