#!/usr/bin/env python3
"""Ingest cities and towns across Lithuania (Lietuvos Respublika).

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, area,
  alternative names (Lithuanian, German, Russian, Polish, Latin, Belarusian)
- OpenStreetMap Nominatim: GeoJSON geometry (city/town boundaries/polygons)

Lithuania has 10 counties (apskritys):
  Vilnius County (Vilniaus): Vilnius (capital), Visaginas, Šalčininkai,
    Švenčionėliai, Nemenčinė, Švenčionys, Pabradė, Trakai, Elektrėnai,
    Grigiškės, Lentvaris, Vievis
  Kaunas County (Kauno): Kaunas, Jonava, Kėdainiai, Garliava, Prienai,
    Kaišiadorys, Raseiniai, Vilkija, Ariogala, Ežerėlis
  Klaipėda County (Klaipėdos): Klaipėda, Palanga, Kretinga, Šilutė,
    Gargždai, Neringa, Nida
  Šiauliai County (Šiaulių): Šiauliai, Radviliškis, Kuršėnai, Joniškis,
    Naujoji Akmenė, Kelmė, Pakruojis
  Panevėžys County (Panevėžio): Panevėžys, Biržai, Rokiškis, Kupiškis,
    Pasvalys, Anykščiai
  Alytus County (Alytaus): Alytus, Varėna, Druskininkai, Lazdijai
  Marijampolė County (Marijampolės): Marijampolė, Vilkaviškis, Šakiai,
    Kazlų Rūda, Kalvarija, Kybartai
  Utena County (Utenos): Utena, Zarasai, Molėtai, Širvintos, Visaginas
  Tauragė County (Tauragės): Tauragė, Jurbarkas, Šilalė, Pagėgiai
  Telšiai County (Telšių): Telšiai, Mažeikiai, Plungė, Skuodas

Linguistic layers:
  - Lithuanian (lit): primary, official language
  - German (deu): historically important — Wilna=Vilnius, Kauen/Kowno=Kaunas,
    Memel=Klaipėda, Schaulen=Šiauliai
  - Russian (rus): significant usage, especially Soviet era
  - Polish (pol): historically important — Wilno=Vilnius, Kowno=Kaunas
  - Latin (lat): scholarly/ecclesiastical
  - Belarusian (bel): border areas and historical usage

References:
- https://en.wikipedia.org/wiki/List_of_cities_in_Lithuania
- https://en.wikipedia.org/wiki/Counties_of_Lithuania
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
OUTPUT_FILE = DATABANK_DIR / "places" / "LT" / "wikidata.jsonl"

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
    language_code: str = "lit",
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
        "country_code": "LT",
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
# Lithuanian cities and towns (pop >= 500 + historically significant)
# (English name, Lithuanian name, County, wikidata_qid, geonames_id)
# ---------------------------------------------------------------------------
LITHUANIAN_CITIES: list[tuple[str, str, str, str, int]] = [
    # =========================================================================
    # VILNIUS COUNTY (Vilniaus apskritis)
    # =========================================================================
    ("Vilnius", "Vilnius", "Vilnius County", "Q216", 593116),
    ("Elektrėnai", "Elektrėnai", "Vilnius County", "Q286554", 599602),
    ("Grigiškės", "Grigiškės", "Vilnius County", "Q950639", 599161),
    ("Lentvaris", "Lentvaris", "Vilnius County", "Q923393", 597532),
    ("Nemenčinė", "Nemenčinė", "Vilnius County", "Q118910", 596664),
    ("Pabradė", "Pabradė", "Vilnius County", "Q1004328", 596473),
    ("Šalčininkai", "Šalčininkai", "Vilnius County", "Q391011", 595016),
    ("Švenčionėliai", "Švenčionėliai", "Vilnius County", "Q392772", 594067),
    ("Švenčionys", "Švenčionys", "Vilnius County", "Q137863", 594064),
    ("Trakai", "Trakai", "Vilnius County", "Q191015", 864523),
    ("Vievis", "Vievis", "Vilnius County", "Q1004332", 593462),
    # =========================================================================
    # KAUNAS COUNTY (Kauno apskritis)
    # =========================================================================
    ("Kaunas", "Kaunas", "Kaunas County", "Q4115712", 598316),
    ("Jonava", "Jonava", "Kaunas County", "Q743218", 598818),
    ("Kėdainiai", "Kėdainiai", "Kaunas County", "Q735138", 598272),
    ("Garliava", "Garliava", "Kaunas County", "Q1004312", 599504),
    ("Prienai", "Prienai", "Kaunas County", "Q499318", 595596),
    ("Kaišiadorys", "Kaišiadorys", "Kaunas County", "Q614855", 598286),
    ("Raseiniai", "Raseiniai", "Kaunas County", "Q658562", 595449),
    ("Vilkija", "Vilkija", "Kaunas County", "Q1994818", 593144),
    ("Ariogala", "Ariogala", "Kaunas County", "Q1004320", 600962),
    ("Ežerėlis", "Ežerėlis", "Kaunas County", "Q2044597", 599579),
    # =========================================================================
    # KLAIPĖDA COUNTY (Klaipėdos apskritis)
    # =========================================================================
    ("Klaipėda", "Klaipėda", "Klaipėda County", "Q776965", 598099),
    ("Palanga", "Palanga", "Klaipėda County", "Q2047414", 596238),
    ("Kretinga", "Kretinga", "Klaipėda County", "Q1788115", 864494),
    ("Šilutė", "Šilutė", "Klaipėda County", "Q391626", 594656),
    ("Gargždai", "Gargždai", "Klaipėda County", "Q259272", 864493),
    ("Neringa", "Neringa", "Klaipėda County", "Q27892", 595842),
    ("Nida", "Nida", "Klaipėda County", "Q1004306", 596612),
    ("Pagėgiai", "Pagėgiai", "Klaipėda County", "Q643376", 595835),
    # =========================================================================
    # ŠIAULIAI COUNTY (Šiaulių apskritis)
    # =========================================================================
    ("Šiauliai", "Šiauliai", "Šiauliai County", "Q134712", 594739),
    ("Radviliškis", "Radviliškis", "Šiauliai County", "Q318686", 595449),
    ("Kuršėnai", "Kuršėnai", "Šiauliai County", "Q835856", 597769),
    ("Joniškis", "Joniškis", "Šiauliai County", "Q847715", 864504),
    ("Naujoji Akmenė", "Naujoji Akmenė", "Šiauliai County", "Q835848", 596719),
    ("Kelmė", "Kelmė", "Šiauliai County", "Q658230", 598257),
    ("Pakruojis", "Pakruojis", "Šiauliai County", "Q1004302", 596260),
    # =========================================================================
    # PANEVĖŽYS COUNTY (Panevėžio apskritis)
    # =========================================================================
    ("Panevėžys", "Panevėžys", "Panevėžys County", "Q1719466", 596128),
    ("Biržai", "Biržai", "Panevėžys County", "Q804035", 600438),
    ("Rokiškis", "Rokiškis", "Panevėžys County", "Q1693963", 864502),
    ("Kupiškis", "Kupiškis", "Panevėžys County", "Q820024", 597806),
    ("Pasvalys", "Pasvalys", "Panevėžys County", "Q945484", 864501),
    ("Anykščiai", "Anykščiai", "Panevėžys County", "Q505416", 600994),
    # =========================================================================
    # ALYTUS COUNTY (Alytaus apskritis)
    # =========================================================================
    ("Alytus", "Alytus", "Alytus County", "Q450625", 601084),
    ("Varėna", "Varėna", "Alytus County", "Q835843", 593406),
    ("Druskininkai", "Druskininkai", "Alytus County", "Q1261509", 599757),
    ("Lazdijai", "Lazdijai", "Alytus County", "Q923643", 597596),
    # =========================================================================
    # MARIJAMPOLĖ COUNTY (Marijampolės apskritis)
    # =========================================================================
    ("Marijampolė", "Marijampolė", "Marijampolė County", "Q1351046", 597231),
    ("Vilkaviškis", "Vilkaviškis", "Marijampolė County", "Q852272", 593153),
    ("Šakiai", "Šakiai", "Marijampolė County", "Q390969", 595044),
    ("Kazlų Rūda", "Kazlų Rūda", "Marijampolė County", "Q945473", 598286),
    ("Kalvarija", "Kalvarija", "Marijampolė County", "Q1004298", 598512),
    ("Kybartai", "Kybartai", "Marijampolė County", "Q1004295", 597729),
    # =========================================================================
    # UTENA COUNTY (Utenos apskritis)
    # =========================================================================
    ("Utena", "Utena", "Utena County", "Q189157", 593672),
    ("Visaginas", "Visaginas", "Utena County", "Q203892", 864515),
    ("Zarasai", "Zarasai", "Utena County", "Q147750", 592891),
    ("Molėtai", "Molėtai", "Utena County", "Q957530", 596867),
    ("Širvintos", "Širvintos", "Utena County", "Q391764", 864521),
    # =========================================================================
    # TAURAGĖ COUNTY (Tauragės apskritis)
    # =========================================================================
    ("Tauragė", "Tauragė", "Tauragė County", "Q193787", 593959),
    ("Jurbarkas", "Jurbarkas", "Tauragė County", "Q835838", 598655),
    ("Šilalė", "Šilalė", "Tauragė County", "Q391582", 594693),
    # =========================================================================
    # TELŠIAI COUNTY (Telšių apskritis)
    # =========================================================================
    ("Telšiai", "Telšiai", "Telšiai County", "Q2222616", 593926),
    ("Mažeikiai", "Mažeikiai", "Telšiai County", "Q203675", 597188),
    ("Plungė", "Plungė", "Telšiai County", "Q977255", 595689),
    ("Skuodas", "Skuodas", "Telšiai County", "Q1004290", 594488),
    # =========================================================================
    # ADDITIONAL SMALLER TOWNS (pop >= 500)
    # =========================================================================
    ("Birštonas", "Birštonas", "Kaunas County", "Q185555", 600443),
    ("Rietavas", "Rietavas", "Telšiai County", "Q3657", 595284),
    ("Simnas", "Simnas", "Alytus County", "Q1892074", 594639),
    ("Žiežmariai", "Žiežmariai", "Kaunas County", "Q4178675", 592778),
    ("Dūkštas", "Dūkštas", "Utena County", "Q2356406", 599727),
    ("Eišiškės", "Eišiškės", "Vilnius County", "Q58880", 597451),
    ("Jieznas", "Jieznas", "Kaunas County", "Q47068", 598058),
    ("Kavarskas", "Kavarskas", "Utena County", "Q2356376", 598304),
    ("Obeliai", "Obeliai", "Panevėžys County", "Q1987043", 596545),
    ("Pandėlys", "Pandėlys", "Panevėžys County", "Q2375484", 596144),
    ("Seda", "Seda", "Telšiai County", "Q394756", 594867),
    ("Tytuvėnai", "Tytuvėnai", "Šiauliai County", "Q1024676", 593748),
    ("Varniai", "Varniai", "Telšiai County", "Q621181", 593378),
    ("Veisiejai", "Veisiejai", "Alytus County", "Q2044626", 593338),
    ("Virbalis", "Virbalis", "Marijampolė County", "Q1024673", 593086),
    ("Žagarė", "Žagarė", "Šiauliai County", "Q393332", 592942),
    # =========================================================================
    # HISTORICALLY SIGNIFICANT (may have smaller population)
    # =========================================================================
    ("Kernavė", "Kernavė", "Vilnius County", "Q215315", 598226),
]

# ---------------------------------------------------------------------------
# Alternative names — German and Polish historical names very important
# ---------------------------------------------------------------------------
ALTERNATIVE_NAMES: dict[str, dict[str, list[str]]] = {
    "Vilnius": {
        "lit": ["Vilnius"],
        "deu": ["Wilna"],
        "pol": ["Wilno"],
        "rus": ["Вильнюс", "Вильна", "Вильно"],
        "bel": ["Вільня", "Вільнюс"],
        "lat": ["Vilna", "Vilnensis"],
        "yid": ["ווילנע"],
    },
    "Kaunas": {
        "lit": ["Kaunas"],
        "deu": ["Kauen", "Kowno"],
        "pol": ["Kowno"],
        "rus": ["Каунас", "Ковно"],
        "bel": ["Коўна", "Каўнас"],
        "lat": ["Couna", "Kowna"],
    },
    "Klaipėda": {
        "lit": ["Klaipėda"],
        "deu": ["Memel"],
        "pol": ["Kłajpeda", "Memel"],
        "rus": ["Клайпеда", "Мемель"],
        "lat": ["Memela", "Clivopedum"],
        "swe": ["Memel"],
    },
    "Šiauliai": {
        "lit": ["Šiauliai"],
        "deu": ["Schaulen"],
        "pol": ["Szawle"],
        "rus": ["Шяуляй", "Шавли"],
        "lat": ["Sauli", "Souli"],
    },
    "Panevėžys": {
        "lit": ["Panevėžys"],
        "deu": ["Ponewiesch"],
        "pol": ["Poniewież"],
        "rus": ["Паневежис"],
        "lat": ["Ponievecia"],
    },
    "Alytus": {
        "lit": ["Alytus"],
        "deu": ["Alitten", "Olita"],
        "pol": ["Olita"],
        "rus": ["Алитус", "Олита"],
        "lat": ["Alita"],
    },
    "Marijampolė": {
        "lit": ["Marijampolė", "Kapsukas"],
        "deu": ["Mariampol"],
        "pol": ["Mariampol"],
        "rus": ["Мариямполе", "Капсукас"],
    },
    "Utena": {
        "lit": ["Utena"],
        "deu": ["Utena"],
        "pol": ["Uciana"],
        "rus": ["Утена"],
    },
    "Telšiai": {
        "lit": ["Telšiai"],
        "deu": ["Telschi"],
        "pol": ["Telsze"],
        "rus": ["Тельшяй"],
        "lat": ["Telsia"],
    },
    "Tauragė": {
        "lit": ["Tauragė"],
        "deu": ["Tauroggen"],
        "pol": ["Taurogi"],
        "rus": ["Таураге"],
    },
    "Jonava": {
        "lit": ["Jonava"],
        "deu": ["Janow"],
        "pol": ["Janów"],
        "rus": ["Йонава"],
    },
    "Kėdainiai": {
        "lit": ["Kėdainiai"],
        "deu": ["Kedahnen", "Keidany"],
        "pol": ["Kiejdany"],
        "rus": ["Кедайняй"],
        "lat": ["Keidani"],
    },
    "Palanga": {
        "lit": ["Palanga"],
        "deu": ["Polangen"],
        "pol": ["Połąga"],
        "rus": ["Паланга"],
        "lat": ["Palanga"],
    },
    "Druskininkai": {
        "lit": ["Druskininkai"],
        "deu": ["Druskieniki"],
        "pol": ["Druskieniki"],
        "rus": ["Друскининкай"],
    },
    "Biržai": {
        "lit": ["Biržai"],
        "deu": ["Birsen", "Birschen"],
        "pol": ["Birże"],
        "rus": ["Биржай"],
    },
    "Rokiškis": {
        "lit": ["Rokiškis"],
        "deu": ["Rakischki"],
        "pol": ["Rakiszki"],
        "rus": ["Рокишкис"],
    },
    "Kretinga": {
        "lit": ["Kretinga"],
        "deu": ["Krottingen"],
        "pol": ["Kretynga"],
        "rus": ["Кретинга"],
    },
    "Šilutė": {
        "lit": ["Šilutė"],
        "deu": ["Heydekrug"],
        "rus": ["Шилуте"],
    },
    "Gargždai": {
        "lit": ["Gargždai"],
        "deu": ["Garsden", "Gorzdy"],
        "rus": ["Гаргждай"],
    },
    "Radviliškis": {
        "lit": ["Radviliškis"],
        "deu": ["Radziwilischki"],
        "pol": ["Radziwiłłiszki"],
        "rus": ["Радвилишкис"],
    },
    "Joniškis": {
        "lit": ["Joniškis"],
        "deu": ["Jonischkis"],
        "pol": ["Janiszki"],
        "rus": ["Йонишкис"],
    },
    "Naujoji Akmenė": {
        "lit": ["Naujoji Akmenė"],
        "deu": ["Neu-Akmene"],
        "rus": ["Науйойи-Акмяне"],
    },
    "Kelmė": {
        "lit": ["Kelmė"],
        "deu": ["Kielmy"],
        "pol": ["Kielmy"],
        "rus": ["Кельме"],
    },
    "Visaginas": {
        "lit": ["Visaginas", "Sniečkus"],
        "rus": ["Висагинас", "Снечкус"],
    },
    "Trakai": {
        "lit": ["Trakai"],
        "deu": ["Traken", "Troki"],
        "pol": ["Troki"],
        "rus": ["Тракай", "Троки"],
        "lat": ["Troci"],
    },
    "Prienai": {
        "lit": ["Prienai"],
        "deu": ["Prieni"],
        "pol": ["Preny"],
        "rus": ["Пренай"],
    },
    "Kupiškis": {
        "lit": ["Kupiškis"],
        "deu": ["Kupischki"],
        "pol": ["Kupiszki"],
        "rus": ["Купишкис"],
    },
    "Pasvalys": {
        "lit": ["Pasvalys"],
        "deu": ["Poswol"],
        "pol": ["Poswol"],
        "rus": ["Пасвалис"],
    },
    "Anykščiai": {
        "lit": ["Anykščiai"],
        "deu": ["Anikscht"],
        "pol": ["Onikszty"],
        "rus": ["Аникщяй"],
    },
    "Varėna": {
        "lit": ["Varėna"],
        "deu": ["Orany"],
        "pol": ["Orany"],
        "rus": ["Варена"],
    },
    "Lazdijai": {
        "lit": ["Lazdijai"],
        "deu": ["Lazdijai"],
        "pol": ["Łoździeje"],
        "rus": ["Лаздияй"],
    },
    "Vilkaviškis": {
        "lit": ["Vilkaviškis"],
        "deu": ["Wilkowischken"],
        "pol": ["Wyłkowyszki"],
        "rus": ["Вилкавишкис"],
    },
    "Šakiai": {
        "lit": ["Šakiai"],
        "deu": ["Schaken"],
        "pol": ["Szaki"],
        "rus": ["Шакяй"],
    },
    "Jurbarkas": {
        "lit": ["Jurbarkas"],
        "deu": ["Georgenburg", "Jurburg"],
        "pol": ["Jurborg"],
        "rus": ["Юрбаркас"],
    },
    "Mažeikiai": {
        "lit": ["Mažeikiai"],
        "deu": ["Moscheiken"],
        "rus": ["Мажейкяй"],
    },
    "Plungė": {
        "lit": ["Plungė"],
        "deu": ["Plungen"],
        "pol": ["Płungiany"],
        "rus": ["Плунге"],
    },
    "Neringa": {
        "lit": ["Neringa"],
        "deu": ["Nidden"],
        "rus": ["Неринга"],
    },
    "Zarasai": {
        "lit": ["Zarasai"],
        "deu": ["Zarasai"],
        "pol": ["Jeziorosy"],
        "rus": ["Зарасай"],
    },
    "Kaišiadorys": {
        "lit": ["Kaišiadorys"],
        "deu": ["Kaischadorys"],
        "pol": ["Koszeadary"],
        "rus": ["Кайшядорис"],
    },
    "Raseiniai": {
        "lit": ["Raseiniai"],
        "deu": ["Rossieni"],
        "pol": ["Rosienie"],
        "rus": ["Расейняй"],
    },
    "Elektrėnai": {
        "lit": ["Elektrėnai"],
        "rus": ["Электренай"],
    },
    "Kazlų Rūda": {
        "lit": ["Kazlų Rūda"],
        "rus": ["Казлу-Руда"],
    },
    "Kalvarija": {
        "lit": ["Kalvarija"],
        "deu": ["Kalvarien"],
        "pol": ["Kalwaria"],
        "rus": ["Калвария"],
    },
    "Kybartai": {
        "lit": ["Kybartai"],
        "deu": ["Kibarten", "Kybartai"],
        "rus": ["Кибартай"],
    },
    "Pakruojis": {
        "lit": ["Pakruojis"],
        "deu": ["Pakruojis"],
        "rus": ["Пакруойис"],
    },
    "Skuodas": {
        "lit": ["Skuodas"],
        "deu": ["Skudy"],
        "pol": ["Szkudy"],
        "rus": ["Скуодас"],
    },
    "Kernavė": {
        "lit": ["Kernavė"],
        "deu": ["Kernave"],
        "pol": ["Kiernów"],
        "rus": ["Кярнаве"],
        "lat": ["Kernavia"],
    },
    "Birštonas": {
        "lit": ["Birštonas"],
        "deu": ["Birschtan"],
        "pol": ["Birsztany"],
        "rus": ["Бирштонас"],
    },
    "Nida": {
        "lit": ["Nida"],
        "deu": ["Nidden"],
        "rus": ["Нида"],
    },
    "Molėtai": {
        "lit": ["Molėtai"],
        "pol": ["Malaty"],
        "rus": ["Молетай"],
    },
    "Širvintos": {
        "lit": ["Širvintos"],
        "pol": ["Szyrwinty"],
        "rus": ["Ширвинтос"],
    },
    "Šilalė": {
        "lit": ["Šilalė"],
        "deu": ["Schillehnen"],
        "rus": ["Шилале"],
    },
    "Garliava": {
        "lit": ["Garliava"],
        "rus": ["Гарлява"],
    },
    "Kuršėnai": {
        "lit": ["Kuršėnai"],
        "deu": ["Kurschany"],
        "rus": ["Куршенай"],
    },
    "Grigiškės": {
        "lit": ["Grigiškės"],
        "pol": ["Grzegorzew"],
        "rus": ["Григишкес"],
    },
    "Pagėgiai": {
        "lit": ["Pagėgiai"],
        "deu": ["Pogegen"],
        "rus": ["Пагегяй"],
    },
    "Lentvaris": {
        "lit": ["Lentvaris"],
        "pol": ["Landwarów"],
        "rus": ["Лентварис"],
    },
    "Ariogala": {
        "lit": ["Ariogala"],
        "deu": ["Ariogala"],
        "pol": ["Ejragola"],
        "rus": ["Ариогала"],
    },
    "Varniai": {
        "lit": ["Varniai"],
        "deu": ["Worni"],
        "pol": ["Worniany"],
        "rus": ["Варняй"],
        "lat": ["Mednicae", "Varniai"],
    },
}

# ---------------------------------------------------------------------------
# Place type classification
# ---------------------------------------------------------------------------
CAPITAL = "P.PPLC"
COUNTY_CAPITAL = "P.PPLA"
CITY = "P.PPL"

COUNTY_CAPITALS = {
    "Kaunas",
    "Klaipėda",
    "Šiauliai",
    "Panevėžys",
    "Alytus",
    "Marijampolė",
    "Utena",
    "Tauragė",
    "Telšiai",
}


def get_place_type(city_name: str) -> str:
    """Determine GeoNames feature code for a Lithuanian city."""
    if city_name == "Vilnius":
        return CAPITAL
    if city_name in COUNTY_CAPITALS:
        return COUNTY_CAPITAL
    return CITY


# ---------------------------------------------------------------------------
# Wikidata SPARQL query
# ---------------------------------------------------------------------------
def query_wikidata(qids: list[str]) -> dict[str, dict]:
    """Query Wikidata for city data using VALUES-based lookup."""
    print("Querying Wikidata SPARQL for Lithuanian cities...")

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
            bd:serviceParam wikibase:language "en,lt"
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
def fetch_nominatim_geometry(city_name: str, country: str = "Lithuania") -> dict | None:
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
    """Ingest all Lithuanian cities with comprehensive metadata."""
    seen_qids: set[str] = set()
    unique_cities = []
    for city_tuple in LITHUANIAN_CITIES:
        qid = city_tuple[3]
        if qid not in seen_qids:
            seen_qids.add(qid)
            unique_cities.append(city_tuple)

    print(f"Ingesting {len(unique_cities)} Lithuanian cities and towns")
    print(f"Output: {OUTPUT_FILE}")
    print()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_qids = [t[3] for t in unique_cities]
    wikidata_lookup = query_wikidata(all_qids)
    print()

    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}

    for i, (city, _lt, _county, _qid, _gn) in enumerate(unique_cities):
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

    for city, lithuanian_name, county, qid, geonames_id in unique_cities:
        wd = wikidata_lookup.get(qid, {})

        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{city}' ({qid}), skipping")
            continue

        source_id = f"wikidata:{qid}"
        source_url = f"https://www.wikidata.org/wiki/{qid}"

        alt_names = ALTERNATIVE_NAMES.get(city, {})
        if not alt_names.get("lit"):
            alt_names["lit"] = [lithuanian_name]
        elif lithuanian_name not in alt_names["lit"]:
            alt_names["lit"].insert(0, lithuanian_name)

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
            language_code="lit",
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
