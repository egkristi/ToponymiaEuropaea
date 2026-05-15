"""Parquet/DuckDB analytical layer for Toponymia Europaea.

Provides immutable Parquet snapshots of the databank for efficient
analytical queries using DuckDB. This enables:
- Fast permutation tests on large datasets
- SQL-based spatial and linguistic queries
- Partitioned storage by country and source
- Reproducible analytical snapshots

See issue #23.
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    import duckdb
    import pyarrow as pa
    import pyarrow.parquet as pq

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


def _check_deps() -> None:
    """Raise ImportError if dependencies are missing."""
    if not HAS_DEPS:
        msg = "duckdb and pyarrow are required: uv add duckdb pyarrow"
        raise ImportError(msg)


def jsonl_to_parquet(
    jsonl_path: Path,
    parquet_path: Path,
    *,
    partition_by: str | None = None,
) -> int:
    """Convert a JSONL file to Parquet format.

    Args:
        jsonl_path: Path to source JSONL file.
        parquet_path: Path to output Parquet file.
        partition_by: Optional field to partition by (creates directory structure).

    Returns:
        Number of records written.
    """
    _check_deps()

    records = []
    with jsonl_path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    if not records:
        return 0

    # Normalize records to have consistent columns
    all_keys = set()
    for rec in records:
        all_keys.update(rec.keys())

    # Build columnar data
    columns: dict[str, list] = {key: [] for key in sorted(all_keys)}
    for rec in records:
        for key in sorted(all_keys):
            columns[key].append(rec.get(key))

    table = pa.table(columns)

    if partition_by and partition_by in columns:
        # Write partitioned dataset
        pq.write_to_dataset(
            table,
            root_path=str(parquet_path),
            partition_cols=[partition_by],
        )
    else:
        pq.write_table(table, str(parquet_path))

    return len(records)


def export_databank_to_parquet(
    databank_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, int]:
    """Export the entire databank to Parquet format.

    Creates partitioned Parquet files organized by country code.

    Args:
        databank_path: Path to databank directory (default: project databank/).
        output_path: Path for output Parquet files (default: databank/parquet/).

    Returns:
        Dict mapping source file paths to record counts.
    """
    _check_deps()

    if databank_path is None:
        databank_path = Path(__file__).parent.parent.parent.parent / "databank"

    if output_path is None:
        output_path = databank_path / "parquet"

    output_path.mkdir(parents=True, exist_ok=True)

    results: dict[str, int] = {}
    places_dir = databank_path / "places"

    if not places_dir.exists():
        return results

    for jsonl_file in sorted(places_dir.rglob("*.jsonl")):
        rel_path = jsonl_file.relative_to(databank_path)
        # Create output path preserving directory structure
        parquet_file = output_path / rel_path.with_suffix(".parquet")
        parquet_file.parent.mkdir(parents=True, exist_ok=True)

        count = jsonl_to_parquet(jsonl_file, parquet_file)
        results[str(rel_path)] = count

    return results


def query_parquet(
    parquet_path: Path,
    sql: str,
) -> list[dict]:
    """Execute a DuckDB SQL query against Parquet files.

    Args:
        parquet_path: Path to Parquet file or directory.
        sql: SQL query. Use 'data' as the table name.

    Returns:
        List of result rows as dicts.
    """
    _check_deps()

    con = duckdb.connect(":memory:")

    # Register the parquet file(s) as a view
    path_str = str(parquet_path)
    if parquet_path.is_dir():
        path_str = str(parquet_path / "**" / "*.parquet")

    # Path is constructed internally, not from user input
    con.execute(
        f"CREATE VIEW data AS SELECT * FROM read_parquet('{path_str}')"  # noqa: S608
    )

    cursor = con.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    con.close()

    return [dict(zip(columns, row, strict=True)) for row in rows]


def query_databank(
    sql: str,
    databank_path: Path | None = None,
) -> list[dict]:
    """Query the databank directly from JSONL using DuckDB.

    This reads JSONL files directly without requiring Parquet export.
    Useful for quick queries and development.

    Args:
        sql: SQL query. Use 'databank' as the table name.
        databank_path: Path to databank directory.

    Returns:
        List of result rows as dicts.
    """
    _check_deps()

    if databank_path is None:
        databank_path = Path(__file__).parent.parent.parent.parent / "databank"

    places_dir = databank_path / "places"
    jsonl_pattern = str(places_dir / "**" / "*.jsonl")

    con = duckdb.connect(":memory:")
    # Path is constructed internally, not from user input
    con.execute(
        f"CREATE VIEW databank AS SELECT * FROM read_json_auto('{jsonl_pattern}')"  # noqa: S608
    )

    cursor = con.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    con.close()

    return [dict(zip(columns, row, strict=True)) for row in rows]
