#!/usr/bin/env python3
"""Ingest GeoNames data for the British Isles.

Downloads and processes GeoNames dump files for Great Britain (GB),
Ireland (IE), and Isle of Man (IM). Filters to features of toponymic
interest with emphasis on Celtic-language place names.

Target: ~10,000–12,000 records total across 3 countries.

Usage:
    uv run python scripts/ingest_british_isles_geonames.py
"""

import contextlib
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from toponymia.connectors.geonames import GeoNamesConnector  # noqa: E402
from toponymia.pipelines.geometry_classify import (  # noqa: E402
    classify_geometry,
    get_geometry_status,
)
from toponymia.pipelines.integrity import sign_record  # noqa: E402

DATABANK_DIR = ROOT / "databank"

# GeoNames TSV column indices
_GEONAME_ID = 0
_NAME = 1
_ASCIINAME = 2
_ALTERNATENAMES = 3
_LATITUDE = 4
_LONGITUDE = 5
_FEATURE_CLASS = 6
_FEATURE_CODE = 7
_COUNTRY_CODE = 8
_POPULATION = 14
_ELEVATION = 15
_DEM = 16

# Countries to ingest with their default language codes
COUNTRIES = {
    "GB": "eng",
    "IE": "eng",
    "IM": "eng",
}

# Feature class/code filters
STANDARD_P_CODES = None  # All P.* subtypes
STANDARD_T_CODES = None  # All T.* subtypes
STANDARD_H_CODES = {"STM", "LK", "RSVR", "RVR", "BAY", "COVE", "FJD", "ESTRY"}
STANDARD_S_CODES = {"FRM", "CSTL", "CH", "MNST", "RSTN", "AIRP", "HSE", "MN", "BLDG", "ANS"}
STANDARD_L_CODES = {"RGN", "AREA", "PRK", "RESN", "CONT", "LCTY"}

# Per-country caps
COUNTRY_CAPS = {
    "GB": {"p_cap": 4000, "t_cap": 2000, "other_cap": 1000},
    "IE": {"p_cap": 2000, "t_cap": 1000, "other_cap": 500},
    "IM": {"p_cap": 500, "t_cap": 200, "other_cap": 100},
}


def parse_elevation(row: list[str]) -> float | None:
    """Parse elevation from DEM or elevation field."""
    elevation = None
    if row[_DEM] and row[_DEM] != "":
        with contextlib.suppress(ValueError):
            elevation = float(row[_DEM])
    if elevation is None and row[_ELEVATION] and row[_ELEVATION] != "":
        with contextlib.suppress(ValueError):
            elevation = float(row[_ELEVATION])
    return elevation


def parse_alt_names(raw: str, lang: str) -> dict[str, list[str]]:
    """Parse alternative names from GeoNames comma-separated field."""
    alt_names: dict[str, list[str]] = {}
    if raw:
        for alt in raw.split(","):
            alt = alt.strip()
            if alt:
                alt_names.setdefault(lang, []).append(alt)
    return alt_names


def make_record(row: list[str], lang: str, country_code: str) -> dict:
    """Create a signed place record from a raw GeoNames TSV row."""
    place_type = f"{row[_FEATURE_CLASS]}.{row[_FEATURE_CODE]}"
    geo_class = classify_geometry(place_type)
    alt_names = parse_alt_names(row[_ALTERNATENAMES], lang)

    record = {
        "name_form": row[_NAME],
        "name_normalized": row[_ASCIINAME] or row[_NAME],
        "latitude": float(row[_LATITUDE]),
        "longitude": float(row[_LONGITUDE]),
        "source_id": row[_GEONAME_ID],
        "source_dataset": "geonames",
        "source_license": "CC-BY-4.0",
        "source_url": f"https://www.geonames.org/{row[_GEONAME_ID]}",
        "country_code": country_code,
        "language_code": lang,
        "place_type": place_type,
        "is_current": True,
        "alternative_names": alt_names,
        "_geometry_class": geo_class,
        "_geometry_status": get_geometry_status(geo_class, None),
        "_phonetic_key": row[_NAME].lower().strip(),
    }

    elevation = parse_elevation(row)
    if elevation is not None:
        record["elevation"] = elevation

    geonames_id = int(row[_GEONAME_ID])
    if geonames_id:
        record["geonames_id"] = geonames_id

    return sign_record(record)


def should_include_non_p(feature_class: str, feature_code: str) -> bool:
    """Check if a non-P/non-T feature should be included."""
    if feature_class == "H":
        return feature_code in STANDARD_H_CODES
    if feature_class == "S":
        return feature_code in STANDARD_S_CODES
    if feature_class == "L":
        return feature_code in STANDARD_L_CODES
    return False


def ingest_country(filepath: Path, country_code: str, lang: str) -> list[dict]:
    """Ingest a country with capped P/T/other buckets."""
    caps = COUNTRY_CAPS[country_code]

    # Collect candidates by category
    p_candidates: list[tuple[int, list[str]]] = []
    t_candidates: list[tuple[float, list[str]]] = []
    other_records: list[dict] = []

    with filepath.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            if len(row) < 19:
                continue
            fc = row[_FEATURE_CLASS]
            fcode = row[_FEATURE_CODE]

            if fc == "P":
                pop = 0
                with contextlib.suppress(ValueError):
                    pop = int(row[_POPULATION])
                if pop > 0:
                    p_candidates.append((pop, row))
            elif fc == "T":
                elev = 0.0
                with contextlib.suppress(ValueError):
                    elev = float(row[_DEM]) if row[_DEM] else 0.0
                t_candidates.append((elev, row))
            elif should_include_non_p(fc, fcode):
                other_records.append(make_record(row, lang, country_code))

    # Sort and cap populated places by population
    p_candidates.sort(key=lambda x: x[0], reverse=True)
    p_records = [make_record(row, lang, country_code) for _, row in p_candidates[: caps["p_cap"]]]

    # Sort and cap terrain features by elevation (notable peaks first)
    t_candidates.sort(key=lambda x: x[0], reverse=True)
    t_records = [make_record(row, lang, country_code) for _, row in t_candidates[: caps["t_cap"]]]

    # Cap other records
    other_capped = other_records[: caps["other_cap"]]

    print(f"  P.*: {len(p_candidates)} with pop>0, kept top {len(p_records)}")
    print(f"  T.*: {len(t_candidates)} total, kept top {len(t_records)} by elevation")
    print(f"  H/S/L: {len(other_records)} total, kept {len(other_capped)}")

    return p_records + t_records + other_capped


def write_records(records: list[dict], output_path: Path) -> None:
    """Write records to JSONL, sorted by name_form for stable ordering."""
    records.sort(key=lambda r: r["name_form"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    """Ingest GeoNames data for Central European countries."""
    connector = GeoNamesConnector()
    total = 0
    stats: dict[str, int] = {}

    for country_code, lang in COUNTRIES.items():
        print(f"\n{'=' * 60}")
        print(f"Processing {country_code} (language: {lang})")
        print(f"{'=' * 60}")

        # Use connector's download mechanism to ensure file is cached
        filepath = connector._ensure_downloaded(country_code)
        print(f"  Data file: {filepath}")

        records = ingest_country(filepath, country_code, lang)

        output_path = DATABANK_DIR / "places" / country_code / "geonames.jsonl"
        write_records(records, output_path)

        stats[country_code] = len(records)
        total += len(records)
        print(f"  Written: {len(records)} records → {output_path}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    for cc, count in stats.items():
        print(f"  {cc}: {count:>6} records")
    print(f"  {'—' * 20}")
    print(f"  Total: {total:>6} records")


if __name__ == "__main__":
    main()
