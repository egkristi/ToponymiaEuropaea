#!/usr/bin/env python3
"""Build static JSON data files from the databank for GitHub Pages."""

import json
import os
from collections import Counter
from pathlib import Path

DATABANK_DIR = Path(__file__).resolve().parent.parent / "databank"
OUTPUT_DIR = Path(__file__).resolve().parent / "data"

# Fields to include in the static places JSON (strip internal _-prefixed fields)
PLACE_FIELDS = [
    "name_form",
    "name_normalized",
    "country_code",
    "place_type",
    "language_code",
    "latitude",
    "longitude",
    "elevation",
    "_depth_m",
    "source_id",
    "source_url",
    "alternative_names",
    "is_current",
    "geometry",
]


def load_places() -> tuple[list[dict], list[dict]]:
    """Load all place records from the databank JSONL files.

    Returns (lightweight_places, full_places) where lightweight contains
    only display fields + id, and full contains all fields.
    """
    places = []
    places_full = []
    places_dir = DATABANK_DIR / "places"
    if not places_dir.exists():
        return places, places_full

    for country_dir in sorted(places_dir.iterdir()):
        if not country_dir.is_dir():
            continue
        country_code = country_dir.name
        for jsonl_file in sorted(country_dir.glob("*.jsonl")):
            with jsonl_file.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    # Add country_code from directory structure if not present
                    if "country_code" not in record:
                        record["country_code"] = country_code
                    # Use _sha256 as stable unique ID
                    place_id = record.get("_sha256", "")
                    # Keep only display-relevant fields + id
                    place = {"id": place_id}
                    place.update(
                        {k: record[k] for k in PLACE_FIELDS if k in record}
                    )
                    places.append(place)
                    # Full record with all fields (rename _sha256 to id)
                    full = {"id": place_id}
                    full.update(
                        {k: v for k, v in record.items() if k != "_sha256"}
                    )
                    places_full.append(full)
    return places, places_full


def load_sources() -> list[dict]:
    """Load sources from sources.jsonl."""
    sources = []
    sources_file = DATABANK_DIR / "sources.jsonl"
    if not sources_file.exists():
        return sources
    with sources_file.open() as f:
        for line in f:
            line = line.strip()
            if line:
                sources.append(json.loads(line))
    return sources


def compute_stats(places: list[dict], sources: list[dict]) -> dict:
    """Compute summary statistics for the dashboard."""
    by_country: Counter = Counter()
    by_source: Counter = Counter()
    by_type: Counter = Counter()

    for p in places:
        cc = p.get("country_code", "??")
        by_country[cc] += 1
        src = p.get("source_id", "unknown")
        by_source[src] += 1
        pt = p.get("place_type", "unknown")
        # Group by first letter (P., H., T., etc.)
        type_group = pt[:2] if pt and len(pt) >= 2 else "other"
        by_type[type_group] += 1

    return {
        "total_places": len(places),
        "by_country": dict(by_country.most_common()),
        "by_source": dict(by_source.most_common()),
        "by_type": dict(by_type.most_common()),
        "sources_count": len(sources),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading places...")
    places, places_full = load_places()
    print(f"  {len(places)} records loaded")

    print("Loading sources...")
    sources = load_sources()
    print(f"  {len(sources)} sources loaded")

    print("Computing stats...")
    stats = compute_stats(places, sources)

    # Write places.json (compact, no extra whitespace)
    places_path = OUTPUT_DIR / "places.json"
    with places_path.open("w") as f:
        json.dump(places, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = places_path.stat().st_size / 1024
    print(f"  {places_path} ({size_kb:.0f} KB)")

    # Write places_full.json (all fields for detail page)
    places_full_path = OUTPUT_DIR / "places_full.json"
    with places_full_path.open("w") as f:
        json.dump(places_full, f, ensure_ascii=False, separators=(",", ":"))
    size_kb_full = places_full_path.stat().st_size / 1024
    print(f"  {places_full_path} ({size_kb_full:.0f} KB)")

    # Write stats.json
    stats_path = OUTPUT_DIR / "stats.json"
    with stats_path.open("w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"  {stats_path}")

    # Write sources.json
    sources_path = OUTPUT_DIR / "sources.json"
    with sources_path.open("w") as f:
        json.dump(sources, f, ensure_ascii=False, indent=2)
    print(f"  {sources_path}")

    print("Done.")


if __name__ == "__main__":
    main()
