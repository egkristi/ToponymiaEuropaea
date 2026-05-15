#!/usr/bin/env python3
"""Ingest all Irish cities and towns with comprehensive metadata.

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, county, area,
  alternative names (Irish/Gaelic, Latin, Norman French, Ulster Scots)
- OpenStreetMap Nominatim: GeoJSON geometry (town boundaries/polygons)

Ireland (Republic of Ireland) has 5 statutory cities and numerous towns.
The country is officially bilingual (English + Irish/Gaelic), with every
place having an official Irish-language name. The country is divided into
4 provinces and 26 counties.

Provinces:
  Leinster (Laighin): Dublin, Wicklow, Wexford, Carlow, Kilkenny,
    Laois, Offaly, Westmeath, Longford, Meath, Louth, Kildare
  Munster (An Mhumhain): Cork, Kerry, Limerick, Tipperary, Clare, Waterford
  Connacht (Connachta): Galway, Mayo, Sligo, Roscommon, Leitrim
  Ulster (Ulaidh, Republic): Donegal, Cavan, Monaghan

References:
- https://en.wikipedia.org/wiki/List_of_towns_and_cities_in_the_Republic_of_Ireland
- https://ga.wikipedia.org/wiki/Liosta_bailte_agus_cathracha_in_Éirinn
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
OUTPUT_FILE = DATABANK_DIR / "places" / "IE" / "wikidata.jsonl"

NOMINATIM_DELAY = 1.1


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
    language_code: str = "eng",
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
        "country_code": "IE",
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
    if county:
        record["municipality"] = county
    if chartered_year is not None:
        record["chartered_year"] = chartered_year
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ---------------------------------------------------------------------------
# Irish cities and towns
# Tuple: (English name, county, wikidata_qid, geonames_id)
# ---------------------------------------------------------------------------
IRISH_CITIES: list[tuple[str, str, str, int | None]] = [
    # --- Statutory Cities ---
    ("Dublin", "Dublin", "Q1761", 2964574),
    ("Cork", "Cork", "Q36647", 2965140),
    ("Galway", "Galway", "Q129610", 2964180),
    ("Limerick", "Limerick", "Q133315", 2962943),
    ("Waterford", "Waterford", "Q183551", 2960992),
    # --- Leinster ---
    ("Drogheda", "Louth", "Q207223", 2964661),
    ("Swords", "Dublin", "Q987745", 2961297),
    ("Dundalk", "Louth", "Q204956", 2964540),
    ("Balbriggan", "Dublin", "Q804704", 2966794),
    ("Naas", "Kildare", "Q216038", 2962334),
    ("Mullingar", "Westmeath", "Q55308", 2962361),
    ("Wexford", "Wexford", "Q209126", 2960964),
    ("Carlow", "Carlow", "Q211703", 2965768),
    ("Dún Laoghaire", "Dublin", "Q745989", 2964506),
    ("Kilkenny", "Kilkenny", "Q109092", 2963398),
    ("Leixlip", "Kildare", "Q987797", 2962974),
    ("Tullamore", "Offaly", "Q321091", 2961086),
    ("Greystones", "Wicklow", "Q938017", 2963848),
    ("Ashbourne", "Meath", "Q1766143", 2966870),
    ("Gorey", "Wexford", "Q1004664", 2963962),
    ("Athy", "Kildare", "Q251091", 2966837),
    ("Edenderry", "Offaly", "Q1016311", 2964436),
    ("Kildare", "Kildare", "Q917865", 2963436),
    ("Clane", "Kildare", "Q632020", 2965484),
    ("Longford", "Longford", "Q645623", 2962840),
    ("Wicklow", "Wicklow", "Q652101", 2960936),
    ("Arklow", "Wicklow", "Q673662", 2966883),
    ("Port Laoise", "Laois", "Q822871", 2962026),
    ("Celbridge", "Kildare", "Q629881", 2965529),
    ("Newbridge", "Kildare", "Q958397", 2962290),
    ("Athlone", "Westmeath", "Q369911", 2966839),
    ("Dunshaughlin", "Meath", "Q267293", 2964472),
    ("Kells", "Meath", "Q917848", 2963528),
    ("Dunboyne", "Meath", "Q1012505", 2964547),
    ("Portarlington", "Laois", "Q1989246", 2962029),
    ("Blessington", "Wicklow", "Q883912", 2966101),
    ("Clondalkin", "Dublin", "Q1102232", 2965381),
    ("Howth", "Dublin", "Q434165", 2963722),
    # --- Munster ---
    ("Tralee", "Kerry", "Q213358", 2961123),
    ("Ennis", "Clare", "Q209128", 2964405),
    ("Clonmel", "Tipperary", "Q217057", 2965353),
    ("Killarney", "Kerry", "Q623382", 2963370),
    ("Cóbh", "Cork", "Q733093", 2965260),
    ("Shannon", "Clare", "Q611919", 3310247),
    ("Dungarvan", "Waterford", "Q581790", 2964528),
    ("Ballincollig", "Cork", "Q2528844", 2966749),
    ("Mallow", "Cork", "Q922247", 2962714),
    ("Clonakilty", "Cork", "Q996703", 2965402),
    ("Kinsale", "Cork", "Q840681", 2963155),
    ("Youghal", "Cork", "Q1012476", 2960869),
    ("Nenagh", "Tipperary", "Q918372", 2962304),
    ("Tipperary", "Tipperary", "Q680220", 2961192),
    ("Cashel", "Tipperary", "Q1002183", 2965664),
    ("Roscrea", "Tipperary", "Q1003178", 2961730),
    ("Cahersiveen", "Kerry", "Q736203", 2965852),
    ("Dingle/Daingean Uí Chúis", "Kerry", "Q932302", 2964782),
    ("Kenmare", "Kerry", "Q166232", 2963522),
    ("Listowel", "Kerry", "Q996487", 2962864),
    ("Bantry", "Cork", "Q807001", 2966356),
    ("Skibbereen", "Cork", "Q1930746", 2961459),
    ("Charleville", "Cork", "Q1066722", 2965516),
    ("Carrick-on-Suir", "Tipperary", "Q1003187", 2965726),
    ("Kilrush", "Clare", "Q963894", 2963218),
    ("Birr", "Offaly", "Q865849", 2966154),
    ("Adare", "Limerick", "Q352590", 2967076),
    ("Lismore", "Waterford", "Q1828038", 2962898),
    ("Millstreet", "Cork", "Q659655", 2962613),
    # --- Connacht ---
    ("Castlebar", "Mayo", "Q749196", 2965654),
    ("Sligo", "Sligo", "Q190002", 2961423),
    ("Ballina", "Mayo", "Q384721", 2966778),
    ("Tuam", "Galway", "Q996691", 2961099),
    ("Westport", "Mayo", "Q1017331", 2960970),
    ("Roscommon", "Roscommon", "Q677631", 2961732),
    ("Oranmore", "Galway", "Q1026389", 2962153),
    ("Athenry", "Galway", "Q755389", 2966843),
    ("Ballinrobe", "Mayo", "Q805277", 2966715),
    ("Carrick-on-Shannon", "Leitrim", "Q589390", 2965727),
    ("Clifden", "Galway", "Q1024913", 2965449),
    ("Claremorris", "Mayo", "Q1095348", 2965471),
    ("Boyle", "Roscommon", "Q1124843", 2966044),
    ("Ballymote", "Sligo", "Q1899651", 2966492),
    # --- Ulster (Republic) ---
    ("Letterkenny", "Donegal", "Q952497", 2962961),
    ("Buncrana", "Donegal", "Q751475", 2654332),
    ("Cavan", "Cavan", "Q215361", 2965535),
    ("Monaghan", "Monaghan", "Q2566709", 2962257),
    ("Ballybofey", "Donegal", "Q805401", 2966668),
    ("Donegal", "Donegal", "Q212489", 2964530),
    ("Bundoran", "Donegal", "Q1009405", 2965929),
    ("Ballyshannon", "Donegal", "Q805462", 2966406),
    ("Killybegs", "Donegal", "Q1741405", 2963295),
    ("Carndonagh", "Donegal", "Q1043934", 2965761),
]

# ---------------------------------------------------------------------------
# Alternative names: Irish (gle), Latin (lat), Norman French (fro),
# Ulster Scots (sco), Old Norse (non)
# Ireland is officially bilingual. Every place has an official Irish name.
# Many places also have Latin names from ecclesiastical/monastic history,
# and some have Norse origins (Viking settlements: Dublin, Waterford, etc.)
# ---------------------------------------------------------------------------
ALTERNATIVE_NAMES: dict[str, dict[str, list[str]]] = {
    "Dublin": {
        "gle": ["Baile Átha Cliath"],
        "lat": ["Dublinia", "Eblana"],
        "non": ["Dyflinn", "Dyflin"],
        "ang": ["Difelin"],
    },
    "Cork": {
        "gle": ["Corcaigh"],
        "lat": ["Corcagia"],
        "non": ["Korkr"],
    },
    "Galway": {
        "gle": ["Gaillimh"],
        "lat": ["Galvia"],
    },
    "Limerick": {
        "gle": ["Luimneach"],
        "lat": ["Limericum"],
        "non": ["Hlymrekr"],
    },
    "Waterford": {
        "gle": ["Port Láirge"],
        "lat": ["Vadrefordia"],
        "non": ["Veðrafjǫrðr"],
    },
    "Drogheda": {
        "gle": ["Droichead Átha"],
        "lat": ["Pontana"],
    },
    "Swords": {
        "gle": ["Sord"],
        "lat": ["Sordae"],
    },
    "Dundalk": {
        "gle": ["Dún Dealgan"],
        "lat": ["Dundalgania"],
    },
    "Balbriggan": {
        "gle": ["Baile Brigín"],
    },
    "Naas": {
        "gle": ["An Nás"],
        "lat": ["Nassium"],
    },
    "Mullingar": {
        "gle": ["An Muileann gCearr"],
        "lat": ["Mollingaria"],
    },
    "Wexford": {
        "gle": ["Loch Garman"],
        "lat": ["Wexfordia"],
        "non": ["Veisafjǫrðr"],
    },
    "Carlow": {
        "gle": ["Ceatharlach"],
        "lat": ["Catherlogia"],
    },
    "Dún Laoghaire": {
        "gle": ["Dún Laoghaire"],
        "eng": ["Dun Laoghaire", "Kingstown"],
    },
    "Kilkenny": {
        "gle": ["Cill Chainnigh"],
        "lat": ["Kilkennia"],
    },
    "Leixlip": {
        "gle": ["Léim an Bhradáin"],
        "non": ["Laxhlaup"],
    },
    "Tullamore": {
        "gle": ["Tulach Mhór"],
    },
    "Greystones": {
        "gle": ["Na Clocha Liatha"],
    },
    "Ashbourne": {
        "gle": ["Cill Dhéagláin"],
    },
    "Gorey": {
        "gle": ["Guaire"],
    },
    "Athy": {
        "gle": ["Baile Átha Í"],
    },
    "Edenderry": {
        "gle": ["Éadan Doire"],
    },
    "Kildare": {
        "gle": ["Cill Dara"],
        "lat": ["Kildaria", "Cella Quercus"],
    },
    "Clane": {
        "gle": ["Claonadh"],
    },
    "Longford": {
        "gle": ["An Longfort"],
        "lat": ["Longfordia"],
    },
    "Wicklow": {
        "gle": ["Cill Mhantáin"],
        "non": ["Víkingaló"],
    },
    "Arklow": {
        "gle": ["An tInbhear Mór"],
        "non": ["Arkló"],
    },
    "Port Laoise": {
        "gle": ["Port Laoise"],
        "eng": ["Portlaoise", "Maryborough"],
    },
    "Celbridge": {
        "gle": ["Cill Droichid"],
    },
    "Newbridge": {
        "gle": ["Droichead Nua"],
    },
    "Athlone": {
        "gle": ["Baile Átha Luain"],
        "lat": ["Athlonia"],
    },
    "Dunshaughlin": {
        "gle": ["Dún Seachlainn"],
    },
    "Kells": {
        "gle": ["Ceanannas"],
        "lat": ["Cenandus", "Kenlis"],
    },
    "Dunboyne": {
        "gle": ["Dún Búinne"],
    },
    "Portarlington": {
        "gle": ["Cúil an tSúdaire"],
    },
    "Blessington": {
        "gle": ["Baile Coimín"],
    },
    "Clondalkin": {
        "gle": ["Cluain Dolcáin"],
    },
    "Howth": {
        "gle": ["Binn Éadair"],
        "non": ["Hǫfuð", "Howth"],
    },
    "Tralee": {
        "gle": ["Trá Lí"],
        "lat": ["Traelia"],
    },
    "Ennis": {
        "gle": ["Inis"],
        "lat": ["Insula"],
    },
    "Clonmel": {
        "gle": ["Cluain Meala"],
        "lat": ["Clonmelia"],
    },
    "Killarney": {
        "gle": ["Cill Airne"],
        "lat": ["Killarnia"],
    },
    "Cóbh": {
        "gle": ["An Cóbh"],
        "eng": ["Cobh", "Queenstown"],
    },
    "Shannon": {
        "gle": ["Sionainn"],
    },
    "Dungarvan": {
        "gle": ["Dún Garbhán"],
    },
    "Ballincollig": {
        "gle": ["Baile an Chollaigh"],
    },
    "Mallow": {
        "gle": ["Mala"],
        "lat": ["Mallovia"],
    },
    "Clonakilty": {
        "gle": ["Cloich na Coillte"],
    },
    "Kinsale": {
        "gle": ["Cionn tSáile"],
        "lat": ["Kinsalia"],
    },
    "Youghal": {
        "gle": ["Eochaill"],
        "lat": ["Youghalia"],
    },
    "Nenagh": {
        "gle": ["An tAonach"],
    },
    "Tipperary": {
        "gle": ["Tiobraid Árann"],
        "lat": ["Tipperaria"],
    },
    "Cashel": {
        "gle": ["Caiseal"],
        "lat": ["Casselia", "Castellum"],
    },
    "Roscrea": {
        "gle": ["Ros Cré"],
        "lat": ["Roscrea"],
    },
    "Cahersiveen": {
        "gle": ["Cathair Saidhbhín"],
    },
    "Dingle/Daingean Uí Chúis": {
        "gle": ["Daingean Uí Chúis", "An Daingean"],
        "eng": ["Dingle"],
    },
    "Kenmare": {
        "gle": ["Neidín"],
    },
    "Listowel": {
        "gle": ["Lios Tuathail"],
    },
    "Bantry": {
        "gle": ["Beanntraí"],
    },
    "Skibbereen": {
        "gle": ["An Sciobairín"],
    },
    "Charleville": {
        "gle": ["An Ráth"],
    },
    "Carrick-on-Suir": {
        "gle": ["Carraig na Siúire"],
    },
    "Kilrush": {
        "gle": ["Cill Rois"],
    },
    "Birr": {
        "gle": ["Biorra"],
        "lat": ["Birra"],
        "eng": ["Parsonstown"],
    },
    "Adare": {
        "gle": ["Áth Dara"],
    },
    "Lismore": {
        "gle": ["Lios Mór"],
        "lat": ["Lismorensis"],
    },
    "Millstreet": {
        "gle": ["Sráid an Mhuilinn"],
    },
    "Castlebar": {
        "gle": ["Caisleán an Bharraigh"],
        "lat": ["Castellum Barri"],
    },
    "Sligo": {
        "gle": ["Sligeach"],
        "lat": ["Sligonia"],
        "non": ["Sligech"],
    },
    "Ballina": {
        "gle": ["Béal an Átha"],
    },
    "Tuam": {
        "gle": ["Tuaim"],
        "lat": ["Tuama"],
    },
    "Westport": {
        "gle": ["Cathair na Mart"],
    },
    "Roscommon": {
        "gle": ["Ros Comáin"],
        "lat": ["Roscomania"],
    },
    "Oranmore": {
        "gle": ["Órán Mór"],
    },
    "Athenry": {
        "gle": ["Baile Átha an Rí"],
        "lat": ["Athenria"],
    },
    "Ballinrobe": {
        "gle": ["Baile an Róba"],
    },
    "Carrick-on-Shannon": {
        "gle": ["Cora Droma Rúisc"],
    },
    "Clifden": {
        "gle": ["An Clochán"],
    },
    "Claremorris": {
        "gle": ["Clár Chlainne Mhuiris"],
    },
    "Boyle": {
        "gle": ["Mainistir na Búille"],
    },
    "Ballymote": {
        "gle": ["Baile an Mhóta"],
    },
    "Letterkenny": {
        "gle": ["Leitir Ceanainn"],
    },
    "Buncrana": {
        "gle": ["Bun Cranncha"],
    },
    "Cavan": {
        "gle": ["An Cabhán"],
        "lat": ["Cabanum"],
    },
    "Monaghan": {
        "gle": ["Muineachán"],
        "lat": ["Monaghanium"],
    },
    "Ballybofey": {
        "gle": ["Bealach Féich"],
    },
    "Donegal": {
        "gle": ["Dún na nGall"],
        "lat": ["Dungallia"],
        "non": ["Dún na nGall"],
    },
    "Bundoran": {
        "gle": ["Bun Dobhráin"],
    },
    "Ballyshannon": {
        "gle": ["Béal Átha Seanaidh"],
    },
    "Killybegs": {
        "gle": ["Na Cealla Beaga"],
    },
    "Carndonagh": {
        "gle": ["Carn Domhnach"],
    },
}


# ---------------------------------------------------------------------------
# Wikidata SPARQL query
# ---------------------------------------------------------------------------
def query_wikidata_irish_cities() -> dict[str, dict]:
    """Query Wikidata for Irish city data using VALUES-based lookup."""
    print("Querying Wikidata SPARQL for Irish cities...")

    seen_qids: set[str] = set()
    all_qids: list[str] = []
    for _, _, qid, _ in IRISH_CITIES:
        if qid not in seen_qids:
            seen_qids.add(qid)
            all_qids.append(qid)

    values_str = " ".join(f"wd:{qid}" for qid in all_qids)

    query = f"""SELECT DISTINCT ?item ?itemLabel ?coord ?population ?area
      ?geonames_id ?elevation ?countyLabel
      (GROUP_CONCAT(DISTINCT ?altLabel; separator="|") AS ?altNames)
    WHERE {{
      VALUES ?item {{ {values_str} }}
      OPTIONAL {{ ?item wdt:P625 ?coord }}
      OPTIONAL {{ ?item wdt:P1082 ?population }}
      OPTIONAL {{ ?item wdt:P2046 ?area }}
      OPTIONAL {{ ?item wdt:P1566 ?geonames_id }}
      OPTIONAL {{ ?item wdt:P2044 ?elevation }}
      OPTIONAL {{ ?item wdt:P131 ?county }}
      OPTIONAL {{
        ?item skos:altLabel ?altLabel .
        FILTER(LANG(?altLabel) IN ("ga","la","fr","sco","en"))
      }}
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en,ga"
      }}
    }}
    GROUP BY ?item ?itemLabel ?coord ?population ?area
             ?geonames_id ?elevation ?countyLabel
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

    with urllib.request.urlopen(req, timeout=90) as resp:  # noqa: S310
        data = json.loads(resp.read())

    results = data["results"]["bindings"]
    print(f"  Got {len(results)} results from Wikidata")

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
            if len(parts) == 2:
                lon, lat = float(parts[0]), float(parts[1])

        # Keep highest population if duplicate QID
        if qid in lookup:
            existing_pop = lookup[qid].get("population") or 0
            new_pop = int(float(pop)) if pop else 0
            if new_pop <= existing_pop:
                continue

        lookup[qid] = {
            "name": name,
            "qid": qid,
            "lat": lat,
            "lon": lon,
            "population": int(float(pop)) if pop else None,
            "area_km2": round(float(area), 2) if area else None,
            "geonames_id": int(gn) if gn else None,
            "county": county or None,
            "elevation": round(float(elev), 1) if elev else None,
            "alt_names_raw": alts,
        }

    return lookup


