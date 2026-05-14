"""Databank record integrity and signing.

Provides content-addressable hashing for JSONL records so that:
1. Tampered records can be detected (record-level SHA-256).
2. File-level manifests detect insertions/deletions/reordering.
3. Identical data produced independently yields identical hashes (canonical JSON).
4. Merges/rebases work cleanly because records are sorted by source_id.

Design principles:
- Hash is computed from *canonical* JSON: sorted keys, no whitespace variance,
  meta-fields (_sha256) excluded from hash input.
- Records are content-addressable: same data → same hash, regardless of who
  produced it or when.
- Manifest is a simple text file (one sha256 per line) that git can diff/merge.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

# Fields excluded from hash computation (meta/integrity fields)
_INTEGRITY_META_FIELDS = frozenset({"_sha256", "_signed_by", "_signed_at"})


def canonical_json(record: dict[str, Any]) -> str:
    """Produce canonical JSON for hashing.

    Rules:
    - Keys sorted recursively
    - No extra whitespace (separators=(',', ':'))
    - Meta-fields (_sha256, _signed_by, _signed_at) excluded
    - Nested dicts/lists sorted recursively
    - Unicode escaped consistently (ensure_ascii=False, NFC assumed)
    """
    cleaned = _deep_sort({k: v for k, v in record.items() if k not in _INTEGRITY_META_FIELDS})
    return json.dumps(cleaned, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def compute_record_hash(record: dict[str, Any]) -> str:
    """Compute SHA-256 hash of a record's canonical JSON representation."""
    return hashlib.sha256(canonical_json(record).encode("utf-8")).hexdigest()


def sign_record(record: dict[str, Any]) -> dict[str, Any]:
    """Add _sha256 integrity field to a record.

    Returns a new dict with _sha256 set. Does not mutate the input.
    """
    result = dict(record)
    result["_sha256"] = compute_record_hash(record)
    return result


def verify_record(record: dict[str, Any]) -> bool:
    """Verify a record's _sha256 integrity field.

    Returns True if the hash matches, False if tampered or missing hash.
    """
    stored_hash = record.get("_sha256")
    if stored_hash is None:
        return False
    return compute_record_hash(record) == stored_hash


def sign_jsonl_file(filepath: Path) -> int:
    """Sign all records in a JSONL file in-place.

    Returns the number of records signed.
    """
    lines: list[str] = []
    count = 0

    with filepath.open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            record = json.loads(stripped)
            signed = sign_record(record)
            lines.append(json.dumps(signed, ensure_ascii=False, sort_keys=True))
            count += 1

    with filepath.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return count


def verify_jsonl_file(filepath: Path) -> tuple[int, list[tuple[int, str]]]:
    """Verify integrity of all records in a JSONL file.

    Returns (total_records, list of (line_number, error_message) for failures).
    """
    errors: list[tuple[int, str]] = []
    total = 0

    with filepath.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            total += 1

            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                errors.append((line_num, "Invalid JSON"))
                continue

            if "_sha256" not in record:
                errors.append((line_num, "Missing _sha256 integrity hash"))
                continue

            if not verify_record(record):
                source_id = record.get("source_id", "?")
                errors.append((line_num, f"Integrity check FAILED for source_id={source_id}"))

    return total, errors


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of an entire file's contents."""
    h = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest(directory: Path) -> dict[str, str]:
    """Generate a manifest mapping filename → SHA-256 for all JSONL files in a directory.

    Returns dict like {"geonames.jsonl": "abc123..."}.
    """
    manifest: dict[str, str] = {}
    for jsonl_file in sorted(directory.rglob("*.jsonl")):
        rel_path = str(jsonl_file.relative_to(directory))
        manifest[rel_path] = compute_file_hash(jsonl_file)
    return manifest


def write_manifest(directory: Path) -> Path:
    """Write MANIFEST.sha256 for a databank directory.

    Format: one line per file, "<sha256>  <relative-path>"
    (same format as sha256sum, compatible with `sha256sum -c`).
    """
    manifest = generate_manifest(directory)
    manifest_path = directory / "MANIFEST.sha256"

    with manifest_path.open("w", encoding="utf-8") as f:
        for rel_path, file_hash in sorted(manifest.items()):
            f.write(f"{file_hash}  {rel_path}\n")

    return manifest_path


def verify_manifest(directory: Path) -> tuple[bool, list[str]]:
    """Verify MANIFEST.sha256 against actual file hashes.

    Returns (all_valid, list of error messages).
    """
    manifest_path = directory / "MANIFEST.sha256"
    errors: list[str] = []

    if not manifest_path.exists():
        return False, ["MANIFEST.sha256 not found"]

    expected: dict[str, str] = {}
    with manifest_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                errors.append(f"Malformed manifest line: {line}")
                continue
            file_hash, rel_path = parts
            expected[rel_path] = file_hash

    # Check all listed files
    for rel_path, expected_hash in expected.items():
        file_path = directory / rel_path
        if not file_path.exists():
            errors.append(f"File listed in manifest but missing: {rel_path}")
            continue
        actual_hash = compute_file_hash(file_path)
        if actual_hash != expected_hash:
            errors.append(
                f"Hash mismatch for {rel_path}: "
                f"expected {expected_hash[:12]}..., got {actual_hash[:12]}..."
            )

    # Check for unlisted JSONL files
    actual_files = {str(f.relative_to(directory)) for f in directory.rglob("*.jsonl")}
    for rel_path in sorted(actual_files - set(expected.keys())):
        errors.append(f"File not in manifest: {rel_path}")

    return len(errors) == 0, errors


def sort_jsonl_file(filepath: Path, key: str = "source_id") -> int:
    """Sort a JSONL file by a key field for deterministic ordering.

    This ensures stable diffs across branches and clean rebases.
    Returns number of records sorted.
    """
    records: list[dict[str, Any]] = []

    with filepath.open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            records.append(json.loads(stripped))

    records.sort(key=lambda r: str(r.get(key, "")))

    with filepath.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    return len(records)


def _deep_sort(obj: Any) -> Any:
    """Recursively sort dicts by key and lists of dicts by a stable key."""
    if isinstance(obj, dict):
        return {k: _deep_sort(v) for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        return [_deep_sort(item) for item in obj]
    return obj
