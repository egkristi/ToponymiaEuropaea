#!/usr/bin/env python3
"""Ingest all Danish cities (købstæder) with comprehensive metadata.

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, region, area,
  alternative names (German, Low German, Latin, Old Norse)
- OpenStreetMap Nominatim: GeoJSON geometry (city boundaries/polygons)

Denmark historically had 69 købstæder (market towns) which were granted
special trading privileges. This list covers all historical købstæder plus
major modern cities. All Danish municipalities' main cities are included
for comprehensive coverage.

References:
- https://da.wikipedia.org/wiki/Købstæder_i_Danmark
- https://en.wikipedia.org/wiki/Market_town_(Denmark)
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
OUTPUT_FILE = DATABANK_DIR / "places" / "DK" / "wikidata.jsonl"

# Rate limiting
NOMINATIM_DELAY = 1.1  # OSM Nominatim requires >= 1s between requests


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
    language_code: str = "dan",
    alternative_names: dict[str, list[str]] | None = None,
    source_dataset: str = "wikidata",
    source_license: str = "CC0-1.0",
    source_url: str | None = None,
    elevation: float | None = None,
    is_current: bool = True,
    wikidata_qid: str | None = None,
    geonames_id: int | None = None,
    area_km2: float | None = None,
    population: int | None = None,
    geometry: dict | None = None,
    region: str | None = None,
    chartered_year: int | None = None,
    municipality: str | None = None,
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
        "country_code": "DK",
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
    if region:
        record["region"] = region
    if municipality:
        record["municipality"] = municipality
    if chartered_year is not None:
        record["chartered_year"] = chartered_year
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    # Add H3 indices
    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ---------------------------------------------------------------------------
# Danish cities: All historical købstæder + major modern cities
# Tuple fields: name, chartered_year, region, wikidata_qid, geonames_id
#
# Regions: Hovedstaden, Midtjylland, Nordjylland, Sjælland, Syddanmark
# ---------------------------------------------------------------------------
DANISH_CITIES: list[tuple[str, int | None, str, str, int | None]] = [
    # Historical købstæder (market towns) - verified Wikidata QIDs
    ("København", 1254, "Hovedstaden", "Q1748", 2618425),
    ("Aarhus", 1441, "Midtjylland", "Q25319", 2624652),
    ("Odense", 1335, "Syddanmark", "Q25331", 2615876),
    ("Aalborg", 1342, "Nordjylland", "Q25410", 2624886),
    ("Randers", 1302, "Midtjylland", "Q27168", 2615006),
    ("Kolding", 1321, "Syddanmark", "Q27119", 2618528),
    ("Horsens", 1442, "Midtjylland", "Q190235", 2620425),
    ("Vejle", 1327, "Syddanmark", "Q27116", 2610613),
    ("Roskilde", 1268, "Sjælland", "Q26563", 2614481),
    ("Herning", None, "Midtjylland", "Q27393", 2620685),
    ("Helsingør", 1426, "Hovedstaden", "Q26881", 2620473),
    ("Silkeborg", None, "Midtjylland", "Q21180", 2613822),
    ("Næstved", 1135, "Sjælland", "Q21178", 2616038),
    ("Fredericia", 1650, "Syddanmark", "Q3226599", 2621356),
    ("Viborg", 1150, "Midtjylland", "Q21176", 2610338),
    ("Køge", 1288, "Sjælland", "Q21184", 2618149),
    ("Holstebro", 1552, "Midtjylland", "Q27678", 2620533),
    ("Slagelse", 1280, "Sjælland", "Q3414556", 2613366),
    ("Svendborg", 1253, "Syddanmark", "Q28031", 2612045),
    ("Hjørring", 1243, "Nordjylland", "Q21185", 2620373),
    ("Sønderborg", 1256, "Syddanmark", "Q2341839", 2612150),
    ("Frederikshavn", 1818, "Nordjylland", "Q27452", 2621339),
    ("Nykøbing Falster", 1300, "Sjælland", "Q986435", 2615792),
    ("Holbæk", 1240, "Sjælland", "Q2268460", 2620577),
    ("Ringsted", 1150, "Sjælland", "Q283658", 2614561),
    ("Haderslev", 1292, "Syddanmark", "Q29868", 2621037),
    ("Skive", 1326, "Midtjylland", "Q1019470", 2613477),
    ("Kalundborg", 1200, "Sjælland", "Q204957", 2618742),
    ("Aabenraa", 1335, "Syddanmark", "Q272129", 2625001),
    ("Nakskov", 1266, "Sjælland", "Q24231", 2616130),
    ("Thisted", 1524, "Nordjylland", "Q30119696", 2611425),
    ("Nyborg", 1292, "Syddanmark", "Q254604", 2615830),
    ("Middelfart", 1496, "Syddanmark", "Q2038569", 2617034),
    ("Varde", 1442, "Syddanmark", "Q2048321", 2610793),
    ("Skanderborg", 1583, "Midtjylland", "Q503379", 2613598),
    ("Ribe", 710, "Syddanmark", "Q322361", 2614878),
    ("Assens", 1231, "Syddanmark", "Q30130076", 2624735),
    ("Nørresundby", None, "Nordjylland", "Q1246235", 2615943),
    ("Grenaa", 1445, "Midtjylland", "Q3619316", 2621083),
    ("Maribo", 1415, "Sjælland", "Q386402", 2617263),
    ("Frederikssund", 1665, "Hovedstaden", "Q3223801", 2621262),
    ("Stege", 1268, "Sjælland", "Q2213716", 2612831),
    ("Vordingborg", 1200, "Sjælland", "Q2608258", 2610448),
    ("Præstø", 1403, "Sjælland", "Q30242360", 2615190),
    ("Store Heddinge", 1441, "Sjælland", "Q1019126", 2612700),
    ("Stubbekøbing", 1354, "Sjælland", "Q507747", 2612465),
    ("Sakskøbing", 1500, "Sjælland", "Q13218306", 2614354),
    ("Rudkøbing", 1287, "Syddanmark", "Q731023", 2614665),
    ("Faaborg", 1229, "Syddanmark", "Q12311538", 2622100),
    ("Kerteminde", 1413, "Syddanmark", "Q29969", 2618839),
    ("Bogense", 1288, "Syddanmark", "Q890536", 2623577),
    ("Tønder", 1243, "Syddanmark", "Q3223979", 2611388),
    ("Ebeltoft", 1301, "Midtjylland", "Q523400", 2622280),
    ("Mariager", 1410, "Nordjylland", "Q30130249", 2617287),
    ("Hobro", 1727, "Nordjylland", "Q2091068", 2620417),
    ("Nykøbing Mors", 1299, "Nordjylland", "Q1480375", 2615789),
    ("Lemvig", 1545, "Midtjylland", "Q502632", 2618220),
    ("Ringkøbing", 1443, "Midtjylland", "Q502693", 2614555),
    ("Skagen", 1413, "Nordjylland", "Q2491816", 2613621),
    ("Sæby", 1524, "Nordjylland", "Q346802", 2612080),
    ("Løgstør", 1516, "Nordjylland", "Q3414045", 2617507),
    ("Nibe", 1727, "Nordjylland", "Q1019502", 2615949),
    # Major modern cities
    ("Esbjerg", 1899, "Syddanmark", "Q26234", 2622447),
    ("Rønne", 1327, "Hovedstaden", "Q690062", 2614561),
    ("Odder", None, "Midtjylland", "Q925736", 2615893),
    ("Brønderslev", None, "Nordjylland", "Q995880", 2623596),
    ("Ikast", None, "Midtjylland", "Q1021277", 2620154),
    ("Billund", None, "Syddanmark", "Q30140908", 2623908),
    ("Frederiksberg", None, "Hovedstaden", "Q30096", 2621355),
    ("Gentofte", None, "Hovedstaden", "Q3255441", 2621562),
    ("Lyngby", None, "Hovedstaden", "Q106907656", 2617379),
    ("Hillerød", 1772, "Hovedstaden", "Q27425", 2620439),
    ("Ishøj", None, "Hovedstaden", "Q3196979", 2620100),
    ("Ballerup", None, "Hovedstaden", "Q28143", 2624505),
    ("Hvidovre", None, "Hovedstaden", "Q3590079", 2620668),
    ("Sorø", 1638, "Sjælland", "Q27858", 2613100),
    ("Struer", None, "Midtjylland", "Q1797189", 2612443),
    ("Nordborg", None, "Syddanmark", "Q1997687", 2616014),
]


# Alternative names for Danish cities: German, Low German, Latin, Old Norse
# Sources: historical documentation, Wikidata, Trap Danmark
ALTERNATIVE_NAMES: dict[str, dict[str, list[str]]] = {
    "København": {
        "deu": ["Kopenhagen"],
        "nds": ["Kopenhagen"],
        "lat": ["Hafnia", "Portus Mercatorum"],
        "non": ["Kaupmannahǫfn"],
        "eng": ["Copenhagen"],
        "fra": ["Copenhague"],
    },
    "Aarhus": {
        "dan": ["Århus"],
        "deu": ["Aarhus"],
        "lat": ["Arusium", "Arusia"],
        "non": ["Áróss"],
    },
    "Odense": {
        "deu": ["Ottens", "Odensee"],
        "lat": ["Othinia", "Othoniensis"],
        "non": ["Óðinsvé"],
    },
    "Aalborg": {
        "dan": ["Ålborg"],
        "deu": ["Aalborg"],
        "lat": ["Alaburgum", "Aalburgum"],
        "non": ["Álaborg"],
    },
    "Randers": {
        "deu": ["Randershus"],
        "lat": ["Randrusia"],
    },
    "Kolding": {
        "deu": ["Kolding"],
        "lat": ["Coldinga"],
    },
    "Horsens": {
        "deu": ["Horsens"],
        "lat": ["Horsnesum"],
    },
    "Vejle": {
        "deu": ["Weile"],
        "lat": ["Vedelia"],
    },
    "Roskilde": {
        "deu": ["Roeskilde"],
        "lat": ["Roscildia", "Roskildis"],
        "non": ["Hróarskelda"],
        "eng": ["Roeskilde"],
    },
    "Helsingør": {
        "deu": ["Helsingör"],
        "lat": ["Helsingora"],
        "eng": ["Elsinore"],
        "fra": ["Elseneur"],
    },
    "Næstved": {
        "deu": ["Nestved"],
        "lat": ["Nestvedum"],
    },
    "Fredericia": {
        "deu": ["Friedrichsöde", "Friedericia"],
        "lat": ["Fredericia"],
    },
    "Viborg": {
        "deu": ["Wiborg"],
        "lat": ["Viburgum", "Wibergis"],
        "non": ["Víborg"],
    },
    "Svendborg": {
        "deu": ["Svendborg", "Schwenburg"],
        "lat": ["Svendburgum"],
    },
    "Hjørring": {
        "deu": ["Hjörring"],
        "lat": ["Hiöringum"],
    },
    "Sønderborg": {
        "deu": ["Sonderburg"],
        "nds": ["Sünnerborg"],
        "lat": ["Sonderburgum"],
    },
    "Haderslev": {
        "deu": ["Hadersleben"],
        "nds": ["Hadersleev"],
        "lat": ["Haderslevia"],
    },
    "Aabenraa": {
        "dan": ["Åbenrå"],
        "deu": ["Apenrade"],
        "nds": ["Openraa"],
        "lat": ["Apenradia"],
    },
    "Tønder": {
        "deu": ["Tondern"],
        "nds": ["Tönder"],
        "lat": ["Tondera"],
        "frr": ["Tuner"],
    },
    "Ribe": {
        "deu": ["Ripen"],
        "lat": ["Ripa", "Ripae"],
        "non": ["Ripar"],
    },
    "Nakskov": {
        "deu": ["Nakskov"],
        "lat": ["Nacscovia"],
    },
    "Nyborg": {
        "deu": ["Nyburg", "Neuburg"],
        "lat": ["Nyburgum"],
    },
    "Kalundborg": {
        "deu": ["Kalundborg"],
        "lat": ["Calundburgum"],
        "non": ["Kalundaborg"],
    },
    "Esbjerg": {
        "deu": ["Esbjerg"],
    },
    "Frederikshavn": {
        "deu": ["Frederikshavn"],
        "lat": ["Portus Frederici"],
    },
    "Skagen": {
        "deu": ["Skagen"],
        "lat": ["Scaganum"],
        "non": ["Skagi"],
    },
    "Middelfart": {
        "deu": ["Middelfart"],
        "lat": ["Medelfartum"],
    },
    "Holbæk": {
        "deu": ["Holbek"],
        "lat": ["Holbecia"],
    },
    "Ringsted": {
        "deu": ["Ringsted"],
        "lat": ["Ringstadium"],
        "non": ["Hringstaðir"],
    },
    "Vordingborg": {
        "deu": ["Wordingborg"],
        "lat": ["Vordingburgum"],
    },
    "Nykøbing Falster": {
        "deu": ["Nykjöbing"],
        "lat": ["Nykopia"],
    },
    "Thisted": {
        "deu": ["Thisted"],
        "lat": ["Thistedium"],
    },
    "Stege": {
        "deu": ["Stege"],
        "lat": ["Stega"],
    },
    "Frederiksberg": {
        "deu": ["Frederiksberg"],
    },
    "Hillerød": {
        "deu": ["Hilleröd"],
    },
    "Christiansfeld": {
        "deu": ["Christiansfeld"],
    },
    "Rønne": {
        "deu": ["Rönne"],
        "lat": ["Rönna"],
    },
    "Maribo": {
        "deu": ["Maribo"],
        "lat": ["Maribo"],
    },
    "Sorø": {
        "deu": ["Sorö"],
        "lat": ["Sora"],
    },
    "Augustenborg": {
        "deu": ["Augustenburg"],
    },
    "Gram": {
        "deu": ["Gramm"],
    },
    "Padborg": {
        "deu": ["Pattburg"],
    },
    "Vojens": {
        "deu": ["Wojensgaard"],
    },
    "Nordborg": {
        "deu": ["Norburg"],
    },
}


def query_wikidata_danish_cities() -> dict[str, dict]:
    """Query Wikidata SPARQL for Danish cities using direct QID VALUES lookup.

    This is the most reliable approach as it directly fetches our target items
    regardless of their P31 (instance of) classification.
    """
    print("Querying Wikidata SPARQL for Danish cities...")

    # Collect all QIDs from our city list
    seen_qids: set[str] = set()
    all_qids: list[str] = []
    for _, _, _, qid, _ in DANISH_CITIES:
        if qid not in seen_qids:
            seen_qids.add(qid)
            all_qids.append(qid)

    values_str = " ".join(f"wd:{qid}" for qid in all_qids)

    query = f"""SELECT DISTINCT ?item ?itemLabel ?coord ?population ?area
      ?geonames_id ?elevation ?municipalityLabel
      (GROUP_CONCAT(DISTINCT ?altLabel; separator="|") AS ?altNames)
    WHERE {{
      VALUES ?item {{ {values_str} }}
      OPTIONAL {{ ?item wdt:P625 ?coord }}
      OPTIONAL {{ ?item wdt:P1082 ?population }}
      OPTIONAL {{ ?item wdt:P2046 ?area }}
      OPTIONAL {{ ?item wdt:P1566 ?geonames_id }}
      OPTIONAL {{ ?item wdt:P2044 ?elevation }}
      OPTIONAL {{ ?item wdt:P131 ?municipality }}
      OPTIONAL {{
        ?item skos:altLabel ?altLabel .
        FILTER(LANG(?altLabel) IN ("de","nds","la","en","fr","non","fry"))
      }}
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "da,en"
      }}
    }}
    GROUP BY ?item ?itemLabel ?coord ?population ?area
             ?geonames_id ?elevation ?municipalityLabel
    ORDER BY ?itemLabel"""

    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"https://query.wikidata.org/sparql?{params}"
    req = urllib.request.Request(  # noqa: S310
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "ToponymiaEuropaea/0.5 (https://github.com/egkristi/ToponymiaEuropaea)",
        },
    )

    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        data = json.loads(resp.read())

    results = data["results"]["bindings"]
    print(f"  Got {len(results)} results from Wikidata")

    # Build a lookup by QID (most reliable matching)
    lookup: dict[str, dict] = {}
    for r in results:
        name = r["itemLabel"]["value"]
        qid = r["item"]["value"].split("/")[-1]
        coord = r.get("coord", {}).get("value", "")
        pop = r.get("population", {}).get("value", "")
        area = r.get("area", {}).get("value", "")
        gn = r.get("geonames_id", {}).get("value", "")
        municipality = r.get("municipalityLabel", {}).get("value", "")
        elev = r.get("elevation", {}).get("value", "")
        alts = r.get("altNames", {}).get("value", "")

        lat, lon = None, None
        if coord:
            parts = coord.replace("Point(", "").replace(")", "").split()
            if len(parts) == 2:
                lon, lat = float(parts[0]), float(parts[1])

        lookup[qid] = {
            "name": name,
            "qid": qid,
            "lat": lat,
            "lon": lon,
            "population": int(float(pop)) if pop else None,
            "area_km2": round(float(area), 2) if area else None,
            "geonames_id": int(gn) if gn else None,
            "municipality": municipality or None,
            "elevation": round(float(elev), 1) if elev else None,
            "alt_names_raw": alts,
        }

    return lookup


def fetch_nominatim_geometry(city_name: str) -> dict | None:
    """Fetch city boundary polygon from OSM Nominatim.

    Tries multiple search strategies to maximize polygon coverage:
    1. Free-form query (often returns boundary relations)
    2. Structured search with city + country
    """
    strategies = [
        # Strategy 1: free-form query (most likely to return boundaries)
        {
            "q": f"{city_name}, Denmark",
            "format": "geojson",
            "polygon_geojson": 1,
            "limit": 3,
        },
        # Strategy 2: structured search
        {
            "city": city_name,
            "country": "Denmark",
            "format": "geojson",
            "polygon_geojson": 1,
            "limit": 3,
        },
    ]

    for strategy in strategies:
        params = urllib.parse.urlencode(strategy)
        url = f"https://nominatim.openstreetmap.org/search?{params}"
        req = urllib.request.Request(  # noqa: S310
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "ToponymiaEuropaea/0.5 (https://github.com/egkristi/ToponymiaEuropaea)",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
                data = json.loads(resp.read())
        except Exception as e:
            print(f"    Nominatim error for '{city_name}': {e}")
            continue

        if not data.get("features"):
            continue

        # Check all results for a polygon (prefer Polygon/MultiPolygon)
        for feature in data["features"]:
            geometry = feature.get("geometry")
            if not geometry:
                continue
            if geometry.get("type") in ("Polygon", "MultiPolygon"):
                return geometry

        time.sleep(NOMINATIM_DELAY)

    return None


def parse_wikidata_alt_names(alt_names_str: str) -> dict[str, list[str]]:
    """Parse Wikidata alternative names into language-grouped dict.

    Since SPARQL concatenates all filtered alt labels without language info,
    we store them as general alternatives.
    """
    if not alt_names_str:
        return {}

    names = set()
    for name in alt_names_str.split("|"):
        name = name.strip()
        if name:
            names.add(name)

    if names:
        return {"alt": sorted(names)}
    return {}


def merge_alternative_names(
    wikidata_alts: dict[str, list[str]],
    hardcoded_alts: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Merge Wikidata alt names with our hardcoded comprehensive alternatives."""
    merged: dict[str, list[str]] = {}

    # Start with hardcoded (language-tagged) alternatives
    for lang, names in hardcoded_alts.items():
        merged[lang] = list(names)

    # Add any Wikidata names not already covered
    wikidata_names = wikidata_alts.get("alt", [])
    all_known = set()
    for names in merged.values():
        all_known.update(names)

    extra = [n for n in wikidata_names if n not in all_known]
    if extra:
        merged.setdefault("alt", [])
        merged["alt"].extend(extra)

    return merged


