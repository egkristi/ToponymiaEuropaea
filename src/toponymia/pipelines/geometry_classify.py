#!/usr/bin/env python3
"""Classify place records by geometry type and add geometry_status field.

Analyses each place record's feature type to determine whether it represents
a point (spot location), a linear feature (river, road, ridge), or an area
(lake, island, valley, administrative region).

Records are updated in-place with:
  - geometry_class: "point" | "line" | "area"
  - geometry_status: "point" | "defined" | "pending"

A "pending" status means the feature should have outline geometry but
doesn't yet — flagging it for future geometry acquisition.
"""

import json
from pathlib import Path

DATABANK_DIR = Path(__file__).resolve().parent.parent.parent.parent / "databank"

# Feature types that are inherently point locations
POINT_TYPES = frozenset(
    [
        # Populated places
        "P.PPL",
        "P.PPLX",
        "P.PPLL",
        "P.PPLA",
        "P.PPLA2",
        "P.PPLA3",
        "P.PPLC",
        "P.PPLQ",
        # Spot features
        "T.PK",
        "T.PT",
        "T.RK",
        "T.PASS",
        "T.SDL",
        # Structures (inherently point-like)
        "S.FRM",
        "S.EST",
        "S.HSE",
        "S.CH",
        "S.FRMQ",
        "S.HUT",
        "S.FT",
        "S.RUIN",
        "S.MN",
        "S.RSTN",
        "S.AIRF",
        "S.RSRT",
        "S.LDNG",
        "S.TOWR",
        "S.MSTY",
        "S.RSTP",
        "S.AIRQ",
        # Hydrographic point features
        "H.FLLS",
        "H.RPDS",
        "H.HBR",
        "H.STMM",
        "H.STMH",
        "H.PND",
        "H.NRWS",
        # Norwegian types (point)
        "Fyrlykt",
        "Fyrstasjon",
        "Enebolig/mindre boligbygg",
        "Gard",
        "Bruk",
        "Navnegard",
        "Seter/støl",
        "Tettsted",
        "Foss",
        "Annen kulturdetalj",
        "Eiendom",
    ]
)

# Feature types that are linear (rivers, ridges, roads, canals)
LINE_TYPES = frozenset(
    [
        "H.STM",
        "H.STMX",
        "H.STMA",
        "H.STMD",
        "H.STMB",
        "H.CNL",
        "H.CHNM",
        "T.RDGE",
        "T.CLF",
        "T.SHOR",
        "T.SPIT",
        # Norwegian types (linear)
        "Elv",
        "Vegstrekning",
        "Banestrekning",
    ]
)

# Feature types that are area/polygon features
AREA_TYPES = frozenset(
    [
        # Hydrographic areas
        "H.LK",
        "H.LKS",
        "H.BAY",
        "H.COVE",
        "H.FJD",
        "H.INLT",
        "H.BOG",
        "H.SWMP",
        "H.MRSH",
        "H.MOOR",
        "H.BGHT",
        "H.GLCR",
        "H.RF",
        "H.SHOL",
        "H.STRT",
        "H.SD",
        "H.LGN",
        "H.BNK",
        "H.LBED",
        "H.CAPG",
        "H.RVN",
        # Terrain areas
        "T.ISL",
        "T.ISLS",
        "T.ISLX",
        "T.ISLET",
        "T.ISLT",
        "T.MT",
        "T.MTS",
        "T.HLL",
        "T.HLLS",
        "T.RKS",
        "T.PEN",
        "T.PENX",
        "T.VAL",
        "T.CAPE",
        "T.HDLD",
        "T.SLP",
        "T.PROM",
        "T.GRGE",
        "T.LAVA",
        "T.UPLD",
        "T.MRN",
        "T.SAND",
        "T.PLAT",
        "T.PLDR",
        "T.INTF",
        # Vegetation/land areas
        "V.FRST",
        "V.HTH",
        "V.MDW",
        "V.GROVE",
        "L.GRAZ",
        "L.FLD",
        "L.LCTY",
        # Administrative areas
        "A.ADM2",
        "A.ADMD",
        # Norwegian types (area)
        "Myr",
        "Dal",
        "Vann",
        "Vik i sjø",
        "Sund i sjø",
        "Fjord",
        "Øy i sjø",
        "Holme i sjø",
        "Nes",
        "Nes i sjø",
        "Halvøy i sjø",
        "Øy",
        "Dalføre",
        "Verneområde",
        "Skogområde",
        "Friluftsområde",
        "Gruppe av vann",
        "Holmegruppe i sjø",
        "Administrativ bydel",
        "Bydel",
        "Kommune",
        "Fylke",
        "Nasjon",
        "By",
        "Tettbebyggelse",
        "Bygdelag (bygd)",
    ]
)