# ---------------------------------------------------------------------------
# Nominatim geometry fetcher
# ---------------------------------------------------------------------------
def fetch_nominatim_geometry(city_name: str) -> dict | None:
    """Fetch town boundary polygon from OSM Nominatim."""
    strategies = [
        {
            "q": f"{city_name}, Ireland",
            "format": "geojson",
            "polygon_geojson": 1,
            "limit": 3,
        },
        {
            "city": city_name,
            "country": "Ireland",
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
    for lang, names in hardcoded_alts.items():
        merged[lang] = list(names)
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
    """Ingest all Irish cities and towns with comprehensive metadata."""
    seen_qids: set[str] = set()
    unique_cities = []
    for city_tuple in IRISH_CITIES:
        qid = city_tuple[2]
        if qid not in seen_qids:
            seen_qids.add(qid)
            unique_cities.append(city_tuple)

    print(f"Ingesting {len(unique_cities)} Irish cities and towns")
    print(f"Output: {OUTPUT_FILE}")
    print()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

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

    wikidata_lookup = query_wikidata_irish_cities()
    print()

    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}

    for i, (city, _county, _qid, _) in enumerate(unique_cities):
        # Use clean name for Nominatim (strip Irish suffixes)
        search_name = city.split("/")[0].strip()
        print(
            f"  [{i + 1:3d}/{len(unique_cities)}] {city}...",
            end=" ",
            flush=True,
        )
        geo = fetch_nominatim_geometry(search_name)
        if geo:
            geometries[city] = geo
            coords_count = len(geo.get("coordinates", []))
            print(f"OK ({geo['type']}, {coords_count} rings)")
        else:
            print("no polygon")

        time.sleep(NOMINATIM_DELAY)

    print(f"\n  Got geometry for {len(geometries)}/{len(unique_cities)} cities")
    print()

    print("Creating records...")
    all_records: list[dict] = []
    skipped_existing = 0

    for city, county, qid, geonames_id in unique_cities:
        wd = wikidata_lookup.get(qid, {})

        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{city}' ({qid}), skipping")
            continue

        source_id = f"wikidata:{qid}"
        source_url = f"https://www.wikidata.org/wiki/{qid}"

        if source_id in existing_source_ids:
            skipped_existing += 1
            continue

        hardcoded_alts = ALTERNATIVE_NAMES.get(city, {})
        wikidata_alts = parse_wikidata_alt_names(wd.get("alt_names_raw", ""))
        alt_names = merge_alternative_names(wikidata_alts, hardcoded_alts)

        geometry = geometries.get(city)
        population = wd.get("population")
        area_km2 = wd.get("area_km2")
        elevation = wd.get("elevation")
        gn_id = wd.get("geonames_id") or geonames_id

        # Place type classification
        if city == "Dublin":
            place_type = "P.PPLC"
        elif city in ("Cork", "Galway", "Limerick", "Waterford"):
            place_type = "P.PPLA"
        elif city in (
            "Carlow",
            "Cavan",
            "Ennis",
            "Kilkenny",
            "Letterkenny",
            "Longford",
            "Mullingar",
            "Naas",
            "Port Laoise",
            "Roscommon",
            "Sligo",
            "Tralee",
            "Tullamore",
            "Wexford",
            "Wicklow",
            "Castlebar",
            "Dundalk",
            "Dungarvan",
            "Nenagh",
            "Tipperary",
        ):
            place_type = "P.PPLA2"
        else:
            place_type = "P.PPL"

        # Determine province from county
        leinster = {
            "Dublin",
            "Wicklow",
            "Wexford",
            "Carlow",
            "Kilkenny",
            "Laois",
            "Offaly",
            "Westmeath",
            "Longford",
            "Meath",
            "Louth",
            "Kildare",
        }
        munster = {"Cork", "Kerry", "Limerick", "Tipperary", "Clare", "Waterford"}
        connacht = {"Galway", "Mayo", "Sligo", "Roscommon", "Leitrim"}
        ulster_roi = {"Donegal", "Cavan", "Monaghan"}

        if county in leinster:
            region = "Leinster"
        elif county in munster:
            region = "Munster"
        elif county in connacht:
            region = "Connacht"
        elif county in ulster_roi:
            region = "Ulster"
        else:
            region = None

        record = make_record(
            name_form=city,
            name_normalized=city.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=source_id,
            place_type=place_type,
            language_code="eng",
            alternative_names=alt_names,
            source_url=source_url,
            wikidata_qid=qid,
            geonames_id=gn_id,
            area_km2=area_km2,
            population=population,
            elevation=elevation,
            geometry=geometry,
            region=region,
            county=f"County {county}",
        )

        all_records.append(record)

    print(f"\nCreated {len(all_records)} new records")
    if skipped_existing:
        print(f"  Skipped {skipped_existing} already-existing records")

    if not all_records:
        print("\nNo new records to add.")
        return

    print("\nSigning records...")
    signed_records = [sign_record(r) for r in all_records]

    with OUTPUT_FILE.open("w") as f:
        for record in signed_records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"\nWrote {len(signed_records)} records to {OUTPUT_FILE}")

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

    print(f"\nRecords with geometry (polygon/multipolygon): {with_geo}")
    print(f"Records with population: {with_pop}")
    print(f"Records with area: {with_area}")
    print(f"Records with elevation: {with_elev}")
    print(f"Records with alternative names: {with_alts}")
    print(f"Records with Wikidata QID: {with_qid}")
    print(f"Records with GeoNames ID: {with_gn}")

    regions: dict[str, int] = {}
    for r in signed_records:
        reg = r.get("region", "unknown")
        regions[reg] = regions.get(reg, 0) + 1

    print("\nBreakdown by province:")
    for reg, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {reg}: {count}")

    counties: dict[str, int] = {}
    for r in signed_records:
        c = r.get("municipality", "unknown")
        counties[c] = counties.get(c, 0) + 1

    print("\nBreakdown by county:")
    for c, count in sorted(counties.items(), key=lambda x: -x[1]):
        print(f"  {c}: {count}")


if __name__ == "__main__":
    main()
