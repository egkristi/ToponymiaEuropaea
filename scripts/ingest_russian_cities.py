#!/usr/bin/env python3
"""Ingest cities and towns across Russia (Российская Федерация).

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, area,
  alternative names (Russian, Tatar, German, Finnish, Latin, Old Church Slavonic)
- OpenStreetMap Nominatim: GeoJSON geometry (city/town boundaries/polygons)

Russia spans 11 time zones and 85 federal subjects grouped into 8 federal
districts:
  Central (Центральный): Moscow Oblast, Tver, Ryazan, Tula, etc.
  Northwestern (Северо-Западный): St Petersburg, Pskov, Novgorod, etc.
  Southern (Южный): Rostov, Krasnodar, Volgograd, Crimea, etc.
  North Caucasian (Северо-Кавказский): Dagestan, Chechnya, Stavropol, etc.
  Volga (Приволжский): Tatarstan, Bashkortostan, Samara, Nizhny Novgorod, etc.
  Urals (Уральский): Sverdlovsk, Chelyabinsk, Tyumen, KhMAO, YaNAO
  Siberian (Сибирский): Novosibirsk, Krasnoyarsk, Irkutsk, Tomsk, etc.
  Far Eastern (Дальневосточный): Vladivostok, Khabarovsk, Yakutsk, etc.

Linguistic layers:
  - Russian (rus): primary, official language throughout
  - Tatar (tat): Tatarstan, Bashkortostan
  - Bashkir (bak): Bashkortostan
  - Chechen (che): Chechnya
  - Chuvash (chv): Chuvashia
  - Udmurt (udm): Udmurtia
  - Mari (chm): Mari El
  - Komi (kpv): Komi Republic
  - Yakut/Sakha (sah): Sakha Republic
  - Buryat (bua): Buryatia
  - German (deu): historical/academic usage
  - Finnish (fin): border cities, Karelia
  - Latin (lat): scholarly/ecclesiastical
  - Old East Slavic (orv): historical forms

References:
- https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_Russia_by_population
- https://en.wikipedia.org/wiki/Federal_subjects_of_Russia
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
OUTPUT_FILE = DATABANK_DIR / "places" / "RU" / "wikidata.jsonl"

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
    language_code: str = "rus",
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
    federal_district: str | None = None,
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
        "country_code": "RU",
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
    if federal_district:
        record["municipality"] = federal_district
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ---------------------------------------------------------------------------
# Russian cities
# (English name, Russian name, region, wikidata_qid, geonames_id)
# ---------------------------------------------------------------------------
RUSSIAN_CITIES: list[tuple[str, str, str, str, int]] = [
    # =========================================================================
    # CENTRAL FEDERAL DISTRICT (Центральный)
    # =========================================================================
    ("Moscow", "Москва", "Moscow", "Q649", 524901),
    ("Voronezh", "Воронеж", "Voronezh Oblast", "Q3426", 472045),
    ("Tula", "Тула", "Tula Oblast", "Q2770", 480562),
    ("Kursk", "Курск", "Kursk Oblast", "Q3159", 538560),
    ("Bryansk", "Брянск", "Bryansk Oblast", "Q2801", 571476),
    ("Vladimir", "Владимир", "Vladimir Oblast", "Q2684", 473247),
    ("Kaluga", "Калуга", "Kaluga Oblast", "Q2837", 553915),
    ("Belgorod", "Белгород", "Belgorod Oblast", "Q3323", 578072),
    ("Smolensk", "Смоленск", "Smolensk Oblast", "Q2337", 491687),
    ("Tver", "Тверь", "Tver Oblast", "Q2288", 480060),
    ("Ryazan", "Рязань", "Ryazan Oblast", "Q2746", 500096),
    ("Tambov", "Тамбов", "Tambov Oblast", "Q3544", 484646),
    ("Mytishchi", "Мытищи", "Moscow Oblast", "Q23185", 523812),
    ("Stary Oskol", "Старый Оскол", "Belgorod Oblast", "Q196486", 487928),
    ("Obninsk", "Обнинск", "Kaluga Oblast", "Q175651", 516436),
    ("Novomoskovsk", "Новомосковск", "Tula Oblast", "Q175161", 518557),
    ("Murom", "Муром", "Vladimir Oblast", "Q162677", 524294),
    ("Sergiyev Posad", "Сергиев Посад", "Moscow Oblast", "Q193722", 496638),
    ("Zheleznogorsk", "Железногорск", "Kursk Oblast", "Q72536", 463343),
    ("Alexandrov", "Александров", "Vladimir Oblast", "Q103377", 583350),
    # Historic Golden Ring cities
    ("Suzdal", "Суздаль", "Vladimir Oblast", "Q15757", 485824),
    ("Rostov Veliky", "Ростов", "Yaroslavl Oblast", "Q193342", 501183),
    ("Pereslavl-Zalessky", "Переславль-Залесский", "Yaroslavl Oblast", "Q178188", 511359),
    # =========================================================================
    # NORTHWESTERN FEDERAL DISTRICT (Северо-Западный)
    # =========================================================================
    ("Saint Petersburg", "Санкт-Петербург", "Saint Petersburg", "Q656", 498817),
    ("Kaliningrad", "Калининград", "Kaliningrad Oblast", "Q1829", 554234),
    ("Veliky Novgorod", "Великий Новгород", "Novgorod Oblast", "Q2235", 519336),
    ("Pskov", "Псков", "Pskov Oblast", "Q2214", 504341),
    ("Petrozavodsk", "Петрозаводск", "Republic of Karelia", "Q1895", 509820),
    ("Syktyvkar", "Сыктывкар", "Komi Republic", "Q2143", 485239),
    ("Murmansk", "Мурманск", "Murmansk Oblast", "Q1763", 524305),
    ("Arkhangelsk", "Архангельск", "Arkhangelsk Oblast", "Q1851", 581049),
    ("Vologda", "Вологда", "Vologda Oblast", "Q2191", 472459),
    ("Gatchina", "Гатчина", "Leningrad Oblast", "Q7436", 561887),
    # Historic cities
    ("Velikiy Ustyug", "Великий Устюг", "Vologda Oblast", "Q111048", 476062),
    ("Staraya Russa", "Старая Русса", "Novgorod Oblast", "Q196479", 489088),
    ("Tikhvin", "Тихвин", "Leningrad Oblast", "Q15336", 483019),
    ("Vyborg", "Выборг", "Leningrad Oblast", "Q14657", 470546),
    # =========================================================================
    # SOUTHERN FEDERAL DISTRICT (Южный)
    # =========================================================================
    ("Rostov-on-Don", "Ростов-на-Дону", "Rostov Oblast", "Q908", 501175),
    ("Krasnodar", "Краснодар", "Krasnodar Krai", "Q3646", 542420),
    ("Volgograd", "Волгоград", "Volgograd Oblast", "Q914", 472757),
    ("Astrakhan", "Астрахань", "Astrakhan Oblast", "Q3927", 580497),
    ("Sevastopol", "Севастополь", "Sevastopol", "Q7525", 694423),
    ("Simferopol", "Симферополь", "Republic of Crimea", "Q19566", 693805),
    ("Volzhsky", "Волжский", "Volgograd Oblast", "Q98995", 472231),
    ("Taganrog", "Таганрог", "Rostov Oblast", "Q170513", 484907),
    ("Novorossiysk", "Новороссийск", "Krasnodar Krai", "Q15760", 518255),
    ("Shakhty", "Шахты", "Rostov Oblast", "Q198206", 496015),
    ("Novocherkassk", "Новочеркасск", "Rostov Oblast", "Q175452", 518970),
    ("Kerch", "Керчь", "Republic of Crimea", "Q157065", 706524),
    ("Bataysk", "Батайск", "Rostov Oblast", "Q104649", 578740),
    ("Elista", "Элиста", "Republic of Kalmykia", "Q3977", 563514),
    ("Anapa", "Анапа", "Krasnodar Krai", "Q15758", 582182),
    ("Yeysk", "Ейск", "Krasnodar Krai", "Q135616", 466885),
    ("Azov", "Азов", "Rostov Oblast", "Q102762", 580054),
    ("Yalta", "Ялта", "Republic of Crimea", "Q128499", 688533),
    ("Yevpatoriia", "Евпатория", "Republic of Crimea", "Q33345", 688105),
    ("Novoshakhtinsk", "Новошахтинск", "Rostov Oblast", "Q155809", 517963),
    # Historic
    ("Tanais", "Танаис", "Rostov Oblast", "Q1153416", 8143962),
    # =========================================================================
    # NORTH CAUCASIAN FEDERAL DISTRICT (Северо-Кавказский)
    # =========================================================================
    ("Makhachkala", "Махачкала", "Republic of Dagestan", "Q5168", 532096),
    ("Stavropol", "Ставрополь", "Stavropol Krai", "Q5206", 487846),
    ("Grozny", "Грозный", "Chechen Republic", "Q5196", 558418),
    ("Khasavyurt", "Хасавюрт", "Republic of Dagestan", "Q147756", 550478),
    ("Maykop", "Майкоп", "Republic of Adygea", "Q3752", 528293),
    ("Kaspiysk", "Каспийск", "Republic of Dagestan", "Q145507", 551847),
    ("Derbent", "Дербент", "Republic of Dagestan", "Q131416", 566532),
    ("Cherkessk", "Черкесск", "Karachay-Cherkess Republic", "Q5326", 569154),
    ("Vladikavkaz", "Владикавказ", "Republic of North Ossetia-Alania", "Q5239", 473700),
    ("Nalchik", "Нальчик", "Kabardino-Balkar Republic", "Q5265", 521118),
    ("Mineralnye Vody", "Минеральные Воды", "Stavropol Krai", "Q158936", 526480),
    ("Pyatigorsk", "Пятигорск", "Stavropol Krai", "Q41970", 503550),
    ("Kislovodsk", "Кисловодск", "Stavropol Krai", "Q153676", 548114),
    ("Nevinnomyssk", "Невинномысск", "Stavropol Krai", "Q165806", 522377),
    # =========================================================================
    # VOLGA FEDERAL DISTRICT (Приволжский)
    # =========================================================================
    ("Kazan", "Казань", "Republic of Tatarstan", "Q900", 551487),
    ("Nizhny Novgorod", "Нижний Новгород", "Nizhny Novgorod Oblast", "Q891", 520555),
    ("Samara", "Самара", "Samara Oblast", "Q894", 499099),
    ("Ufa", "Уфа", "Republic of Bashkortostan", "Q911", 479561),
    ("Perm", "Пермь", "Perm Krai", "Q915", 511196),
    ("Saratov", "Саратов", "Saratov Oblast", "Q5332", 498677),
    ("Tolyatti", "Тольятти", "Samara Oblast", "Q1341", 482283),
    ("Izhevsk", "Ижевск", "Udmurt Republic", "Q5426", 554840),
    ("Ulyanovsk", "Ульяновск", "Ulyanovsk Oblast", "Q5627", 479123),
    ("Orenburg", "Оренбург", "Orenburg Oblast", "Q5337", 515003),
    ("Naberezhnye Chelny", "Набережные Челны", "Republic of Tatarstan", "Q95041", 523750),
    ("Cheboksary", "Чебоксары", "Chuvash Republic", "Q5470", 569696),
    ("Penza", "Пенза", "Penza Oblast", "Q5540", 511565),
    ("Kirov", "Киров", "Kirov Oblast", "Q5384", 548408),
    ("Saransk", "Саранск", "Republic of Mordovia", "Q5343", 498698),
    ("Yoshkar-Ola", "Йошкар-Ола", "Mari El Republic", "Q5449", 466806),
    ("Sterlitamak", "Стерлитамак", "Republic of Bashkortostan", "Q196489", 487495),
    ("Nizhnekamsk", "Нижнекамск", "Republic of Tatarstan", "Q172657", 521118),
    ("Engels", "Энгельс", "Saratov Oblast", "Q198748", 563464),
    ("Balakovo", "Балаково", "Saratov Oblast", "Q104560", 579492),
    ("Almetyevsk", "Альметьевск", "Republic of Tatarstan", "Q103483", 582432),
    ("Orsk", "Орск", "Orenburg Oblast", "Q47166", 514734),
    ("Salavat", "Салават", "Republic of Bashkortostan", "Q193443", 499292),
    ("Novocheboksarsk", "Новочебоксарск", "Chuvash Republic", "Q175433", 518976),
    ("Oktyabrsky", "Октябрьский", "Republic of Bashkortostan", "Q176325", 515879),
    ("Dimitrovgrad", "Димитровград", "Ulyanovsk Oblast", "Q135285", 566199),
    ("Neftekamsk", "Нефтекамск", "Republic of Bashkortostan", "Q172601", 522942),
    ("Berezniki", "Березники", "Perm Krai", "Q105002", 577206),
    ("Rybinsk", "Рыбинск", "Yaroslavl Oblast", "Q193413", 500004),
    ("Novokuybyshevsk", "Новокуйбышевск", "Samara Oblast", "Q175124", 518659),
    # Historic
    ("Bolgar", "Болгар", "Republic of Tatarstan", "Q32511429", 7595800),
    ("Sviyazhsk", "Свияжск", "Republic of Tatarstan", "Q194145", 0),
    # =========================================================================
    # URALS FEDERAL DISTRICT (Уральский)
    # =========================================================================
    ("Yekaterinburg", "Екатеринбург", "Sverdlovsk Oblast", "Q887", 1486209),
    ("Chelyabinsk", "Челябинск", "Chelyabinsk Oblast", "Q906", 1508291),
    ("Tyumen", "Тюмень", "Tyumen Oblast", "Q5815", 1488754),
    ("Surgut", "Сургут", "Khanty-Mansi Autonomous Okrug", "Q183002", 1490624),
    ("Magnitogorsk", "Магнитогорск", "Chelyabinsk Oblast", "Q95449", 532288),
    ("Nizhny Tagil", "Нижний Тагил", "Sverdlovsk Oblast", "Q98967", 520494),
    ("Kurgan", "Курган", "Kurgan Oblast", "Q13379", 1501321),
    ("Nizhnevartovsk", "Нижневартовск", "Khanty-Mansi Autonomous Okrug", "Q172637", 1497543),
    ("Zlatoust", "Златоуст", "Chelyabinsk Oblast", "Q140087", 462444),
    ("Kamensk-Uralsky", "Каменск-Уральский", "Sverdlovsk Oblast", "Q105444", 1504826),
    ("Kopeysk", "Копейск", "Chelyabinsk Oblast", "Q155148", 1502603),
    ("Pervouralsk", "Первоуральск", "Sverdlovsk Oblast", "Q19157", 510808),
    ("Nefteyugansk", "Нефтеюганск", "Khanty-Mansi Autonomous Okrug", "Q172616", 1497917),
    ("Novy Urengoy", "Новый Уренгой", "Yamalo-Nenets Autonomous Okrug", "Q175470", 1496511),
    ("Noyabrsk", "Ноябрьск", "Yamalo-Nenets Autonomous Okrug", "Q175524", 1496503),
    ("Troitsk", "Троицк", "Chelyabinsk Oblast", "Q196694", 1489246),
    # Historic
    ("Tobolsk", "Тобольск", "Tyumen Oblast", "Q168782", 1489530),
    ("Verkhoturye", "Верхотурье", "Sverdlovsk Oblast", "Q133052", 1487219),
    # =========================================================================
    # SIBERIAN FEDERAL DISTRICT (Сибирский)
    # =========================================================================
    ("Novosibirsk", "Новосибирск", "Novosibirsk Oblast", "Q883", 1496747),
    ("Krasnoyarsk", "Красноярск", "Krasnoyarsk Krai", "Q919", 1502026),
    ("Omsk", "Омск", "Omsk Oblast", "Q898", 1496153),
    ("Barnaul", "Барнаул", "Altai Krai", "Q6014", 1510853),
    ("Irkutsk", "Иркутск", "Irkutsk Oblast", "Q6576", 2023469),
    ("Tomsk", "Томск", "Tomsk Oblast", "Q976", 1489425),
    ("Kemerovo", "Кемерово", "Kemerovo Oblast", "Q6066", 1503901),
    ("Abakan", "Абакан", "Republic of Khakassia", "Q875", 1512236),
    ("Biysk", "Бийск", "Altai Krai", "Q102667", 1510018),
    ("Achinsk", "Ачинск", "Krasnoyarsk Krai", "Q104232", 1512165),
    ("Rubtsovsk", "Рубцовск", "Altai Krai", "Q193380", 1493467),
    ("Berdsk", "Бердск", "Novosibirsk Oblast", "Q104991", 1510350),
    ("Seversk", "Северск", "Tomsk Oblast", "Q193909", 1538637),
    ("Anzhero-Sudzhensk", "Анжеро-Судженск", "Kemerovo Oblast", "Q103620", 1511494),
    ("Belovo", "Белово", "Kemerovo Oblast", "Q104717", 1510469),
    # Historic
    ("Kyzyl", "Кызыл", "Tuva Republic", "Q6904", 0),
    ("Gorno-Altaysk", "Горно-Алтайск", "Altai Republic", "Q7379", 1506274),
    # =========================================================================
    # FAR EASTERN FEDERAL DISTRICT (Дальневосточный)
    # =========================================================================
    ("Vladivostok", "Владивосток", "Primorsky Krai", "Q959", 2013348),
    ("Khabarovsk", "Хабаровск", "Khabarovsk Krai", "Q4454", 2022890),
    ("Yakutsk", "Якутск", "Sakha Republic", "Q6610", 2013159),
    ("Ulan-Ude", "Улан-Удэ", "Republic of Buryatia", "Q6816", 7536080),
    ("Chita", "Чита", "Zabaykalsky Krai", "Q53139", 2025339),
    ("Yuzhno-Sakhalinsk", "Южно-Сахалинск", "Sakhalin Oblast", "Q7859", 2119441),
    ("Petropavlovsk-Kamchatsky", "Петропавловск-Камчатский", "Kamchatka Krai", "Q7842", 2122104),
    ("Komsomolsk-on-Amur", "Комсомольск-на-Амуре", "Khabarovsk Krai", "Q79462", 2022041),
    ("Blagoveshchensk", "Благовещенск", "Amur Oblast", "Q79538", 2026643),
    ("Magadan", "Магадан", "Magadan Oblast", "Q7788", 2123426),
    ("Anadyr", "Анадырь", "Chukotka Autonomous Okrug", "Q7928", 2127202),
    ("Birobidzhan", "Биробиджан", "Jewish Autonomous Oblast", "Q79556", 2026573),
    # =========================================================================
    # ADDITIONAL CITIES (Golden Ring, administrative, etc.)
    # =========================================================================
    ("Yaroslavl", "Ярославль", "Yaroslavl Oblast", "Q2423", 468902),
    ("Kostroma", "Кострома", "Kostroma Oblast", "Q2592", 543878),
    ("Ivanovo", "Иваново", "Ivanovo Oblast", "Q2630", 555312),
    ("Armavir", "Армавир", "Krasnodar Krai", "Q15767", 580922),
    ("Kamyshin", "Камышин", "Volgograd Oblast", "Q144170", 553287),
    ("Murino", "Мурино", "Leningrad Oblast", "Q1978797", 524311),
]

# ---------------------------------------------------------------------------
# Federal district mapping by region
# ---------------------------------------------------------------------------
FEDERAL_DISTRICT: dict[str, str] = {
    "Moscow": "Central",
    "Moscow Oblast": "Central",
    "Voronezh Oblast": "Central",
    "Tula Oblast": "Central",
    "Kursk Oblast": "Central",
    "Bryansk Oblast": "Central",
    "Vladimir Oblast": "Central",
    "Kaluga Oblast": "Central",
    "Belgorod Oblast": "Central",
    "Smolensk Oblast": "Central",
    "Tver Oblast": "Central",
    "Ryazan Oblast": "Central",
    "Tambov Oblast": "Central",
    "Yaroslavl Oblast": "Central",
    "Kostroma Oblast": "Central",
    "Ivanovo Oblast": "Central",
    "Saint Petersburg": "Northwestern",
    "Leningrad Oblast": "Northwestern",
    "Kaliningrad Oblast": "Northwestern",
    "Novgorod Oblast": "Northwestern",
    "Pskov Oblast": "Northwestern",
    "Republic of Karelia": "Northwestern",
    "Komi Republic": "Northwestern",
    "Murmansk Oblast": "Northwestern",
    "Arkhangelsk Oblast": "Northwestern",
    "Vologda Oblast": "Northwestern",
    "Rostov Oblast": "Southern",
    "Krasnodar Krai": "Southern",
    "Volgograd Oblast": "Southern",
    "Astrakhan Oblast": "Southern",
    "Republic of Crimea": "Southern",
    "Sevastopol": "Southern",
    "Republic of Kalmykia": "Southern",
    "Republic of Dagestan": "North Caucasian",
    "Chechen Republic": "North Caucasian",
    "Stavropol Krai": "North Caucasian",
    "Republic of Adygea": "North Caucasian",
    "Karachay-Cherkess Republic": "North Caucasian",
    "Republic of North Ossetia-Alania": "North Caucasian",
    "Kabardino-Balkar Republic": "North Caucasian",
    "Republic of Tatarstan": "Volga",
    "Republic of Bashkortostan": "Volga",
    "Nizhny Novgorod Oblast": "Volga",
    "Samara Oblast": "Volga",
    "Perm Krai": "Volga",
    "Saratov Oblast": "Volga",
    "Orenburg Oblast": "Volga",
    "Ulyanovsk Oblast": "Volga",
    "Penza Oblast": "Volga",
    "Kirov Oblast": "Volga",
    "Republic of Mordovia": "Volga",
    "Chuvash Republic": "Volga",
    "Udmurt Republic": "Volga",
    "Mari El Republic": "Volga",
    "Sverdlovsk Oblast": "Urals",
    "Chelyabinsk Oblast": "Urals",
    "Tyumen Oblast": "Urals",
    "Kurgan Oblast": "Urals",
    "Khanty-Mansi Autonomous Okrug": "Urals",
    "Yamalo-Nenets Autonomous Okrug": "Urals",
    "Novosibirsk Oblast": "Siberian",
    "Krasnoyarsk Krai": "Siberian",
    "Omsk Oblast": "Siberian",
    "Altai Krai": "Siberian",
    "Irkutsk Oblast": "Siberian",
    "Tomsk Oblast": "Siberian",
    "Kemerovo Oblast": "Siberian",
    "Republic of Khakassia": "Siberian",
    "Tuva Republic": "Siberian",
    "Altai Republic": "Siberian",
    "Primorsky Krai": "Far Eastern",
    "Khabarovsk Krai": "Far Eastern",
    "Sakha Republic": "Far Eastern",
    "Republic of Buryatia": "Far Eastern",
    "Zabaykalsky Krai": "Far Eastern",
    "Sakhalin Oblast": "Far Eastern",
    "Kamchatka Krai": "Far Eastern",
    "Amur Oblast": "Far Eastern",
    "Magadan Oblast": "Far Eastern",
    "Chukotka Autonomous Okrug": "Far Eastern",
    "Jewish Autonomous Oblast": "Far Eastern",
}

# ---------------------------------------------------------------------------
# Alternative names in regional and historical languages
# ---------------------------------------------------------------------------
ALTERNATIVE_NAMES: dict[str, dict[str, list[str]]] = {
    "Moscow": {
        "rus": ["Москва"],
        "deu": ["Moskau"],
        "fin": ["Moskova"],
        "lat": ["Moscovia", "Mosqua"],
        "orv": ["Москъва", "Москов"],
        "tat": ["Мәскәү"],
    },
    "Saint Petersburg": {
        "rus": ["Санкт-Петербург", "Петроград", "Ленинград"],
        "deu": ["Sankt Petersburg", "Petrograd", "Leningrad"],
        "fin": ["Pietari"],
        "lat": ["Petropolis", "Sanctopolis"],
        "swe": ["Sankt Petersburg"],
    },
    "Novosibirsk": {
        "rus": ["Новосибирск"],
        "deu": ["Nowosibirsk"],
        "lat": ["Novossibiria"],
    },
    "Yekaterinburg": {
        "rus": ["Екатеринбург", "Свердловск"],
        "deu": ["Jekaterinburg", "Swerdlowsk"],
        "lat": ["Catharinoburgia"],
    },
    "Kazan": {
        "rus": ["Казань"],
        "tat": ["Казан"],
        "deu": ["Kasan"],
        "lat": ["Casanum"],
        "orv": ["Казанъ"],
    },
    "Nizhny Novgorod": {
        "rus": ["Нижний Новгород", "Горький"],
        "deu": ["Nischni Nowgorod", "Gorki"],
        "lat": ["Novogardia Inferior"],
        "orv": ["Нижьній Новъгородъ"],
    },
    "Chelyabinsk": {
        "rus": ["Челябинск"],
        "deu": ["Tscheljabinsk"],
        "bak": ["Силәбе"],
        "tat": ["Чиләбе"],
    },
    "Krasnodar": {
        "rus": ["Краснодар", "Екатеринодар"],
        "deu": ["Krasnodar", "Jekaterinodar"],
    },
    "Samara": {
        "rus": ["Самара", "Куйбышев"],
        "deu": ["Samara", "Kuibyschew"],
        "tat": ["Самар"],
    },
    "Ufa": {
        "rus": ["Уфа"],
        "bak": ["Өфө"],
        "tat": ["Өфе"],
        "deu": ["Ufa"],
        "lat": ["Upha"],
    },
    "Rostov-on-Don": {
        "rus": ["Ростов-на-Дону"],
        "deu": ["Rostow am Don"],
        "lat": ["Rostovium ad Tanaim"],
    },
    "Omsk": {
        "rus": ["Омск"],
        "deu": ["Omsk"],
        "tat": ["Омби"],
    },
    "Krasnoyarsk": {
        "rus": ["Красноярск"],
        "deu": ["Krasnojarsk"],
    },
    "Voronezh": {
        "rus": ["Воронеж"],
        "deu": ["Woronesch"],
        "lat": ["Voronexia"],
    },
    "Perm": {
        "rus": ["Пермь", "Молотов"],
        "deu": ["Perm", "Molotow"],
        "lat": ["Permia"],
        "kpv": ["Перым"],
    },
    "Volgograd": {
        "rus": ["Волгоград", "Сталинград", "Царицын"],
        "deu": ["Wolgograd", "Stalingrad", "Zarizyn"],
        "lat": ["Tsaritsyna"],
    },
    "Tyumen": {
        "rus": ["Тюмень"],
        "deu": ["Tjumen"],
        "tat": ["Төмән"],
    },
    "Saratov": {
        "rus": ["Саратов"],
        "deu": ["Saratow"],
        "tat": ["Сарытау"],
    },
    "Tolyatti": {
        "rus": ["Тольятти", "Ставрополь-на-Волге"],
        "deu": ["Toljatti"],
    },
    "Makhachkala": {
        "rus": ["Махачкала", "Порт-Петровск"],
        "deu": ["Machatschkala"],
    },
    "Barnaul": {
        "rus": ["Барнаул"],
        "deu": ["Barnaul"],
    },
    "Izhevsk": {
        "rus": ["Ижевск", "Устинов"],
        "udm": ["Ижкар"],
        "deu": ["Ischewsk"],
    },
    "Khabarovsk": {
        "rus": ["Хабаровск"],
        "deu": ["Chabarowsk"],
    },
    "Ulyanovsk": {
        "rus": ["Ульяновск", "Симбирск"],
        "deu": ["Uljanowsk", "Simbirsk"],
        "tat": ["Үлянауыск", "Сембер"],
    },
    "Irkutsk": {
        "rus": ["Иркутск"],
        "deu": ["Irkutsk"],
        "bua": ["Эрхүү"],
    },
    "Vladivostok": {
        "rus": ["Владивосток"],
        "deu": ["Wladiwostok"],
        "lat": ["Vladivostokium"],
    },
    "Yaroslavl": {
        "rus": ["Ярославль"],
        "deu": ["Jaroslawl"],
        "lat": ["Iaroslavia"],
        "orv": ["Ярославль"],
    },
    "Naberezhnye Chelny": {
        "rus": ["Набережные Челны", "Брежнев"],
        "tat": ["Яр Чаллы"],
    },
    "Tomsk": {
        "rus": ["Томск"],
        "deu": ["Tomsk"],
    },
    "Kemerovo": {
        "rus": ["Кемерово"],
        "deu": ["Kemerowo"],
    },
    "Orenburg": {
        "rus": ["Оренбург", "Чкалов"],
        "deu": ["Orenburg", "Tschkalow"],
        "tat": ["Оренбург"],
        "bak": ["Оренбур"],
    },
    "Ryazan": {
        "rus": ["Рязань"],
        "deu": ["Rjasan"],
        "lat": ["Riesania"],
        "orv": ["Рѧзань"],
    },
    "Cheboksary": {
        "rus": ["Чебоксары"],
        "chv": ["Шупашкар"],
        "deu": ["Tscheboksary"],
    },
    "Kaliningrad": {
        "rus": ["Калининград", "Кёнигсберг"],
        "deu": ["Königsberg", "Kaliningrad"],
        "lat": ["Regiomontum", "Königsberga"],
        "fin": ["Kuninkaanmäki"],
    },
    "Penza": {
        "rus": ["Пенза"],
        "deu": ["Pensa"],
    },
    "Sevastopol": {
        "rus": ["Севастополь"],
        "deu": ["Sewastopol"],
        "lat": ["Sebastopolis"],
    },
    "Kirov": {
        "rus": ["Киров", "Вятка", "Хлынов"],
        "deu": ["Kirow", "Wjatka"],
        "lat": ["Viatca"],
        "orv": ["Хлыновъ"],
    },
    "Tula": {
        "rus": ["Тула"],
        "deu": ["Tula"],
        "lat": ["Tula"],
    },
    "Astrakhan": {
        "rus": ["Астрахань"],
        "deu": ["Astrachan"],
        "lat": ["Astrachanium"],
        "tat": ["Әстерхан"],
    },
    "Stavropol": {
        "rus": ["Ставрополь"],
        "deu": ["Stawropol"],
        "lat": ["Stavropolis"],
    },
    "Ulan-Ude": {
        "rus": ["Улан-Удэ", "Верхнеудинск"],
        "bua": ["Улаан-Үдэ"],
        "deu": ["Ulan-Ude", "Werchne-Udinsk"],
    },
    "Kursk": {
        "rus": ["Курск"],
        "deu": ["Kursk"],
        "orv": ["Курьскъ"],
    },
    "Surgut": {
        "rus": ["Сургут"],
        "deu": ["Surgut"],
    },
    "Tver": {
        "rus": ["Тверь", "Калинин"],
        "deu": ["Twer", "Kalinin"],
        "lat": ["Tveria"],
        "orv": ["Тьфѣрь"],
    },
    "Magnitogorsk": {
        "rus": ["Магнитогорск"],
        "deu": ["Magnitogorsk"],
    },
    "Bryansk": {
        "rus": ["Брянск"],
        "deu": ["Brjansk"],
        "orv": ["Дебрянскъ"],
    },
    "Vladimir": {
        "rus": ["Владимир"],
        "deu": ["Wladimir"],
        "lat": ["Vladimeria"],
        "orv": ["Володимиръ"],
    },
    "Chita": {
        "rus": ["Чита"],
        "bua": ["Шэтэ"],
        "deu": ["Tschita"],
    },
    "Simferopol": {
        "rus": ["Симферополь"],
        "deu": ["Simferopol"],
        "lat": ["Simferopolim"],
    },
    "Kaluga": {
        "rus": ["Калуга"],
        "deu": ["Kaluga"],
    },
    "Nizhny Tagil": {
        "rus": ["Нижний Тагил"],
        "deu": ["Nischni Tagil"],
    },
    "Belgorod": {
        "rus": ["Белгород"],
        "deu": ["Belgorod"],
        "orv": ["Бѣлъгородъ"],
    },
    "Yakutsk": {
        "rus": ["Якутск"],
        "sah": ["Дьокуускай"],
        "deu": ["Jakutsk"],
    },
    "Saransk": {
        "rus": ["Саранск"],
        "deu": ["Saransk"],
    },
    "Smolensk": {
        "rus": ["Смоленск"],
        "deu": ["Smolensk"],
        "lat": ["Smolencia"],
        "orv": ["Смольньскъ"],
    },
    "Kurgan": {
        "rus": ["Курган"],
        "deu": ["Kurgan"],
    },
    "Grozny": {
        "rus": ["Грозный"],
        "che": ["Соьлжа-ГӀала"],
        "deu": ["Grosny"],
    },
    "Yoshkar-Ola": {
        "rus": ["Йошкар-Ола", "Царевококшайск"],
        "chm": ["Йошкар-Ола"],
        "deu": ["Joschkar-Ola"],
    },
    "Petrozavodsk": {
        "rus": ["Петрозаводск"],
        "fin": ["Petroskoi"],
        "deu": ["Petrosawodsk"],
        "lat": ["Petropolis"],
    },
    "Veliky Novgorod": {
        "rus": ["Великий Новгород", "Новгород"],
        "deu": ["Nowgorod"],
        "lat": ["Novogardia Magna"],
        "fin": ["Novgorod"],
        "orv": ["Новъгородъ"],
    },
    "Pskov": {
        "rus": ["Псков"],
        "deu": ["Pskow", "Pleskau"],
        "lat": ["Plescovia"],
        "fin": ["Pihkova"],
        "orv": ["Пльсковъ"],
    },
    "Vladikavkaz": {
        "rus": ["Владикавказ", "Орджоникидзе", "Дзауджикау"],
        "deu": ["Wladikawkas"],
    },
    "Nalchik": {
        "rus": ["Нальчик"],
        "deu": ["Naltschik"],
    },
    "Murmansk": {
        "rus": ["Мурманск", "Романов-на-Мурмане"],
        "deu": ["Murmansk"],
        "fin": ["Murmanski"],
        "lat": ["Murmancia"],
    },
    "Arkhangelsk": {
        "rus": ["Архангельск"],
        "deu": ["Archangelsk"],
        "lat": ["Archangelia"],
        "fin": ["Arkangeli"],
    },
    "Vologda": {
        "rus": ["Вологда"],
        "deu": ["Wologda"],
        "orv": ["Вологда"],
    },
    "Vyborg": {
        "rus": ["Выборг"],
        "fin": ["Viipuri"],
        "swe": ["Viborg"],
        "deu": ["Wiborg"],
        "lat": ["Viburgum"],
    },
    "Kostroma": {
        "rus": ["Кострома"],
        "deu": ["Kostroma"],
        "lat": ["Costroma"],
        "orv": ["Кострома"],
    },
    "Ivanovo": {
        "rus": ["Иваново", "Иваново-Вознесенск"],
        "deu": ["Iwanowo"],
    },
    "Suzdal": {
        "rus": ["Суздаль"],
        "deu": ["Susdal"],
        "lat": ["Susdalia"],
        "orv": ["Суждаль"],
    },
    "Rostov Veliky": {
        "rus": ["Ростов Великий", "Ростов"],
        "deu": ["Rostow der Große"],
        "lat": ["Rostovia Magna"],
        "orv": ["Ростовъ"],
    },
    "Pereslavl-Zalessky": {
        "rus": ["Переславль-Залесский"],
        "deu": ["Pereslawl-Salesski"],
    },
    "Derbent": {
        "rus": ["Дербент"],
        "deu": ["Derbent"],
        "lat": ["Derbentum"],
    },
    "Tobolsk": {
        "rus": ["Тобольск"],
        "deu": ["Tobolsk"],
        "lat": ["Tobolscium"],
        "tat": ["Тубыл"],
    },
    "Staraya Russa": {
        "rus": ["Старая Русса"],
        "deu": ["Staraja Russa"],
        "orv": ["Руса"],
    },
    "Velikiy Ustyug": {
        "rus": ["Великий Устюг"],
        "deu": ["Weliki Ustjug"],
    },
    "Kyzyl": {
        "rus": ["Кызыл"],
        "deu": ["Kysyl"],
    },
    "Gorno-Altaysk": {
        "rus": ["Горно-Алтайск"],
        "deu": ["Gorno-Altaisk"],
    },
    "Syktyvkar": {
        "rus": ["Сыктывкар", "Усть-Сысольск"],
        "kpv": ["Сыктывкар"],
        "deu": ["Syktywkar"],
    },
    "Elista": {
        "rus": ["Элиста"],
        "deu": ["Elista"],
    },
    "Maykop": {
        "rus": ["Майкоп"],
        "deu": ["Maikop"],
    },
    "Cherkessk": {
        "rus": ["Черкесск"],
        "deu": ["Tscherkessk"],
    },
    "Petropavlovsk-Kamchatsky": {
        "rus": ["Петропавловск-Камчатский"],
        "deu": ["Petropawlowsk-Kamtschatski"],
    },
    "Komsomolsk-on-Amur": {
        "rus": ["Комсомольск-на-Амуре"],
        "deu": ["Komsomolsk am Amur"],
    },
    "Blagoveshchensk": {
        "rus": ["Благовещенск"],
        "deu": ["Blagoweschtschensk"],
    },
    "Magadan": {
        "rus": ["Магадан"],
        "deu": ["Magadan"],
    },
    "Anadyr": {
        "rus": ["Анадырь"],
        "deu": ["Anadyr"],
    },
    "Birobidzhan": {
        "rus": ["Биробиджан"],
        "deu": ["Birobidschan"],
    },
    "Yuzhno-Sakhalinsk": {
        "rus": ["Южно-Сахалинск", "Тоёхара"],
        "deu": ["Juschno-Sachalinsk"],
    },
    "Pyatigorsk": {
        "rus": ["Пятигорск"],
        "deu": ["Pjatigorsk"],
        "lat": ["Pyatigorskium"],
    },
    "Kislovodsk": {
        "rus": ["Кисловодск"],
        "deu": ["Kislowodsk"],
    },
    "Mineralnye Vody": {
        "rus": ["Минеральные Воды"],
        "deu": ["Mineralnyje Wody"],
    },
    "Gatchina": {
        "rus": ["Гатчина", "Красногвардейск", "Троцк"],
        "fin": ["Hatsina"],
        "deu": ["Gatschina"],
    },
    "Taganrog": {
        "rus": ["Таганрог"],
        "deu": ["Taganrog"],
        "lat": ["Taganrogium"],
    },
    "Kerch": {
        "rus": ["Керчь"],
        "deu": ["Kertsch"],
        "lat": ["Panticapaeum"],
    },
    "Yalta": {
        "rus": ["Ялта"],
        "deu": ["Jalta"],
        "lat": ["Jalta"],
    },
    "Yevpatoriia": {
        "rus": ["Евпатория"],
        "deu": ["Jewpatorija"],
        "lat": ["Eupatoria"],
    },
    "Tikhvin": {
        "rus": ["Тихвин"],
        "fin": ["Tihvinä"],
    },
    "Bolgar": {
        "rus": ["Болгар", "Булгар"],
        "tat": ["Болгар"],
        "lat": ["Bulgarium"],
    },
    "Sterlitamak": {
        "rus": ["Стерлитамак"],
        "bak": ["Стәрлетамаҡ"],
        "tat": ["Стәрлетамак"],
    },
    "Novorossiysk": {
        "rus": ["Новороссийск"],
        "deu": ["Noworossijsk"],
    },
    "Obninsk": {
        "rus": ["Обнинск"],
    },
    "Verkhoturye": {
        "rus": ["Верхотурье"],
        "deu": ["Werchoturje"],
    },
    "Anapa": {
        "rus": ["Анапа"],
        "lat": ["Gorgippia"],
    },
    "Azov": {
        "rus": ["Азов"],
        "deu": ["Asow"],
        "lat": ["Tana", "Azovium"],
    },
    "Tanais": {
        "rus": ["Танаис"],
        "lat": ["Tanais"],
    },
    "Sviyazhsk": {
        "rus": ["Свияжск"],
        "tat": ["Зөя"],
    },
    "Armavir": {
        "rus": ["Армавир"],
        "deu": ["Armawir"],
    },
}

# ---------------------------------------------------------------------------
# Place type classification
# ---------------------------------------------------------------------------
CAPITAL = "P.PPLC"
FEDERAL_DISTRICT_CAPITAL = "P.PPLA"
REGIONAL_CAPITAL = "P.PPLA2"
CITY = "P.PPL"

FEDERAL_DISTRICT_CAPITALS = {
    "Moscow",  # Central
    "Saint Petersburg",  # Northwestern
    "Rostov-on-Don",  # Southern
    "Pyatigorsk",  # North Caucasian
    "Nizhny Novgorod",  # Volga
    "Yekaterinburg",  # Urals
    "Novosibirsk",  # Siberian
    "Khabarovsk",  # Far Eastern
}

REGIONAL_CAPITALS = {
    "Kazan",
    "Chelyabinsk",
    "Krasnodar",
    "Samara",
    "Ufa",
    "Perm",
    "Volgograd",
    "Saratov",
    "Voronezh",
    "Krasnoyarsk",
    "Omsk",
    "Barnaul",
    "Irkutsk",
    "Vladivostok",
    "Yaroslavl",
    "Tyumen",
    "Tomsk",
    "Kemerovo",
    "Orenburg",
    "Ryazan",
    "Tula",
    "Kursk",
    "Bryansk",
    "Vladimir",
    "Kaluga",
    "Belgorod",
    "Smolensk",
    "Tver",
    "Tambov",
    "Astrakhan",
    "Izhevsk",
    "Ulyanovsk",
    "Cheboksary",
    "Penza",
    "Kirov",
    "Saransk",
    "Kaliningrad",
    "Veliky Novgorod",
    "Pskov",
    "Petrozavodsk",
    "Syktyvkar",
    "Murmansk",
    "Arkhangelsk",
    "Vologda",
    "Makhachkala",
    "Grozny",
    "Stavropol",
    "Vladikavkaz",
    "Nalchik",
    "Maykop",
    "Cherkessk",
    "Kurgan",
    "Abakan",
    "Yakutsk",
    "Ulan-Ude",
    "Chita",
    "Yuzhno-Sakhalinsk",
    "Petropavlovsk-Kamchatsky",
    "Blagoveshchensk",
    "Magadan",
    "Anadyr",
    "Birobidzhan",
    "Kyzyl",
    "Gorno-Altaysk",
    "Elista",
    "Simferopol",
    "Sevastopol",
    "Kostroma",
    "Ivanovo",
    "Yoshkar-Ola",
}


def get_place_type(city_name: str) -> str:
    """Determine GeoNames feature code for a Russian city."""
    if city_name == "Moscow":
        return CAPITAL
    if city_name in FEDERAL_DISTRICT_CAPITALS:
        return FEDERAL_DISTRICT_CAPITAL
    if city_name in REGIONAL_CAPITALS:
        return REGIONAL_CAPITAL
    return CITY


# ---------------------------------------------------------------------------
# Wikidata SPARQL query
# ---------------------------------------------------------------------------
def query_wikidata(qids: list[str]) -> dict[str, dict]:
    """Query Wikidata for city data using VALUES-based lookup."""
    print("Querying Wikidata SPARQL for Russian cities...")

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
            bd:serviceParam wikibase:language "en,ru"
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
def fetch_nominatim_geometry(city_name: str, country: str = "Russia") -> dict | None:
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
    """Ingest all Russian cities with comprehensive metadata."""
    seen_qids: set[str] = set()
    unique_cities = []
    for city_tuple in RUSSIAN_CITIES:
        qid = city_tuple[3]
        if qid not in seen_qids:
            seen_qids.add(qid)
            unique_cities.append(city_tuple)

    print(f"Ingesting {len(unique_cities)} Russian cities and towns")
    print(f"Output: {OUTPUT_FILE}")
    print()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_qids = [t[3] for t in unique_cities]
    wikidata_lookup = query_wikidata(all_qids)
    print()

    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}

    for i, (city, _ru, _region, _qid, _gn) in enumerate(unique_cities):
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

    for city, russian_name, region, qid, geonames_id in unique_cities:
        wd = wikidata_lookup.get(qid, {})

        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{city}' ({qid}), skipping")
            continue

        source_id = f"wikidata:{qid}"
        source_url = f"https://www.wikidata.org/wiki/{qid}"

        alt_names = ALTERNATIVE_NAMES.get(city, {})
        if not alt_names.get("rus"):
            alt_names["rus"] = [russian_name]
        elif russian_name not in alt_names["rus"]:
            alt_names["rus"].insert(0, russian_name)

        geometry = geometries.get(city)
        population = wd.get("population")
        area_km2 = wd.get("area_km2")
        elevation = wd.get("elevation")
        gn_id = wd.get("geonames_id") or geonames_id
        fed_district = FEDERAL_DISTRICT.get(region, "")
        place_type = get_place_type(city)

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
            federal_district=fed_district,
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

    print("\nBreakdown by federal district:")
    fd_counts: dict[str, int] = {}
    for r in signed_records:
        fd = r.get("municipality", "Unknown")
        fd_counts[fd] = fd_counts.get(fd, 0) + 1
    for fd, count in sorted(fd_counts.items(), key=lambda x: -x[1]):
        print(f"  {fd}: {count}")

    print("\nBreakdown by region:")
    for reg, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {reg}: {count}")


if __name__ == "__main__":
    main()
