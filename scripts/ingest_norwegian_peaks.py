#!/usr/bin/env python3
"""Ingest mountain peaks across Norway (Kongeriket Norge) from Wikidata.

Sources:
- Wikidata SPARQL: coordinates, elevation, topographic prominence,
  topographic isolation, parent peak, mountain range, GeoNames IDs,
  alternative names (Norwegian Bokmål, Nynorsk, Northern Sami, English)

Norway has extensive mountain terrain covering much of the country:
  Jotunheimen: Galdhøpiggen (2469m), Glittertind (2452m), Store Skagastølstind
  Rondane: Rondslottet (2178m), Storronden (2138m), Vinjeronden (2044m)
  Dovrefjell: Snøhetta (2286m), Svånåtindan (1926m)
  Lyngen Alps: Jiehkkevárri (1833m), Storsteinsfjellet
  Lofoten: Higravstinden (1146m), Rulten (1062m)
  Hardangervidda/Hardanger: Hardangerjøkulen (1863m), Folgefonna
  Romsdalsalpene: Romsdalshorn (1550m), Store Trolltind (1788m)
  Sunnmørsalpane: Slogen (1564m), Kolåstinden
  Børgefjell: Kvigtind (1699m)
  Saltfjellet: Ølfjellet, Istind

Topographic metrics:
  - Elevation: height above sea level (meters)
  - Prominence: vertical drop to the highest col connecting to a higher peak
  - Isolation: distance to nearest point of equal or greater elevation
  - Parent peak: nearest higher peak via the key col
  - Mountain range: the range or massif the peak belongs to
  - Dominance ratio: prominence / elevation (measure of independence)

Linguistic layers:
  - Norwegian Bokmål (nob): primary official standard
  - Norwegian Nynorsk (nno): second official standard
  - Northern Sami (sme): indigenous Sami names, especially in northern Norway
  - Lule Sami (smj): Sami names in Nordland/Troms
  - English (eng): international/anglicized forms

References:
- https://en.wikipedia.org/wiki/List_of_mountains_of_Norway
- https://en.wikipedia.org/wiki/List_of_highest_points_in_Norway_by_county
- https://no.wikipedia.org/wiki/Liste_over_fjelltopper_i_Norge
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from toponymia.pipelines.geometry_classify import (  # noqa: E402
    classify_geometry,
    get_geometry_status,
)
from toponymia.pipelines.integrity import sign_record  # noqa: E402

try:
    import h3  # noqa: E402

    HAS_H3 = True
except ImportError:
    HAS_H3 = False

DATABANK_DIR = ROOT / "databank"
OUTPUT_FILE = DATABANK_DIR / "places" / "NO" / "wikidata.jsonl"


def phonetic_key(name: str) -> str:
    """Simple phonetic key: lowercase, stripped."""
    return name.lower().strip()


def make_h3(lat: float, lng: float) -> dict[str, str]:
    """Compute H3 indices at resolutions 7, 9, 11."""
    if not HAS_H3:
        return {}
    return {f"_h3_r{r}": str(h3.latlng_to_cell(lat, lng, r)) for r in (7, 9, 11)}


def make_record(
    *,
    name_form: str,
    name_normalized: str,
    latitude: float,
    longitude: float,
    source_id: str,
    place_type: str,
    language_code: str = "nor",
    alternative_names: dict[str, list[str]] | None = None,
    source_dataset: str = "wikidata",
    source_license: str = "CC0-1.0",
    source_url: str | None = None,
    elevation: float | None = None,
    is_current: bool = True,
    wikidata_qid: str | None = None,
    geonames_id: int | None = None,
    prominence_m: float | None = None,
    isolation_km: float | None = None,
    parent_peak_qid: str | None = None,
    parent_peak_name: str | None = None,
    mountain_range: str | None = None,
    mountain_range_qid: str | None = None,
    dominance_ratio: float | None = None,
) -> dict:
    """Create a fully enriched place record for a mountain peak."""
    geo_class = classify_geometry(place_type)
    geo_status = get_geometry_status(geo_class, None)

    record: dict = {
        "name_form": name_form,
        "name_normalized": name_normalized,
        "latitude": latitude,
        "longitude": longitude,
        "source_id": source_id,
        "source_dataset": source_dataset,
        "source_license": source_license,
        "country_code": "NO",
        "language_code": language_code,
        "place_type": place_type,
        "is_current": is_current,
        "alternative_names": alternative_names or {},
        "_geometry_class": geo_class,
        "_geometry_status": geo_status,
        "_phonetic_key": phonetic_key(name_form),
    }

    if source_url:
        record["source_url"] = source_url
    if elevation is not None:
        record["elevation"] = elevation
    if wikidata_qid:
        record["wikidata_qid"] = wikidata_qid
    if geonames_id:
        record["geonames_id"] = geonames_id
    if prominence_m is not None:
        record["prominence_m"] = prominence_m
    if isolation_km is not None:
        record["isolation_km"] = isolation_km
    if parent_peak_qid:
        record["parent_peak_qid"] = parent_peak_qid
    if parent_peak_name:
        record["parent_peak_name"] = parent_peak_name
    if mountain_range:
        record["mountain_range"] = mountain_range
    if mountain_range_qid:
        record["mountain_range_qid"] = mountain_range_qid
    if dominance_ratio is not None:
        record["dominance_ratio"] = dominance_ratio

    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ---------------------------------------------------------------------------
# HTTP helper with retry
# ---------------------------------------------------------------------------
def sparql_query(query: str, timeout: int = 120, retries: int = 3) -> dict:
    """Execute a SPARQL query against Wikidata with retry logic."""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"https://query.wikidata.org/sparql?{params}"
    req = urllib.request.Request(  # noqa: S310
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": ("ToponymiaEuropaea/0.5 (https://github.com/egkristi/ToponymiaEuropaea)"),
        },
    )

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
                return json.loads(resp.read())
        except Exception as e:
            if attempt < retries - 1:
                wait = (attempt + 1) * 5
                print(f"    Retry {attempt + 1}/{retries} after error: {e}")
                print(f"    Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise

    return {}  # unreachable, but satisfies type checker


# ---------------------------------------------------------------------------
# Wikidata SPARQL — Phase 1: Discovery
# ---------------------------------------------------------------------------
def discover_peaks() -> list[dict]:
    """Discover all Norwegian mountain peaks with coordinates + elevation."""
    print("Phase 1: Discovering Norwegian peaks from Wikidata...")

    # Query each instance type separately to avoid timeouts
    instance_types = [
        ("Q8502", "mountain", "T.MT"),
        ("Q54050", "hill", "T.HLL"),
        ("Q207326", "mountain peak", "T.PK"),
    ]

    seen: dict[str, dict] = {}

    for type_qid, type_label, place_type in instance_types:
        print(f"  Querying {type_label}s (wd:{type_qid})...")

        query = f"""SELECT DISTINCT ?item ?itemLabel ?coord ?elevation
        WHERE {{
          ?item wdt:P17 wd:Q20 .
          ?item wdt:P31 wd:{type_qid} .
          ?item wdt:P625 ?coord .
          ?item wdt:P2044 ?elevation .
          SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "nb,nn,no,en"
          }}
        }}
        ORDER BY DESC(?elevation)"""

        data = sparql_query(query)
        results = data["results"]["bindings"]
        print(f"    Got {len(results)} results")

        for r in results:
            qid = r["item"]["value"].split("/")[-1]
            name = r["itemLabel"]["value"]
            elev = float(r["elevation"]["value"])

            coord = r.get("coord", {}).get("value", "")
            lat, lon = None, None
            if coord:
                parts = coord.replace("Point(", "").replace(")", "").split()
                if len(parts) == 2:
                    lon, lat = float(parts[0]), float(parts[1])

            if lat is None or lon is None:
                continue

            if qid not in seen or elev > seen[qid]["elevation"]:
                seen[qid] = {
                    "qid": qid,
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "elevation": elev,
                    "place_type": place_type,
                }

        time.sleep(2)

    peaks = list(seen.values())
    print(f"  Unique peaks discovered: {len(peaks)}")
    return peaks


# ---------------------------------------------------------------------------
# Wikidata SPARQL — Phase 2: Detailed metrics batch lookup
# ---------------------------------------------------------------------------
def query_peak_details(qids: list[str]) -> dict[str, dict]:
    """Query Wikidata for detailed peak metrics using VALUES-based batching."""
    print("Phase 2: Fetching detailed metrics...")

    batches = [qids[i : i + 80] for i in range(0, len(qids), 80)]
    lookup: dict[str, dict] = {}

    for batch_idx, batch in enumerate(batches):
        values_str = " ".join(f"wd:{qid}" for qid in batch)

        query = f"""SELECT DISTINCT ?item ?prominence ?isolation
          ?parent ?parentName ?range ?rangeName ?geonames
          ?nob_name ?nno_name ?sme_name ?smj_name ?eng_name
        WHERE {{
          VALUES ?item {{ {values_str} }}
          OPTIONAL {{ ?item wdt:P2660 ?prominence }}
          OPTIONAL {{ ?item wdt:P2659 ?isolation }}
          OPTIONAL {{ ?item wdt:P3137 ?parent .
                     ?parent rdfs:label ?parentName .
                     FILTER(LANG(?parentName) = "nb") }}
          OPTIONAL {{ ?item wdt:P4552 ?range .
                     ?range rdfs:label ?rangeName .
                     FILTER(LANG(?rangeName) = "nb") }}
          OPTIONAL {{ ?item wdt:P1566 ?geonames }}
          OPTIONAL {{ ?item rdfs:label ?nob_name . FILTER(LANG(?nob_name) = "nb") }}
          OPTIONAL {{ ?item rdfs:label ?nno_name . FILTER(LANG(?nno_name) = "nn") }}
          OPTIONAL {{ ?item rdfs:label ?sme_name . FILTER(LANG(?sme_name) = "se") }}
          OPTIONAL {{ ?item rdfs:label ?smj_name . FILTER(LANG(?smj_name) = "smj") }}
          OPTIONAL {{ ?item rdfs:label ?eng_name . FILTER(LANG(?eng_name) = "en") }}
        }}"""

        data = sparql_query(query)
        results = data["results"]["bindings"]
        print(f"  Batch {batch_idx + 1}/{len(batches)}: {len(results)} results")

        for r in results:
            qid = r["item"]["value"].split("/")[-1]

            prom = r.get("prominence", {}).get("value")
            iso = r.get("isolation", {}).get("value")
            parent_uri = r.get("parent", {}).get("value")
            parent_label = r.get("parentName", {}).get("value")
            range_uri = r.get("range", {}).get("value")
            range_label = r.get("rangeName", {}).get("value")
            gn = r.get("geonames", {}).get("value")

            nob = r.get("nob_name", {}).get("value")
            nno = r.get("nno_name", {}).get("value")
            sme = r.get("sme_name", {}).get("value")
            smj = r.get("smj_name", {}).get("value")
            eng = r.get("eng_name", {}).get("value")

            parent_qid = None
            if parent_uri:
                parent_qid = parent_uri.split("/")[-1]

            range_qid = None
            if range_uri:
                range_qid = range_uri.split("/")[-1]

            # Only update if we have new data or no existing entry
            existing = lookup.get(qid, {})

            entry = {
                "prominence": float(prom) if prom else existing.get("prominence"),
                "isolation": float(iso) if iso else existing.get("isolation"),
                "parent_qid": parent_qid or existing.get("parent_qid"),
                "parent_name": parent_label or existing.get("parent_name"),
                "range_qid": range_qid or existing.get("range_qid"),
                "range_name": range_label or existing.get("range_name"),
                "geonames_id": int(gn) if gn else existing.get("geonames_id"),
                "nob": nob or existing.get("nob"),
                "nno": nno or existing.get("nno"),
                "sme": sme or existing.get("sme"),
                "smj": smj or existing.get("smj"),
                "eng": eng or existing.get("eng"),
            }

            lookup[qid] = entry

        if batch_idx < len(batches) - 1:
            time.sleep(2)

    return lookup


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    """Ingest Norwegian mountain peaks with comprehensive topographic metadata."""
    # Phase 1: Discover all Norwegian peaks
    peaks = discover_peaks()

    if not peaks:
        print("\nNo peaks discovered. Check Wikidata connectivity.")
        return

    print(f"\nTotal peaks to process: {len(peaks)}")
    print(f"Output: {OUTPUT_FILE}")
    print()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Phase 2: Fetch detailed metrics
    all_qids = [p["qid"] for p in peaks]
    time.sleep(2)
    details_lookup = query_peak_details(all_qids)
    print()

    # Create records
    print("Creating records...")
    all_records: list[dict] = []

    for peak in peaks:
        qid = peak["qid"]
        name = peak["name"]
        lat = peak["lat"]
        lon = peak["lon"]
        elevation = peak["elevation"]
        place_type = peak["place_type"]

        details = details_lookup.get(qid, {})

        source_id = f"wikidata:{qid}"
        source_url = f"https://www.wikidata.org/wiki/{qid}"

        # Build alternative names
        alt_names: dict[str, list[str]] = {}
        nob = details.get("nob")
        nno = details.get("nno")
        sme = details.get("sme")
        smj = details.get("smj")
        eng = details.get("eng")

        if nob:
            alt_names["nob"] = [nob]
        if nno and nno != nob:
            alt_names["nno"] = [nno]
        if sme:
            alt_names["sme"] = [sme]
        if smj:
            alt_names["smj"] = [smj]
        if eng and eng != name:
            alt_names["eng"] = [eng]

        # Topographic metrics
        prominence = details.get("prominence")
        isolation = details.get("isolation")
        parent_qid = details.get("parent_qid")
        parent_name = details.get("parent_name")
        range_name = details.get("range_name")
        range_qid = details.get("range_qid")
        geonames_id = details.get("geonames_id")

        # Dominance ratio
        dominance = None
        if prominence is not None and elevation > 0:
            dominance = round(prominence / elevation, 4)

        record = make_record(
            name_form=name,
            name_normalized=name.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=source_id,
            place_type=place_type,
            language_code="nor",
            alternative_names=alt_names,
            source_url=source_url,
            wikidata_qid=qid,
            geonames_id=geonames_id,
            elevation=elevation,
            prominence_m=prominence,
            isolation_km=isolation,
            parent_peak_qid=parent_qid,
            parent_peak_name=parent_name,
            mountain_range=range_name,
            mountain_range_qid=range_qid,
            dominance_ratio=dominance,
        )

        all_records.append(record)

    print(f"\nCreated {len(all_records)} records")

    if not all_records:
        print("\nNo records to write.")
        return

    print("\nSigning records...")
    signed_records = [sign_record(r) for r in all_records]

    with OUTPUT_FILE.open("w") as f:
        for record in signed_records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"\nWrote {len(signed_records)} records to {OUTPUT_FILE}")

    # Summary statistics
    with_prom = sum(1 for r in signed_records if r.get("prominence_m") is not None)
    with_iso = sum(1 for r in signed_records if r.get("isolation_km") is not None)
    with_parent = sum(1 for r in signed_records if r.get("parent_peak_qid"))
    with_range = sum(1 for r in signed_records if r.get("mountain_range"))
    with_gn = sum(1 for r in signed_records if r.get("geonames_id"))
    with_alts = sum(
        1
        for r in signed_records
        if r.get("alternative_names") and any(r["alternative_names"].values())
    )
    with_dominance = sum(1 for r in signed_records if r.get("dominance_ratio") is not None)

    # Alt name language breakdown
    alt_nob = sum(1 for r in signed_records if r.get("alternative_names", {}).get("nob"))
    alt_nno = sum(1 for r in signed_records if r.get("alternative_names", {}).get("nno"))
    alt_sme = sum(1 for r in signed_records if r.get("alternative_names", {}).get("sme"))
    alt_smj = sum(1 for r in signed_records if r.get("alternative_names", {}).get("smj"))
    alt_eng = sum(1 for r in signed_records if r.get("alternative_names", {}).get("eng"))

    print(f"\nRecords with prominence: {with_prom}")
    print(f"Records with isolation: {with_iso}")
    print(f"Records with parent peak: {with_parent}")
    print(f"Records with mountain range: {with_range}")
    print(f"Records with dominance ratio: {with_dominance}")
    print(f"Records with GeoNames ID: {with_gn}")
    print(f"Records with alternative names: {with_alts}")
    print(f"  - Bokmål (nob): {alt_nob}")
    print(f"  - Nynorsk (nno): {alt_nno}")
    print(f"  - Northern Sami (sme): {alt_sme}")
    print(f"  - Lule Sami (smj): {alt_smj}")
    print(f"  - English (eng): {alt_eng}")

    # Place type breakdown
    type_counts: dict[str, int] = {}
    for r in signed_records:
        t = r.get("place_type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    print("\nBreakdown by place type:")
    for ptype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {ptype}: {count}")

    # Elevation stats
    elevations = [r["elevation"] for r in signed_records if r.get("elevation")]
    if elevations:
        print(f"\nElevation range: {min(elevations):.0f}m – {max(elevations):.0f}m")
        avg_elev = sum(elevations) / len(elevations)
        print(f"Average elevation: {avg_elev:.0f}m")

    # Top 10 by elevation
    sorted_records = sorted(signed_records, key=lambda r: r.get("elevation", 0), reverse=True)
    print("\nTop 10 peaks by elevation:")
    for r in sorted_records[:10]:
        prom_s = f"{r['prominence_m']:.0f}m" if r.get("prominence_m") else "—"
        print(
            f"  {r['name_form']:30s} {r['elevation']:6.0f}m  "
            f"prom={prom_s:>7s}  "
            f"range={r.get('mountain_range', '—')}"
        )


if __name__ == "__main__":
    main()
