"""Validation tooling for the gold-standard kernel records."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

KERNEL_DIR = Path(__file__).parent.parent.parent.parent / "databank" / "kernel"
CRITERIA_FILE = KERNEL_DIR / "criteria.json"
GOLD_FILE = KERNEL_DIR / "gold.jsonl"

REQUIRED_FIELDS = [
    "name_form",
    "latitude",
    "longitude",
    "source_id",
    "language_code",
    "verified_by",
    "verified_date",
    "etymology",
    "segmentation",
    "sources",
]

ETYMOLOGY_REQUIRED = ["lemma", "meaning", "language_code"]
SEGMENTATION_ITEM_REQUIRED = ["component", "morph_type", "meaning"]


@dataclass
class KernelValidationError:
    """A single validation error in a kernel record."""

    line: int
    field: str
    message: str


@dataclass
class KernelValidationResult:
    """Result of validating the kernel."""

    total_records: int = 0
    valid_records: int = 0
    errors: list[KernelValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def validate_kernel(gold_file: Path | None = None) -> KernelValidationResult:
    """Validate all records in the gold-standard kernel file.

    Args:
        gold_file: Path to the gold.jsonl file. Defaults to the
                   standard location in databank/kernel/.

    Returns:
        KernelValidationResult with errors (if any).
    """
    if gold_file is None:
        gold_file = GOLD_FILE

    result = KernelValidationResult()

    if not gold_file.exists():
        result.errors.append(
            KernelValidationError(
                line=0, field="file", message=f"Kernel file not found: {gold_file}"
            )
        )
        return result

    with gold_file.open() as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            result.total_records += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                result.errors.append(
                    KernelValidationError(line=line_num, field="json", message=f"Invalid JSON: {e}")
                )
                continue

            errors = _validate_record(record, line_num)
            if errors:
                result.errors.extend(errors)
            else:
                result.valid_records += 1

    return result


def _validate_record(record: dict, line_num: int) -> list[KernelValidationError]:
    """Validate a single kernel record."""
    errors: list[KernelValidationError] = []

    # Check required top-level fields
    for field_name in REQUIRED_FIELDS:
        if field_name not in record:
            errors.append(
                KernelValidationError(
                    line=line_num,
                    field=field_name,
                    message=f"Missing required field: {field_name}",
                )
            )

    # Validate coordinates
    lat = record.get("latitude")
    lon = record.get("longitude")
    if isinstance(lat, (int, float)) and not (-90 <= lat <= 90):
        errors.append(
            KernelValidationError(
                line=line_num,
                field="latitude",
                message=f"Latitude out of range: {lat}",
            )
        )
    if isinstance(lon, (int, float)) and not (-180 <= lon <= 180):
        errors.append(
            KernelValidationError(
                line=line_num,
                field="longitude",
                message=f"Longitude out of range: {lon}",
            )
        )

    # Validate etymology object
    etymology = record.get("etymology")
    if isinstance(etymology, dict):
        for ety_field in ETYMOLOGY_REQUIRED:
            if ety_field not in etymology:
                errors.append(
                    KernelValidationError(
                        line=line_num,
                        field=f"etymology.{ety_field}",
                        message=f"Missing etymology field: {ety_field}",
                    )
                )

    # Validate segmentation array
    segmentation = record.get("segmentation")
    if isinstance(segmentation, list):
        if len(segmentation) == 0:
            errors.append(
                KernelValidationError(
                    line=line_num,
                    field="segmentation",
                    message="Segmentation array must not be empty",
                )
            )
        for i, seg in enumerate(segmentation):
            if isinstance(seg, dict):
                for seg_field in SEGMENTATION_ITEM_REQUIRED:
                    if seg_field not in seg:
                        errors.append(
                            KernelValidationError(
                                line=line_num,
                                field=f"segmentation[{i}].{seg_field}",
                                message=f"Missing segmentation field: {seg_field}",
                            )
                        )

    # Validate sources
    sources = record.get("sources")
    if isinstance(sources, list) and len(sources) == 0:
        errors.append(
            KernelValidationError(
                line=line_num,
                field="sources",
                message="Sources array must not be empty",
            )
        )

    # Validate language_code format (ISO 639-3: 3 lowercase letters)
    lang = record.get("language_code")
    if isinstance(lang, str) and (len(lang) != 3 or not lang.isalpha() or not lang.islower()):
        errors.append(
            KernelValidationError(
                line=line_num,
                field="language_code",
                message=f"Invalid ISO 639-3 code: {lang}",
            )
        )

    return errors
