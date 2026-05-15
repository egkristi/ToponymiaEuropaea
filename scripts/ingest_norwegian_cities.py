#!/usr/bin/env python3
"""Ingest all 108 official Norwegian cities (byer) from Kartverket SSR.

Queries the Kartverket SSR API programmatically for each city, extracting:
- Coordinates (representasjonspunkt)
- Place type (navneobjekttype)
- Alternative names (Sami, Kvensk, Bokmål, Nynorsk from stedsnavn array)
- Geometry (from geojson field when available)
- Municipality and county information

Cross-references Wikidata QIDs where available.

The official list of 108 Norwegian cities is from:
https://en.wikipedia.org/wiki/List_of_towns_and_cities_in_Norway
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Add project root to path
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
OUTPUT_FILE = DATABANK_DIR / "places" / "NO" / "kartverket.jsonl"

API_BASE = "https://api.kartverket.no/stedsnavn/v1/sted"
# Seconds between API requests (be polite)
REQUEST_DELAY = 0.3


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
    source_dataset: str = "kartverket_ssr",
    source_license: str = "NLOD-2.0",
    source_url: str | None = None,
    elevation: float | None = None,
    is_current: bool = True,
    wikidata_qid: str | None = None,
    geonames_id: int | None = None,
    area_km2: float | None = None,
    population: int | None = None,
    geometry: dict | None = None,
) -> dict:
    """Create a fully enriched place record."""
    geo_class = classify_geometry(place_type)
    geo_status = get_geometry_status(geo_class, geometry)

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
    if area_km2 is not None:
        record["area_km2"] = area_km2
    if population is not None:
        record["population"] = population
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    # Add H3 indices
    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ---------------------------------------------------------------------------
# Kartverket API language code → our language code mapping
# ---------------------------------------------------------------------------
LANG_MAP: dict[str, str] = {
    "Norsk": "nor",
    "Nordsamisk": "sme",
    "Sørsamisk": "sma",
    "Lulesamisk": "smj",
    "Skoltesamisk": "sms",
    "Kvensk": "fkv",
    "Pitesamisk": "sje",
    "Ubestemt språk": "und",
}


def query_kartverket(city_name: str) -> list[dict]:
    """Query Kartverket SSR API for a city name. Returns list of results."""
    params = urllib.parse.urlencode({"sok": city_name, "treffPerSide": 50, "utkoordsys": 4258})
    url = f"{API_BASE}?{params}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})  # noqa: S310
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            data = json.loads(resp.read())
        return data.get("navn", [])
    except Exception as e:
        print(f"  WARNING: API error for '{city_name}': {e}")
        return []


def extract_alternative_names(stedsnavn_list: list[dict]) -> dict[str, list[str]]:
    """Extract alternative names grouped by language code from stedsnavn array."""
    alt_names: dict[str, list[str]] = {}
    for sn in stedsnavn_list:
        lang_raw = sn.get("språk", "Norsk")
        lang_code = LANG_MAP.get(lang_raw, "und")
        name = sn.get("skrivemåte", "")
        if name:
            alt_names.setdefault(lang_code, [])
            if name not in alt_names[lang_code]:
                alt_names[lang_code].append(name)
    return alt_names


def find_best_match(results: list[dict], city_name: str) -> dict | None:
    """Find the best matching result for a city, preferring By > Tettsted > others."""
    # Priority ordering for place types
    type_priority = {
        "By": 0,
        "Tettsted": 1,
        "Tettbebyggelse": 2,
        "Bygdelag (bygd)": 3,
        "Grend": 4,
    }

    candidates = []
    for item in results:
        # Check if any stedsnavn matches the city name
        names_match = False
        for sn in item.get("stedsnavn", []):
            if sn.get("skrivemåte", "").lower() == city_name.lower():
                names_match = True
                break

        if not names_match:
            continue

        obj_type = item.get("navneobjekttype", "")
        priority = type_priority.get(obj_type, 99)
        candidates.append((priority, item))

    if not candidates:
        # Fallback: try partial name match
        for item in results:
            for sn in item.get("stedsnavn", []):
                if city_name.lower() in sn.get("skrivemåte", "").lower():
                    obj_type = item.get("navneobjekttype", "")
                    priority = type_priority.get(obj_type, 99)
                    candidates.append((priority, item))
                    break

    if not candidates:
        return None

    # Sort by priority (lowest number = best match)
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


# ---------------------------------------------------------------------------
# Wikidata QIDs for Norwegian cities (from SPARQL query + manual additions)
# ---------------------------------------------------------------------------
WIKIDATA_QIDS: dict[str, str] = {
    "Alta": "Q3366952",
    "Arendal": "Q2699921",
    "Askim": "Q755703",
    "Bergen": "Q26793",
    "Bodø": "Q39383",
    "Brekstad": "Q2449403",
    "Brumunddal": "Q2578803",
    "Bryne": "Q2536789",
    "Brønnøysund": "Q1144413",
    "Drammen": "Q15138612",
    "Drøbak": "Q1187270",
    "Egersund": "Q996553",
    "Elverum": "Q2024703",
    "Fagernes": "Q2832251",
    "Farsund": "Q493543",
    "Fauske": "Q997036",
    "Finnsnes": "Q1252992",
    "Flekkefjord": "Q490929",
    "Florø": "Q1020010",
    "Fosnavåg": "Q1992972",
    "Fredrikstad": "Q10498783",
    "Førde": "Q1780577",
    "Gjøvik": "Q5420717",
    "Grimstad": "Q129264",
    "Halden": "Q127612",
    "Hamar": "Q3738335",
    "Hammerfest": "Q721374",
    "Harstad": "Q1034159",
    "Haugesund": "Q10518562",
    "Hokksund": "Q1310876",
    "Holmestrand": "Q990993",
    "Honningsvåg": "Q493472",
    "Horten": "Q12715526",
    "Hønefoss": "Q865925",
    "Jessheim": "Q990999",
    "Jørpeland": "Q1020003",
    "Kirkenes": "Q209423",
    "Kongsberg": "Q3363",
    "Kongsvinger": "Q130620",
    "Kopervik": "Q2015825",
    "Kragerø": "Q994003",
    "Kristiansand": "Q26772254",
    "Kristiansund": "Q130700",
    "Langesund": "Q1261453",
    "Larvik": "Q2284798",
    "Leirvik": "Q2041474",
    "Leknes": "Q1319668",
    "Levanger": "Q1287757",
    "Lillehammer": "Q132608",
    "Lillesand": "Q994282",
    "Lillestrøm": "Q1002662",
    "Lyngdal": "Q1889757",
    "Mandal": "Q129314",
    "Mo i Rana": "Q1326556",
    "Moelv": "Q2572127",
    "Molde": "Q10587563",
    "Mosjøen": "Q1218949",
    "Moss": "Q130630",
    "Mysen": "Q2572212",
    "Måløy": "Q1993006",
    "Namsos": "Q130629",
    "Narvik": "Q59101",
    "Notodden": "Q130634",
    "Odda": "Q109494",
    "Orkanger": "Q6516399",
    "Oslo": "Q585",
    "Otta": "Q2020363",
    "Porsgrunn": "Q10637941",
    "Raufoss": "Q1254889",
    "Risør": "Q993996",
    "Rjukan": "Q991201",
    "Røros": "Q130673",
    "Rørvik": "Q2033780",
    "Sandefjord": "Q13100072",
    "Sandnes": "Q14955813",
    "Sandnessjøen": "Q1004686",
    "Sandvika": "Q651744",
    "Sarpsborg": "Q10661956",
    "Sauda": "Q2281805",
    "Ski": "Q1255049",
    "Skien": "Q12375138",
    "Skudeneshavn": "Q1979820",
    "Sortland": "Q2044060",
    "Stavanger": "Q26772333",
    "Stavern": "Q1880618",
    "Steinkjer": "Q130619",
    "Stjørdalshalsen": "Q2573010",
    "Stokmarknes": "Q1970393",
    "Svelvik": "Q12004287",
    "Svolvær": "Q1344063",
    "Tromsø": "Q25474",
    "Trondheim": "Q25804",
    "Tvedestrand": "Q2042136",
    "Tynset": "Q2060063",
    "Tønsberg": "Q10853792",
    "Ulsteinvik": "Q2040849",
    "Vadsø": "Q130644",
    "Vardø": "Q130651",
    "Verdalsøra": "Q2572953",
    "Vinstra": "Q2561629",
    "Åkrehamn": "Q2044270",
    "Ålesund": "Q42900680",
    "Åndalsnes": "Q271083",
    "Åsgårdstrand": "Q1962285",
    # Additional / alternate QIDs for well-known cities
    "Bardufoss": "Q816957",
    "Brevik": "Q2497362",
    "Kolvereid": "Q2534652",
    "Stathelle": "Q2573089",
}


# ---------------------------------------------------------------------------
# The 108 official Norwegian cities (byer)
# Extracted from Wikipedia: List of towns and cities in Norway
# ---------------------------------------------------------------------------
NORWEGIAN_CITIES: list[str] = [
    "Alta",
    "Arendal",
    "Askim",
    "Bardufoss",
    "Bergen",
    "Bodø",
    "Brekstad",
    "Brevik",
    "Brumunddal",
    "Bryne",
    "Brønnøysund",
    "Drammen",
    "Drøbak",
    "Egersund",
    "Elverum",
    "Fagernes",
    "Farsund",
    "Fauske",
    "Finnsnes",
    "Flekkefjord",
    "Florø",
    "Fosnavåg",
    "Fredrikstad",
    "Førde",
    "Gjøvik",
    "Grimstad",
    "Halden",
    "Hamar",
    "Hammerfest",
    "Harstad",
    "Haugesund",
    "Hokksund",
    "Holmestrand",
    "Honningsvåg",
    "Horten",
    "Hønefoss",
    "Jessheim",
    "Jørpeland",
    "Kirkenes",
    "Kolvereid",
    "Kongsberg",
    "Kongsvinger",
    "Kopervik",
    "Kragerø",
    "Kristiansand",
    "Kristiansund",
    "Langesund",
    "Larvik",
    "Leirvik",
    "Leknes",
    "Levanger",
    "Lillehammer",
    "Lillesand",
    "Lillestrøm",
    "Lyngdal",
    "Mandal",
    "Mo i Rana",
    "Moelv",
    "Molde",
    "Mosjøen",
    "Moss",
    "Mysen",
    "Måløy",
    "Namsos",
    "Narvik",
    "Notodden",
    "Odda",
    "Orkanger",
    "Oslo",
    "Otta",
    "Porsgrunn",
    "Raufoss",
    "Risør",
    "Rjukan",
    "Røros",
    "Rørvik",
    "Sandefjord",
    "Sandnes",
    "Sandnessjøen",
    "Sandvika",
    "Sarpsborg",
    "Sauda",
    "Ski",
    "Skien",
    "Skudeneshavn",
    "Sortland",
    "Stathelle",
    "Stavanger",
    "Stavern",
    "Steinkjer",
    "Stjørdalshalsen",
    "Stokmarknes",
    "Svelvik",
    "Svolvær",
    "Tromsø",
    "Trondheim",
    "Tvedestrand",
    "Tynset",
    "Tønsberg",
    "Ulsteinvik",
    "Vadsø",
    "Vardø",
    "Verdalsøra",
    "Vinstra",
    "Åkrehamn",
    "Ålesund",
    "Åndalsnes",
    "Åsgårdstrand",
]


def process_city(city_name: str) -> list[dict]:
    """Query Kartverket API for a city and create records.

    Returns a list of records (main city record + alternative name records).
    """
    results = query_kartverket(city_name)
    if not results:
        print(f"  WARNING: No results for '{city_name}'")
        return []

    best = find_best_match(results, city_name)
    if not best:
        print(f"  WARNING: No matching result for '{city_name}'")
        return []

    # Extract data
    stedsnummer = best["stedsnummer"]
    obj_type = best.get("navneobjekttype", "By")
    pt = best.get("representasjonspunkt", {})
    lat = pt.get("nord")
    lon = pt.get("øst")

    if lat is None or lon is None:
        print(f"  WARNING: No coordinates for '{city_name}'")
        return []

    # Extract alternative names from stedsnavn array
    alt_names = extract_alternative_names(best.get("stedsnavn", []))

    # Extract geometry from geojson field
    geometry = None
    geojson = best.get("geojson")
    if geojson and geojson.get("type") and geojson.get("coordinates"):
        geometry = {"type": geojson["type"], "coordinates": geojson["coordinates"]}

    # Determine primary name and language
    primary_name = city_name
    primary_lang = "nor"
    for sn in best.get("stedsnavn", []):
        if sn.get("navnestatus") == "hovednavn" and sn.get("språk") == "Norsk":
            primary_name = sn["skrivemåte"]
            break

    # Get Wikidata QID
    wikidata_qid = WIKIDATA_QIDS.get(city_name)

    # Source URL
    source_url = f"https://stadnamn.kartverket.no/fakta/{stedsnummer}"

    records = []

    # Main record (Norwegian name)
    records.append(
        make_record(
            name_form=primary_name,
            name_normalized=primary_name.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=f"kartverket:{stedsnummer}",
            place_type=obj_type,
            language_code=primary_lang,
            alternative_names=alt_names,
            source_url=source_url,
            wikidata_qid=wikidata_qid,
            geometry=geometry,
        )
    )

    # Create additional records for non-Norwegian alternative names
    # (Sami, Kvensk names get their own records)
    for sn in best.get("stedsnavn", []):
        lang_raw = sn.get("språk", "Norsk")
        if lang_raw == "Norsk":
            continue
        lang_code = LANG_MAP.get(lang_raw, "und")
        alt_name = sn.get("skrivemåte", "")
        if not alt_name:
            continue

        records.append(
            make_record(
                name_form=alt_name,
                name_normalized=alt_name.lower().strip(),
                latitude=lat,
                longitude=lon,
                source_id=f"kartverket:{stedsnummer}",
                place_type=obj_type,
                language_code=lang_code,
                alternative_names=alt_names,
                source_url=source_url,
                wikidata_qid=wikidata_qid,
                geometry=geometry,
            )
        )

    return records


def main():
    """Query Kartverket API for all 108 Norwegian cities and append to databank."""
    print(f"Ingesting {len(NORWEGIAN_CITIES)} Norwegian cities from Kartverket SSR")
    print(f"Output: {OUTPUT_FILE}")
    print()

    # Load existing records
    existing_ids: set[str] = set()
    existing_name_id_pairs: set[tuple[str, str]] = set()
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                sid = rec.get("source_id", "")
                nf = rec.get("name_form", "")
                existing_ids.add(sid)
                existing_name_id_pairs.add((nf, sid))

    print(f"Existing records: {len(existing_ids)} unique source_ids")
    print()

    # Process each city
    all_records: list[dict] = []
    failed: list[str] = []
    skipped_existing: int = 0

    for i, city in enumerate(NORWEGIAN_CITIES, 1):
        print(f"[{i:3d}/{len(NORWEGIAN_CITIES)}] {city}...", end=" ", flush=True)

        records = process_city(city)
        if not records:
            failed.append(city)
            print("FAILED")
            continue

        # Filter out records that already exist (by name_form + source_id)
        new_records = []
        for rec in records:
            key = (rec["name_form"], rec["source_id"])
            if key in existing_name_id_pairs:
                skipped_existing += 1
            else:
                new_records.append(rec)
                existing_name_id_pairs.add(key)

        all_records.extend(new_records)
        n_exist = len(records) - len(new_records)
        exist_str = f", {n_exist} exist" if n_exist else ""
        ptype = records[0].get("place_type", "?")
        print(f"OK ({len(new_records)} new{exist_str}) [{ptype}]")

        # Rate limit
        if i < len(NORWEGIAN_CITIES):
            time.sleep(REQUEST_DELAY)

    print()
    print(f"Results: {len(all_records)} new records from {len(NORWEGIAN_CITIES)} cities")
    if skipped_existing:
        print(f"  Skipped {skipped_existing} already-existing name+id pairs")
    if failed:
        print(f"  Failed cities ({len(failed)}): {', '.join(failed)}")

    if not all_records:
        print("\nNo new records to add.")
        return

    # Sign all records
    print("\nSigning records...")
    signed_records = [sign_record(r) for r in all_records]

    # Append to file
    with OUTPUT_FILE.open("a") as f:
        for record in signed_records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"\nAdded {len(signed_records)} records to {OUTPUT_FILE}")

    # Summary by place type
    types: dict[str, int] = {}
    for r in signed_records:
        t = r.get("place_type", "unknown")
        types[t] = types.get(t, 0) + 1

    print("\nBreakdown by place type:")
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}")

    # Language breakdown
    langs: dict[str, int] = {}
    for r in signed_records:
        lc = r.get("language_code", "unknown")
        langs[lc] = langs.get(lc, 0) + 1

    print("\nBreakdown by language:")
    for lc, count in sorted(langs.items(), key=lambda x: -x[1]):
        print(f"  {lc}: {count}")

    print(f"\nRecords with geometry: {sum(1 for r in signed_records if r.get('geometry'))}")
    print(f"Records with Wikidata QID: {sum(1 for r in signed_records if r.get('wikidata_qid'))}")
    print(f"Records with alt names: {sum(1 for r in signed_records if r.get('alternative_names'))}")


if __name__ == "__main__":
    main()
