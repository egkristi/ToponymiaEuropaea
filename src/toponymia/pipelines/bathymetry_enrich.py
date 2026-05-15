#!/usr/bin/env python3
"""Enrich hydrological databank records with bathymetry (depth) data.

Iterates over all place records in the databank and, for hydrological
features eligible for depth data, queries bathymetry sources to add:
  - _depth_m: maximum/spot depth in meters
  - _depth_mean_m: mean depth (where available, e.g. NVE lakes)
  - _depth_source: data provenance ("gebco", "emodnet", "nve")
  - _depth_resolution_m: spatial resolution of the measurement

Only features with specific hydrological place_types are processed
(lakes, fjords, bays, straits, etc.).

Usage:
    python -m toponymia.pipelines.bathymetry_enrich [--dry-run] [--limit N]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from toponymia.connectors.bathymetry import (
    DEPTH_ELIGIBLE_TYPES,
    BathymetryConnector,
)

logger = logging.getLogger(__name__)

DATABANK_DIR = Path(__file__).resolve().parent.parent.parent.parent / "databank"


def enrich_record(
    record: dict,
    connector: BathymetryConnector,
) -> bool:
    """Enrich a single record with depth data.

    Returns True if depth data was added/updated, False otherwise.
    """
    place_type = record.get("place_type", "")
    if place_type not in DEPTH_ELIGIBLE_TYPES:
        return False

    lat = record.get("latitude")
    lon = record.get("longitude")
    if lat is None or lon is None:
        return False

    # Skip if already has depth data from same source
    if record.get("_depth_m") is not None and record.get("_depth_source"):
        return False

    country_code = record.get("country_code", "")
    result = connector.get_depth(lat, lon, place_type=place_type, country_code=country_code)

    if result is None:
        return False

    record["_depth_m"] = result.depth_m
    if result.depth_mean_m is not None:
        record["_depth_mean_m"] = result.depth_mean_m
    if result.depth_max_m is not None:
        record["_depth_max_m"] = result.depth_max_m
    record["_depth_source"] = result.source
    if result.resolution_m is not None:
        record["_depth_resolution_m"] = result.resolution_m

    return True


def process_file(
    jsonl_path: Path,
    connector: BathymetryConnector,
    *,
    dry_run: bool = False,
    limit: int | None = None,
) -> dict:
    """Process a single JSONL file, enriching eligible records.

    Returns stats dict with counts.
    """
    records: list[dict] = []
    eligible = 0
    enriched = 0
    skipped_existing = 0
    errors = 0

    with jsonl_path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    processed = 0
    for record in records:
        place_type = record.get("place_type", "")
        if place_type not in DEPTH_ELIGIBLE_TYPES:
            continue

        eligible += 1

        # Already has depth data
        if record.get("_depth_m") is not None:
            skipped_existing += 1
            continue

        if limit is not None and processed >= limit:
            continue

        processed += 1

        if dry_run:
            continue

        try:
            if enrich_record(record, connector):
                enriched += 1
        except Exception as exc:
            errors += 1
            logger.warning(
                "Error enriching %s: %s",
                record.get("name_form", "?"),
                exc,
            )

    if not dry_run and enriched > 0:
        with jsonl_path.open("w") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "total": len(records),
        "eligible": eligible,
        "enriched": enriched,
        "skipped_existing": skipped_existing,
        "errors": errors,
    }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enrich hydrological records with bathymetry depth data"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report eligible records without making API calls",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of API calls per file (for testing)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP request timeout in seconds",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    places_dir = DATABANK_DIR / "places"
    if not places_dir.exists():
        logger.error("No databank/places directory found at %s", places_dir)
        sys.exit(1)

    connector = BathymetryConnector(timeout=args.timeout)

    print(f"Mode:        {'DRY RUN' if args.dry_run else 'ENRICH'}")
    print(f"Databank:    {places_dir}")
    if args.limit:
        print(f"Limit:       {args.limit} API calls per file")
    print("-" * 60)

    total_stats = {
        "total": 0,
        "eligible": 0,
        "enriched": 0,
        "skipped_existing": 0,
        "errors": 0,
    }

    jsonl_files = sorted(places_dir.rglob("*.jsonl"))
    for jsonl_path in jsonl_files:
        rel_path = jsonl_path.relative_to(DATABANK_DIR)
        stats = process_file(jsonl_path, connector, dry_run=args.dry_run, limit=args.limit)

        print(
            f"  {rel_path}: {stats['total']} records, "
            f"{stats['eligible']} eligible, "
            f"{stats['enriched']} enriched, "
            f"{stats['skipped_existing']} already had depth"
        )

        for key in total_stats:
            total_stats[key] += stats[key]

    print("-" * 60)
    print(f"TOTAL        {total_stats['total']} records")
    print(f"  Eligible:   {total_stats['eligible']} hydrological features")
    print(f"  Enriched:   {total_stats['enriched']} (depth data added)")
    print(f"  Existing:   {total_stats['skipped_existing']} (already had depth)")
    print(f"  Errors:     {total_stats['errors']}")

    if args.dry_run:
        print("\n(Dry run — no API calls were made)")


if __name__ == "__main__":
    main()
