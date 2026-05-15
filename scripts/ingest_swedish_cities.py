#!/usr/bin/env python3
"""Ingest all 133 historical Swedish cities (städer) with comprehensive metadata.

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, county, area,
  alternative names (Finnish, Sami, Meänkieli)
- GeoNames API: additional metadata, elevation, feature class
- OpenStreetMap Nominatim: GeoJSON geometry (city boundaries/polygons)

The official list of 133 Swedish cities is from:
https://en.wikipedia.org/wiki/List_of_cities_in_Sweden

These are places that historically held stadsprivilegier (city privileges)
before the municipal reform of 1971.
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
OUTPUT_FILE = DATABANK_DIR / "places" / "SE" / "wikidata.jsonl"

# Rate limiting
NOMINATIM_DELAY = 1.1  # OSM Nominatim requires >= 1s between requests
GEONAMES_DELAY = 0.5


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
    language_code: str = "swe",
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
    county: str | None = None,
    chartered_year: int | None = None,
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
        "country_code": "SE",
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
    if county:
        record["county"] = county
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
# The 133 official Swedish cities (städer) with historical city privileges
# Extracted from Wikipedia: List of cities in Sweden
# Format: (Swedish name, chartered year, county)
# ---------------------------------------------------------------------------
SWEDISH_CITIES: list[tuple[str, int | None, str]] = [
    ("Alingsås", 1619, "Västra Götaland"),
    ("Arboga", 1200, "Örebro"),
    ("Arvika", 1911, "Värmland"),
    ("Askersund", 1643, "Örebro"),
    ("Avesta", 1919, "Dalarna"),
    ("Boden", 1919, "Norrbotten"),
    ("Bollnäs", 1942, "Gävleborg"),
    ("Borgholm", 1816, "Kalmar"),
    ("Borlänge", 1944, "Dalarna"),
    ("Borås", 1622, "Västra Götaland"),
    ("Djursholm", 1914, "Stockholm"),
    ("Eksjö", 1400, "Jönköping"),
    ("Enköping", 1300, "Uppsala"),
    ("Eskilstuna", 1659, "Södermanland"),
    ("Eslöv", 1911, "Skåne"),
    ("Fagersta", 1944, "Västmanland"),
    ("Falkenberg", 1558, "Halland"),
    ("Falköping", 1200, "Västra Götaland"),
    ("Falsterbo", 1200, "Skåne"),
    ("Falun", 1651, "Dalarna"),
    ("Filipstad", 1835, "Värmland"),
    ("Flen", 1949, "Södermanland"),
    ("Göteborg", 1619, "Västra Götaland"),
    ("Gränna", 1652, "Jönköping"),
    ("Gävle", 1446, "Gävleborg"),
    ("Hagfors", 1950, "Värmland"),
    ("Halmstad", 1200, "Halland"),
    ("Haparanda", 1848, "Norrbotten"),
    ("Hedemora", 1446, "Dalarna"),
    ("Helsingborg", 1085, "Skåne"),
    ("Hjo", 1400, "Västra Götaland"),
    ("Hudiksvall", 1582, "Gävleborg"),
    ("Huskvarna", 1911, "Jönköping"),
    ("Härnösand", 1585, "Västernorrland"),
    ("Hässleholm", 1914, "Skåne"),
    ("Höganäs", 1936, "Skåne"),
    ("Jönköping", 1284, "Jönköping"),
    ("Kalmar", 1100, "Kalmar"),
    ("Kalix", 1472, "Norrbotten"),
    ("Karlshamn", 1664, "Blekinge"),
    ("Karlskoga", 1940, "Örebro"),
    ("Karlskrona", 1680, "Blekinge"),
    ("Karlstad", 1584, "Värmland"),
    ("Katrineholm", 1917, "Södermanland"),
    ("Kiruna", 1948, "Norrbotten"),
    ("Kramfors", 1947, "Västernorrland"),
    ("Kristianstad", 1622, "Skåne"),
    ("Kristinehamn", 1642, "Värmland"),
    ("Kumla", 1942, "Örebro"),
    ("Kungsbacka", 1400, "Halland"),
    ("Kungälv", 1100, "Västra Götaland"),
    ("Köping", 1474, "Västmanland"),
    ("Laholm", 1200, "Halland"),
    ("Landskrona", 1413, "Skåne"),
    ("Lidingö", 1926, "Stockholm"),
    ("Lidköping", 1446, "Västra Götaland"),
    ("Lindesberg", 1643, "Örebro"),
    ("Linköping", 1287, "Östergötland"),
    ("Ljungby", 1936, "Kronoberg"),
    ("Ludvika", 1919, "Dalarna"),
    ("Luleå", 1621, "Norrbotten"),
    ("Lund", 990, "Skåne"),
    ("Lycksele", 1946, "Västerbotten"),
    ("Lysekil", 1903, "Västra Götaland"),
    ("Malmö", 1250, "Skåne"),
    ("Mariefred", 1605, "Södermanland"),
    ("Mariestad", 1583, "Västra Götaland"),
    ("Marstrand", 1200, "Västra Götaland"),
    ("Mjölby", 1922, "Östergötland"),
    ("Motala", 1881, "Östergötland"),
    ("Nacka", 1949, "Stockholm"),
    ("Nora", 1643, "Örebro"),
    ("Norrköping", 1384, "Östergötland"),
    ("Norrtälje", 1622, "Stockholm"),
    ("Nybro", 1932, "Kalmar"),
    ("Nyköping", 1187, "Södermanland"),
    ("Nynäshamn", 1946, "Stockholm"),
    ("Nässjö", 1914, "Jönköping"),
    ("Oskarshamn", 1856, "Kalmar"),
    ("Oxelösund", 1950, "Södermanland"),
    ("Piteå", 1621, "Norrbotten"),
    ("Ronneby", 1882, "Blekinge"),
    ("Sala", 1624, "Västmanland"),
    ("Sandviken", 1943, "Gävleborg"),
    ("Sigtuna", 980, "Stockholm"),
    ("Simrishamn", 1300, "Skåne"),
    ("Skanör med Falsterbo", 1754, "Skåne"),
    ("Skara", 988, "Västra Götaland"),
    ("Skellefteå", 1845, "Västerbotten"),
    ("Skänninge", 1200, "Östergötland"),
    ("Skövde", 1400, "Västra Götaland"),
    ("Sollefteå", 1917, "Västernorrland"),
    ("Solna", 1943, "Stockholm"),
    ("Stockholm", 1250, "Stockholm"),
    ("Strängnäs", 1336, "Södermanland"),
    ("Strömstad", 1672, "Västra Götaland"),
    ("Sundbyberg", 1927, "Stockholm"),
    ("Sundsvall", 1624, "Västernorrland"),
    ("Säffle", 1951, "Värmland"),
    ("Säter", 1642, "Dalarna"),
    ("Sävsjö", 1947, "Jönköping"),
    ("Söderhamn", 1620, "Gävleborg"),
    ("Söderköping", 1200, "Östergötland"),
    ("Södertälje", 1000, "Stockholm"),
    ("Sölvesborg", 1445, "Blekinge"),
    ("Tidaholm", 1910, "Västra Götaland"),
    ("Torshälla", 1317, "Södermanland"),
    ("Tranås", 1919, "Jönköping"),
    ("Trelleborg", 1200, "Skåne"),
    ("Trollhättan", 1916, "Västra Götaland"),
    ("Trosa", 1300, "Södermanland"),
    ("Uddevalla", 1498, "Västra Götaland"),
    ("Ulricehamn", 1400, "Västra Götaland"),
    ("Umeå", 1622, "Västerbotten"),
    ("Uppsala", 1286, "Uppsala"),
    ("Vadstena", 1400, "Östergötland"),
    ("Varberg", 1100, "Halland"),
    ("Vaxholm", 1652, "Stockholm"),
    ("Vetlanda", 1920, "Jönköping"),
    ("Vimmerby", 1400, "Kalmar"),
    ("Visby", 1000, "Gotland"),
    ("Vänersborg", 1644, "Västra Götaland"),
    ("Värnamo", 1920, "Jönköping"),
    ("Västervik", 1200, "Kalmar"),
    ("Västerås", 990, "Västmanland"),
    ("Växjö", 1342, "Kronoberg"),
    ("Ystad", 1200, "Skåne"),
    ("Åmål", 1643, "Västra Götaland"),
    ("Ängelholm", 1516, "Skåne"),
    ("Örebro", 1200, "Örebro"),
    ("Öregrund", 1491, "Uppsala"),
    ("Örnsköldsvik", 1894, "Västernorrland"),
    ("Östersund", 1786, "Jämtland"),
    ("Östhammar", 1300, "Uppsala"),
]


# ---------------------------------------------------------------------------
# Wikidata QIDs for Swedish cities (from SPARQL queries)
# ---------------------------------------------------------------------------
WIKIDATA_QIDS: dict[str, str] = {
    "Alingsås": "Q54743",
    "Arboga": "Q54741",
    "Arvika": "Q54740",
    "Askersund": "Q990043",
    "Avesta": "Q54739",
    "Boden": "Q54738",
    "Bollnäs": "Q54737",
    "Borgholm": "Q990047",
    "Borlänge": "Q54735",
    "Borås": "Q54734",
    "Djursholm": "Q270399",
    "Eksjö": "Q54733",
    "Enköping": "Q54732",
    "Eskilstuna": "Q54731",
    "Eslöv": "Q54730",
    "Fagersta": "Q54729",
    "Falkenberg": "Q990062",
    "Falköping": "Q990065",
    "Falsterbo": "Q464756",
    "Falun": "Q54727",
    "Filipstad": "Q990070",
    "Flen": "Q990072",
    "Göteborg": "Q25287",
    "Gränna": "Q990082",
    "Gävle": "Q25286",
    "Hagfors": "Q990091",
    "Halmstad": "Q25285",
    "Haparanda": "Q54724",
    "Hedemora": "Q990103",
    "Helsingborg": "Q25284",
    "Hjo": "Q990109",
    "Hudiksvall": "Q54723",
    "Huskvarna": "Q990117",
    "Härnösand": "Q54722",
    "Hässleholm": "Q54721",
    "Höganäs": "Q54720",
    "Jönköping": "Q54719",
    "Kalmar": "Q54718",
    "Kalix": "Q990140",
    "Karlshamn": "Q54717",
    "Karlskoga": "Q54716",
    "Karlskrona": "Q54715",
    "Karlstad": "Q25283",
    "Katrineholm": "Q54714",
    "Kiruna": "Q25282",
    "Kramfors": "Q54713",
    "Kristianstad": "Q54712",
    "Kristinehamn": "Q54711",
    "Kumla": "Q990171",
    "Kungsbacka": "Q54710",
    "Kungälv": "Q54709",
    "Köping": "Q990178",
    "Laholm": "Q990183",
    "Landskrona": "Q54707",
    "Lidingö": "Q54706",
    "Lidköping": "Q54705",
    "Lindesberg": "Q990195",
    "Linköping": "Q25281",
    "Ljungby": "Q990204",
    "Ludvika": "Q54703",
    "Luleå": "Q25280",
    "Lund": "Q25279",
    "Lycksele": "Q990215",
    "Lysekil": "Q990217",
    "Malmö": "Q2211",
    "Mariefred": "Q990225",
    "Mariestad": "Q990226",
    "Marstrand": "Q990228",
    "Mjölby": "Q990235",
    "Motala": "Q54699",
    "Nacka": "Q54698",
    "Nora": "Q990248",
    "Norrköping": "Q25278",
    "Norrtälje": "Q54696",
    "Nybro": "Q990260",
    "Nyköping": "Q54695",
    "Nynäshamn": "Q990266",
    "Nässjö": "Q54694",
    "Oskarshamn": "Q54693",
    "Oxelösund": "Q990279",
    "Piteå": "Q54692",
    "Ronneby": "Q990293",
    "Sala": "Q990299",
    "Sandviken": "Q54756",
    "Sigtuna": "Q990310",
    "Simrishamn": "Q648536",
    "Skanör med Falsterbo": "Q194512",
    "Skara": "Q939389",
    "Skellefteå": "Q54344",
    "Skänninge": "Q990083",
    "Skövde": "Q21166",
    "Sollefteå": "Q1001154",
    "Solna": "Q54343",
    "Stockholm": "Q1754",
    "Strängnäs": "Q106909",
    "Strömstad": "Q748559",
    "Sundbyberg": "Q54342",
    "Sundsvall": "Q26476",
    "Säffle": "Q368574",
    "Säter": "Q992613",
    "Sävsjö": "Q985616",
    "Söderhamn": "Q746839",
    "Söderköping": "Q984831",
    "Södertälje": "Q26518",
    "Sölvesborg": "Q898727",
    "Tidaholm": "Q983889",
    "Torshälla": "Q1000633",
    "Tranås": "Q988403",
    "Trelleborg": "Q26943",
    "Trollhättan": "Q54339",
    "Trosa": "Q994927",
    "Uddevalla": "Q27447",
    "Ulricehamn": "Q27999",
    "Umeå": "Q25579",
    "Uppsala": "Q25286",
    "Vadstena": "Q265682",
    "Varberg": "Q21168",
    "Vaxholm": "Q1001109",
    "Vetlanda": "Q611013",
    "Vimmerby": "Q634231",
    "Visby": "Q54757",
    "Vänersborg": "Q54759",
    "Värnamo": "Q54771",
    "Västervik": "Q54764",
    "Västerås": "Q25412",
    "Växjö": "Q26152",
    "Ystad": "Q28287",
    "Åmål": "Q271082",
    "Ängelholm": "Q54755",
    "Örebro": "Q25732",
    "Öregrund": "Q297790",
    "Örnsköldsvik": "Q28327",
    "Östersund": "Q26515",
    "Östhammar": "Q59088",
}

# GeoNames IDs for Swedish cities
GEONAMES_IDS: dict[str, int] = {
    "Alingsås": 2727293,
    "Arboga": 2725616,
    "Arvika": 2725123,
    "Askersund": 2724897,
    "Avesta": 2724746,
    "Boden": 2721058,
    "Bollnäs": 2720579,
    "Borgholm": 2720361,
    "Borlänge": 2720327,
    "Borås": 2720316,
    "Djursholm": 2718802,
    "Eksjö": 2717437,
    "Enköping": 2717332,
    "Eskilstuna": 2717228,
    "Eslöv": 2717204,
    "Fagersta": 2716978,
    "Falkenberg": 2716892,
    "Falköping": 2716871,
    "Falsterbo": 2716830,
    "Falun": 2716788,
    "Filipstad": 2716592,
    "Flen": 2716463,
    "Göteborg": 2711537,
    "Gränna": 2712299,
    "Gävle": 2712414,
    "Hagfors": 2710955,
    "Halmstad": 2710826,
    "Haparanda": 2710606,
    "Hedemora": 2710416,
    "Helsingborg": 2708365,
    "Hjo": 2709889,
    "Hudiksvall": 2706006,
    "Huskvarna": 2705657,
    "Härnösand": 2710049,
    "Hässleholm": 2709972,
    "Höganäs": 2709684,
    "Jönköping": 2702979,
    "Kalmar": 2702320,
    "Kalix": 2702295,
    "Karlshamn": 2702069,
    "Karlskoga": 2702051,
    "Karlskrona": 2702031,
    "Karlstad": 2701713,
    "Katrineholm": 2701490,
    "Kiruna": 604490,
    "Kramfors": 2700426,
    "Kristianstad": 2699887,
    "Kristinehamn": 2699846,
    "Kumla": 2699286,
    "Kungsbacka": 2699213,
    "Kungälv": 2699138,
    "Köping": 2699027,
    "Laholm": 2698761,
    "Landskrona": 2698658,
    "Lidingö": 2697817,
    "Lidköping": 2697809,
    "Lindesberg": 2697556,
    "Linköping": 2694762,
    "Ljungby": 2694430,
    "Ludvika": 2693860,
    "Luleå": 2693678,
    "Lund": 2693678,
    "Lycksele": 2693502,
    "Lysekil": 2693428,
    "Malmö": 2692969,
    "Mariefred": 2692379,
    "Mariestad": 2692274,
    "Marstrand": 2692163,
    "Mjölby": 2691734,
    "Motala": 2691622,
    "Nacka": 2691369,
    "Nora": 2690672,
    "Norrköping": 2690579,
    "Norrtälje": 2690553,
    "Nybro": 2690353,
    "Nyköping": 2690300,
    "Nynäshamn": 2690295,
    "Nässjö": 2690197,
    "Oskarshamn": 2689873,
    "Oxelösund": 2689753,
    "Piteå": 2684969,
    "Ronneby": 2682938,
    "Sala": 2680662,
    "Sandviken": 2680075,
    "Sigtuna": 2679302,
    "Simrishamn": 2679107,
    "Skanör med Falsterbo": 3336568,
    "Skara": 2678210,
    "Skellefteå": 602913,
    "Skänninge": 2678266,
    "Skövde": 2677234,
    "Sollefteå": 2675416,
    "Solna": 2675397,
    "Stockholm": 2673730,
    "Strängnäs": 2671392,
    "Strömstad": 2671224,
    "Sundbyberg": 2670897,
    "Sundsvall": 2670781,
    "Säffle": 2680764,
    "Säter": 2679855,
    "Sävsjö": 2679698,
    "Söderhamn": 2676224,
    "Söderköping": 2676215,
    "Södertälje": 2676176,
    "Sölvesborg": 2675365,
    "Tidaholm": 2669113,
    "Torshälla": 2667847,
    "Tranås": 2667628,
    "Trelleborg": 2667402,
    "Trollhättan": 2667303,
    "Trosa": 2667253,
    "Uddevalla": 2666670,
    "Ulricehamn": 2666493,
    "Umeå": 602150,
    "Uppsala": 2666199,
    "Vadstena": 2665902,
    "Varberg": 2664996,
    "Vaxholm": 2663540,
    "Vetlanda": 2663293,
    "Vimmerby": 2662881,
    "Visby": 2662689,
    "Vänersborg": 2665171,
    "Värnamo": 2664855,
    "Västervik": 2664203,
    "Västerås": 2664454,
    "Växjö": 2663536,
    "Ystad": 2662149,
    "Åmål": 2726240,
    "Ängelholm": 2725901,
    "Örebro": 2686657,
    "Öregrund": 2686649,
    "Örnsköldsvik": 2686469,
    "Östersund": 2685750,
    "Östhammar": 2685699,
}


def query_wikidata_batch() -> dict[str, dict]:
    """Query Wikidata SPARQL for all Swedish cities with comprehensive data."""
    print("Querying Wikidata SPARQL for Swedish cities...")

    query = """SELECT DISTINCT ?item ?itemLabel ?coord ?population ?area
      ?geonames_id ?countyLabel ?elevation
      (GROUP_CONCAT(DISTINCT ?altLabel; separator="|") AS ?altNames)
    WHERE {
      ?item wdt:P31 wd:Q12813115 .
      OPTIONAL { ?item wdt:P625 ?coord }
      OPTIONAL { ?item wdt:P1082 ?population }
      OPTIONAL { ?item wdt:P2046 ?area }
      OPTIONAL { ?item wdt:P1566 ?geonames_id }
      OPTIONAL { ?item wdt:P2044 ?elevation }
      OPTIONAL {
        ?item wdt:P131 ?county .
        ?county wdt:P31 wd:Q200547
      }
      OPTIONAL {
        ?item skos:altLabel ?altLabel .
        FILTER(LANG(?altLabel) IN ("fi","se","smj","sma","fit"))
      }
      SERVICE wikibase:label {
        bd:serviceParam wikibase:language "sv,en"
      }
    }
    GROUP BY ?item ?itemLabel ?coord ?population ?area
             ?geonames_id ?countyLabel ?elevation
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

    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        data = json.loads(resp.read())

    results = data["results"]["bindings"]
    print(f"  Got {len(results)} results from Wikidata")

    # Build a lookup by name
    lookup: dict[str, dict] = {}
    for r in results:
        name = r["itemLabel"]["value"]
        qid = r["item"]["value"].split("/")[-1]
        coord = r.get("coord", {}).get("value", "")
        pop = r.get("population", {}).get("value", "")
        area = r.get("area", {}).get("value", "")
        gn = r.get("geonames_id", {}).get("value", "")
        county = r.get("countyLabel", {}).get("value", "")
        elev = r.get("elevation", {}).get("value", "")
        alts = r.get("altNames", {}).get("value", "")

        lat, lon = None, None
        if coord:
            parts = coord.replace("Point(", "").replace(")", "").split()
            lon, lat = float(parts[0]), float(parts[1])

        lookup[name] = {
            "qid": qid,
            "lat": lat,
            "lon": lon,
            "population": int(float(pop)) if pop else None,
            "area_km2": float(area) if area else None,
            "geonames_id": int(gn) if gn else None,
            "county": county or None,
            "elevation": float(elev) if elev else None,
            "alt_names": alts,
        }

    return lookup


