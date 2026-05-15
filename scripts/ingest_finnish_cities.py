#!/usr/bin/env python3
"""Ingest all Finnish cities (kaupunki) with comprehensive metadata.

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, region, area,
  alternative names (Swedish, Sami, Latin, German, Russian, English)
- OpenStreetMap Nominatim: GeoJSON geometry (city boundaries/polygons)

Finland has 107 municipalities with kaupunki (city) status as of 2024.
This includes all historical cities and municipalities that have adopted
city status. Finland is officially bilingual (Finnish + Swedish), with
many cities having official Swedish names, particularly on the coast and
in the Åland Islands. Northern cities may also have Sami names.

Regions (maakunnat): Finland has 19 regions.

References:
- https://fi.wikipedia.org/wiki/Luettelo_Suomen_kaupungeista
- https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Finland
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
OUTPUT_FILE = DATABANK_DIR / "places" / "FI" / "wikidata.jsonl"

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
    language_code: str = "fin",
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
    city_rights_year: int | None = None,
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
        "country_code": "FI",
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
    if city_rights_year is not None:
        record["city_rights_year"] = city_rights_year
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    # Add H3 indices
    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ---------------------------------------------------------------------------
# Finnish cities: All kaupunki (city-status municipalities)
# Tuple: (Finnish name, city_rights_year, region, wikidata_qid, geonames_id)
#
# Regions (19 maakunnat):
#   Uusimaa, Varsinais-Suomi, Satakunta, Kanta-Häme, Pirkanmaa,
#   Päijät-Häme, Kymenlaakso, Etelä-Karjala, Etelä-Savo, Pohjois-Savo,
#   Pohjois-Karjala, Keski-Suomi, Etelä-Pohjanmaa, Pohjanmaa,
#   Keski-Pohjanmaa, Pohjois-Pohjanmaa, Kainuu, Lappi, Ahvenanmaa
# ---------------------------------------------------------------------------
FINNISH_CITIES: list[tuple[str, int | None, str, str, int]] = [
    # Major cities (over 100k)
    ("Helsinki", 1550, "Uusimaa", "Q1757", 658225),
    ("Espoo", 1972, "Uusimaa", "Q47034", 660129),
    ("Tampere", 1779, "Pirkanmaa", "Q40840", 634964),
    ("Vantaa", 1972, "Uusimaa", "Q127623", 632453),
    ("Oulu", 1605, "Pohjois-Pohjanmaa", "Q47048", 643492),
    ("Turku", 1229, "Varsinais-Suomi", "Q38511", 633680),
    # Large cities (50k-100k)
    ("Jyväskylä", 1837, "Keski-Suomi", "Q134620", 655194),
    ("Lahti", 1905, "Päijät-Häme", "Q28911", 648360),
    ("Kuopio", 1775, "Pohjois-Savo", "Q162279", 650224),
    ("Pori", 1558, "Satakunta", "Q180233", 638726),
    ("Kouvola", 1960, "Kymenlaakso", "Q204382", 650893),
    ("Joensuu", 1848, "Pohjois-Karjala", "Q186237", 656820),
    # Medium cities (30k-50k)
    ("Lappeenranta", 1649, "Etelä-Karjala", "Q181854", 648949),
    ("Hämeenlinna", 1639, "Kanta-Häme", "Q202158", 649691),
    ("Vaasa", 1606, "Pohjanmaa", "Q125080", 633419),
    ("Seinäjoki", 1960, "Etelä-Pohjanmaa", "Q6157", 637614),
    ("Rovaniemi", 1960, "Lappi", "Q103717", 640276),
    ("Mikkeli", 1838, "Etelä-Savo", "Q190583", 651750),
    ("Kotka", 1879, "Kymenlaakso", "Q192155", 650782),
    ("Salo", 1960, "Varsinais-Suomi", "Q210987", 638399),
    ("Porvoo", 1346, "Uusimaa", "Q193367", 638882),
    ("Kokkola", 1620, "Keski-Pohjanmaa", "Q207891", 649941),
    ("Lohja", 1926, "Uusimaa", "Q214777", 647596),
    ("Hyvinkää", 1960, "Uusimaa", "Q207753", 660561),
    ("Järvenpää", 1967, "Uusimaa", "Q208293", 655590),
    ("Rauma", 1442, "Satakunta", "Q37013", 639104),
    ("Kajaani", 1651, "Kainuu", "Q193180", 656752),
    ("Kerava", 1970, "Uusimaa", "Q216900", 652580),
    ("Savonlinna", 1639, "Etelä-Savo", "Q683512", 637528),
    ("Nokia", 1977, "Pirkanmaa", "Q192870", 643169),
    ("Ylöjärvi", 2004, "Pirkanmaa", "Q543800", 632476),
    # Smaller cities (15k-30k)
    ("Kangasala", 2018, "Pirkanmaa", "Q986322", 656063),
    ("Kaarina", 1993, "Varsinais-Suomi", "Q735563", 655912),
    ("Raasepori", 2009, "Uusimaa", "Q633371", 632785),
    ("Imatra", 1971, "Etelä-Karjala", "Q211020", 658626),
    ("Raisio", 1974, "Varsinais-Suomi", "Q372075", 639127),
    ("Sastamala", 2009, "Pirkanmaa", "Q1001927", 636946),
    ("Tornio", 1621, "Lappi", "Q214021", 634000),
    ("Iisalmi", 1891, "Pohjois-Savo", "Q748533", 659262),
    ("Varkaus", 1962, "Pohjois-Savo", "Q683525", 632699),
    ("Valkeakoski", 1963, "Pirkanmaa", "Q322126", 632665),
    ("Riihimäki", 1960, "Kanta-Häme", "Q429864", 639386),
    ("Hollola", 2017, "Päijät-Häme", "Q990578", 659928),
    ("Kuusamo", 2012, "Pohjois-Pohjanmaa", "Q207999", 651116),
    ("Naantali", 1443, "Varsinais-Suomi", "Q503862", 643247),
    ("Forssa", 1964, "Kanta-Häme", "Q829842", 660379),
    ("Pietarsaari", 1652, "Pohjanmaa", "Q1679567", 640027),
    ("Heinola", 1839, "Päijät-Häme", "Q849934", 660344),
    ("Uusikaupunki", 1617, "Varsinais-Suomi", "Q207295", 632474),
    ("Kauhajoki", 2001, "Etelä-Pohjanmaa", "Q5992", 654993),
    ("Lieksa", 1973, "Pohjois-Karjala", "Q608752", 647967),
    ("Hamina", 1653, "Kymenlaakso", "Q367780", 660601),
    ("Kemi", 1869, "Lappi", "Q203619", 653909),
    ("Akaa", 2007, "Pirkanmaa", "Q413747", 660760),
    # Smaller cities (under 15k)
    ("Loviisa", 1745, "Uusimaa", "Q748513", 648094),
    ("Harjavalta", 1977, "Satakunta", "Q986578", 660389),
    ("Virrat", 1977, "Pirkanmaa", "Q938820", 632310),
    ("Parkano", 1977, "Pirkanmaa", "Q953070", 638798),
    ("Mänttä-Vilppula", 2009, "Pirkanmaa", "Q1016922", 642897),
    ("Huittinen", 1977, "Satakunta", "Q165285", 659895),
    ("Kankaanpää", 1972, "Satakunta", "Q990569", 655983),
    ("Äänekoski", 1973, "Keski-Suomi", "Q258447", 632135),
    ("Loimaa", 2005, "Varsinais-Suomi", "Q915420", 647652),
    ("Kokemäki", 1977, "Satakunta", "Q986409", 649960),
    ("Somero", 1993, "Varsinais-Suomi", "Q939727", 636059),
    ("Alavus", 1977, "Etelä-Pohjanmaa", "Q5981", 661089),
    ("Orivesi", 1986, "Pirkanmaa", "Q953081", 643032),
    ("Keuruu", 1986, "Keski-Suomi", "Q742854", 652368),
    ("Nurmes", 1974, "Pohjois-Karjala", "Q656988", 643198),
    ("Outokumpu", 1977, "Pohjois-Karjala", "Q952374", 643020),
    ("Kitee", 2013, "Pohjois-Karjala", "Q491603", 652295),
    ("Pieksämäki", 1962, "Etelä-Savo", "Q613701", 638965),
    ("Suonenjoki", 1977, "Pohjois-Savo", "Q259636", 636304),
    ("Haapajärvi", 1977, "Pohjois-Pohjanmaa", "Q316211", 660498),
    ("Nivala", 1992, "Pohjois-Pohjanmaa", "Q985458", 643133),
    ("Ylivieska", 1971, "Pohjois-Pohjanmaa", "Q735583", 632355),
    ("Oulainen", 1977, "Pohjois-Pohjanmaa", "Q985459", 643466),
    ("Raahe", 1649, "Pohjois-Pohjanmaa", "Q622592", 639118),
    ("Kalajoki", 2002, "Pohjois-Pohjanmaa", "Q939758", 655795),
    ("Kempele", 2019, "Pohjois-Pohjanmaa", "Q985451", 653790),
    ("Ii", 2007, "Pohjois-Pohjanmaa", "Q853584", 659415),
    ("Pudasjärvi", 2004, "Pohjois-Pohjanmaa", "Q912952", 639247),
    ("Kuhmo", 1986, "Kainuu", "Q939771", 651077),
    ("Kemijärvi", 1973, "Lappi", "Q744704", 653746),
    ("Sodankylä", 2018, "Lappi", "Q502175", 636354),
    ("Inari", 2014, "Lappi", "Q755702", 659516),
    ("Mariehamn", 1861, "Ahvenanmaa", "Q48329", 649735),
    # Additional cities with kaupunki status
    ("Hanko", 1874, "Uusimaa", "Q216790", 660591),
    ("Karkkila", 1977, "Uusimaa", "Q530309", 655804),
]

# ---------------------------------------------------------------------------
# Alternative names: Swedish, Sami, Latin, Russian, German, English
# Finland is officially bilingual (Finnish/Swedish). Many cities,
# especially coastal and southern ones, have official Swedish names.
# Northern cities may have Northern Sami (sme) or Inari Sami (smn) names.
# ---------------------------------------------------------------------------
ALTERNATIVE_NAMES: dict[str, dict[str, list[str]]] = {
    "Helsinki": {
        "swe": ["Helsingfors"],
        "lat": ["Helsingia", "Helsingforsia"],
        "rus": ["Хельсинки"],
        "deu": ["Helsinki"],
        "eng": ["Helsinki"],
        "sme": ["Helsset"],
    },
    "Espoo": {
        "swe": ["Esbo"],
        "rus": ["Эспоо"],
    },
    "Tampere": {
        "swe": ["Tammerfors"],
        "lat": ["Tammerforsia"],
        "rus": ["Тампере"],
        "deu": ["Tammerfors"],
        "eng": ["Tampere"],
    },
    "Vantaa": {
        "swe": ["Vanda"],
        "rus": ["Вантаа"],
    },
    "Oulu": {
        "swe": ["Uleåborg"],
        "lat": ["Uloa"],
        "rus": ["Оулу"],
        "deu": ["Uleåborg"],
        "sme": ["Oulu"],
    },
    "Turku": {
        "swe": ["Åbo"],
        "lat": ["Aboa", "Turcu"],
        "rus": ["Турку"],
        "deu": ["Åbo"],
        "eng": ["Turku"],
    },
    "Jyväskylä": {
        "swe": ["Jyväskylä"],
        "rus": ["Ювяскюля"],
    },
    "Lahti": {
        "swe": ["Lahtis"],
        "lat": ["Lahdesia"],
        "rus": ["Лахти"],
    },
    "Kuopio": {
        "swe": ["Kuopio"],
        "lat": ["Cuopio"],
        "rus": ["Куопио"],
    },
    "Pori": {
        "swe": ["Björneborg"],
        "lat": ["Arctopolis", "Bjorneburgum"],
        "rus": ["Пори"],
        "deu": ["Björneborg"],
    },
    "Kouvola": {
        "swe": ["Kouvola"],
        "rus": ["Коувола"],
    },
    "Joensuu": {
        "swe": ["Joensuu"],
        "rus": ["Йоэнсуу"],
    },
    "Lappeenranta": {
        "swe": ["Villmanstrand"],
        "lat": ["Villmanstrandia"],
        "rus": ["Лаппеэнранта"],
        "deu": ["Willmanstrand"],
    },
    "Hämeenlinna": {
        "swe": ["Tavastehus"],
        "lat": ["Tavastia"],
        "rus": ["Хямеэнлинна"],
        "deu": ["Tavastehus"],
    },
    "Vaasa": {
        "swe": ["Vasa"],
        "lat": ["Wasa", "Vasanum"],
        "rus": ["Вааса"],
        "deu": ["Wasa"],
    },
    "Seinäjoki": {
        "swe": ["Seinäjoki"],
        "rus": ["Сейняйоки"],
    },
    "Rovaniemi": {
        "swe": ["Rovaniemi"],
        "rus": ["Рованиеми"],
        "sme": ["Roavvenjárga"],
        "smn": ["Ruávinjargâ"],
    },
    "Mikkeli": {
        "swe": ["S:t Michel", "Sankt Michel"],
        "lat": ["S. Michaelis"],
        "rus": ["Миккели"],
    },
    "Kotka": {
        "swe": ["Kotka"],
        "rus": ["Котка"],
    },
    "Salo": {
        "swe": ["Salo"],
        "rus": ["Сало"],
    },
    "Porvoo": {
        "swe": ["Borgå"],
        "lat": ["Borga"],
        "rus": ["Порвоо"],
        "deu": ["Borgå"],
    },
    "Kokkola": {
        "swe": ["Karleby", "Gamlakarleby"],
        "lat": ["Carolostadium"],
        "rus": ["Коккола"],
        "deu": ["Gamlakarleby"],
    },
    "Lohja": {
        "swe": ["Lojo"],
        "rus": ["Лохья"],
    },
    "Hyvinkää": {
        "swe": ["Hyvinge"],
        "rus": ["Хювинкяа"],
    },
    "Järvenpää": {
        "swe": ["Träskända"],
        "rus": ["Ярвенпяа"],
    },
    "Rauma": {
        "swe": ["Raumo"],
        "lat": ["Raumum"],
        "rus": ["Раума"],
        "deu": ["Raumo"],
    },
    "Kajaani": {
        "swe": ["Kajana"],
        "lat": ["Cajana", "Cajaneburgum"],
        "rus": ["Каяани"],
    },
    "Kerava": {
        "swe": ["Kervo"],
        "rus": ["Керава"],
    },
    "Savonlinna": {
        "swe": ["Nyslott"],
        "lat": ["Neostadium"],
        "rus": ["Савонлинна"],
        "deu": ["Nyslott"],
    },
    "Nokia": {
        "swe": ["Nokia"],
    },
    "Raasepori": {
        "swe": ["Raseborg"],
        "deu": ["Raseborg"],
    },
    "Imatra": {
        "swe": ["Imatra"],
        "rus": ["Иматра"],
    },
    "Tornio": {
        "swe": ["Torneå"],
        "lat": ["Tornea"],
        "rus": ["Торнио"],
        "deu": ["Torneå"],
        "sme": ["Duortnus"],
    },
    "Pietarsaari": {
        "swe": ["Jakobstad"],
        "lat": ["Jacobstadium"],
        "rus": ["Пиетарсаари"],
        "deu": ["Jakobstadt"],
    },
    "Heinola": {
        "swe": ["Heinola"],
        "rus": ["Хейнола"],
    },
    "Uusikaupunki": {
        "swe": ["Nystad"],
        "lat": ["Neostadium"],
        "rus": ["Уусикаупунки"],
        "deu": ["Nystad"],
    },
    "Hamina": {
        "swe": ["Fredrikshamn"],
        "lat": ["Fridericihamnia"],
        "rus": ["Хамина", "Фридрихсгам"],
        "deu": ["Fredrikshamn"],
    },
    "Kemi": {
        "swe": ["Kemi"],
        "rus": ["Кеми"],
        "sme": ["Giema"],
    },
    "Loviisa": {
        "swe": ["Lovisa"],
        "lat": ["Lovisium"],
        "rus": ["Ловийса"],
        "deu": ["Lowisa"],
    },
    "Hanko": {
        "swe": ["Hangö"],
        "lat": ["Hango"],
        "rus": ["Ханко"],
        "deu": ["Hangö"],
    },
    "Naantali": {
        "swe": ["Nådendal"],
        "lat": ["Vallis Gratiae"],
        "rus": ["Наантали"],
    },
    "Raahe": {
        "swe": ["Brahestad"],
        "lat": ["Brahestadium"],
        "rus": ["Раахе"],
        "deu": ["Brahestad"],
    },
    "Iisalmi": {
        "swe": ["Idensalmi"],
        "rus": ["Иисалми"],
    },
    "Mariehamn": {
        "fin": ["Maarianhamina"],
        "rus": ["Мариехамн"],
        "deu": ["Mariehamn"],
    },
    "Kemijärvi": {
        "swe": ["Kemijärvi"],
        "rus": ["Кемиярви"],
        "sme": ["Giemajávri"],
    },
    "Inari": {
        "swe": ["Enare"],
        "sme": ["Anár"],
        "smn": ["Aanaar"],
    },
    "Sodankylä": {
        "sme": ["Soađegilli"],
        "smn": ["Suáđigil"],
    },
    "Kuusamo": {
        "swe": ["Kuusamo"],
        "rus": ["Куусамо"],
    },
    "Forssa": {
        "swe": ["Forssa"],
    },
    "Riihimäki": {
        "swe": ["Riihimäki"],
    },
    "Valkeakoski": {
        "swe": ["Valkeakoski"],
    },
    "Varkaus": {
        "swe": ["Varkaus"],
        "rus": ["Варкаус"],
    },
    "Pieksämäki": {
        "swe": ["Pieksämäki"],
        "rus": ["Пиексямяки"],
    },
    "Nurmes": {
        "swe": ["Nurmes"],
        "rus": ["Нурмес"],
    },
    "Lieksa": {
        "swe": ["Lieksa"],
        "rus": ["Лиекса"],
    },
    "Ylivieska": {
        "swe": ["Ylivieska"],
    },
    "Kuhmo": {
        "swe": ["Kuhmo"],
        "rus": ["Кухмо"],
    },
}


# ---------------------------------------------------------------------------
# Wikidata SPARQL query
# ---------------------------------------------------------------------------
def query_wikidata_finnish_cities() -> dict[str, dict]:
    """Query Wikidata for Finnish city data using VALUES-based lookup."""
    print("Querying Wikidata SPARQL for Finnish cities...")

    # Collect unique QIDs
    seen_qids: set[str] = set()
    all_qids: list[str] = []
    for _, _, _, qid, _ in FINNISH_CITIES:
        if qid not in seen_qids:
            seen_qids.add(qid)
            all_qids.append(qid)

    values_str = " ".join(f"wd:{qid}" for qid in all_qids)

    query = f"""SELECT DISTINCT ?item ?itemLabel ?coord ?population ?area
      ?geonames_id ?elevation ?regionLabel ?municipalityLabel
      (GROUP_CONCAT(DISTINCT ?altLabel; separator="|") AS ?altNames)
    WHERE {{
      VALUES ?item {{ {values_str} }}
      OPTIONAL {{ ?item wdt:P625 ?coord }}
      OPTIONAL {{ ?item wdt:P1082 ?population }}
      OPTIONAL {{ ?item wdt:P2046 ?area }}
      OPTIONAL {{ ?item wdt:P1566 ?geonames_id }}
      OPTIONAL {{ ?item wdt:P2044 ?elevation }}
      OPTIONAL {{ ?item wdt:P131 ?municipality }}
      OPTIONAL {{ ?item wdt:P706 ?region }}
      OPTIONAL {{
        ?item skos:altLabel ?altLabel .
        FILTER(LANG(?altLabel) IN (
          "sv","se","smn","la","de","ru","en","fr"
        ))
      }}
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "fi,sv,en"
      }}
    }}
    GROUP BY ?item ?itemLabel ?coord ?population ?area
             ?geonames_id ?elevation ?regionLabel ?municipalityLabel
    ORDER BY ?itemLabel"""

    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"https://query.wikidata.org/sparql?{params}"
    req = urllib.request.Request(  # noqa: S310
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": ("ToponymiaEuropaea/0.5 (https://github.com/egkristi/ToponymiaEuropaea)"),
        },
    )

    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        data = json.loads(resp.read())

    results = data["results"]["bindings"]
    print(f"  Got {len(results)} results from Wikidata")

    # Build a lookup by QID
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


# ---------------------------------------------------------------------------
# Nominatim geometry fetcher
# ---------------------------------------------------------------------------
def fetch_nominatim_geometry(city_name: str) -> dict | None:
    """Fetch city boundary polygon from OSM Nominatim.

    Tries multiple search strategies to maximize polygon coverage:
    1. Free-form query (often returns boundary relations)
    2. Structured search with city + country
    """
    strategies = [
        # Strategy 1: free-form query (most likely to return boundaries)
        {
            "q": f"{city_name}, Finland",
            "format": "geojson",
            "polygon_geojson": 1,
            "limit": 3,
        },
        # Strategy 2: structured search
        {
            "city": city_name,
            "country": "Finland",
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
                "User-Agent": (
                    "ToponymiaEuropaea/0.5 (https://github.com/egkristi/ToponymiaEuropaea)"
                ),
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
    """Parse Wikidata alternative names into language-grouped dict."""
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
    """Merge Wikidata alt names with our hardcoded alternatives."""
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    """Ingest all Finnish cities with comprehensive metadata."""
    # Deduplicate city list by QID
    seen_qids: set[str] = set()
    unique_cities = []
    for city_tuple in FINNISH_CITIES:
        qid = city_tuple[3]
        if qid not in seen_qids:
            seen_qids.add(qid)
            unique_cities.append(city_tuple)

    print(f"Ingesting {len(unique_cities)} Finnish cities")
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
    wikidata_lookup = query_wikidata_finnish_cities()
    print()

    # Step 2: Fetch geometry from Nominatim for each city
    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}

    for i, (city, _, _, _qid, _) in enumerate(unique_cities):
        print(
            f"  [{i + 1:3d}/{len(unique_cities)}] {city}...",
            end=" ",
            flush=True,
        )
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

    for city, city_rights_year, region, qid, geonames_id in unique_cities:
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

        # Municipality from Wikidata
        municipality = wd.get("municipality")

        # GeoNames ID: prefer Wikidata, fall back to our list
        gn_id = wd.get("geonames_id") or geonames_id

        # Place type: capital vs regional capital vs city
        if city == "Helsinki":
            place_type = "P.PPLC"
        elif city in (
            "Turku",
            "Tampere",
            "Oulu",
            "Kuopio",
            "Jyväskylä",
            "Rovaniemi",
            "Vaasa",
            "Joensuu",
            "Lappeenranta",
            "Mikkeli",
            "Hämeenlinna",
            "Seinäjoki",
            "Kokkola",
            "Kajaani",
            "Mariehamn",
            "Lahti",
            "Pori",
            "Kotka",
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
            language_code="fin",
            alternative_names=alt_names,
            source_url=source_url,
            wikidata_qid=qid,
            geonames_id=gn_id,
            area_km2=area_km2,
            population=population,
            elevation=elevation,
            geometry=geometry,
            region=region,
            municipality=municipality,
            city_rights_year=city_rights_year,
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
