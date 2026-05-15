#!/usr/bin/env python3
"""Ingest settlements from the Faroe Islands, Shetland, and the Hebrides.

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, area, elevation,
  alternative names in multiple language layers
- OpenStreetMap Nominatim: GeoJSON geometry (settlement boundaries/polygons)

Regions covered:
  Faroe Islands (FO): Autonomous territory of Denmark, 18 islands, ~54,000 pop.
    Language layers: Faroese (fao), Danish (dan), Old Norse (non), Latin (lat)
  Shetland (GB-SCT): Scottish archipelago, ~23,000 pop. Northernmost UK.
    Language layers: Scots (sco), Norn/Old Norse (non), Scottish Gaelic (gla)
  Hebrides (GB-SCT): Inner & Outer Hebrides, western Scotland.
    Language layers: Scottish Gaelic (gla), Old Norse (non), Scots (sco)

Linguistic heritage:
  - Faroese derives from Old West Norse, closely related to Icelandic
  - Shetland Norn (extinct Norse language) replaced by Scots; place-names
    are overwhelmingly Norse in origin (vík, ból, staðr, dalr, nes, fjörðr)
  - Hebrides: Gaelic-dominant with heavy Norse overlay from Viking settlement
    (9th-13th century). Many names show Norse-Gaelic hybridization.

References:
- https://en.wikipedia.org/wiki/List_of_cities_and_towns_in_the_Faroe_Islands
- https://en.wikipedia.org/wiki/Shetland#Settlements
- https://en.wikipedia.org/wiki/Outer_Hebrides
- https://en.wikipedia.org/wiki/Inner_Hebrides
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
OUTPUT_FO = DATABANK_DIR / "places" / "FO" / "wikidata.jsonl"
OUTPUT_GB = DATABANK_DIR / "places" / "GB" / "wikidata.jsonl"

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
    country_code: str,
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
    island: str | None = None,
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
        "country_code": country_code,
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
    if island:
        record["island"] = island
    if municipality:
        record["municipality"] = municipality
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ===========================================================================
# FAROE ISLANDS SETTLEMENTS
# Tuple: (Faroese name, island, municipality, wikidata_qid, geonames_id)
# ===========================================================================
FAROE_SETTLEMENTS: list[tuple[str, str, str, str, int]] = [
    # --- Streymoy ---
    ("Tórshavn", "Streymoy", "Tórshavn", "Q10704", 2611396),
    ("Hoyvík", "Streymoy", "Tórshavn", "Q677723", 2619693),
    ("Argir", "Streymoy", "Tórshavn", "Q647534", 2624653),
    ("Vestmanna", "Streymoy", "Kvívík", "Q608352", 2610343),
    ("Kollafjørður", "Streymoy", "Tórshavn", "Q266643", 2618511),
    ("Kvívík", "Streymoy", "Kvívík", "Q933130", 2618085),
    ("Hósvík", "Streymoy", "Tórshavn", "Q740111", 2619744),
    ("Streymnes", "Streymoy", "Tórshavn", "Q610017", 2612230),
    ("Hvalvík", "Streymoy", "Kvívík", "Q585244", 2619580),
    ("Kaldbak", "Streymoy", "Tórshavn", "Q1025151", 2619192),
    ("Velbastaður", "Streymoy", "Tórshavn", "Q1194901", 2610565),
    ("Hvítanes", "Streymoy", "Tórshavn", "Q603859", 2619504),
    ("Leynar", "Streymoy", "Kvívík", "Q587264", 2617771),
    ("Haldarsvík", "Streymoy", "Tórshavn", "Q1032883", 2620913),
    ("Kirkjubøur", "Streymoy", "Tórshavn", "Q578732", 2618846),
    ("Tjørnuvík", "Streymoy", "Tórshavn", "Q1093578", 2611614),
    ("Saksun", "Streymoy", "Tórshavn", "Q928875", 2614323),
    ("Norðradalur", "Streymoy", "Tórshavn", "Q978702", 2616143),
    ("Kaldbaksbotnur", "Streymoy", "Tórshavn", "Q925121", 0),
    # --- Eysturoy ---
    ("Fuglafjørður", "Eysturoy", "Fuglafjørður", "Q731990", 2621808),
    ("Saltangará", "Eysturoy", "Runavík", "Q1025146", 2614304),
    ("Leirvík", "Eysturoy", "Eystur", "Q840634", 2617844),
    ("Strendur", "Eysturoy", "Runavík", "Q1025132", 2612233),
    ("Toftir", "Eysturoy", "Nes", "Q840631", 2611567),
    ("Skála", "Eysturoy", "Eystur", "Q1025359", 2613915),
    ("Eiði", "Eysturoy", "Eiði", "Q691775", 2622676),
    ("Norðragøta", "Eysturoy", "Eystur", "Q676532", 2616142),
    ("Runavík", "Eysturoy", "Runavík", "Q754664", 2614402),
    ("Syðrugøta", "Eysturoy", "Eystur", "Q1025144", 2611962),
    ("Glyvrar", "Eysturoy", "Runavík", "Q1011161", 2621340),
    ("Søldarfjørður", "Eysturoy", "Runavík", "Q1094343", 2613140),
    ("Nes", "Eysturoy", "Nes", "Q1079297", 2616498),
    ("Norðskáli", "Eysturoy", "Eystur", "Q1094638", 2616140),
    ("Rituvík", "Eysturoy", "Runavík", "Q1194895", 2614699),
    ("Oyri", "Eysturoy", "Runavík", "Q977969", 2615253),
    ("Oyrarbakki", "Eysturoy", "Runavík", "Q1093197", 2615259),
    ("Saltnes", "Eysturoy", "Runavík", "Q1062942", 2614295),
    ("Skálabotnur", "Eysturoy", "Eystur", "Q1079334", 2613929),
    ("Oyndarfjørður", "Eysturoy", "Eystur", "Q730352", 2615261),
    ("Funningur", "Eysturoy", "Eystur", "Q585236", 2621765),
    ("Funningsfjørður", "Eysturoy", "Eystur", "Q542954", 2621767),
    ("Gjógv", "Eysturoy", "Eystur", "Q939708", 2621415),
    ("Elduvík", "Eysturoy", "Eystur", "Q222955", 2622625),
    ("Skipanes", "Eysturoy", "Eystur", "Q1079313", 2613735),
    ("Gøtugjógv", "Eysturoy", "Eystur", "Q1031808", 2621294),
    ("Gøtueiði", "Eysturoy", "Eystur", "Q1078870", 2621296),
    ("Lambareiði", "Eysturoy", "Eystur", "Q968666", 2618011),
    ("Selatrað", "Eysturoy", "Eystur", "Q1063000", 2614098),
    ("Oyrareingir", "Eysturoy", "Eystur", "Q1062967", 2615258),
    # --- Vágar ---
    ("Sørvágur", "Vágar", "Sørvágur", "Q906365", 2612890),
    ("Miðvágur", "Vágar", "Vágar", "Q855785", 2616914),
    ("Sandavágur", "Vágar", "Vágar", "Q845272", 2614265),
    ("Bøur", "Vágar", "Sørvágur", "Q855276", 2623713),
    ("Gásadalur", "Vágar", "Sørvágur", "Q226056", 2621596),
    # --- Borðoy ---
    ("Klaksvík", "Borðoy", "Klaksvík", "Q189361", 2618795),
    ("Norðoyri", "Borðoy", "Klaksvík", "Q255015", 2616144),
    ("Árnafjørður", "Borðoy", "Klaksvík", "Q252240", 2624633),
    ("Ánirnar", "Borðoy", "Klaksvík", "Q252128", 2624689),
    # --- Viðoy ---
    ("Viðareiði", "Viðoy", "Viðoy", "Q901774", 2610302),
    ("Hvannasund", "Viðoy", "Viðoy", "Q933117", 2619568),
    # --- Kunoy ---
    ("Kunoy", "Kunoy", "Kunoy", "Q1093548", 0),
    ("Haraldssund", "Kunoy", "Kunoy", "Q1025148", 2620774),
    # --- Svínoy ---
    ("Svínoy", "Svínoy", "Svínoy", "Q1416487", 0),
    # --- Sandoy ---
    ("Sandur", "Sandoy", "Sandoy", "Q842901", 2614212),
    ("Skopun", "Sandoy", "Sandoy", "Q944256", 2613660),
    ("Dalur", "Sandoy", "Sandoy", "Q519723", 2623092),
    ("Skálavík", "Sandoy", "Sandoy", "Q1093560", 2613921),
    ("Húsavík", "Sandoy", "Sandoy", "Q1025376", 2619612),
    # --- Suðuroy ---
    ("Vágur", "Suðuroy", "Vágur", "Q754670", 2610806),
    ("Tvøroyri", "Suðuroy", "Tvøroyri", "Q754666", 2611060),
    ("Trongisvágur", "Suðuroy", "Tvøroyri", "Q247637", 2611209),
    ("Hvalba", "Suðuroy", "Hvalba", "Q666627", 2619592),
    ("Sumba", "Suðuroy", "Sumba", "Q901784", 2612128),
    ("Porkeri", "Suðuroy", "Hvalba", "Q943723", 2615132),
    ("Froðba", "Suðuroy", "Tvøroyri", "Q301686", 2621852),
    ("Fámjin", "Suðuroy", "Fámjin", "Q932433", 2622348),
    ("Lopra", "Suðuroy", "Sumba", "Q369892", 2617406),
    ("Øravík", "Suðuroy", "Tvøroyri", "Q285039", 2615720),
    ("Hov", "Suðuroy", "Hov", "Q1025136", 2619734),
    # --- Nólsoy ---
    ("Nólsoy", "Nólsoy", "Tórshavn", "Q946470", 2616437),
    # --- Hestur ---
    ("Hestur", "Hestur", "Hestur", "Q1035832", 0),
    # --- Koltur ---
    ("Koltur", "Koltur", "Koltur", "Q746837", 0),
    # --- Skúvoy ---
    ("Skúvoy", "Skúvoy", "Skúvoy", "Q6274717", 0),
    # --- Mykines ---
    ("Mykines", "Mykines", "Sørvágur", "Q1180285", 0),
]

# ===========================================================================
# SHETLAND SETTLEMENTS
# ===========================================================================
SHETLAND_SETTLEMENTS: list[tuple[str, str, str, int]] = [
    ("Lerwick", "Mainland", "Q213485", 2644605),
    ("Scalloway", "Mainland", "Q1014090", 2638439),
    ("Brae", "Mainland", "Q1010066", 2654970),
    ("Symbister", "Whalsay", "Q1293028", 8426371),
    ("Baltasound", "Unst", "Q805562", 2656431),
    ("Walls", "Mainland", "Q2816645", 2634865),
    ("Sandwick", "Mainland", "Q7417104", 2638534),
    ("Aith", "Mainland", "Q4699305", 2657586),
    ("Hillswick", "Mainland", "Q5764039", 2646885),
    ("Hamnavoe", "Mainland", "Q689132", 12261628),
    ("Voe", "Mainland", "Q18162982", 2634946),
    ("Mossbank", "Mainland", "Q6916633", 2642147),
    ("Vidlin", "Mainland", "Q7928111", 13276916),
    ("Cunningsburgh", "Mainland", "Q2816653", 13283226),
    ("Sandness", "Mainland", "Q7416433", 2638571),
    ("Ollaberry", "Mainland", "Q7088252", 2640979),
    ("North Roe", "Mainland", "Q7056554", 2641273),
    ("Boddam", "Mainland", "Q4936401", 2655287),
    ("Bigton", "Mainland", "Q4907032", 11240127),
    ("Bixter", "Mainland", "Q4919307", 13276912),
    ("Whiteness", "Mainland", "Q7996182", 12264827),
    ("Weisdale", "Mainland", "Q7980375", 11256862),
    ("Tingwall", "Mainland", "Q2435784", 2635795),
    ("Gulberwick", "Mainland", "Q5617285", 11072618),
    ("Quarff", "Mainland", "Q7269149", 2639807),
    ("Hoswick", "Mainland", "Q5909542", 11240129),
    ("Sumburgh", "Mainland", "Q7637052", 2636544),
    ("Mid Yell", "Yell", "Q6841058", 2642554),
    ("Ulsta", "Yell", "Q7879929", 2635188),
    ("Gutcher", "Yell", "Q5621704", 2647748),
    ("Burravoe", "Yell", "Q852208", 2654245),
    ("Cullivoe", "Yell", "Q899534", 12265213),
    ("Haroldswick", "Unst", "Q2642797", 2647454),
    ("Uyeasound", "Unst", "Q1783763", 8426372),
    ("Skaw", "Unst", "Q598075", 13282661),
    ("Houbie", "Fetlar", "Q64520888", 10277903),
    ("Scatness", "Mainland", "Q7430582", 12263581),
    ("Laxo", "Mainland", "Q6505294", 12195583),
    ("Twatt", "Mainland", "Q3399533", 2635320),
    ("Firth", "Mainland", "Q5454295", 12264909),
    ("Sullom", "Mainland", "Q80117987", 13283129),
    ("Veensgarth", "Mainland", "Q9368332", 6693639),
]

# ===========================================================================
# HEBRIDES SETTLEMENTS (Outer and Inner Hebrides)
# ===========================================================================
HEBRIDES_SETTLEMENTS: list[tuple[str, str, str, int]] = [
    # --- Lewis (Outer Hebrides) ---
    ("Stornoway", "Lewis", "Q165845", 2636790),
    ("Carloway", "Lewis", "Q1043339", 2653772),
    ("Callanish", "Lewis", "Q1027162", 2653988),
    ("Barvas", "Lewis", "Q3250474", 2656204),
    ("Port of Ness", "Lewis", "Q7231213", 2640013),
    ("Arnol", "Lewis", "Q2188244", 2657033),
    ("Shawbost", "Lewis", "Q3776618", 12262195),
    ("Leurbost", "Lewis", "Q3775785", 2644580),
    ("Tong", "Lewis", "Q7820910", 0),
    ("Bayble", "Lewis", "Q4874382", 2656140),
    ("Achmore", "Lewis", "Q778459", 10277710),
    ("Gravir", "Lewis", "Q1543984", 2648188),
    ("Lionel", "Lewis", "Q6555493", 2644423),
    ("Swainbost", "Lewis", "Q7653007", 2636441),
    ("Shader", "Lewis", "Q37951790", 2638160),
    ("Melbost", "Lewis", "Q6811687", 12262191),
    ("Gress", "Lewis", "Q5607615", 2647914),
    ("Coll", "Lewis", "Q5145776", 2652574),
    ("South Dell", "Lewis", "Q7567026", 2637440),
    ("North Galson", "Lewis", "Q38031867", 2641351),
    ("Swordale", "Lewis", "Q35031531", 2636365),
    # --- Harris (Outer Hebrides) ---
    ("Tarbert", "Harris", "Q2121588", 2636239),
    ("Leverburgh", "Harris", "Q2243731", 7909718),
    ("Northton", "Harris", "Q109266014", 11240119),
    ("Luskentyre", "Harris", "Q19585980", 0),
    ("Rodel", "Harris", "Q3438145", 10711846),
    ("Rhenigidale", "Harris", "Q7386078", 0),
    ("Scarista", "Harris", "Q37925896", 0),
    # --- North Uist (Outer Hebrides) ---
    ("Lochmaddy", "North Uist", "Q1738877", 2643811),
    ("Sollas", "North Uist", "Q7558325", 2637545),
    ("Newtonferry", "North Uist", "Q13157688", 2640018),
    # --- Benbecula (Outer Hebrides) ---
    ("Balivanich", "Benbecula", "Q805000", 9883821),
    # --- South Uist (Outer Hebrides) ---
    ("Lochboisdale", "South Uist", "Q1016308", 2643844),
    # --- Barra (Outer Hebrides) ---
    ("Castlebay", "Barra", "Q1049581", 2653609),
    ("Borve", "Barra", "Q894291", 2655153),
    ("Eoligarry", "Barra", "Q1346301", 0),
    # --- Skye (Inner Hebrides) ---
    ("Portree", "Skye", "Q1010998", 2640043),
    ("Broadford", "Skye", "Q922593", 2654619),
    ("Dunvegan", "Skye", "Q747568", 2650610),
    ("Kyleakin", "Skye", "Q1018753", 2645077),
    ("Uig", "Skye", "Q515476", 2635240),
    # --- Mull (Inner Hebrides) ---
    ("Tobermory", "Mull", "Q416901", 2635771),
    ("Craignure", "Mull", "Q2920373", 2651884),
    # --- Islay (Inner Hebrides) ---
    ("Bowmore", "Islay", "Q51906", 2655095),
    ("Port Ellen", "Islay", "Q1019330", 2640028),
    ("Port Charlotte", "Islay", "Q51915", 2640041),
    # --- Tiree (Inner Hebrides) ---
    ("Scarinish", "Tiree", "Q3778620", 2638413),
    # --- Colonsay (Inner Hebrides) ---
    ("Scalasaig", "Colonsay", "Q7429691", 2638474),
]

# ===========================================================================
# ALTERNATIVE NAMES
# ===========================================================================
FAROE_ALT_NAMES: dict[str, dict[str, list[str]]] = {
    "Tórshavn": {
        "dan": ["Thorshavn"],
        "non": ["Þórshǫfn"],
        "lat": ["Portus Thoris"],
        "eng": ["Torshavn"],
    },
    "Klaksvík": {
        "dan": ["Klaksvík"],
        "non": ["Klakksvík"],
    },
    "Hoyvík": {
        "dan": ["Hoyvík"],
        "non": ["Heyvík"],
    },
    "Argir": {
        "dan": ["Argir"],
        "non": ["Argir"],
    },
    "Fuglafjørður": {
        "dan": ["Fuglafjørður"],
        "non": ["Fuglafjǫrðr"],
        "eng": ["Fuglafjordur"],
    },
    "Vágur": {
        "dan": ["Vágur"],
        "non": ["Vágr"],
    },
    "Vestmanna": {
        "dan": ["Vestmanna"],
        "non": ["Vestmannahǫfn"],
        "eng": ["Westmanna"],
    },
    "Sørvágur": {
        "dan": ["Sørvágur"],
        "non": ["Suðrvágr"],
    },
    "Miðvágur": {
        "dan": ["Miðvágur"],
        "non": ["Miðvágr"],
    },
    "Saltangará": {
        "dan": ["Saltangará"],
    },
    "Leirvík": {
        "dan": ["Leirvík"],
        "non": ["Leirvík"],
    },
    "Sandavágur": {
        "dan": ["Sandavágur"],
        "non": ["Sandvágr"],
    },
    "Strendur": {
        "dan": ["Strendur"],
        "non": ["Strendr"],
    },
    "Toftir": {
        "dan": ["Toftir"],
        "non": ["Toftir"],
    },
    "Tvøroyri": {
        "dan": ["Tvøroyri"],
        "non": ["Þveráeyri"],
    },
    "Kollafjørður": {
        "dan": ["Kollafjørður"],
        "non": ["Kollafjǫrðr"],
    },
    "Skála": {
        "dan": ["Skála"],
        "non": ["Skáli"],
    },
    "Eiði": {
        "dan": ["Eiði"],
        "non": ["Eið"],
    },
    "Norðragøta": {
        "dan": ["Norðragøta"],
        "non": ["Nørðragøta"],
    },
    "Hvalba": {
        "dan": ["Hvalba"],
        "non": ["Hvalba"],
    },
    "Runavík": {
        "dan": ["Runavík"],
        "non": ["Rúnavík"],
    },
    "Sandur": {
        "dan": ["Sandur"],
        "non": ["Sandr"],
    },
    "Trongisvágur": {
        "dan": ["Trongisvágur"],
        "non": ["Þrǫngsvágr"],
    },
    "Kvívík": {
        "dan": ["Kvívík"],
        "non": ["Kvívík"],
    },
    "Viðareiði": {
        "dan": ["Viðareiði"],
        "non": ["Viðareiði"],
        "eng": ["Vidareidi"],
    },
    "Kirkjubøur": {
        "dan": ["Kirkjubøur"],
        "non": ["Kirkjubǿr"],
        "lat": ["Kirkiubø"],
        "eng": ["Kirkjubour"],
    },
    "Sumba": {
        "dan": ["Sumba"],
        "non": ["Sumba"],
    },
    "Hvannasund": {
        "dan": ["Hvannasund"],
        "non": ["Hvannasund"],
    },
    "Nólsoy": {
        "dan": ["Nólsoy"],
        "non": ["Nólsey"],
    },
    "Gjógv": {
        "dan": ["Gjógv"],
        "non": ["Gjógv"],
        "eng": ["Gjogv"],
    },
    "Haldarsvík": {
        "dan": ["Haldarsvík"],
        "non": ["Hallvarðsvík"],
    },
    "Kunoy": {
        "dan": ["Kunoy"],
        "non": ["Kunóy"],
    },
    "Saksun": {
        "dan": ["Saksun"],
        "non": ["Saksun"],
    },
    "Bøur": {
        "dan": ["Bøur"],
        "non": ["Bǿr"],
    },
    "Gásadalur": {
        "dan": ["Gásadalur"],
        "non": ["Gásadalr"],
    },
    "Mykines": {
        "dan": ["Mykines"],
        "non": ["Mykines"],
    },
    "Skúvoy": {
        "dan": ["Skúvoy"],
        "non": ["Skúfey"],
    },
    "Tjørnuvík": {
        "dan": ["Tjørnuvík"],
        "non": ["Tjǫrnuvík"],
    },
}

SHETLAND_ALT_NAMES: dict[str, dict[str, list[str]]] = {
    "Lerwick": {
        "sco": ["Lerook", "Lerrick"],
        "non": ["Leirvik"],
        "gla": ["Liùrabhaig"],
    },
    "Scalloway": {
        "sco": ["Scallowa"],
        "non": ["Skálavágr"],
        "gla": ["Sgalabhagh"],
    },
    "Brae": {
        "sco": ["Brae"],
        "non": ["Breiðr"],
    },
    "Symbister": {
        "non": ["Simbister"],
    },
    "Baltasound": {
        "non": ["Baltasund"],
        "sco": ["Baltasund"],
    },
    "Walls": {
        "sco": ["Waas"],
        "non": ["Válar"],
    },
    "Sandwick": {
        "non": ["Sandvík"],
    },
    "Hillswick": {
        "non": ["Hildasvík"],
    },
    "Hamnavoe": {
        "non": ["Hafnarvágr"],
    },
    "Voe": {
        "non": ["Vágr"],
    },
    "Tingwall": {
        "non": ["Þingvǫllr"],
        "sco": ["Tingwall"],
    },
    "Sumburgh": {
        "non": ["Svinborg"],
    },
    "Mid Yell": {
        "non": ["Miðjall"],
        "sco": ["Mid Yell"],
    },
    "Haroldswick": {
        "sco": ["Haroldswick"],
        "non": ["Haraldsvík"],
    },
    "Skaw": {
        "non": ["Skagi"],
        "sco": ["Skaw"],
    },
    "Gutcher": {
        "non": ["Goðsgerðr"],
    },
    "Burravoe": {
        "non": ["Borgarfjǫrðr"],
        "sco": ["Burravoe"],
    },
    "Cullivoe": {
        "non": ["Kolluvágr"],
        "sco": ["Cullivoe"],
    },
    "Twatt": {
        "non": ["Þveit"],
    },
    "Ollaberry": {
        "non": ["Ólafsborg"],
    },
    "Laxo": {
        "non": ["Laxá"],
    },
    "Scatness": {
        "non": ["Skatanes"],
    },
    "Sullom": {
        "non": ["Súlheimr"],
    },
    "Aith": {
        "non": ["Eið"],
    },
    "Cunningsburgh": {
        "non": ["Konungsborg"],
    },
    "Firth": {
        "non": ["Fjǫrðr"],
    },
    "Quarff": {
        "non": ["Hvarf"],
    },
    "Boddam": {
        "non": ["Boðhamn"],
        "sco": ["Boddam"],
    },
    "North Roe": {
        "non": ["Norðra Rá"],
    },
    "Mossbank": {
        "non": ["Mosabrekkr"],
    },
    "Weisdale": {
        "non": ["Vestridalr"],
    },
    "Sandness": {
        "non": ["Sandnes"],
    },
    "Houbie": {
        "non": ["Hóbýr"],
    },
}

HEBRIDES_ALT_NAMES: dict[str, dict[str, list[str]]] = {
    "Stornoway": {
        "gla": ["Steòrnabhagh"],
        "non": ["Stjórnuvágr"],
    },
    "Carloway": {
        "gla": ["Càrlabhagh"],
        "non": ["Karlsvágr"],
    },
    "Callanish": {
        "gla": ["Calanais"],
    },
    "Barvas": {
        "gla": ["Barbhas"],
        "non": ["Barfas"],
    },
    "Port of Ness": {
        "gla": ["Port Nis"],
        "non": ["Nes"],
    },
    "Arnol": {
        "gla": ["Àrnol"],
        "non": ["Arnólf"],
    },
    "Shawbost": {
        "gla": ["Siabost"],
        "non": ["Sjávarbolstaðr"],
    },
    "Leurbost": {
        "gla": ["Liùrbost"],
        "non": ["Leirbolstaðr"],
    },
    "Tong": {
        "gla": ["Tunga"],
        "non": ["Tunga"],
    },
    "Bayble": {
        "gla": ["Pabail"],
        "non": ["Papar-bólr"],
    },
    "Achmore": {
        "gla": ["An Acha Mòr"],
    },
    "Gravir": {
        "gla": ["Grabhair"],
        "non": ["Grafar"],
    },
    "Lionel": {
        "gla": ["Lìonail"],
    },
    "Swainbost": {
        "gla": ["Suaineabost"],
        "non": ["Sveinbolstaðr"],
    },
    "Shader": {
        "gla": ["Siadar"],
        "non": ["Setr"],
    },
    "Melbost": {
        "gla": ["Mealabost"],
        "non": ["Melarbolstaðr"],
    },
    "Gress": {
        "gla": ["Griais"],
        "non": ["Gras"],
    },
    "Coll": {
        "gla": ["Col"],
    },
    "South Dell": {
        "gla": ["Dail bho Dheas"],
        "non": ["Dalr"],
    },
    "North Galson": {
        "gla": ["Gabhsann a Tuath"],
        "non": ["Galsun"],
    },
    "Swordale": {
        "gla": ["Suardail"],
        "non": ["Svarðdalr"],
    },
    "Tarbert": {
        "gla": ["An Tairbeart"],
        "non": ["Tarbat"],
    },
    "Leverburgh": {
        "gla": ["An Tòb"],
    },
    "Northton": {
        "gla": ["An Taobh Tuath"],
    },
    "Luskentyre": {
        "gla": ["Losgaintir"],
        "non": ["Losgentir"],
    },
    "Rodel": {
        "gla": ["Ròghadal"],
        "non": ["Rogarvallr"],
    },
    "Rhenigidale": {
        "gla": ["Rèinigeadal"],
        "non": ["Reynidalr"],
    },
    "Scarista": {
        "gla": ["Sgarasta"],
        "non": ["Skarfastaðr"],
    },
    "Lochmaddy": {
        "gla": ["Loch nam Madadh"],
    },
    "Sollas": {
        "gla": ["Solas"],
    },
    "Newtonferry": {
        "gla": ["Port nan Long"],
    },
    "Balivanich": {
        "gla": ["Baile a' Mhanaich"],
    },
    "Lochboisdale": {
        "gla": ["Loch Baghasdail"],
        "non": ["Bagasdalr"],
    },
    "Castlebay": {
        "gla": ["Bàgh a' Chaisteil"],
    },
    "Borve": {
        "gla": ["Borgh"],
        "non": ["Borg"],
    },
    "Eoligarry": {
        "gla": ["Eòlaigearraidh"],
        "non": ["Eyjólfsgarðr"],
    },
    "Portree": {
        "gla": ["Port Rìgh"],
        "non": ["Portrí"],
    },
    "Broadford": {
        "gla": ["An t-Àth Leathann"],
    },
    "Dunvegan": {
        "gla": ["Dùn Bheagain"],
        "non": ["Dúnbegan"],
    },
    "Kyleakin": {
        "gla": ["Caol Àcain"],
        "non": ["Kyleakin"],
    },
    "Uig": {
        "gla": ["Ùig"],
        "non": ["Vík"],
    },
    "Tobermory": {
        "gla": ["Tobar Mhoire"],
        "lat": ["Fons Mariae"],
    },
    "Craignure": {
        "gla": ["Creag an Iubhair"],
    },
    "Bowmore": {
        "gla": ["Bogha Mòr"],
    },
    "Port Ellen": {
        "gla": ["Port Ìlein"],
    },
    "Port Charlotte": {
        "gla": ["Port Sgioba"],
    },
    "Scarinish": {
        "gla": ["Sgairinis"],
    },
    "Scalasaig": {
        "gla": ["Sgalasaig"],
        "non": ["Skálasæti"],
    },
}


# ---------------------------------------------------------------------------
# Wikidata SPARQL query
# ---------------------------------------------------------------------------
def query_wikidata(qids: list[str]) -> dict[str, dict]:
    """Query Wikidata for settlement data using VALUES-based lookup."""
    print("Querying Wikidata SPARQL...")

    # Split into batches of 80 to avoid query size limits
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
            bd:serviceParam wikibase:language "en,fo,gd,sco"
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

            # Keep highest population if duplicate QID
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
def fetch_nominatim_geometry(
    name: str,
    country: str = "Faroe Islands",
    *,
    region: str | None = None,
) -> dict | None:
    """Fetch settlement boundary polygon from OSM Nominatim."""
    search_name = name.split("/")[0].strip()

    strategies: list[dict] = []
    if region:
        strategies.append(
            {
                "q": f"{search_name}, {region}, {country}",
                "format": "geojson",
                "polygon_geojson": 1,
                "limit": 3,
            }
        )
    strategies.append(
        {
            "q": f"{search_name}, {country}",
            "format": "geojson",
            "polygon_geojson": 1,
            "limit": 3,
        }
    )

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
            print(f"    Nominatim error for '{name}': {e}")
            continue

        if not data.get("features"):
            time.sleep(NOMINATIM_DELAY)
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
# Ingest Faroe Islands
# ---------------------------------------------------------------------------
def ingest_faroe_islands(wikidata_lookup: dict[str, dict]) -> list[dict]:
    """Ingest Faroe Islands settlements."""
    print("\n=== FAROE ISLANDS ===")
    print(f"Settlements: {len(FAROE_SETTLEMENTS)}")

    # Fetch geometries
    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}
    for i, (name, island, _mun, _qid, _gn) in enumerate(FAROE_SETTLEMENTS):
        print(f"  [{i + 1:3d}/{len(FAROE_SETTLEMENTS)}] {name}...", end=" ", flush=True)
        geo = fetch_nominatim_geometry(name, "Faroe Islands", region=island)
        if geo:
            geometries[name] = geo
            print(f"OK ({geo['type']})")
        else:
            print("no polygon")
        time.sleep(NOMINATIM_DELAY)

    print(f"\n  Got geometry for {len(geometries)}/{len(FAROE_SETTLEMENTS)} settlements")

    # Create records
    records: list[dict] = []
    for name, island, municipality, qid, geonames_id in FAROE_SETTLEMENTS:
        wd = wikidata_lookup.get(qid, {})
        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{name}' ({qid}), skipping")
            continue

        # Place type: Tórshavn is capital, Klaksvík second city
        if name == "Tórshavn":
            place_type = "P.PPLC"
        elif name in ("Klaksvík", "Runavík", "Tvøroyri", "Fuglafjørður"):
            place_type = "P.PPLA"
        elif (wd.get("population") or 0) >= 500:
            place_type = "P.PPL"
        else:
            place_type = "P.PPL"

        alt_names = FAROE_ALT_NAMES.get(name, {})
        geometry = geometries.get(name)
        gn_id = wd.get("geonames_id") or geonames_id

        record = make_record(
            name_form=name,
            name_normalized=name.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=f"wikidata:{qid}",
            place_type=place_type,
            country_code="FO",
            language_code="fao",
            alternative_names=alt_names,
            source_url=f"https://www.wikidata.org/wiki/{qid}",
            wikidata_qid=qid,
            geonames_id=gn_id,
            area_km2=wd.get("area_km2"),
            population=wd.get("population"),
            elevation=wd.get("elevation"),
            geometry=geometry,
            region="Faroe Islands",
            island=island,
            municipality=municipality,
        )
        records.append(record)

    return records


# ---------------------------------------------------------------------------
# Ingest Shetland
# ---------------------------------------------------------------------------
def ingest_shetland(wikidata_lookup: dict[str, dict]) -> list[dict]:
    """Ingest Shetland settlements."""
    print("\n=== SHETLAND ===")
    print(f"Settlements: {len(SHETLAND_SETTLEMENTS)}")

    # Fetch geometries
    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}
    for i, (name, sub_area, _qid, _gn) in enumerate(SHETLAND_SETTLEMENTS):
        print(
            f"  [{i + 1:3d}/{len(SHETLAND_SETTLEMENTS)}] {name}...",
            end=" ",
            flush=True,
        )
        geo = fetch_nominatim_geometry(name, "United Kingdom", region=f"Shetland, {sub_area}")
        if geo:
            geometries[name] = geo
            print(f"OK ({geo['type']})")
        else:
            print("no polygon")
        time.sleep(NOMINATIM_DELAY)

    print(f"\n  Got geometry for {len(geometries)}/{len(SHETLAND_SETTLEMENTS)} settlements")

    # Create records
    records: list[dict] = []
    for name, sub_area, qid, geonames_id in SHETLAND_SETTLEMENTS:
        wd = wikidata_lookup.get(qid, {})
        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{name}' ({qid}), skipping")
            continue

        # Place type
        if name == "Lerwick":
            place_type = "P.PPLA2"
        elif name == "Scalloway":
            place_type = "P.PPLA3"
        else:
            place_type = "P.PPL"

        alt_names = SHETLAND_ALT_NAMES.get(name, {})
        geometry = geometries.get(name)
        gn_id = wd.get("geonames_id") or geonames_id

        record = make_record(
            name_form=name,
            name_normalized=name.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=f"wikidata:{qid}",
            place_type=place_type,
            country_code="GB",
            language_code="eng",
            alternative_names=alt_names,
            source_url=f"https://www.wikidata.org/wiki/{qid}",
            wikidata_qid=qid,
            geonames_id=gn_id,
            area_km2=wd.get("area_km2"),
            population=wd.get("population"),
            elevation=wd.get("elevation"),
            geometry=geometry,
            region="Scotland",
            island=f"Shetland ({sub_area})",
            municipality="Shetland Islands",
        )
        records.append(record)

    return records


# ---------------------------------------------------------------------------
# Ingest Hebrides
# ---------------------------------------------------------------------------
def ingest_hebrides(wikidata_lookup: dict[str, dict]) -> list[dict]:
    """Ingest Hebrides settlements."""
    print("\n=== HEBRIDES ===")
    print(f"Settlements: {len(HEBRIDES_SETTLEMENTS)}")

    # Fetch geometries
    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}
    for i, (name, island, _qid, _gn) in enumerate(HEBRIDES_SETTLEMENTS):
        print(
            f"  [{i + 1:3d}/{len(HEBRIDES_SETTLEMENTS)}] {name}...",
            end=" ",
            flush=True,
        )
        geo = fetch_nominatim_geometry(name, "United Kingdom", region=f"{island}, Scotland")
        if geo:
            geometries[name] = geo
            print(f"OK ({geo['type']})")
        else:
            print("no polygon")
        time.sleep(NOMINATIM_DELAY)

    print(f"\n  Got geometry for {len(geometries)}/{len(HEBRIDES_SETTLEMENTS)} settlements")

    # Create records
    records: list[dict] = []
    for name, island, qid, geonames_id in HEBRIDES_SETTLEMENTS:
        wd = wikidata_lookup.get(qid, {})
        lat = wd.get("lat")
        lon = wd.get("lon")

        if lat is None or lon is None:
            print(f"  WARNING: No coordinates for '{name}' ({qid}), skipping")
            continue

        # Place type
        if name == "Stornoway":
            place_type = "P.PPLA2"
        elif name in ("Portree", "Tobermory", "Tarbert", "Lochmaddy", "Castlebay"):
            place_type = "P.PPLA3"
        else:
            place_type = "P.PPL"

        alt_names = HEBRIDES_ALT_NAMES.get(name, {})
        geometry = geometries.get(name)
        gn_id = wd.get("geonames_id") or geonames_id

        # Determine admin area
        outer_hebrides = {"Lewis", "Harris", "North Uist", "Benbecula", "South Uist", "Barra"}
        admin_area = "Na h-Eileanan Siar" if island in outer_hebrides else "Highland"
        if island in ("Islay", "Mull", "Colonsay", "Tiree"):
            admin_area = "Argyll and Bute"

        record = make_record(
            name_form=name,
            name_normalized=name.lower().strip(),
            latitude=lat,
            longitude=lon,
            source_id=f"wikidata:{qid}",
            place_type=place_type,
            country_code="GB",
            language_code="eng",
            alternative_names=alt_names,
            source_url=f"https://www.wikidata.org/wiki/{qid}",
            wikidata_qid=qid,
            geonames_id=gn_id,
            area_km2=wd.get("area_km2"),
            population=wd.get("population"),
            elevation=wd.get("elevation"),
            geometry=geometry,
            region="Scotland",
            island=island,
            municipality=admin_area,
        )
        records.append(record)

    return records


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    """Ingest all island settlements with comprehensive metadata."""
    print("=" * 70)
    print("ISLAND SETTLEMENTS INGESTION")
    print("Faroe Islands + Shetland + Hebrides")
    print("=" * 70)

    # Collect all QIDs
    all_qids: list[str] = []
    seen_qids: set[str] = set()

    for _, _, _, qid, _ in FAROE_SETTLEMENTS:
        if qid not in seen_qids:
            seen_qids.add(qid)
            all_qids.append(qid)
    for _, _, qid, _ in SHETLAND_SETTLEMENTS:
        if qid not in seen_qids:
            seen_qids.add(qid)
            all_qids.append(qid)
    for _, _, qid, _ in HEBRIDES_SETTLEMENTS:
        if qid not in seen_qids:
            seen_qids.add(qid)
            all_qids.append(qid)

    print(f"\nTotal unique QIDs to query: {len(all_qids)}")

    # Query Wikidata for all
    wikidata_lookup = query_wikidata(all_qids)
    print(f"Got data for {len(wikidata_lookup)} QIDs from Wikidata")

    # Ingest each region
    fo_records = ingest_faroe_islands(wikidata_lookup)
    shetland_records = ingest_shetland(wikidata_lookup)
    hebrides_records = ingest_hebrides(wikidata_lookup)

    # Write Faroe Islands
    OUTPUT_FO.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nSigning {len(fo_records)} Faroe Islands records...")
    fo_signed = [sign_record(r) for r in fo_records]
    with OUTPUT_FO.open("w") as f:
        for record in fo_signed:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"Wrote {len(fo_signed)} records to {OUTPUT_FO}")

    # Append Shetland + Hebrides to GB
    gb_records = shetland_records + hebrides_records
    print(f"\nSigning {len(gb_records)} Shetland + Hebrides records...")
    gb_signed = [sign_record(r) for r in gb_records]

    # Read existing GB records
    existing_gb: list[str] = []
    existing_source_ids: set[str] = set()
    if OUTPUT_GB.exists():
        with OUTPUT_GB.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    existing_gb.append(line)
                    rec = json.loads(line)
                    existing_source_ids.add(rec.get("source_id", ""))

    # Filter out duplicates
    new_gb = [r for r in gb_signed if r.get("source_id") not in existing_source_ids]
    print(f"  {len(new_gb)} new records (skipped {len(gb_signed) - len(new_gb)} duplicates)")

    with OUTPUT_GB.open("w") as f:
        for line in existing_gb:
            f.write(line + "\n")
        for record in new_gb:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"GB file now has {len(existing_gb) + len(new_gb)} records")

    # Summary stats
    all_records = fo_signed + new_gb
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Faroe Islands: {len(fo_signed)} records")
    print(f"  Shetland: {len(shetland_records)} records")
    print(f"  Hebrides: {len(hebrides_records)} records")
    print(f"  Total new: {len(all_records)} records")

    with_geo = sum(1 for r in all_records if r.get("geometry"))
    with_pop = sum(1 for r in all_records if r.get("population"))
    with_alts = sum(
        1
        for r in all_records
        if r.get("alternative_names") and any(r["alternative_names"].values())
    )
    print(f"\n  With geometry: {with_geo}/{len(all_records)}")
    print(f"  With population: {with_pop}/{len(all_records)}")
    print(f"  With alternative names: {with_alts}/{len(all_records)}")


if __name__ == "__main__":
    main()
