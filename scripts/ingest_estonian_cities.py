#!/usr/bin/env python3
"""Ingest cities and towns across Estonia (Eesti Vabariik).

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, area,
  alternative names (Estonian, German, Russian, Finnish, Swedish, Latin)
- OpenStreetMap Nominatim: GeoJSON geometry (city/town boundaries/polygons)

Estonia has 47 cities (linnad) across 15 counties (maakonnad):
  Harju County (Harjumaa): Tallinn (capital), Maardu, Keila, Saue, Paldiski,
    Kehra, Loksa
  Tartu County (Tartumaa): Tartu, Elva, Kallaste
  Ida-Viru County (Ida-Virumaa): Narva, Kohtla-Järve, Sillamäe, Jõhvi,
    Kiviõli, Püssi, Narva-Jõesuu
  Pärnu County (Pärnumaa): Pärnu, Sindi, Kilingi-Nõmme
  Viljandi County (Viljandimaa): Viljandi, Võhma, Suure-Jaani, Abja-Paluoja,
    Karksi-Nuia, Mõisaküla
  Lääne-Viru County (Lääne-Virumaa): Rakvere, Tapa, Tamsalu, Kunda
  Saare County (Saaremaa): Kuressaare
  Valga County (Valgamaa): Valga, Tõrva, Otepää
  Võru County (Võrumaa): Võru, Antsla
  Rapla County (Raplamaa): Rapla
  Järva County (Järvamaa): Paide, Türi
  Jõgeva County (Jõgevamaa): Jõgeva, Põltsamaa, Mustvee
  Hiiu County (Hiiumaa): Kärdla
  Lääne County (Läänemaa): Haapsalu, Lihula
  Põlva County (Põlvamaa): Põlva, Räpina

Linguistic layers:
  - Estonian (est): primary, official language
  - German (deu): historically very important — Baltic German heritage
    (Reval=Tallinn, Dorpat=Tartu, Narwa=Narva, Pernau=Pärnu,
     Fellin=Viljandi, Wesenberg=Rakvere, Arensburg=Kuressaare,
     Hapsal=Haapsalu)
  - Russian (rus): significant minority language
  - Finnish (fin): closely related, Tallinna, Tartto
  - Swedish (swe): historical coastal names
  - Latin (lat): scholarly/ecclesiastical forms

References:
- https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Estonia
- https://en.wikipedia.org/wiki/Counties_of_Estonia
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
OUTPUT_FILE = DATABANK_DIR / "places" / "EE" / "wikidata.jsonl"

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
    language_code: str = "est",
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
        "country_code": "EE",
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
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ---------------------------------------------------------------------------
# Estonian cities — all 47 linnad
# (English name, Estonian name, County, wikidata_qid, geonames_id)
# ---------------------------------------------------------------------------
ESTONIAN_CITIES: list[tuple[str, str, str, str, int]] = [
    # =========================================================================
    # HARJU COUNTY (Harjumaa)
    # =========================================================================
    ("Tallinn", "Tallinn", "Harju County", "Q1770", 588409),
    ("Maardu", "Maardu", "Harju County", "Q206555", 590447),
    ("Keila", "Keila", "Harju County", "Q207275", 591472),
    ("Saue", "Saue", "Harju County", "Q86206", 588780),
    ("Paldiski", "Paldiski", "Harju County", "Q204091", 589663),
    ("Kehra", "Kehra", "Harju County", "Q985464", 591476),
    ("Loksa", "Loksa", "Harju County", "Q213740", 590552),
    # =========================================================================
    # TARTU COUNTY (Tartumaa)
    # =========================================================================
    ("Tartu", "Tartu", "Tartu County", "Q13972", 588335),
    ("Elva", "Elva", "Tartu County", "Q213071", 592279),
    ("Kallaste", "Kallaste", "Tartu County", "Q613714", 591703),
    # =========================================================================
    # IDA-VIRU COUNTY (Ida-Virumaa)
    # =========================================================================
    ("Narva", "Narva", "Ida-Viru County", "Q102158", 590031),
    ("Kohtla-Järve", "Kohtla-Järve", "Ida-Viru County", "Q201391", 591260),
    ("Sillamäe", "Sillamäe", "Ida-Viru County", "Q207748", 588686),
    ("Jõhvi", "Jõhvi", "Ida-Viru County", "Q211059", 591893),
    ("Kiviõli", "Kiviõli", "Ida-Viru County", "Q216119", 591313),
    ("Püssi", "Püssi", "Ida-Viru County", "Q172263", 589253),
    ("Narva-Jõesuu", "Narva-Jõesuu", "Ida-Viru County", "Q723372", 590030),
    # =========================================================================
    # PÄRNU COUNTY (Pärnumaa)
    # =========================================================================
    ("Pärnu", "Pärnu", "Pärnu County", "Q102365", 589580),
    ("Sindi", "Sindi", "Pärnu County", "Q730707", 588673),
    ("Kilingi-Nõmme", "Kilingi-Nõmme", "Pärnu County", "Q1146736", 591381),
    # =========================================================================
    # VILJANDI COUNTY (Viljandimaa)
    # =========================================================================
    ("Viljandi", "Viljandi", "Viljandi County", "Q44840", 587577),
    ("Võhma", "Võhma", "Viljandi County", "Q171333", 587517),
    ("Suure-Jaani", "Suure-Jaani", "Viljandi County", "Q370242", 588532),
    ("Abja-Paluoja", "Abja-Paluoja", "Viljandi County", "Q321784", 592626),
    ("Karksi-Nuia", "Karksi-Nuia", "Viljandi County", "Q1023750", 589922),
    ("Mõisaküla", "Mõisaküla", "Viljandi County", "Q819395", 590186),
    # =========================================================================
    # LÄÄNE-VIRU COUNTY (Lääne-Virumaa)
    # =========================================================================
    ("Rakvere", "Rakvere", "Lääne-Viru County", "Q191889", 589165),
    ("Tapa", "Tapa", "Lääne-Viru County", "Q650577", 588348),
    ("Tamsalu", "Tamsalu", "Lääne-Viru County", "Q217682", 588365),
    ("Kunda", "Kunda", "Lääne-Viru County", "Q213178", 590975),
    # =========================================================================
    # SAARE COUNTY (Saaremaa)
    # =========================================================================
    ("Kuressaare", "Kuressaare", "Saare County", "Q188179", 590939),
    # =========================================================================
    # VALGA COUNTY (Valgamaa)
    # =========================================================================
    ("Valga", "Valga", "Valga County", "Q193905", 587876),
    ("Tõrva", "Tõrva", "Valga County", "Q819514", 588204),
    ("Otepää", "Otepää", "Valga County", "Q339347", 589782),
    # =========================================================================
    # VÕRU COUNTY (Võrumaa)
    # =========================================================================
    ("Võru", "Võru", "Võru County", "Q205271", 587450),
    ("Antsla", "Antsla", "Võru County", "Q154994", 592459),
    # =========================================================================
    # RAPLA COUNTY (Raplamaa)
    # =========================================================================
    ("Rapla", "Rapla", "Rapla County", "Q215971", 589116),
    # =========================================================================
    # JÄRVA COUNTY (Järvamaa)
    # =========================================================================
    ("Paide", "Paide", "Järva County", "Q45114", 589709),
    ("Türi", "Türi", "Järva County", "Q141796", 588153),
    # =========================================================================
    # JÕGEVA COUNTY (Jõgevamaa)
    # =========================================================================
    ("Jõgeva", "Jõgeva", "Jõgeva County", "Q117513", 591902),
    ("Põltsamaa", "Põltsamaa", "Jõgeva County", "Q642660", 589379),
    ("Mustvee", "Mustvee", "Jõgeva County", "Q842021", 590067),
    # =========================================================================
    # HIIU COUNTY (Hiiumaa)
    # =========================================================================
    ("Kärdla", "Kärdla", "Hiiu County", "Q155066", 591632),
    # =========================================================================
    # LÄÄNE COUNTY (Läänemaa)
    # =========================================================================
    ("Haapsalu", "Haapsalu", "Lääne County", "Q191106", 592225),
    ("Lihula", "Lihula", "Lääne County", "Q375497", 590657),
    # =========================================================================
    # PÕLVA COUNTY (Põlvamaa)
    # =========================================================================
    ("Põlva", "Põlva", "Põlva County", "Q45100", 589375),
    ("Räpina", "Räpina", "Põlva County", "Q1483558", 589117),
]

# ---------------------------------------------------------------------------
# Alternative names — Baltic German heritage is historically crucial
# ---------------------------------------------------------------------------
ALTERNATIVE_NAMES: dict[str, dict[str, list[str]]] = {
    "Tallinn": {
        "est": ["Tallinn"],
        "deu": ["Reval"],
        "rus": ["Таллин", "Ревель"],
        "fin": ["Tallinna"],
        "swe": ["Reval"],
        "lat": ["Revalia", "Tallinna"],
        "dan": ["Reval"],
    },
    "Tartu": {
        "est": ["Tartu"],
        "deu": ["Dorpat", "Dörpt"],
        "rus": ["Тарту", "Дерпт", "Юрьев"],
        "fin": ["Tartto"],
        "swe": ["Dorpat"],
        "lat": ["Tarbatum", "Dorpatum"],
    },
    "Narva": {
        "est": ["Narva"],
        "deu": ["Narwa"],
        "rus": ["Нарва"],
        "fin": ["Narva"],
        "swe": ["Narva"],
        "lat": ["Narva"],
    },
    "Pärnu": {
        "est": ["Pärnu"],
        "deu": ["Pernau"],
        "rus": ["Пярну", "Пернов"],
        "fin": ["Pärnu", "Pernau"],
        "swe": ["Pernau"],
        "lat": ["Pernavia"],
    },
    "Kohtla-Järve": {
        "est": ["Kohtla-Järve"],
        "rus": ["Кохтла-Ярве"],
        "deu": ["Kochtla-Järwe"],
    },
    "Viljandi": {
        "est": ["Viljandi"],
        "deu": ["Fellin"],
        "rus": ["Вильянди", "Феллин"],
        "fin": ["Viljanti"],
        "lat": ["Fellinum"],
    },
    "Maardu": {
        "est": ["Maardu"],
        "deu": ["Maart"],
        "rus": ["Маарду"],
    },
    "Rakvere": {
        "est": ["Rakvere"],
        "deu": ["Wesenberg"],
        "rus": ["Раквере", "Везенберг"],
        "fin": ["Rakvere"],
        "lat": ["Wesenberga"],
    },
    "Kuressaare": {
        "est": ["Kuressaare", "Kingissepa"],
        "deu": ["Arensburg"],
        "rus": ["Курессааре", "Аренсбург"],
        "fin": ["Kuressaare"],
        "swe": ["Arensburg"],
        "lat": ["Arensburgum"],
    },
    "Sillamäe": {
        "est": ["Sillamäe"],
        "rus": ["Силламяэ"],
        "deu": ["Sillamägi"],
    },
    "Valga": {
        "est": ["Valga"],
        "deu": ["Walk"],
        "rus": ["Валга", "Валк"],
        "fin": ["Valga"],
        "lat": ["Valca"],
    },
    "Võru": {
        "est": ["Võru"],
        "deu": ["Werro"],
        "rus": ["Выру", "Верро"],
        "fin": ["Võru"],
        "lat": ["Verro"],
    },
    "Keila": {
        "est": ["Keila"],
        "deu": ["Kegel"],
        "rus": ["Кейла"],
    },
    "Jõhvi": {
        "est": ["Jõhvi"],
        "deu": ["Jewe"],
        "rus": ["Йыхви"],
        "lat": ["Iewi"],
    },
    "Haapsalu": {
        "est": ["Haapsalu"],
        "deu": ["Hapsal"],
        "rus": ["Хаапсалу", "Гапсаль"],
        "fin": ["Haapsalu"],
        "swe": ["Hapsal"],
        "lat": ["Hapsalia"],
    },
    "Paide": {
        "est": ["Paide"],
        "deu": ["Weißenstein"],
        "rus": ["Пайде", "Вейсенштейн"],
        "lat": ["Weissenstein"],
    },
    "Saue": {
        "est": ["Saue"],
        "deu": ["Friedheim"],
        "rus": ["Сауэ"],
    },
    "Elva": {
        "est": ["Elva"],
        "deu": ["Elwa"],
        "rus": ["Элва"],
    },
    "Põlva": {
        "est": ["Põlva"],
        "deu": ["Pölwe"],
        "rus": ["Пылва"],
    },
    "Tapa": {
        "est": ["Tapa"],
        "deu": ["Taps"],
        "rus": ["Тапа"],
    },
    "Rapla": {
        "est": ["Rapla"],
        "deu": ["Rappel"],
        "rus": ["Рапла"],
    },
    "Türi": {
        "est": ["Türi"],
        "deu": ["Turgel"],
        "rus": ["Тюри"],
    },
    "Jõgeva": {
        "est": ["Jõgeva"],
        "deu": ["Laisholm"],
        "rus": ["Йыгева"],
    },
    "Kiviõli": {
        "est": ["Kiviõli"],
        "rus": ["Кивиыли"],
    },
    "Põltsamaa": {
        "est": ["Põltsamaa"],
        "deu": ["Oberpahlen"],
        "rus": ["Пылтсамаа", "Оберпален"],
        "lat": ["Oberpalia"],
    },
    "Paldiski": {
        "est": ["Paldiski"],
        "deu": ["Baltischport", "Baltisch-Port"],
        "rus": ["Палдиски", "Балтийский Порт"],
        "swe": ["Rågervik"],
    },
    "Sindi": {
        "est": ["Sindi"],
        "deu": ["Zintenhof"],
        "rus": ["Синди"],
    },
    "Kunda": {
        "est": ["Kunda"],
        "deu": ["Kunda"],
        "rus": ["Кунда"],
    },
    "Kärdla": {
        "est": ["Kärdla"],
        "deu": ["Kertel"],
        "rus": ["Кярдла"],
        "swe": ["Kärrdal"],
    },
    "Kehra": {
        "est": ["Kehra"],
        "deu": ["Kedder"],
        "rus": ["Кехра"],
    },
    "Tõrva": {
        "est": ["Tõrva"],
        "deu": ["Törwa"],
        "rus": ["Тырва"],
    },
    "Narva-Jõesuu": {
        "est": ["Narva-Jõesuu"],
        "deu": ["Hungerburg"],
        "rus": ["Нарва-Йыэсуу", "Усть-Нарва", "Гунгербург"],
    },
    "Loksa": {
        "est": ["Loksa"],
        "deu": ["Loksa"],
        "rus": ["Локса"],
    },
    "Tamsalu": {
        "est": ["Tamsalu"],
        "deu": ["Tamsal"],
        "rus": ["Тамсалу"],
    },
    "Otepää": {
        "est": ["Otepää"],
        "deu": ["Odenpäh"],
        "rus": ["Отепя"],
        "lat": ["Odenpea"],
    },
    "Räpina": {
        "est": ["Räpina"],
        "deu": ["Rappin"],
        "rus": ["Ряпина"],
    },
    "Kilingi-Nõmme": {
        "est": ["Kilingi-Nõmme"],
        "deu": ["Kilingi-Nõmme"],
        "rus": ["Килинги-Нымме"],
    },
    "Karksi-Nuia": {
        "est": ["Karksi-Nuia"],
        "deu": ["Karkus"],
        "rus": ["Каркси-Нуйа"],
    },
    "Võhma": {
        "est": ["Võhma"],
        "rus": ["Выхма"],
    },
    "Lihula": {
        "est": ["Lihula"],
        "deu": ["Leal"],
        "rus": ["Лихула"],
        "lat": ["Lealia"],
    },
    "Antsla": {
        "est": ["Antsla"],
        "deu": ["Anzen"],
        "rus": ["Антсла"],
    },
    "Suure-Jaani": {
        "est": ["Suure-Jaani"],
        "deu": ["Groß-St. Johannis"],
        "rus": ["Сууре-Яани"],
    },
    "Mustvee": {
        "est": ["Mustvee"],
        "deu": ["Tschorna"],
        "rus": ["Муствеэ"],
    },
    "Abja-Paluoja": {
        "est": ["Abja-Paluoja"],
        "deu": ["Abja"],
        "rus": ["Абья-Палуоя"],
    },
    "Püssi": {
        "est": ["Püssi"],
        "rus": ["Пюсси"],
    },
    "Mõisaküla": {
        "est": ["Mõisaküla"],
        "deu": ["Moiseküll"],
        "rus": ["Мыйзакюла"],
    },
    "Kallaste": {
        "est": ["Kallaste"],
        "deu": ["Kallaste"],
        "rus": ["Калласте"],
    },
}

# ---------------------------------------------------------------------------
# Place type classification
# ---------------------------------------------------------------------------
CAPITAL = "P.PPLC"
COUNTY_CAPITAL = "P.PPLA"
CITY = "P.PPL"

# County capitals (maakonnakeskused)
COUNTY_CAPITALS = {
    "Tartu",  # Tartu County
    "Narva",  # Ida-Viru County (de facto; Jõhvi is administrative)
    "Pärnu",  # Pärnu County
    "Viljandi",  # Viljandi County
    "Rakvere",  # Lääne-Viru County
    "Kuressaare",  # Saare County
    "Valga",  # Valga County
    "Võru",  # Võru County
    "Rapla",  # Rapla County
    "Paide",  # Järva County
    "Jõgeva",  # Jõgeva County
    "Kärdla",  # Hiiu County
    "Haapsalu",  # Lääne County
    "Põlva",  # Põlva County
    "Jõhvi",  # Ida-Viru County (administrative capital)
}


def get_place_type(city_name: str) -> str:
    """Determine GeoNames feature code for an Estonian city."""
    if city_name == "Tallinn":
        return CAPITAL
    if city_name in COUNTY_CAPITALS:
        return COUNTY_CAPITAL
    return CITY


# ---------------------------------------------------------------------------
# Wikidata SPARQL query
# ---------------------------------------------------------------------------
def query_wikidata(qids: list[str]) -> dict[str, dict]:
    """Query Wikidata for city data using VALUES-based lookup."""
    print("Querying Wikidata SPARQL for Estonian cities...")

    batches = [qids[i : i + 80] for i in range(0, len(qids), 80)]
    lookup: dict[str, dict] = {}

    for batch_idx, batch in enumerate(batches):
        values_str = " ".join(f"wd:{qid}" for qid in batch)

        query = f"""SELECT DISTINCT ?item ?itemLabel ?coord ?population ?area
          ?geonames_id ?elevation
        WHERE {{
          VALUES ?item {{ {values_str} }}
          OPTIONAL {{ ?item wdt:P625 ?coord }}
          OPTIONAL {{ ?item wdt:P1082 ?population }}
          OPTIONAL {{ ?item wdt:P2046 ?area }}
          OPTIONAL {{ ?item wdt:P1566 ?geonames_id }}
          OPTIONAL {{ ?item wdt:P2044 ?elevation }}
          SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "en,et"
          }}
        }}
        ORDER BY ?itemLabel"""

        params = urllib.parse.urlencode({"query": query, "format": "json"})
        url = f"https://query.wikidata.org/sparql?{params}"
        req = urllib.request.Request(  # noqa: S310
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": (
                    "ToponymiaEuropaea/0.5 (https://github.com/egkristi/ToponymiaEuropaea)"
                ),
            },
        )

        with urllib.request.urlopen(req, timeout=90) as resp:  # noqa: S310
            data = json.loads(resp.read())

        results = data["results"]["bindings"]
        print(f"  Batch {batch_idx + 1}/{len(batches)}: {len(results)} results")

        for r in results:
            qid = r["item"]["value"].split("/")[-1]
            coord = r.get("coord", {}).get("value", "")
            pop = r.get("population", {}).get("value", "")
            area = r.get("area", {}).get("value", "")
            gn = r.get("geonames_id", {}).get("value", "")
            elev = r.get("elevation", {}).get("value", "")

            lat, lon = None, None
            if coord:
                parts = coord.replace("Point(", "").replace(")", "").split()
                if len(parts) == 2:
                    lon, lat = float(parts[0]), float(parts[1])

            if qid in lookup:
                existing_pop = lookup[qid].get("population") or 0
                new_pop = int(float(pop)) if pop else 0
                if new_pop <= existing_pop:
                    continue

            lookup[qid] = {
                "qid": qid,
                "lat": lat,
                "lon": lon,
                "population": int(float(pop)) if pop else None,
                "area_km2": round(float(area), 2) if area else None,
                "geonames_id": int(gn) if gn else None,
                "elevation": round(float(elev), 1) if elev else None,
            }

        if batch_idx < len(batches) - 1:
            time.sleep(2)

    return lookup


# ---------------------------------------------------------------------------
# Nominatim geometry fetcher
# ---------------------------------------------------------------------------
def fetch_nominatim_geometry(city_name: str, country: str = "Estonia") -> dict | None:
    """Fetch city boundary polygon from OSM Nominatim."""
    search_name = city_name.split("/")[0].strip()

    strategies = [
        {
            "q": f"{search_name}, {country}",
            "format": "geojson",
            "polygon_geojson": 1,
            "limit": 3,
        },
        {
            "city": search_name,
            "country": country,
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    """Ingest all Estonian cities with comprehensive metadata."""
    seen_qids: set[str] = set()
    unique_cities = []
    for city_tuple in ESTONIAN_CITIES:
        qid = city_tuple[3]
        if qid not in seen_qids:
            seen_qids.add(qid)
            unique_cities.append(city_tuple)

    print(f"Ingesting {len(unique_cities)} Estonian cities and towns")
    print(f"Output: {OUTPUT_FILE}")
    print()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_qids = [t[3] for t in unique_cities]
    wikidata_lookup = query_wikidata(all_qids)
    print()

    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}

    for i, (city, _et, _county, _qid, _gn) in enumerate(unique_cities):
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

    print("Creating records...")
    all_records: list[dict] = []

    for city, estonian_name, county, qid, geonames_id in unique_cities:
        wd = wikidata_lookup.get(qid, {})

        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{city}' ({qid}), skipping")
            continue

        source_id = f"wikidata:{qid}"
        source_url = f"https://www.wikidata.org/wiki/{qid}"

        alt_names = ALTERNATIVE_NAMES.get(city, {})
        if not alt_names.get("est"):
            alt_names["est"] = [estonian_name]
        elif estonian_name not in alt_names["est"]:
            alt_names["est"].insert(0, estonian_name)

        geometry = geometries.get(city)
        population = wd.get("population")
        area_km2 = wd.get("area_km2")
        elevation = wd.get("elevation")
        gn_id = wd.get("geonames_id") or geonames_id
        place_type = get_place_type(city)

        record = make_record(
            name_form=city,
            name_normalized=city.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=source_id,
            place_type=place_type,
            language_code="est",
            alternative_names=alt_names,
            source_url=source_url,
            wikidata_qid=qid,
            geonames_id=gn_id,
            area_km2=area_km2,
            population=population,
            elevation=elevation,
            geometry=geometry,
            region=county,
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

    counties: dict[str, int] = {}
    for r in signed_records:
        c = r.get("region", "unknown")
        counties[c] = counties.get(c, 0) + 1

    print("\nBreakdown by county:")
    for county, count in sorted(counties.items(), key=lambda x: -x[1]):
        print(f"  {county}: {count}")


if __name__ == "__main__":
    main()
