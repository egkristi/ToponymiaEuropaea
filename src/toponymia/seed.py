"""Seed script: loads JSONL databank into PostgreSQL and exports Parquet snapshots.

Usage:
    python -m toponymia.seed

Environment variables:
    DATABASE_URL: PostgreSQL connection string
    PARQUET_PATH: Output directory for Parquet files (default: /data/parquet)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import psycopg2  # noqa: F401

    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


def load_jsonl_to_postgres(databank_path: Path, database_url: str) -> int:
    """Load JSONL records into the PostgreSQL places table.

    Args:
        databank_path: Path to the databank directory.
        database_url: PostgreSQL connection URL.

    Returns:
        Number of records inserted.
    """
    if not HAS_PSYCOPG2:
        print("psycopg2 not installed, skipping PostgreSQL seed")
        return 0

    import psycopg2

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    count = 0
    places_dir = databank_path / "places"

    if not places_dir.exists():
        print(f"No places directory at {places_dir}")
        return 0

    for jsonl_file in sorted(places_dir.rglob("*.jsonl")):
        print(f"  Loading {jsonl_file.relative_to(databank_path)}...")
        with jsonl_file.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)

                cur.execute(
                    """
                    INSERT INTO places (
                        name, normalized_name, country_code, source,
                        source_id, lat, lon, phonetic_key, h3_index,
                        language_code, feature_class, feature_code,
                        admin1, admin2, metadata
                    ) VALUES (
                        %(name)s, %(normalized_name)s, %(country_code)s, %(source)s,
                        %(source_id)s, %(lat)s, %(lon)s, %(phonetic_key)s, %(h3_index)s,
                        %(language_code)s, %(feature_class)s, %(feature_code)s,
                        %(admin1)s, %(admin2)s, %(metadata)s
                    )
                    ON CONFLICT DO NOTHING
                    """,
                    {
                        "name": record.get("name", ""),
                        "normalized_name": record.get("normalized_name"),
                        "country_code": record.get("country_code", "XX"),
                        "source": record.get("source", "unknown"),
                        "source_id": record.get("source_id"),
                        "lat": record.get("lat"),
                        "lon": record.get("lon"),
                        "phonetic_key": record.get("_phonetic_key"),
                        "h3_index": record.get("_h3_index"),
                        "language_code": record.get("language_code"),
                        "feature_class": record.get("feature_class"),
                        "feature_code": record.get("feature_code"),
                        "admin1": record.get("admin1"),
                        "admin2": record.get("admin2"),
                        "metadata": json.dumps(
                            {
                                k: v
                                for k, v in record.items()
                                if k
                                not in {
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
                            }
                        ),
                    },
                )
                count += 1

    conn.commit()
    cur.close()
    conn.close()
    return count


def export_parquet(databank_path: Path, parquet_path: Path) -> int:
    """Export databank to Parquet format using the analytical layer.

    Args:
        databank_path: Path to the databank directory.
        parquet_path: Output path for Parquet files.

    Returns:
        Total records exported.
    """
    try:
        from toponymia.pipelines.analytical import export_databank_to_parquet
    except ImportError:
        print("DuckDB/PyArrow not available, skipping Parquet export")
        return 0

    results = export_databank_to_parquet(databank_path, parquet_path)
    total = sum(results.values())
    for path, count in results.items():
        print(f"  Exported {path}: {count} records")
    return total


def main() -> None:
    """Run the seed process."""
    database_url = os.environ.get("DATABASE_URL", "")
    parquet_path = Path(os.environ.get("PARQUET_PATH", "/data/parquet"))
    databank_path = Path(os.environ.get("DATABANK_PATH", "/data/databank"))

    # Fallback for local development
    if not databank_path.exists():
        local_databank = Path(__file__).parent.parent.parent / "databank"
        if local_databank.exists():
            databank_path = local_databank

    print("=== Toponymia Europaea Seed ===")
    print(f"  Databank: {databank_path}")
    print(f"  Parquet:  {parquet_path}")
    print()

    # Step 1: Load into PostgreSQL
    if database_url:
        print("[1/2] Loading JSONL → PostgreSQL...")
        pg_count = load_jsonl_to_postgres(databank_path, database_url)
        print(f"  Inserted {pg_count} records into PostgreSQL")
    else:
        print("[1/2] Skipping PostgreSQL (no DATABASE_URL)")

    print()

    # Step 2: Export Parquet snapshots
    print("[2/2] Exporting JSONL → Parquet...")
    pq_count = export_parquet(databank_path, parquet_path)
    print(f"  Exported {pq_count} records to Parquet")

    print()
    print("=== Seed complete ===")


if __name__ == "__main__":
    sys.exit(main() or 0)
