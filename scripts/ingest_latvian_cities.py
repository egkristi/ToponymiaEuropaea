#!/usr/bin/env python3
"""Ingest cities and towns across Latvia (Latvijas Republika).

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, area,
  alternative names (Latvian, German, Russian, Polish, Latin, Latgalian)
- OpenStreetMap Nominatim: GeoJSON geometry (city/town boundaries/polygons)

Latvia uses statistical regions (since 2021 reform):
  Riga region: Riga (capital), Jūrmala, Mārupe, Salaspils, Olaine, Ādaži,
    Ikšķile, Baloži, Ķekava, Baldone, Vangaži, Saulkrasti, Ķegums, Ogre,
    Lielvārde, Iecava
  Vidzeme region: Valmiera, Cēsis, Sigulda, Limbaži, Gulbene, Alūksne,
    Madona, Smiltene, Valka, Rūjiena, Salacgrīva, Cesvaine, Līgatne,
    Strenči, Mazsalaca, Aloja, Ape, Staicele, Ainaži, Lubāna, Varakļāni,
    Koknese, Pļaviņas, Straupe
  Kurzeme region: Liepāja, Ventspils, Kuldīga, Saldus, Talsi, Aizpute,
    Grobiņa, Kandava, Brocēni, Priekule, Skrunda, Stende, Sabile,
    Valdemārpils, Pāvilosta, Piltene, Durbe
  Zemgale region: Jelgava, Bauska, Dobele, Tukums, Jēkabpils, Aizkraukle,
    Līvāni, Jaunjelgava, Auce, Viesīte, Aknīste, Ilūkste
  Latgale region: Daugavpils, Rēzekne, Ludza, Krāslava, Preiļi, Balvi,
    Viļāni, Kārsava, Dagda, Zilupe, Viļaka, Seda, Subate, Medumi

Linguistic layers:
  - Latvian (lav): primary, official language
  - German (deu): historically very important — Baltic German heritage
    (Riga, Dünaburg=Daugavpils, Libau=Liepāja, Mitau=Jelgava,
     Windau=Ventspils, Wenden=Cēsis, Goldingen=Kuldīga, Wolmar=Valmiera)
  - Russian (rus): significant minority language, especially in Latgale
  - Polish (pol): historical usage in Latgale
  - Latin (lat): scholarly/ecclesiastical
  - Latgalian (ltg): regional language in Latgale

References:
- https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Latvia
- https://en.wikipedia.org/wiki/Statistical_regions_of_Latvia
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
OUTPUT_FILE = DATABANK_DIR / "places" / "LV" / "wikidata.jsonl"

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
    language_code: str = "lav",
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
        "country_code": "LV",
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
# Latvian cities and towns (pop >= 400 + historically significant)
# (English name, Latvian name, Region, wikidata_qid, geonames_id)
# Excludes Skrunda-1 (abandoned Soviet military base)
# ---------------------------------------------------------------------------
LATVIAN_CITIES: list[tuple[str, str, str, str, int]] = [
    # =========================================================================
    # RIGA REGION (Rīgas reģions)
    # =========================================================================
    ("Riga", "Rīga", "Riga", "Q1773", 456172),
    ("Jūrmala", "Jūrmala", "Riga", "Q178382", 459201),
    ("Ogre", "Ogre", "Riga", "Q731915", 457065),
    ("Salaspils", "Salaspils", "Riga", "Q732986", 455898),
    ("Mārupe", "Mārupe", "Riga", "Q987175", 864723),
    ("Olaine", "Olaine", "Riga", "Q249715", 457052),
    ("Ādaži", "Ādaži", "Riga", "Q336006", 461650),
    ("Ikšķile", "Ikšķile", "Riga", "Q753029", 7628358),
    ("Baloži", "Baloži", "Riga", "Q757043", 864721),
    ("Lielvārde", "Lielvārde", "Riga", "Q597346", 457965),
    ("Iecava", "Iecava", "Riga", "Q1023764", 459624),
    ("Ķekava", "Ķekava", "Riga", "Q344608", 458880),
    ("Baldone", "Baldone", "Riga", "Q789351", 461224),
    ("Vangaži", "Vangaži", "Riga", "Q849832", 454537),
    ("Saulkrasti", "Saulkrasti", "Riga", "Q840823", 455812),
    ("Ķegums", "Ķegums", "Riga", "Q344621", 458892),
    # =========================================================================
    # VIDZEME REGION (Vidzemes reģions)
    # =========================================================================
    ("Valmiera", "Valmiera", "Vidzeme", "Q108037", 453754),
    ("Cēsis", "Cēsis", "Vidzeme", "Q107582", 460570),
    ("Sigulda", "Sigulda", "Vidzeme", "Q465698", 455718),
    ("Limbaži", "Limbaži", "Vidzeme", "Q166684", 457890),
    ("Gulbene", "Gulbene", "Vidzeme", "Q753010", 459668),
    ("Alūksne", "Alūksne", "Vidzeme", "Q291333", 461528),
    ("Madona", "Madona", "Vidzeme", "Q586048", 457714),
    ("Smiltene", "Smiltene", "Vidzeme", "Q840806", 455406),
    ("Valka", "Valka", "Vidzeme", "Q323774", 454572),
    ("Rūjiena", "Rūjiena", "Vidzeme", "Q765976", 456008),
    ("Salacgrīva", "Salacgrīva", "Vidzeme", "Q659665", 455910),
    ("Koknese", "Koknese", "Vidzeme", "Q504681", 458687),
    ("Pļaviņas", "Pļaviņas", "Vidzeme", "Q567747", 456635),
    ("Cesvaine", "Cesvaine", "Vidzeme", "Q757050", 460568),
    ("Līgatne", "Līgatne", "Vidzeme", "Q853761", 11352681),
    ("Strenči", "Strenči", "Vidzeme", "Q851399", 455166),
    ("Mazsalaca", "Mazsalaca", "Vidzeme", "Q844468", 457533),
    ("Aloja", "Aloja", "Vidzeme", "Q659019", 461539),
    ("Ape", "Ape", "Vidzeme", "Q618119", 461442),
    ("Staicele", "Staicele", "Vidzeme", "Q844464", 455298),
    ("Ainaži", "Ainaži", "Vidzeme", "Q405931", 461628),
    ("Lubāna", "Lubāna", "Vidzeme", "Q844477", 457799),
    ("Varakļāni", "Varakļāni", "Vidzeme", "Q849141", 454530),
    ("Straupe", "Straupe", "Vidzeme", "Q124349", 0),
    # =========================================================================
    # KURZEME REGION (Kurzemes reģions)
    # =========================================================================
    ("Liepāja", "Liepāja", "Kurzeme", "Q167668", 457954),
    ("Ventspils", "Ventspils", "Kurzeme", "Q104036", 454311),
    ("Kuldīga", "Kuldīga", "Kurzeme", "Q155281", 11352717),
    ("Saldus", "Saldus", "Kurzeme", "Q744247", 455890),
    ("Talsi", "Talsi", "Kurzeme", "Q520405", 454970),
    ("Aizpute", "Aizpute", "Kurzeme", "Q411723", 11352432),
    ("Grobiņa", "Grobiņa", "Kurzeme", "Q757049", 11352985),
    ("Kandava", "Kandava", "Kurzeme", "Q849152", 459031),
    ("Brocēni", "Brocēni", "Kurzeme", "Q840836", 460786),
    ("Priekule", "Priekule", "Kurzeme", "Q908683", 11352988),
    ("Skrunda", "Skrunda", "Kurzeme", "Q267871", 11352464),
    ("Stende", "Stende", "Kurzeme", "Q909654", 11352938),
    ("Sabile", "Sabile", "Kurzeme", "Q650475", 11352937),
    ("Valdemārpils", "Valdemārpils", "Kurzeme", "Q846341", 11352785),
    ("Pāvilosta", "Pāvilosta", "Kurzeme", "Q840717", 11352779),
    ("Piltene", "Piltene", "Kurzeme", "Q838491", 11352782),
    ("Durbe", "Durbe", "Kurzeme", "Q840801", 11352571),
    # =========================================================================
    # ZEMGALE REGION (Zemgales reģions)
    # =========================================================================
    ("Jelgava", "Jelgava", "Zemgale", "Q179830", 459279),
    ("Bauska", "Bauska", "Zemgale", "Q498256", 461114),
    ("Dobele", "Dobele", "Zemgale", "Q729447", 460312),
    ("Tukums", "Tukums", "Zemgale", "Q636935", 454768),
    ("Jēkabpils", "Jēkabpils", "Zemgale", "Q191120", 459283),
    ("Aizkraukle", "Aizkraukle", "Zemgale", "Q411715", 461615),
    ("Līvāni", "Līvāni", "Zemgale", "Q849156", 457860),
    ("Jaunjelgava", "Jaunjelgava", "Zemgale", "Q835771", 459402),
    ("Auce", "Auce", "Zemgale", "Q758578", 461336),
    ("Viesīte", "Viesīte", "Zemgale", "Q641220", 454216),
    ("Aknīste", "Aknīste", "Zemgale", "Q420333", 461566),
    ("Ilūkste", "Ilūkste", "Zemgale", "Q580373", 11352531),
    # =========================================================================
    # LATGALE REGION (Latgales reģions)
    # =========================================================================
    ("Daugavpils", "Daugavpils", "Latgale", "Q80021", 460413),
    ("Rēzekne", "Rēzekne", "Latgale", "Q180379", 456202),
    ("Ludza", "Ludza", "Latgale", "Q744259", 457776),
    ("Krāslava", "Krāslava", "Latgale", "Q638592", 458623),
    ("Preiļi", "Preiļi", "Latgale", "Q858476", 456530),
    ("Balvi", "Balvi", "Latgale", "Q218402", 461163),
    ("Viļāni", "Viļāni", "Latgale", "Q836513", 454178),
    ("Kārsava", "Kārsava", "Latgale", "Q849147", 7628351),
    ("Dagda", "Dagda", "Latgale", "Q757101", 460474),
    ("Zilupe", "Zilupe", "Latgale", "Q203375", 453850),
    ("Viļaka", "Viļaka", "Latgale", "Q26441", 454130),
    ("Seda", "Seda", "Latgale", "Q578527", 455786),
    ("Subate", "Subate", "Latgale", "Q60044", 455102),
    ("Medumi", "Medumi", "Latgale", "Q2035921", 457482),
]

# ---------------------------------------------------------------------------
# Alternative names — Baltic German heritage is historically crucial
# ---------------------------------------------------------------------------
ALTERNATIVE_NAMES: dict[str, dict[str, list[str]]] = {
    "Riga": {
        "lav": ["Rīga"],
        "deu": ["Riga"],
        "rus": ["Рига"],
        "pol": ["Ryga"],
        "lat": ["Riga"],
        "ltg": ["Reiga"],
        "swe": ["Riga"],
    },
    "Daugavpils": {
        "lav": ["Daugavpils"],
        "deu": ["Dünaburg"],
        "rus": ["Даугавпилс", "Двинск", "Динабург"],
        "pol": ["Dyneburg", "Dźwińsk"],
        "lat": ["Duneburgum"],
        "ltg": ["Daugpiļs"],
    },
    "Liepāja": {
        "lav": ["Liepāja"],
        "deu": ["Libau"],
        "rus": ["Лиепая", "Либава"],
        "pol": ["Lipawa"],
        "lat": ["Liba", "Libavia"],
        "ltg": ["Līpuoja"],
    },
    "Jelgava": {
        "lav": ["Jelgava"],
        "deu": ["Mitau"],
        "rus": ["Елгава", "Митава"],
        "pol": ["Mitawa"],
        "lat": ["Mitavia"],
        "ltg": ["Jelgova"],
    },
    "Jūrmala": {
        "lav": ["Jūrmala"],
        "deu": ["Riga-Strand", "Rigaer Strand"],
        "rus": ["Юрмала"],
    },
    "Ventspils": {
        "lav": ["Ventspils"],
        "deu": ["Windau"],
        "rus": ["Вентспилс", "Виндава"],
        "pol": ["Windawa"],
        "lat": ["Vindovia", "Windavia"],
        "ltg": ["Ventspiļs"],
    },
    "Rēzekne": {
        "lav": ["Rēzekne"],
        "deu": ["Rositten"],
        "rus": ["Резекне", "Режица"],
        "pol": ["Rzeżyca"],
        "lat": ["Rositanum"],
        "ltg": ["Rēzekne", "Rēzne"],
    },
    "Valmiera": {
        "lav": ["Valmiera"],
        "deu": ["Wolmar"],
        "rus": ["Валмиера", "Вольмар"],
        "pol": ["Wolmar"],
        "lat": ["Woldemaria", "Wolmaria"],
    },
    "Ogre": {
        "lav": ["Ogre"],
        "deu": ["Oger"],
        "rus": ["Огре"],
    },
    "Jēkabpils": {
        "lav": ["Jēkabpils"],
        "deu": ["Jakobstadt"],
        "rus": ["Екабпилс", "Якобштадт"],
        "pol": ["Jakobsztadt"],
        "lat": ["Jacobopolis"],
        "ltg": ["Jākubmīsts"],
    },
    "Salaspils": {
        "lav": ["Salaspils"],
        "deu": ["Kirchholm"],
        "rus": ["Саласпилс"],
    },
    "Tukums": {
        "lav": ["Tukums"],
        "deu": ["Tuckum"],
        "rus": ["Тукумс"],
        "lat": ["Tuccumum"],
    },
    "Cēsis": {
        "lav": ["Cēsis"],
        "deu": ["Wenden"],
        "rus": ["Цесис", "Венден"],
        "pol": ["Wenden"],
        "lat": ["Wenda", "Cessis"],
    },
    "Sigulda": {
        "lav": ["Sigulda"],
        "deu": ["Segewold"],
        "rus": ["Сигулда", "Зегевольд"],
    },
    "Kuldīga": {
        "lav": ["Kuldīga"],
        "deu": ["Goldingen"],
        "rus": ["Кулдига", "Гольдинген"],
        "pol": ["Goldyngi"],
        "lat": ["Goldinga"],
    },
    "Bauska": {
        "lav": ["Bauska"],
        "deu": ["Bauske"],
        "rus": ["Бауска"],
        "lat": ["Bausca"],
    },
    "Saldus": {
        "lav": ["Saldus"],
        "deu": ["Frauenburg"],
        "rus": ["Салдус"],
    },
    "Talsi": {
        "lav": ["Talsi"],
        "deu": ["Talsen"],
        "rus": ["Талси"],
    },
    "Dobele": {
        "lav": ["Dobele"],
        "deu": ["Doblen"],
        "rus": ["Добеле"],
    },
    "Mārupe": {
        "lav": ["Mārupe"],
        "rus": ["Марупе"],
    },
    "Limbaži": {
        "lav": ["Limbaži"],
        "deu": ["Lemsal"],
        "rus": ["Лимбажи"],
        "lat": ["Lemsalia"],
    },
    "Gulbene": {
        "lav": ["Gulbene"],
        "deu": ["Schwanenburg"],
        "rus": ["Гулбене"],
    },
    "Alūksne": {
        "lav": ["Alūksne"],
        "deu": ["Marienburg"],
        "rus": ["Алуксне", "Мариенбург"],
        "lat": ["Marienburgum"],
    },
    "Madona": {
        "lav": ["Madona"],
        "deu": ["Modohn"],
        "rus": ["Мадона"],
    },
    "Ludza": {
        "lav": ["Ludza"],
        "deu": ["Ludsen", "Luzin"],
        "rus": ["Лудза", "Люцин"],
        "pol": ["Lucyn"],
        "ltg": ["Ludza", "Ludzys"],
    },
    "Krāslava": {
        "lav": ["Krāslava"],
        "deu": ["Kräslau", "Kreslawka"],
        "rus": ["Краслава"],
        "pol": ["Krasław"],
        "ltg": ["Krōslova"],
    },
    "Līvāni": {
        "lav": ["Līvāni"],
        "deu": ["Livenhof"],
        "rus": ["Ливаны"],
        "ltg": ["Līvuoni"],
    },
    "Aizkraukle": {
        "lav": ["Aizkraukle"],
        "deu": ["Ascheraden"],
        "rus": ["Айзкраукле"],
    },
    "Preiļi": {
        "lav": ["Preiļi"],
        "deu": ["Preli"],
        "rus": ["Прейли"],
        "ltg": ["Preiļi"],
    },
    "Balvi": {
        "lav": ["Balvi"],
        "deu": ["Bolwi"],
        "rus": ["Балви"],
        "ltg": ["Bolvi"],
    },
    "Smiltene": {
        "lav": ["Smiltene"],
        "deu": ["Smilten"],
        "rus": ["Смилтене"],
    },
    "Valka": {
        "lav": ["Valka"],
        "deu": ["Walk"],
        "rus": ["Валка", "Валк"],
        "lat": ["Valca"],
    },
    "Aizpute": {
        "lav": ["Aizpute"],
        "deu": ["Hasenpoth"],
        "rus": ["Айзпуте"],
        "lat": ["Hasenpothia"],
    },
    "Grobiņa": {
        "lav": ["Grobiņa"],
        "deu": ["Grobin"],
        "rus": ["Гробиня"],
        "swe": ["Gröbin"],
        "lat": ["Grobinia"],
    },
    "Kandava": {
        "lav": ["Kandava"],
        "deu": ["Kandau"],
        "rus": ["Кандава"],
    },
    "Olaine": {
        "lav": ["Olaine"],
        "deu": ["Olai"],
        "rus": ["Олайне"],
    },
    "Ādaži": {
        "lav": ["Ādaži"],
        "deu": ["Neuermühlen"],
        "rus": ["Адажи"],
    },
    "Ikšķile": {
        "lav": ["Ikšķile"],
        "deu": ["Uexküll", "Üxküll"],
        "rus": ["Икшкиле"],
        "lat": ["Ykeskola"],
    },
    "Baloži": {
        "lav": ["Baloži"],
        "rus": ["Баложи"],
    },
    "Lielvārde": {
        "lav": ["Lielvārde"],
        "deu": ["Lennewarden"],
        "rus": ["Лиелварде"],
    },
    "Iecava": {
        "lav": ["Iecava"],
        "deu": ["Eckau"],
        "rus": ["Иецава"],
    },
    "Ķekava": {
        "lav": ["Ķekava"],
        "rus": ["Кекава"],
    },
    "Baldone": {
        "lav": ["Baldone"],
        "deu": ["Baldohn"],
        "rus": ["Балдоне"],
    },
    "Saulkrasti": {
        "lav": ["Saulkrasti"],
        "deu": ["Neubad"],
        "rus": ["Саулкрасти"],
    },
    "Brocēni": {
        "lav": ["Brocēni"],
        "deu": ["Brotzen"],
        "rus": ["Броцены"],
    },
    "Pļaviņas": {
        "lav": ["Pļaviņas"],
        "deu": ["Stockmannshof"],
        "rus": ["Плявиняс"],
    },
    "Viļāni": {
        "lav": ["Viļāni"],
        "deu": ["Marienhausen"],
        "rus": ["Вилани"],
        "ltg": ["Viļāni"],
    },
    "Rūjiena": {
        "lav": ["Rūjiena"],
        "deu": ["Rujen"],
        "rus": ["Руйиена"],
    },
    "Salacgrīva": {
        "lav": ["Salacgrīva"],
        "deu": ["Salismünde"],
        "rus": ["Салацгрива"],
    },
    "Koknese": {
        "lav": ["Koknese"],
        "deu": ["Kokenhusen"],
        "rus": ["Кокнесе"],
        "lat": ["Koknesium"],
    },
    "Auce": {
        "lav": ["Auce"],
        "deu": ["Autz"],
        "rus": ["Ауце"],
    },
    "Ķegums": {
        "lav": ["Ķegums"],
        "rus": ["Кегумс"],
    },
    "Ilūkste": {
        "lav": ["Ilūkste"],
        "deu": ["Illuxt"],
        "rus": ["Илуксте", "Иллукст"],
        "ltg": ["Eluikste"],
    },
    "Priekule": {
        "lav": ["Priekule"],
        "deu": ["Preekuln"],
        "rus": ["Приекуле"],
    },
    "Kārsava": {
        "lav": ["Kārsava"],
        "deu": ["Karsau"],
        "rus": ["Карсава"],
        "ltg": ["Kuorsova"],
    },
    "Dagda": {
        "lav": ["Dagda"],
        "deu": ["Dagda"],
        "rus": ["Дагда"],
        "ltg": ["Dagda"],
    },
    "Skrunda": {
        "lav": ["Skrunda"],
        "deu": ["Schrunden"],
        "rus": ["Скрунда"],
    },
    "Jaunjelgava": {
        "lav": ["Jaunjelgava"],
        "deu": ["Friedrichstadt"],
        "rus": ["Яунелгава"],
    },
    "Varakļāni": {
        "lav": ["Varakļāni"],
        "deu": ["Warkland"],
        "rus": ["Варакляны"],
        "ltg": ["Varakļōni"],
    },
    "Stende": {
        "lav": ["Stende"],
        "deu": ["Stenden"],
        "rus": ["Стенде"],
    },
    "Viesīte": {
        "lav": ["Viesīte"],
        "deu": ["Wiesite"],
        "rus": ["Виесите"],
    },
    "Lubāna": {
        "lav": ["Lubāna"],
        "deu": ["Lubahn"],
        "rus": ["Лубана"],
    },
    "Sabile": {
        "lav": ["Sabile"],
        "deu": ["Zabeln"],
        "rus": ["Сабиле"],
    },
    "Zilupe": {
        "lav": ["Zilupe"],
        "deu": ["Rosenau"],
        "rus": ["Зилупе"],
        "ltg": ["Zylupi"],
    },
    "Cesvaine": {
        "lav": ["Cesvaine"],
        "deu": ["Sesswegen"],
        "rus": ["Цесвайне"],
    },
    "Valdemārpils": {
        "lav": ["Valdemārpils"],
        "deu": ["Sassmacken"],
        "rus": ["Валдемарпилс"],
    },
    "Viļaka": {
        "lav": ["Viļaka"],
        "deu": ["Marienhausen"],
        "rus": ["Вилака"],
        "ltg": ["Viļaka"],
    },
    "Seda": {
        "lav": ["Seda"],
        "rus": ["Седа"],
    },
    "Mazsalaca": {
        "lav": ["Mazsalaca"],
        "deu": ["Salisburg"],
        "rus": ["Мазсалаца"],
    },
    "Aloja": {
        "lav": ["Aloja"],
        "deu": ["Allendorf"],
        "rus": ["Алоя"],
    },
    "Līgatne": {
        "lav": ["Līgatne"],
        "deu": ["Ligat"],
        "rus": ["Лигатне"],
    },
    "Strenči": {
        "lav": ["Strenči"],
        "deu": ["Stackeln"],
        "rus": ["Стренчи"],
    },
    "Aknīste": {
        "lav": ["Aknīste"],
        "deu": ["Aknist"],
        "rus": ["Акнисте"],
    },
    "Pāvilosta": {
        "lav": ["Pāvilosta"],
        "deu": ["Paulshafen"],
        "rus": ["Павилоста"],
    },
    "Piltene": {
        "lav": ["Piltene"],
        "deu": ["Pilten"],
        "rus": ["Пилтене"],
        "lat": ["Piltena"],
    },
    "Ape": {
        "lav": ["Ape"],
        "deu": ["Hoppenhof"],
        "rus": ["Апе"],
    },
    "Staicele": {
        "lav": ["Staicele"],
        "deu": ["Staizele"],
        "rus": ["Стайцеле"],
    },
    "Ainaži": {
        "lav": ["Ainaži"],
        "deu": ["Heinaste", "Haynasch"],
        "rus": ["Айнажи"],
    },
    "Subate": {
        "lav": ["Subate"],
        "deu": ["Subbath"],
        "rus": ["Субате"],
        "ltg": ["Subate"],
    },
    "Durbe": {
        "lav": ["Durbe"],
        "deu": ["Durben"],
        "rus": ["Дурбе"],
        "lat": ["Durbia"],
    },
    "Medumi": {
        "lav": ["Medumi"],
        "rus": ["Медуми"],
    },
    "Straupe": {
        "lav": ["Straupe"],
        "deu": ["Roop"],
        "rus": ["Страупе"],
    },
    "Vangaži": {
        "lav": ["Vangaži"],
        "rus": ["Вангажи"],
    },
}

# ---------------------------------------------------------------------------
# Place type classification
# ---------------------------------------------------------------------------
CAPITAL = "P.PPLC"
REGIONAL_CAPITAL = "P.PPLA"
CITY = "P.PPL"

# Regional capitals (approximate — major city per region)
REGIONAL_CAPITALS = {
    "Daugavpils",  # Latgale
    "Liepāja",  # Kurzeme
    "Jelgava",  # Zemgale
    "Valmiera",  # Vidzeme
    "Jūrmala",  # Riga region (second city)
}


def get_place_type(city_name: str) -> str:
    """Determine GeoNames feature code for a Latvian city."""
    if city_name == "Riga":
        return CAPITAL
    if city_name in REGIONAL_CAPITALS:
        return REGIONAL_CAPITAL
    return CITY


# ---------------------------------------------------------------------------
# Wikidata SPARQL query
# ---------------------------------------------------------------------------
def query_wikidata(qids: list[str]) -> dict[str, dict]:
    """Query Wikidata for city data using VALUES-based lookup."""
    print("Querying Wikidata SPARQL for Latvian cities...")

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
            bd:serviceParam wikibase:language "en,lv"
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
def fetch_nominatim_geometry(city_name: str, country: str = "Latvia") -> dict | None:
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
    """Ingest all Latvian cities with comprehensive metadata."""
    seen_qids: set[str] = set()
    unique_cities = []
    for city_tuple in LATVIAN_CITIES:
        qid = city_tuple[3]
        if qid not in seen_qids:
            seen_qids.add(qid)
            unique_cities.append(city_tuple)

    print(f"Ingesting {len(unique_cities)} Latvian cities and towns")
    print(f"Output: {OUTPUT_FILE}")
    print()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_qids = [t[3] for t in unique_cities]
    wikidata_lookup = query_wikidata(all_qids)
    print()

    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}

    for i, (city, _lv, _region, _qid, _gn) in enumerate(unique_cities):
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

    for city, latvian_name, region, qid, geonames_id in unique_cities:
        wd = wikidata_lookup.get(qid, {})

        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{city}' ({qid}), skipping")
            continue

        source_id = f"wikidata:{qid}"
        source_url = f"https://www.wikidata.org/wiki/{qid}"

        alt_names = ALTERNATIVE_NAMES.get(city, {})
        if not alt_names.get("lav"):
            alt_names["lav"] = [latvian_name]
        elif latvian_name not in alt_names["lav"]:
            alt_names["lav"].insert(0, latvian_name)

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
            language_code="lav",
            alternative_names=alt_names,
            source_url=source_url,
            wikidata_qid=qid,
            geonames_id=gn_id,
            area_km2=area_km2,
            population=population,
            elevation=elevation,
            geometry=geometry,
            region=region,
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

    regions: dict[str, int] = {}
    for r in signed_records:
        reg = r.get("region", "unknown")
        regions[reg] = regions.get(reg, 0) + 1

    print("\nBreakdown by region:")
    for region, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {region}: {count}")


if __name__ == "__main__":
    main()