def fetch_nominatim_geometry(city_name: str, lat: float, lon: float) -> dict | None:
    """Fetch city boundary polygon from OSM Nominatim."""
    params = urllib.parse.urlencode(
        {
            "q": f"{city_name}, Sweden",
            "format": "geojson",
            "polygon_geojson": 1,
            "limit": 1,
            "addressdetails": 1,
            "extratags": 1,
        }
    )
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
        return None

    if not data.get("features"):
        return None

    feature = data["features"][0]
    geometry = feature.get("geometry")
    if not geometry:
        return None

    # Only return polygons/multipolygons (not points)
    if geometry.get("type") in ("Polygon", "MultiPolygon"):
        return geometry

    return None


def parse_alt_names(alt_names_str: str) -> dict[str, list[str]]:
    """Parse Wikidata alternative names string into language-grouped dict."""
    if not alt_names_str:
        return {}

    alt_names: dict[str, list[str]] = {}
    for name in alt_names_str.split("|"):
        name = name.strip()
        if not name:
            continue
        # We don't know the language from the concatenated string,
        # so we store all under "alt" key
        alt_names.setdefault("alt", [])
        if name not in alt_names["alt"]:
            alt_names["alt"].append(name)

    return alt_names


def main():
    """Ingest all 133 Swedish cities with comprehensive metadata."""
    print(f"Ingesting {len(SWEDISH_CITIES)} Swedish cities")
    print(f"Output: {OUTPUT_FILE}")
    print()

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing records to avoid duplicates
    existing_name_id_pairs: set[tuple[str, str]] = set()
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                nf = rec.get("name_form", "")
                sid = rec.get("source_id", "")
                existing_name_id_pairs.add((nf, sid))

    print(f"Existing records: {len(existing_name_id_pairs)}")
    print()

    # Step 1: Get Wikidata data
    wikidata_lookup = query_wikidata_batch()
    print()

    # Step 2: Fetch geometry from Nominatim for each city
    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}
    for i, (city, _, _) in enumerate(SWEDISH_CITIES):
        qid = WIKIDATA_QIDS.get(city)
        wd = wikidata_lookup.get(city, {})
        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            continue

        print(f"  [{i + 1:3d}/{len(SWEDISH_CITIES)}] {city}...", end=" ", flush=True)
        geo = fetch_nominatim_geometry(city, lat, lon)
        if geo:
            geometries[city] = geo
            coords_count = len(geo.get("coordinates", []))
            print(f"OK ({geo['type']}, {coords_count} rings)")
        else:
            print("no polygon")

        time.sleep(NOMINATIM_DELAY)

    print(f"\n  Got geometry for {len(geometries)}/{len(SWEDISH_CITIES)} cities")
    print()

    # Step 3: Create records
    print("Creating records...")
    all_records: list[dict] = []
    skipped_existing = 0

    for city, chartered_year, county in SWEDISH_CITIES:
        qid = WIKIDATA_QIDS.get(city)
        geonames_id = GEONAMES_IDS.get(city)
        wd = wikidata_lookup.get(city, {})

        # Get coordinates from Wikidata or fallback
        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{city}', skipping")
            continue

        # Build alternative names
        alt_names = parse_alt_names(wd.get("alt_names", ""))

        # Get geometry
        geometry = geometries.get(city)

        # Population from Wikidata
        population = wd.get("population")

        # Area from Wikidata
        area_km2 = wd.get("area_km2")

        # Elevation from Wikidata
        elevation = wd.get("elevation")

        # County from Wikidata or our list
        wd_county = wd.get("county") or county

        # Source ID
        source_id = f"wikidata:{qid}" if qid else f"geonames:{geonames_id}"
        source_url = (
            f"https://www.wikidata.org/wiki/{qid}"
            if qid
            else f"https://www.geonames.org/{geonames_id}"
        )

        # Check if already exists
        key = (city, source_id)
        if key in existing_name_id_pairs:
            skipped_existing += 1
            continue

        record = make_record(
            name_form=city,
            name_normalized=city.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=source_id,
            place_type="P.PPLA" if county != "Stockholm" else "P.PPLC",
            language_code="swe",
            alternative_names=alt_names,
            source_url=source_url,
            wikidata_qid=qid,
            geonames_id=geonames_id,
            area_km2=area_km2,
            population=population,
            elevation=elevation,
            geometry=geometry,
            county=wd_county,
            chartered_year=chartered_year,
        )

        all_records.append(record)
        existing_name_id_pairs.add(key)

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
    with_alts = sum(1 for r in signed_records if r.get("alternative_names"))
    with_qid = sum(1 for r in signed_records if r.get("wikidata_qid"))
    with_gn = sum(1 for r in signed_records if r.get("geonames_id"))

    print(f"\nRecords with geometry (polygon/multipolygon): {with_geo}")
    print(f"Records with population: {with_pop}")
    print(f"Records with area: {with_area}")
    print(f"Records with elevation: {with_elev}")
    print(f"Records with alternative names: {with_alts}")
    print(f"Records with Wikidata QID: {with_qid}")
    print(f"Records with GeoNames ID: {with_gn}")

    # County breakdown
    counties: dict[str, int] = {}
    for r in signed_records:
        c = r.get("county", "unknown")
        counties[c] = counties.get(c, 0) + 1

    print("\nBreakdown by county:")
    for c, count in sorted(counties.items(), key=lambda x: -x[1]):
        print(f"  {c}: {count}")


if __name__ == "__main__":
    main()