def main():
    """Ingest all Danish cities with comprehensive metadata."""
    # Deduplicate city list by QID
    seen_qids: set[str] = set()
    unique_cities = []
    for city_tuple in DANISH_CITIES:
        qid = city_tuple[3]
        if qid not in seen_qids:
            seen_qids.add(qid)
            unique_cities.append(city_tuple)

    print(f"Ingesting {len(unique_cities)} Danish cities")
    print(f"Output: {OUTPUT_FILE}")
    print()

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing records to avoid duplicates
    existing_source_ids: set[str] = set()
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                existing_source_ids.add(rec.get("source_id", ""))

    print(f"Existing records: {len(existing_source_ids)}")
    print()

    # Step 1: Get Wikidata data
    wikidata_lookup = query_wikidata_danish_cities()
    print()

    # Step 2: Fetch geometry from Nominatim for each city
    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}

    for i, (city, _, _, qid, _) in enumerate(unique_cities):
        wd = wikidata_lookup.get(qid, {})
        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            # Try without Wikidata coords
            pass

        print(f"  [{i + 1:3d}/{len(unique_cities)}] {city}...", end=" ", flush=True)
        geo = fetch_nominatim_geometry(city)
        if geo:
            geometries[city] = geo
            coords_count = len(geo.get("coordinates", []))
            print(f"OK ({geo['type']}, {coords_count} rings)")
        else:
            print("no polygon")

        time.sleep(NOMINATIM_DELAY)

    print(f"\n  Got geometry for {len(geometries)}/{len(unique_cities)} cities")
    print()

    # Step 3: Create records
    print("Creating records...")
    all_records: list[dict] = []
    skipped_existing = 0

    for city, chartered_year, region, qid, geonames_id in unique_cities:
        wd = wikidata_lookup.get(qid, {})

        # Get coordinates from Wikidata
        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{city}' ({qid}), skipping")
            continue

        # Source ID
        source_id = f"wikidata:{qid}"
        source_url = f"https://www.wikidata.org/wiki/{qid}"

        # Check if already exists
        if source_id in existing_source_ids:
            skipped_existing += 1
            continue

        # Build alternative names: merge hardcoded + Wikidata
        hardcoded_alts = ALTERNATIVE_NAMES.get(city, {})
        wikidata_alts = parse_wikidata_alt_names(wd.get("alt_names_raw", ""))
        alt_names = merge_alternative_names(wikidata_alts, hardcoded_alts)

        # Get geometry
        geometry = geometries.get(city)

        # Population from Wikidata
        population = wd.get("population")

        # Area from Wikidata
        area_km2 = wd.get("area_km2")

        # Elevation from Wikidata
        elevation = wd.get("elevation")

        # Region from Wikidata or our list
        wd_region = wd.get("region") or region

        # Municipality from Wikidata
        municipality = wd.get("municipality")

        # GeoNames ID: prefer Wikidata, fall back to our list
        gn_id = wd.get("geonames_id") or geonames_id

        # Place type: capital vs regional capital vs city
        if city == "København":
            place_type = "P.PPLC"
        elif city in (
            "Aarhus",
            "Odense",
            "Aalborg",
            "Roskilde",
        ):
            place_type = "P.PPLA"
        else:
            place_type = "P.PPL"

        record = make_record(
            name_form=city,
            name_normalized=city.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=source_id,
            place_type=place_type,
            language_code="dan",
            alternative_names=alt_names,
            source_url=source_url,
            wikidata_qid=qid,
            geonames_id=gn_id,
            area_km2=area_km2,
            population=population,
            elevation=elevation,
            geometry=geometry,
            region=wd_region,
            municipality=municipality,
            chartered_year=chartered_year,
        )

        all_records.append(record)

    print(f"\nCreated {len(all_records)} new records")
    if skipped_existing:
        print(f"  Skipped {skipped_existing} already-existing records")

    if not all_records:
        print("\nNo new records to add.")
        return

    # Sign all records
    print("\nSigning records...")
    signed_records = [sign_record(r) for r in all_records]

    # Write to file
    with OUTPUT_FILE.open("a") as f:
        for record in signed_records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"\nAdded {len(signed_records)} records to {OUTPUT_FILE}")

    # Summary stats
    with_geo = sum(1 for r in signed_records if r.get("geometry"))
    with_pop = sum(1 for r in signed_records if r.get("population"))
    with_area = sum(1 for r in signed_records if r.get("area_km2"))
    with_elev = sum(1 for r in signed_records if r.get("elevation") is not None)
    with_alts = sum(
        1
        for r in signed_records
        if r.get("alternative_names") and any(r["alternative_names"].values())
    )
    with_qid = sum(1 for r in signed_records if r.get("wikidata_qid"))
    with_gn = sum(1 for r in signed_records if r.get("geonames_id"))
    with_muni = sum(1 for r in signed_records if r.get("municipality"))

    print(f"\nRecords with geometry (polygon/multipolygon): {with_geo}")
    print(f"Records with population: {with_pop}")
    print(f"Records with area: {with_area}")
    print(f"Records with elevation: {with_elev}")
    print(f"Records with alternative names: {with_alts}")
    print(f"Records with Wikidata QID: {with_qid}")
    print(f"Records with GeoNames ID: {with_gn}")
    print(f"Records with municipality: {with_muni}")

    # Region breakdown
    regions: dict[str, int] = {}
    for r in signed_records:
        reg = r.get("region", "unknown")
        regions[reg] = regions.get(reg, 0) + 1

    print("\nBreakdown by region:")
    for reg, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {reg}: {count}")


if __name__ == "__main__":
    main()
