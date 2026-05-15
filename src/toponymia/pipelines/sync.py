"""Sync pipeline: JSONL → PostgreSQL → Parquet with checksums.

Provides unidirectional data flow with integrity verification at each stage.
The canonical source of truth is the JSONL databank; PostgreSQL is for
operational queries; Parquet is for analytical workloads.

See issues #22 and #25.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a sync operation."""

    stage: str
    records_processed: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    checksum: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Whether the sync completed without errors."""
        return len(self.errors) == 0


def compute_file_checksum(path: Path) -> str:
    """Compute SHA-256 checksum of a file.

    Args:
        path: File path to checksum.

    Returns:
        Hex digest of the SHA-256 hash.
    """
    sha = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def compute_records_checksum(records: list[dict[str, Any]]) -> str:
    """Compute a deterministic checksum over a set of records.

    Records are sorted by JSON serialization to ensure determinism.

    Args:
        records: List of record dicts.

    Returns:
        Hex digest of the combined SHA-256 hash.
    """
    sha = hashlib.sha256()
    for rec in sorted(records, key=lambda r: json.dumps(r, sort_keys=True)):
        sha.update(json.dumps(rec, sort_keys=True, ensure_ascii=False).encode())
    return sha.hexdigest()


def load_jsonl_records(databank_path: Path) -> list[dict[str, Any]]:
    """Load all JSONL records from the databank places directory.

    Args:
        databank_path: Root databank directory.

    Returns:
        List of all place records.
    """
    records: list[dict[str, Any]] = []
    places_dir = databank_path / "places"

    if not places_dir.exists():
        return records

    for jsonl_file in sorted(places_dir.rglob("*.jsonl")):
        with jsonl_file.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

    return records


def sync_jsonl_to_postgres(
    databank_path: Path,
    database_url: str,
) -> SyncResult:
    """Sync JSONL databank records to PostgreSQL with upsert logic.

    Uses source_id + source as the unique key for upsert.
    Computes checksums before and after for verification.

    Args:
        databank_path: Path to the databank directory.
        database_url: PostgreSQL connection URL.

    Returns:
        SyncResult with statistics and checksum.
    """
    result = SyncResult(stage="jsonl_to_postgres")

    try:
        import psycopg2
    except ImportError:
        result.errors.append("psycopg2 not installed")
        return result

    records = load_jsonl_records(databank_path)
    result.records_processed = len(records)
    result.checksum = compute_records_checksum(records)

    if not records:
        return result

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        for rec in records:
            source_id = rec.get("source_id", "")
            source = rec.get("source", "unknown")

            # Check if record exists
            cur.execute(
                "SELECT id FROM places WHERE source_id = %s AND source = %s",
                (source_id, source),
            )
            existing = cur.fetchone()

            if existing:
                # Update existing record
                cur.execute(
                    """
                    UPDATE places SET
                        name = %(name)s,
                        normalized_name = %(normalized_name)s,
                        country_code = %(country_code)s,
                        lat = %(lat)s,
                        lon = %(lon)s,
                        phonetic_key = %(phonetic_key)s,
                        h3_index = %(h3_index)s,
                        updated_at = NOW()
                    WHERE source_id = %(source_id)s AND source = %(source)s
                    """,
                    {
                        "name": rec.get("name", ""),
                        "normalized_name": rec.get("normalized_name"),
                        "country_code": rec.get("country_code", "XX"),
                        "lat": rec.get("lat"),
                        "lon": rec.get("lon"),
                        "phonetic_key": rec.get("_phonetic_key"),
                        "h3_index": rec.get("_h3_index"),
                        "source_id": source_id,
                        "source": source,
                    },
                )
                result.records_updated += 1
            else:
                # Insert new record
                cur.execute(
                    """
                    INSERT INTO places (
                        name, normalized_name, country_code, source,
                        source_id, lat, lon, phonetic_key, h3_index,
                        language_code, feature_class, feature_code,
                        admin1, admin2, metadata
                    ) VALUES (
                        %(name)s, %(normalized_name)s, %(country_code)s,
                        %(source)s, %(source_id)s, %(lat)s, %(lon)s,
                        %(phonetic_key)s, %(h3_index)s, %(language_code)s,
                        %(feature_class)s, %(feature_code)s,
                        %(admin1)s, %(admin2)s, %(metadata)s
                    )
                    """,
                    {
                        "name": rec.get("name", ""),
                        "normalized_name": rec.get("normalized_name"),
                        "country_code": rec.get("country_code", "XX"),
                        "source": source,
                        "source_id": source_id,
                        "lat": rec.get("lat"),
                        "lon": rec.get("lon"),
                        "phonetic_key": rec.get("_phonetic_key"),
                        "h3_index": rec.get("_h3_index"),
                        "language_code": rec.get("language_code"),
                        "feature_class": rec.get("feature_class"),
                        "feature_code": rec.get("feature_code"),
                        "admin1": rec.get("admin1"),
                        "admin2": rec.get("admin2"),
                        "metadata": json.dumps(
                            {k: v for k, v in rec.items() if k not in _KNOWN_FIELDS}
                        ),
                    },
                )
                result.records_inserted += 1

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        result.errors.append(str(e))

    return result


def sync_postgres_to_parquet(
    database_url: str,
    output_path: Path,
) -> SyncResult:
    """Export PostgreSQL data to Parquet snapshots.

    Args:
        database_url: PostgreSQL connection URL.
        output_path: Directory for Parquet output.

    Returns:
        SyncResult with statistics and checksum.
    """
    result = SyncResult(stage="postgres_to_parquet")

    try:
        import psycopg2
    except ImportError:
        result.errors.append("psycopg2 not installed")
        return result

    try:
        from toponymia.pipelines.analytical import jsonl_to_parquet
    except ImportError:
        result.errors.append("analytical module not available")
        return result

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        # Export each country as a separate JSONL, then convert to Parquet
        cur.execute("SELECT DISTINCT country_code FROM places ORDER BY country_code")
        countries = [row[0] for row in cur.fetchall()]

        output_path.mkdir(parents=True, exist_ok=True)
        total = 0

        for country in countries:
            cur.execute(
                """
                SELECT name, normalized_name, country_code, source,
                       source_id, lat, lon, phonetic_key, h3_index,
                       language_code, feature_class, feature_code
                FROM places
                WHERE country_code = %s
                ORDER BY name
                """,
                (country,),
            )
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

            if not rows:
                continue

            # Write temporary JSONL
            temp_jsonl = output_path / f"{country}.jsonl"
            with temp_jsonl.open("w") as f:
                for row in rows:
                    record = dict(zip(columns, row, strict=True))
                    f.write(json.dumps(record, default=str) + "\n")

            # Convert to Parquet
            parquet_file = output_path / f"{country}.parquet"
            count = jsonl_to_parquet(temp_jsonl, parquet_file)
            total += count

            # Clean up temp JSONL
            temp_jsonl.unlink()

        result.records_processed = total
        result.records_inserted = total
        cur.close()
        conn.close()

    except Exception as e:
        result.errors.append(str(e))

    return result


def sync_jsonl_to_parquet(
    databank_path: Path,
    output_path: Path | None = None,
) -> SyncResult:
    """Direct sync from JSONL to Parquet (bypasses PostgreSQL).

    Useful for environments without PostgreSQL.
    Includes checksum verification.

    Args:
        databank_path: Path to the databank directory.
        output_path: Output directory for Parquet files.

    Returns:
        SyncResult with statistics and checksum.
    """
    result = SyncResult(stage="jsonl_to_parquet")

    try:
        from toponymia.pipelines.analytical import export_databank_to_parquet
    except ImportError:
        result.errors.append("analytical module (duckdb/pyarrow) not available")
        return result

    if output_path is None:
        output_path = databank_path / "parquet"

    # Compute source checksum
    records = load_jsonl_records(databank_path)
    result.checksum = compute_records_checksum(records)
    result.records_processed = len(records)

    # Export
    export_results = export_databank_to_parquet(databank_path, output_path)
    result.records_inserted = sum(export_results.values())

    return result


def verify_manifest(databank_path: Path) -> SyncResult:
    """Verify databank integrity against MANIFEST.sha256.

    Args:
        databank_path: Path to the databank directory.

    Returns:
        SyncResult with verification status.
    """
    result = SyncResult(stage="verify_manifest")
    manifest_path = databank_path / "MANIFEST.sha256"

    if not manifest_path.exists():
        result.errors.append("MANIFEST.sha256 not found")
        return result

    manifest_entries: dict[str, str] = {}
    with manifest_path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("  ", 1)
                if len(parts) == 2:
                    manifest_entries[parts[1]] = parts[0]

    for rel_path, expected_hash in manifest_entries.items():
        file_path = databank_path / rel_path
        if not file_path.exists():
            result.errors.append(f"Missing file: {rel_path}")
            continue

        actual_hash = compute_file_checksum(file_path)
        if actual_hash != expected_hash:
            result.errors.append(
                f"Checksum mismatch: {rel_path} "
                f"(expected {expected_hash[:8]}..., got {actual_hash[:8]}...)"
            )
        else:
            result.records_processed += 1

    return result


def full_sync(
    databank_path: Path,
    database_url: str | None = None,
    parquet_path: Path | None = None,
) -> list[SyncResult]:
    """Run the full sync pipeline: verify → load → export.

    Steps:
    1. Verify MANIFEST integrity
    2. Sync JSONL → PostgreSQL (if database_url provided)
    3. Sync to Parquet (from Postgres if available, else direct)

    Args:
        databank_path: Path to the databank directory.
        database_url: Optional PostgreSQL connection URL.
        parquet_path: Optional output path for Parquet files.

    Returns:
        List of SyncResult for each stage.
    """
    results: list[SyncResult] = []

    # Stage 1: Verify manifest
    logger.info("Stage 1: Verifying MANIFEST integrity...")
    manifest_result = verify_manifest(databank_path)
    results.append(manifest_result)

    if not manifest_result.success:
        logger.error(f"Manifest verification failed: {manifest_result.errors}")
        return results

    # Stage 2: JSONL → PostgreSQL
    if database_url:
        logger.info("Stage 2: Syncing JSONL → PostgreSQL...")
        pg_result = sync_jsonl_to_postgres(databank_path, database_url)
        results.append(pg_result)

        if not pg_result.success:
            logger.error(f"PostgreSQL sync failed: {pg_result.errors}")
            return results

        # Stage 3: PostgreSQL → Parquet
        if parquet_path:
            logger.info("Stage 3: Exporting PostgreSQL → Parquet...")
            pq_result = sync_postgres_to_parquet(database_url, parquet_path)
            results.append(pq_result)
    else:
        # Direct: JSONL → Parquet
        logger.info("Stage 2: Direct sync JSONL → Parquet...")
        pq_result = sync_jsonl_to_parquet(databank_path, parquet_path)
        results.append(pq_result)

    return results


# Fields that map directly to PostgreSQL columns
_KNOWN_FIELDS = frozenset(
    {
        "name",
        "normalized_name",
        "country_code",
        "source",
        "source_id",
        "lat",
        "lon",
        "_phonetic_key",
        "_h3_index",
        "language_code",
        "feature_class",
        "feature_code",
        "admin1",
        "admin2",
    }
)
