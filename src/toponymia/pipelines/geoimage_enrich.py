#!/usr/bin/env python3
"""Enrich databank records with links to geolocated images.

Iterates over all place records in the databank and queries Wikimedia
Commons for nearby geotagged photographs.  Adds an _image_links field
containing structured image references that can be presented to users.

Fields added:
  - _image_links: list of image objects with title, page_url, thumb_url, license, distance_m

Usage:
    python -m toponymia.pipelines.geoimage_enrich [--dry-run] [--limit N] [--radius M]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from toponymia.connectors.geoimage import GeoImageConnector

logger = logging.getLogger(__name__)

DATABANK_DIR = Path(__file__).resolve().parent.parent.parent.parent / "databank"


def enrich_record(
    record: dict,
    connector: GeoImageConnector,
) -> bool:
    """Enrich a single record with geolocated image links.

    Returns True if image links were added, False otherwise.
    """
    lat = record.get("latitude")
    lon = record.get("longitude")
    if lat is None or lon is None:
        return False

    # Skip if already has image links
    if record.get("_image_links"):
        return False

    result = connector.get_images(lat, lon)
    if result is None or not result.images:
        return False

    record["_image_links"] = [
        {
            "title": img.title,
            "page_url": img.page_url,
            "thumb_url": img.thumb_url,
            "license": img.license,
            "distance_m": img.distance_m,
            "source": img.source,
        }
        for img in result.images
    ]
    return True


def process_file(
    jsonl_path: Path,
    connector: GeoImageConnector,
    *,
    dry_run: bool = False,
    limit: int | None = None,
) -> dict:
    """Process a single JSONL file, enriching records with image links.

    Returns stats dict with counts.
    """
    records: list[dict] = []
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
        # Already has image links
        if record.get("_image_links"):
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
                f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    return {
        "total": len(records),
        "enriched": enriched,
        "skipped_existing": skipped_existing,
        "errors": errors,
    }


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Enrich place records with geolocated image links")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report counts without making API calls",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of API calls per file (for testing)",
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=1000,
        help="Search radius in meters (default: 1000)",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=5,
        help="Maximum images per location (default: 5)",
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

    connector = GeoImageConnector(
        timeout=args.timeout,
        radius_m=args.radius,
        max_images=args.max_images,
    )

    print(f"Mode:        {'DRY RUN' if args.dry_run else 'ENRICH'}")
    print(f"Databank:    {places_dir}")
    print(f"Radius:      {args.radius}m")
    print(f"Max images:  {args.max_images}")
    if args.limit:
        print(f"Limit:       {args.limit} API calls per file")
    print("-" * 60)

    total_stats = {
        "total": 0,
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
            f"{stats['enriched']} enriched, "
            f"{stats['skipped_existing']} already had images"
        )

        for key in total_stats:
            total_stats[key] += stats[key]

    print("-" * 60)
    print(f"TOTAL        {total_stats['total']} records")
    print(f"  Enriched:   {total_stats['enriched']} (image links added)")
    print(f"  Existing:   {total_stats['skipped_existing']} (already had images)")
    print(f"  Errors:     {total_stats['errors']}")


if __name__ == "__main__":
    main()
