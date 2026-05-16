"""Ingest all Kartverket place names within 30km of a given point.

Uses the /punkt endpoint (max 5km radius) tiled across the area,
then filters to exact 30km radius and deduplicates by stedsnummer.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import httpx

# === Configuration ===
CENTER_LAT = 60.9815455
CENTER_LON = 5.0711678
RADIUS_KM = 30
QUERY_RADIUS_M = 5000  # Max API allows
GRID_SPACING_KM = 8  # Spacing between grid points (< 2*5km for overlap)
API_BASE = "https://api.kartverket.no/stedsnavn/v1/punkt"
RATE_LIMIT = 0.25  # seconds between requests
OUTPUT_PATH = Path("databank/places/NO/kartverket_sunnfjord_30km.jsonl")

# Language code mapping
LANGUAGE_MAP = {
    "norsk": "nor",
    "nob": "nob",
    "nno": "nno",
    "nordsamisk": "sme",
    "lulesamisk": "smj",
    "sørsamisk": "sma",
    "kvensk": "fkv",
    "finsk": "fin",
    "sme": "sme",
    "smj": "smj",
    "sma": "sma",
    "fkv": "fkv",
    "fin": "fin",
    "nor": "nor",
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.asin(math.sqrt(a))


def generate_grid_points(
    center_lat: float, center_lon: float, radius_km: float, spacing_km: float
) -> list[tuple[float, float]]:
    """Generate a grid of query points covering the circle."""
    points = []
    km_per_deg_lat = 111.32
    km_per_deg_lon = 111.32 * math.cos(math.radians(center_lat))

    n_steps = int(radius_km / spacing_km) + 1

    for i in range(-n_steps, n_steps + 1):
        for j in range(-n_steps, n_steps + 1):
            dy_km = i * spacing_km
            dx_km = j * spacing_km

            # Check if grid point is within radius + query_radius (to catch edge names)
            dist = math.sqrt(dx_km**2 + dy_km**2)
            if dist > radius_km + QUERY_RADIUS_M / 1000:
                continue

            lat = center_lat + dy_km / km_per_deg_lat
            lon = center_lon + dx_km / km_per_deg_lon

            points.append((lat, lon))

    return points


def query_punkt(
    client: httpx.Client, lat: float, lon: float, radius_m: int = QUERY_RADIUS_M
) -> list[dict]:
    """Query the /punkt endpoint for a single point."""
    all_names = []
    page = 1
    max_pages = 500

    while page <= max_pages:
        params = {
            "nord": lat,
            "ost": lon,
            "koordsys": 4258,
            "radius": radius_m,
            "treffPerSide": 500,
            "side": page,
        }

        response = client.get(API_BASE, params=params)
        response.raise_for_status()
        data = response.json()

        names = data.get("navn", [])
        if not names:
            break

        all_names.extend(names)

        metadata = data.get("metadata", {})
        total = metadata.get("totaltAntallTreff", 0)
        per_page = metadata.get("treffPerSide", 500)

        if page * per_page >= total:
            break

        page += 1
        time.sleep(RATE_LIMIT)

    return all_names


def parse_entry(entry: dict) -> list[dict]:
    """Parse a single API entry into databank records."""
    records = []

    # Get coordinates
    rep = entry.get("representasjonspunkt", {})
    lat = rep.get("nord")
    lon = rep.get("øst", rep.get("ost"))

    if lat is None or lon is None:
        # Try geojson fallback
        geojson = entry.get("geojson", {})
        geometry = geojson.get("geometry", {})
        coords = geometry.get("coordinates", [])
        if len(coords) >= 2:
            lon, lat = coords[0], coords[1]

    if lat is None or lon is None:
        return records

    navneobjekttype = entry.get("navneobjekttype", "")
    stedsnummer = str(entry.get("stedsnummer", ""))

    stedsnavn_list = entry.get("stedsnavn", [])
    if not stedsnavn_list:
        return records

    # Collect all name forms for alternatives
    all_forms = []
    for skriv in stedsnavn_list:
        form = skriv.get("skrivemåte", "")
        spraak = skriv.get("språk", "Norsk")
        if form:
            all_forms.append((form, spraak))

    for skriv in stedsnavn_list:
        name_form = skriv.get("skrivemåte", "")
        if not name_form:
            continue

        spraak = skriv.get("språk", "Norsk")
        iso_code = LANGUAGE_MAP.get(spraak.lower(), "nor")

        navnestatus = skriv.get("navnestatus", "")
        skrivematestatus = skriv.get("skrivemåtestatus", "")
        is_current = (
            navnestatus
            in (
                "hovednavn",
                "vedtatt",
                "godkjent",
                "samlevedtak",
            )
            or "godkjent" in skrivematestatus.lower()
        )

        # Build alternatives (other name forms for this place)
        alternatives: dict[str, list[str]] = {}
        for form, lang in all_forms:
            if form == name_form:
                continue
            alt_code = LANGUAGE_MAP.get(lang.lower(), "nor")
            alternatives.setdefault(alt_code, []).append(form)

        # Compute sha256
        canonical = json.dumps(
            {
                "name_form": name_form,
                "latitude": float(lat),
                "longitude": float(lon),
                "source_id": f"kartverket:{stedsnummer}",
            },
            sort_keys=True,
        )
        sha = hashlib.sha256(canonical.encode()).hexdigest()

        record = {
            "name_form": name_form,
            "name_normalized": name_form.lower().strip(),
            "latitude": float(lat),
            "longitude": float(lon),
            "source_id": f"kartverket:{stedsnummer}",
            "source_dataset": "kartverket_ssr",
            "source_url": f"https://api.kartverket.no/stedsnavn/v1/sted/{stedsnummer}",
            "source_license": "NLOD-2.0",
            "language_code": iso_code,
            "country_code": "NO",
            "place_type": navneobjekttype,
            "is_current": is_current,
            "alternative_names": alternatives,
            "_phonetic_key": name_form.lower().strip(),
            "_geometry_status": "pending",
            "_sha256": sha,
        }

        records.append(record)

    return records


def main() -> None:
    print(f"Center: {CENTER_LAT}, {CENTER_LON}")
    print(f"Radius: {RADIUS_KM}km")
    print(f"Query radius: {QUERY_RADIUS_M}m, grid spacing: {GRID_SPACING_KM}km")

    # Generate grid of query points
    grid_points = generate_grid_points(CENTER_LAT, CENTER_LON, RADIUS_KM, GRID_SPACING_KM)
    print(f"Grid points to query: {len(grid_points)}")

    # Query API for each grid point
    client = httpx.Client(timeout=30.0, headers={"Accept": "application/json"})
    all_entries: dict[str, dict] = {}  # stedsnummer -> entry (dedup)

    for i, (lat, lon) in enumerate(grid_points):
        dist_from_center = haversine_km(CENTER_LAT, CENTER_LON, lat, lon)
        print(
            f"  [{i + 1}/{len(grid_points)}] Querying ({lat:.4f}, {lon:.4f}) "
            f"[{dist_from_center:.1f}km from center]...",
            end="",
            flush=True,
        )

        try:
            names = query_punkt(client, lat, lon)
            new_count = 0
            for entry in names:
                sn = str(entry.get("stedsnummer", ""))
                if sn and sn not in all_entries:
                    all_entries[sn] = entry
                    new_count += 1
            print(f" {len(names)} hits, {new_count} new (total unique: {len(all_entries)})")
        except Exception as e:
            print(f" ERROR: {e}")

        time.sleep(RATE_LIMIT)

    print(f"\nTotal unique places (stedsnummer): {len(all_entries)}")

    # Parse and filter to exact radius
    records = []
    seen_keys: set[str] = set()

    for entry in all_entries.values():
        parsed = parse_entry(entry)
        for rec in parsed:
            # Filter to within 30km of center
            dist = haversine_km(CENTER_LAT, CENTER_LON, rec["latitude"], rec["longitude"])
            if dist > RADIUS_KM:
                continue

            # Dedup by source_id + name_form
            key = f"{rec['source_id']}:{rec['name_form']}"
            if key in seen_keys:
                continue
            seen_keys.add(key)
            records.append(rec)

    print(f"Records within {RADIUS_KM}km: {len(records)}")

    # Sort by distance from center
    records.sort(key=lambda r: haversine_km(CENTER_LAT, CENTER_LON, r["latitude"], r["longitude"]))

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Written {len(records)} records to {OUTPUT_PATH}")

    # Stats
    place_types: dict[str, int] = {}
    languages: dict[str, int] = {}
    for r in records:
        pt = r.get("place_type", "unknown")
        place_types[pt] = place_types.get(pt, 0) + 1
        lang = r.get("language_code", "unknown")
        languages[lang] = languages.get(lang, 0) + 1

    print("\nPlace types (top 20):")
    for pt, count in sorted(place_types.items(), key=lambda x: -x[1])[:20]:
        print(f"  {pt}: {count}")

    print("\nLanguages:")
    for lang, count in sorted(languages.items(), key=lambda x: -x[1]):
        print(f"  {lang}: {count}")


if __name__ == "__main__":
    main()