def classify_geometry(place_type: str | None) -> str:
    """Classify a place type into point, line, or area."""
    if not place_type:
        return "unknown"
    if place_type in POINT_TYPES:
        return "point"
    if place_type in LINE_TYPES:
        return "line"
    if place_type in AREA_TYPES:
        return "area"
    return "unknown"


def get_geometry_status(geometry_class: str, geometry: dict | None) -> str:
    """Determine geometry status based on class and existing geometry data."""
    if geometry and geometry.get("type"):
        return "defined"
    if geometry_class == "point":
        return "point"
    if geometry_class in ("line", "area"):
        return "pending"
    return "unknown"


def process_file(jsonl_path: Path, dry_run: bool = False) -> dict:
    """Process a single JSONL file, adding geometry classification fields.

    Returns stats dict with counts.
    """
    stats = {
        "total": 0,
        "point": 0,
        "line": 0,
        "area": 0,
        "unknown": 0,
        "defined": 0,
        "pending": 0,
        "modified": 0,
    }
    records = []

    with jsonl_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            stats["total"] += 1

            place_type = record.get("place_type", "")
            geo_class = classify_geometry(place_type)
            existing_geometry = record.get("geometry")
            geo_status = get_geometry_status(geo_class, existing_geometry)

            stats[geo_class] += 1
            if geo_status == "defined":
                stats["defined"] += 1
            elif geo_status == "pending":
                stats["pending"] += 1

            # Add/update fields if changed
            if (
                record.get("_geometry_class") != geo_class
                or record.get("_geometry_status") != geo_status
            ):
                record["_geometry_class"] = geo_class
                record["_geometry_status"] = geo_status
                stats["modified"] += 1

            records.append(record)

    if not dry_run and stats["modified"] > 0:
        with jsonl_path.open("w") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return stats


def main():
    """Run geometry classification across all databank place files."""
    import argparse

    parser = argparse.ArgumentParser(description="Classify place records by geometry type")
    parser.add_argument("--dry-run", action="store_true", help="Analyse without modifying files")
    args = parser.parse_args()

    places_dir = DATABANK_DIR / "places"
    if not places_dir.exists():
        print("No databank/places directory found.")
        return

    totals = {
        "total": 0,
        "point": 0,
        "line": 0,
        "area": 0,
        "unknown": 0,
        "defined": 0,
        "pending": 0,
        "modified": 0,
    }

    print(f"{'Mode:':<12} {'DRY RUN' if args.dry_run else 'WRITE'}")
    print(f"{'Databank:':<12} {places_dir}")
    print("-" * 60)

    for country_dir in sorted(places_dir.iterdir()):
        if not country_dir.is_dir():
            continue
        for jsonl_file in sorted(country_dir.glob("*.jsonl")):
            stats = process_file(jsonl_file, dry_run=args.dry_run)
            rel = jsonl_file.relative_to(DATABANK_DIR)
            print(
                f"  {rel}: {stats['total']} records "
                f"(pt:{stats['point']} ln:{stats['line']} "
                f"ar:{stats['area']} ?:{stats['unknown']}) "
                f"pending:{stats['pending']} "
                f"modified:{stats['modified']}"
            )
            for k in totals:
                totals[k] += stats[k]

    print("-" * 60)
    print(f"{'TOTAL':<12} {totals['total']} records")
    print(f"  Point:     {totals['point']:5} (spot locations)")
    print(f"  Line:      {totals['line']:5} (need polyline geometry)")
    print(f"  Area:      {totals['area']:5} (need polygon geometry)")
    print(f"  Unknown:   {totals['unknown']:5} (unclassified type)")
    print(f"  Defined:   {totals['defined']:5} (geometry already present)")
    print(f"  PENDING:   {totals['pending']:5} (⚠ need geometry acquisition)")
    print(f"  Modified:  {totals['modified']:5} records")

    if args.dry_run:
        print("\n(Dry run — no files were modified)")


if __name__ == "__main__":
    main()
