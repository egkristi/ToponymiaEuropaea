#!/usr/bin/env python3
"""Ingest cities and towns across the British Isles (United Kingdom).

Sources:
- Wikidata SPARQL: coordinates, population, GeoNames IDs, area,
  alternative names (Scottish Gaelic, Welsh, Irish, Latin, Old English, Norse)
- OpenStreetMap Nominatim: GeoJSON geometry (city/town boundaries/polygons)

The United Kingdom comprises four constituent countries:
  England (Q21): 48 ceremonial counties, capital London
  Scotland (Q22): 32 council areas, capital Edinburgh
  Wales (Q25): 22 principal areas, capital Cardiff
  Northern Ireland (Q26): 11 districts, capital Belfast

Linguistic layers:
  - English (eng): primary language throughout
  - Scottish Gaelic (gla/gd): Scotland, especially Highlands & Islands
  - Welsh (cym/cy): Wales, officially bilingual
  - Irish (gle/ga): Northern Ireland (some official status)
  - Scots (sco): Lowland Scotland, parts of Ulster
  - Latin (lat): ecclesiastical/Roman heritage
  - Old English (ang): Anglo-Saxon origins
  - Old Norse (non): Viking settlement names (Danelaw, Scotland)
  - Norman French (fro): post-1066 influence

References:
- https://en.wikipedia.org/wiki/List_of_cities_in_the_United_Kingdom
- https://en.wikipedia.org/wiki/List_of_towns_in_Scotland
- https://en.wikipedia.org/wiki/List_of_towns_in_Wales
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
OUTPUT_FILE = DATABANK_DIR / "places" / "GB" / "wikidata.jsonl"

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
        "country_code": "GB",
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
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ---------------------------------------------------------------------------
# British cities and towns
# Tuple: (English name, region, admin_area, wikidata_qid, geonames_id)
# ---------------------------------------------------------------------------
BRITISH_CITIES: list[tuple[str, str, str, str, int]] = [
    # =========================================================================
    # ENGLAND
    # =========================================================================
    # --- Major Cities (pop > 200k) ---
    ("London", "England", "Greater London", "Q84", 2643743),
    ("Birmingham", "England", "Birmingham", "Q2256", 2655603),
    ("Manchester", "England", "Manchester", "Q18125", 2643123),
    ("Leeds", "England", "Leeds", "Q39121", 2644688),
    ("Sheffield", "England", "Sheffield", "Q42448", 2638077),
    ("Liverpool", "England", "Liverpool", "Q24826", 2644210),
    ("Bristol", "England", "City of Bristol", "Q23154", 2654675),
    ("Leicester", "England", "City of Leicester", "Q83065", 2644668),
    ("Coventry", "England", "Coventry", "Q6225", 2652221),
    ("Newcastle upon Tyne", "England", "Newcastle upon Tyne", "Q1425428", 2641673),
    ("Bradford", "England", "Bradford", "Q22905", 2654993),
    ("Nottingham", "England", "City of Nottingham", "Q41262", 2641170),
    ("Sunderland", "England", "Sunderland", "Q188304", 2636531),
    ("Brighton and Hove", "England", "East Sussex", "Q1022488", 11550750),
    ("Southampton", "England", "City of Southampton", "Q79848", 2637487),
    ("Plymouth", "England", "City of Plymouth", "Q43382", 2640194),
    ("Milton Keynes", "England", "City of Milton Keynes", "Q204234", 2642465),
    ("Kingston upon Hull", "England", "City of Kingston upon Hull", "Q128147", 2645425),
    ("Stoke-on-Trent", "England", "City of Stoke-on-Trent", "Q134902", 2636841),
    ("Derby", "England", "City of Derby", "Q43475", 2651347),
    ("Wolverhampton", "England", "City of Wolverhampton", "Q126269", 2633691),
    ("Portsmouth", "England", "City of Portsmouth", "Q72259", 2639996),
    ("Luton", "England", "Luton", "Q203889", 2643339),
    ("York", "England", "City of York", "Q42462", 2633352),
    ("Norwich", "England", "Norwich", "Q130191", 2641181),
    ("Peterborough", "England", "City of Peterborough", "Q172438", 2640354),
    ("Bournemouth", "England", "Bournemouth, Christchurch and Poole", "Q170478", 2655095),
    # --- Medium Cities (pop 100k-200k) ---
    ("Reading", "England", "Reading", "Q161491", 2639577),
    ("Oxford", "England", "Oxford", "Q34217", 2640729),
    ("Gloucester", "England", "Gloucester", "Q170497", 2648404),
    ("Preston", "England", "Preston", "Q184090", 2639912),
    ("Middlesbrough", "England", "Middlesbrough", "Q171866", 2642607),
    ("Blackpool", "England", "Blackpool", "Q170377", 2655459),
    ("Exeter", "England", "Exeter", "Q134672", 2649808),
    ("Cambridge", "England", "Cambridge", "Q350", 2653941),
    ("Ipswich", "England", "Ipswich", "Q184775", 2646057),
    ("Northampton", "England", "West Northamptonshire", "Q192240", 2641430),
    ("Swindon", "England", "Swindon", "Q200942", 2636427),
    ("Warrington", "England", "Warrington", "Q215733", 2634739),
    # --- Historic / Notable Cities ---
    ("Bath", "England", "Bath and North East Somerset", "Q22889", 2656173),
    ("Canterbury", "England", "Canterbury", "Q29303", 2653877),
    ("Winchester", "England", "Winchester", "Q172157", 2633858),
    ("Durham", "England", "County Durham", "Q179815", 2650628),
    ("Carlisle", "England", "Cumberland", "Q192896", 2653775),
    ("Chester", "England", "Cheshire West and Chester", "Q170263", 2653228),
    ("Lincoln", "England", "Lincolnshire", "Q180057", 2644487),
    ("Salisbury", "England", "Wiltshire", "Q160642", 2638664),
    ("Worcester", "England", "Worcestershire", "Q613294", 2633563),
    ("Hereford", "England", "Herefordshire", "Q204720", 2647074),
    ("Lancaster", "England", "Lancashire", "Q210652", 2644972),
    ("Chichester", "England", "West Sussex", "Q207639", 2653192),
    ("Colchester", "England", "Essex", "Q184163", 2652618),
    ("Scarborough", "England", "North Yorkshire", "Q743521", 2638419),
    ("Whitby", "England", "North Yorkshire", "Q213180", 2634032),
    ("Hastings", "England", "East Sussex", "Q29245", 2647541),
    ("Dover", "England", "Kent", "Q179224", 2651048),
    # =========================================================================
    # SCOTLAND
    # =========================================================================
    ("Glasgow", "Scotland", "Glasgow City", "Q4093", 2648579),
    ("Edinburgh", "Scotland", "City of Edinburgh", "Q23436", 2650225),
    ("Aberdeen", "Scotland", "Aberdeen City", "Q36405", 2657832),
    ("Dundee", "Scotland", "Dundee City", "Q123709", 2650752),
    ("Paisley", "Scotland", "Renfrewshire", "Q211870", 2640677),
    ("East Kilbride", "Scotland", "South Lanarkshire", "Q654226", 2650405),
    ("Livingston", "Scotland", "West Lothian", "Q848287", 2644204),
    ("Hamilton", "Scotland", "South Lanarkshire", "Q4131", 2647570),
    ("Dunfermline", "Scotland", "Fife", "Q211950", 2650732),
    ("Kirkcaldy", "Scotland", "Fife", "Q691685", 2645298),
    ("Perth", "Scotland", "Perth and Kinross", "Q203000", 2640358),
    ("Inverness", "Scotland", "Highland", "Q160493", 2646088),
    ("Ayr", "Scotland", "South Ayrshire", "Q654216", 2656708),
    ("Kilmarnock", "Scotland", "East Ayrshire", "Q576562", 2645605),
    ("Greenock", "Scotland", "Inverclyde", "Q217831", 2647948),
    ("Stirling", "Scotland", "Stirling", "Q182923", 2636910),
    ("Falkirk", "Scotland", "Falkirk", "Q623687", 2649723),
    ("Dumfries", "Scotland", "Dumfries and Galloway", "Q652035", 2650798),
    ("Elgin", "Scotland", "Moray", "Q841074", 2650122),
    ("Arbroath", "Scotland", "Angus", "Q630668", 2657215),
    ("St Andrews", "Scotland", "Fife", "Q207736", 2638864),
    ("Peterhead", "Scotland", "Aberdeenshire", "Q1016944", 2640351),
    ("Fort William", "Scotland", "Highland", "Q848909", 2649169),
    ("Oban", "Scotland", "Argyll and Bute", "Q935702", 2641108),
    ("Thurso", "Scotland", "Highland", "Q526576", 2635881),
    ("Kirkwall", "Scotland", "Orkney Islands", "Q208329", 2645198),
    ("Lerwick", "Scotland", "Shetland Islands", "Q213485", 2644605),
    ("Stornoway", "Scotland", "Na h-Eileanan Siar", "Q165845", 2636790),
    ("Wick", "Scotland", "Highland", "Q1010891", 2633922),
    ("Fraserburgh", "Scotland", "Aberdeenshire", "Q138873", 2649089),
    ("Montrose", "Scotland", "Angus", "Q420303", 2642302),
    ("Hawick", "Scotland", "Scottish Borders", "Q407183", 2647297),
    ("Galashiels", "Scotland", "Scottish Borders", "Q1016925", 2648928),
    ("Stranraer", "Scotland", "Dumfries and Galloway", "Q1001935", 2636719),
    ("Dunbar", "Scotland", "East Lothian", "Q1002133", 2650776),
    ("Musselburgh", "Scotland", "East Lothian", "Q37718", 2641942),
    ("Linlithgow", "Scotland", "West Lothian", "Q1016911", 2644444),
    ("Nairn", "Scotland", "Highland", "Q980084", 2641910),
    ("Crieff", "Scotland", "Perth and Kinross", "Q639666", 2651983),
    ("Dunblane", "Scotland", "Stirling", "Q614314", 2650769),
    ("Helensburgh", "Scotland", "Argyll and Bute", "Q1007088", 2647178),
    ("Campbeltown", "Scotland", "Argyll and Bute", "Q1012490", 2653928),
    ("Rothesay", "Scotland", "Argyll and Bute", "Q1818828", 2639148),
    ("Pitlochry", "Scotland", "Perth and Kinross", "Q1011665", 2640283),
    # =========================================================================
    # WALES
    # =========================================================================
    ("Cardiff", "Wales", "Cardiff", "Q10690", 2653822),
    ("Swansea", "Wales", "Swansea", "Q23051", 2636432),
    ("Newport", "Wales", "Newport", "Q101254", 2641598),
    ("Wrexham", "Wales", "Wrexham County Borough", "Q496368", 2633485),
    ("Merthyr Tydfil", "Wales", "Merthyr Tydfil County Borough", "Q752762", 2642705),
    ("Barry", "Wales", "The Vale of Glamorgan", "Q809009", 2656235),
    ("Neath", "Wales", "Neath Port Talbot", "Q2003342", 7299867),
    ("Bridgend", "Wales", "Bridgend County Borough", "Q6497774", 2654755),
    ("Llanelli", "Wales", "Carmarthenshire", "Q990125", 2644100),
    ("Rhyl", "Wales", "Denbighshire", "Q2020203", 7291924),
    ("Bangor", "Wales", "Gwynedd", "Q234178", 7298620),
    ("Caerphilly", "Wales", "Caerphilly County Borough", "Q909119", 7296029),
    ("Aberystwyth", "Wales", "Ceredigion", "Q213154", 2657782),
    ("Carmarthen", "Wales", "Carmarthenshire", "Q1012685", 2653836),
    ("Brecon", "Wales", "Powys", "Q904472", 2654736),
    ("Caernarfon", "Wales", "Gwynedd", "Q42858164", 2653858),
    ("Pembroke", "Wales", "Pembrokeshire", "Q1016834", 2640438),
    ("Conwy", "Wales", "Conwy County Borough", "Q3398996", 2652341),
    ("Tenby", "Wales", "Pembrokeshire", "Q671946", 2635697),
    ("St Davids", "Wales", "Pembrokeshire", "Q212927", 2638832),
    ("Harlech", "Wales", "Gwynedd", "Q1017183", 2647356),
    ("Holyhead", "Wales", "Isle of Anglesey", "Q257446", 2646505),
    ("Llandudno", "Wales", "Conwy County Borough", "Q33225172", 2644044),
    ("Machynlleth", "Wales", "Powys", "Q675460", 2643254),
    ("Dolgellau", "Wales", "Gwynedd", "Q24671087", 2651058),
    ("Newtown", "Wales", "Powys", "Q1017359", 2641596),
    ("Milford Haven", "Wales", "Pembrokeshire", "Q991055", 2642534),
    # =========================================================================
    # NORTHERN IRELAND
    # =========================================================================
    ("Belfast", "Northern Ireland", "Belfast", "Q10686", 2655984),
    ("Derry", "Northern Ireland", "Derry City and Strabane", "Q163584", 2643736),
    ("Lisburn", "Northern Ireland", "Lisburn and Castlereagh", "Q1828035", 2644089),
    ("Newry", "Northern Ireland", "Newry, Mourne and Down", "Q269980", 2641629),
    ("Bangor", "Northern Ireland", "Ards and North Down", "Q806551", 2656299),
    ("Craigavon", "Northern Ireland", "Armagh City, Banbridge and Craigavon", "Q1004085", 2651929),
    ("Ballymena", "Northern Ireland", "Mid and East Antrim", "Q805451", 2656476),
    ("Newtownabbey", "Northern Ireland", "Antrim and Newtownabbey", "Q918947", 2641521),
    ("Coleraine", "Northern Ireland", "Causeway Coast and Glens", "Q1108185", 2652508),
    ("Omagh", "Northern Ireland", "Fermanagh and Omagh", "Q510513", 2641068),
    ("Enniskillen", "Northern Ireland", "Fermanagh and Omagh", "Q990109", 2649994),
    ("Strabane", "Northern Ireland", "Derry City and Strabane", "Q1027659", 2636734),
    ("Larne", "Northern Ireland", "Mid and East Antrim", "Q935686", 2644924),
    ("Armagh", "Northern Ireland", "Armagh City, Banbridge and Craigavon", "Q193452", 2657298),
    ("Downpatrick", "Northern Ireland", "Newry, Mourne and Down", "Q1024917", 2651026),
    ("Carrickfergus", "Northern Ireland", "Mid and East Antrim", "Q1020354", 2653713),
    ("Cookstown", "Northern Ireland", "Mid Ulster", "Q1129639", 2652266),
    ("Dungannon", "Northern Ireland", "Mid Ulster", "Q1025602", 2650810),
    ("Newtownstewart", "Northern Ireland", "Derry City and Strabane", "Q2779526", 2641502),
]

# ---------------------------------------------------------------------------
# Alternative names: gla (Scottish Gaelic), cym (Welsh), gle (Irish),
# lat (Latin), ang (Old English), non (Old Norse), sco (Scots)
# ---------------------------------------------------------------------------
ALTERNATIVE_NAMES: dict[str, dict[str, list[str]]] = {
    # --- England ---
    "London": {
        "lat": ["Londinium", "Augusta"],
        "ang": ["Lundenwic", "Lundenburh"],
        "cym": ["Llundain"],
        "gla": ["Lunnainn"],
        "gle": ["Londain"],
        "non": ["Lundúnir"],
    },
    "Birmingham": {
        "ang": ["Beormingahām"],
        "lat": ["Birminghamia"],
    },
    "Manchester": {
        "lat": ["Mamucium", "Mancunium"],
        "ang": ["Mameceastre"],
        "cym": ["Manceinion"],
    },
    "Leeds": {
        "ang": ["Loidis"],
        "lat": ["Ledesia"],
        "cym": ["Loidis"],
    },
    "Sheffield": {
        "ang": ["Scēaffeld"],
    },
    "Liverpool": {
        "cym": ["Lerpwl"],
        "gla": ["Poll a' Ghrùthain"],
    },
    "Bristol": {
        "ang": ["Brycgstow"],
        "lat": ["Bristolia"],
        "cym": ["Bryste"],
    },
    "Leicester": {
        "lat": ["Ratae Corieltauvorum"],
        "ang": ["Ligera Ceaster"],
    },
    "Coventry": {
        "lat": ["Coventria"],
        "ang": ["Cofantree"],
    },
    "Newcastle upon Tyne": {
        "lat": ["Novum Castellum"],
        "ang": ["Monkchester"],
        "sco": ["Newcastle upon Tyne"],
    },
    "Bradford": {
        "ang": ["Brādanford"],
    },
    "Nottingham": {
        "ang": ["Snottingham"],
        "lat": ["Nottinghamia"],
        "non": ["Snotingham"],
    },
    "Southampton": {
        "lat": ["Clausentum"],
        "ang": ["Hāmtūn", "Hamwic"],
    },
    "Plymouth": {
        "lat": ["Plymuthia"],
    },
    "Kingston upon Hull": {
        "eng": ["Hull"],
        "lat": ["Hullum"],
    },
    "Stoke-on-Trent": {
        "eng": ["The Potteries"],
    },
    "Derby": {
        "non": ["Djúra-bý", "Deoraby"],
        "ang": ["Norðworþig"],
        "lat": ["Derbia"],
    },
    "Wolverhampton": {
        "ang": ["Wulfrūnehēahantūn"],
    },
    "Portsmouth": {
        "lat": ["Portus Magnus"],
        "ang": ["Portesmuð"],
    },
    "York": {
        "lat": ["Eboracum"],
        "ang": ["Eoforwīc"],
        "non": ["Jórvík"],
        "cym": ["Efrog", "Caer Efrog"],
        "gla": ["Eabhraig"],
        "gle": ["Eabhrac"],
    },
    "Norwich": {
        "ang": ["Norðwīc"],
        "lat": ["Norvicum"],
        "non": ["Norðvík"],
    },
    "Peterborough": {
        "ang": ["Medeshamstede"],
        "lat": ["Petriburgum"],
    },
    "Reading": {
        "ang": ["Rēadingas"],
    },
    "Oxford": {
        "lat": ["Oxonia", "Oxonium"],
        "ang": ["Oxnaford"],
        "cym": ["Rhydychen"],
    },
    "Gloucester": {
        "lat": ["Glevum", "Claudia Castra"],
        "ang": ["Gleawceaster"],
        "cym": ["Caerloyw"],
    },
    "Exeter": {
        "lat": ["Isca Dumnoniorum"],
        "ang": ["Exanceaster"],
        "cym": ["Caerwysg"],
    },
    "Cambridge": {
        "lat": ["Cantabrigia"],
        "ang": ["Grantebrycge"],
        "cym": ["Caergrawnt"],
    },
    "Bath": {
        "lat": ["Aquae Sulis", "Bathonia"],
        "ang": ["Baðum", "Ācemannesceastre"],
        "cym": ["Caerfaddon"],
    },
    "Canterbury": {
        "lat": ["Durovernum Cantiacorum", "Cantuaria"],
        "ang": ["Cantwareburh"],
        "cym": ["Caergaint"],
    },
    "Winchester": {
        "lat": ["Venta Belgarum"],
        "ang": ["Wintanceaster"],
        "cym": ["Caer Wynt"],
    },
    "Durham": {
        "ang": ["Dunholm"],
        "lat": ["Dunelmia"],
        "non": ["Dún Holmr"],
    },
    "Carlisle": {
        "lat": ["Luguvalium"],
        "ang": ["Luel"],
        "cym": ["Caerliwelydd"],
        "gla": ["Cathair Luail"],
    },
    "Chester": {
        "lat": ["Deva Victrix", "Cestria"],
        "ang": ["Legaceaster"],
        "cym": ["Caer"],
    },
    "Lincoln": {
        "lat": ["Lindum Colonia"],
        "ang": ["Lindcylene"],
        "cym": ["Caerllion ar Dŵr"],
    },
    "Salisbury": {
        "lat": ["Sarum", "Nova Sarum"],
        "ang": ["Searobyrig"],
    },
    "Worcester": {
        "lat": ["Vertis", "Vigornium"],
        "ang": ["Wigoraceaster"],
        "cym": ["Caerwrangon"],
    },
    "Hereford": {
        "ang": ["Hereford"],
        "cym": ["Henffordd"],
        "lat": ["Herefordia"],
    },
    "Lancaster": {
        "lat": ["Lancastria"],
        "ang": ["Lōnceaster"],
    },
    "Colchester": {
        "lat": ["Camulodunum", "Colonia Victricensis"],
        "ang": ["Colnceaster"],
    },
    "Dover": {
        "lat": ["Dubris", "Portus Dubris"],
        "ang": ["Dofras"],
        "cym": ["Dofr"],
    },
    "Whitby": {
        "non": ["Hvítabýr"],
        "ang": ["Streoneshealh"],
    },
    "Scarborough": {
        "non": ["Skarðaborg"],
    },
    "Hastings": {
        "ang": ["Hæstingas"],
        "lat": ["Hastingia"],
    },
    "Chichester": {
        "lat": ["Noviomagus Reginorum"],
        "ang": ["Cisseceaster"],
    },
    "Ipswich": {
        "ang": ["Gipeswīc"],
    },
    # --- Scotland ---
    "Glasgow": {
        "gla": ["Glaschu"],
        "lat": ["Glasguensis", "Glasgovia"],
        "sco": ["Glesga"],
    },
    "Edinburgh": {
        "gla": ["Dùn Èideann"],
        "lat": ["Edinburgum"],
        "sco": ["Edinbrae", "Embro"],
        "cym": ["Caeredin"],
        "ang": ["Edinburh"],
    },
    "Aberdeen": {
        "gla": ["Obar Dheathain"],
        "lat": ["Aberdonia"],
        "sco": ["Aiberdeen"],
    },
    "Dundee": {
        "gla": ["Dùn Dèagh"],
        "lat": ["Taodunum"],
        "sco": ["Dundee"],
    },
    "Paisley": {
        "gla": ["Pàislig"],
        "sco": ["Paisley"],
    },
    "East Kilbride": {
        "gla": ["Cille Bhrìghde an Ear"],
    },
    "Livingston": {
        "gla": ["Baile Dhunlèibhe"],
    },
    "Hamilton": {
        "gla": ["Baile Hamaltan"],
        "sco": ["Hamiltoun"],
    },
    "Dunfermline": {
        "gla": ["Dùn Phàrlain"],
        "sco": ["Dunfaurlin"],
    },
    "Kirkcaldy": {
        "gla": ["Cair Chaladain"],
        "sco": ["Kirkcaldy"],
    },
    "Perth": {
        "gla": ["Peairt"],
        "lat": ["Perthia"],
        "sco": ["Perth"],
    },
    "Inverness": {
        "gla": ["Inbhir Nis"],
        "lat": ["Invernessium"],
        "sco": ["Innerness"],
    },
    "Ayr": {
        "gla": ["Inbhir Àir"],
        "lat": ["Aeria"],
        "sco": ["Ayr"],
    },
    "Kilmarnock": {
        "gla": ["Cill Mheàrnaig"],
        "sco": ["Kilmarnock"],
    },
    "Greenock": {
        "gla": ["Grianaig"],
        "sco": ["Greenock"],
    },
    "Stirling": {
        "gla": ["Sruighlea"],
        "lat": ["Strivilingum"],
        "sco": ["Stirlin"],
    },
    "Falkirk": {
        "gla": ["An Eaglais Bhreac"],
        "sco": ["Fawkirk"],
    },
    "Dumfries": {
        "gla": ["Dùn Phris"],
        "sco": ["Dumfries"],
    },
    "Elgin": {
        "gla": ["Eilginn"],
        "sco": ["Elgin"],
    },
    "Arbroath": {
        "gla": ["Obar Bhrothaig"],
        "sco": ["Arbroath"],
        "lat": ["Aberbrothock"],
    },
    "St Andrews": {
        "gla": ["Cill Rìmhinn"],
        "lat": ["Sancti Andreae"],
        "sco": ["St Andras"],
    },
    "Peterhead": {
        "gla": ["Ceann Phàdraig"],
        "sco": ["Peterheid"],
    },
    "Fort William": {
        "gla": ["An Gearasdan"],
    },
    "Oban": {
        "gla": ["An t-Òban"],
    },
    "Thurso": {
        "gla": ["Inbhir Theòrsa"],
        "non": ["Þórsá"],
    },
    "Kirkwall": {
        "gla": ["Bàgh na h-Eaglaise"],
        "non": ["Kirkjuvágr"],
        "sco": ["Kirkwaa"],
    },
    "Lerwick": {
        "gla": ["Liùrabhaig"],
        "non": ["Leirvik"],
        "sco": ["Lerwick"],
    },
    "Stornoway": {
        "gla": ["Steòrnabhagh"],
        "non": ["Stjórnuvágr"],
    },
    "Wick": {
        "gla": ["Inbhir Ùige"],
        "non": ["Vík"],
    },
    "Fraserburgh": {
        "gla": ["A' Bhruaich"],
        "sco": ["Faithlie", "The Broch"],
    },
    "Montrose": {
        "gla": ["Monadh Rois"],
    },
    "Hawick": {
        "gla": ["Hamhaig"],
        "sco": ["Hawick"],
    },
    "Galashiels": {
        "gla": ["An Geal Àth"],
        "sco": ["Gala"],
    },
    "Stranraer": {
        "gla": ["An t-Sròn Reamhar"],
        "sco": ["Stranrawer"],
    },
    "Dunbar": {
        "gla": ["Dùn Bàrr"],
        "sco": ["Dunbar"],
    },
    "Musselburgh": {
        "gla": ["Baile nam Feusgan"],
        "sco": ["Musselburgh"],
        "lat": ["Inveresk"],
    },
    "Linlithgow": {
        "gla": ["Gleann Iucha"],
        "sco": ["Lithgae"],
    },
    "Nairn": {
        "gla": ["Inbhir Narann"],
    },
    "Crieff": {
        "gla": ["Craoibh"],
    },
    "Dunblane": {
        "gla": ["Dùn Bhlàthain"],
        "lat": ["Dunblanensis"],
    },
    "Helensburgh": {
        "gla": ["Baile Eilidh"],
    },
    "Campbeltown": {
        "gla": ["Ceann Loch Chille Chiarain"],
        "sco": ["Campbelton"],
    },
    "Rothesay": {
        "gla": ["Baile Bhòid"],
    },
    "Pitlochry": {
        "gla": ["Baile Chloichridh"],
    },
    # --- Wales ---
    "Cardiff": {
        "cym": ["Caerdydd"],
        "lat": ["Cardiffia"],
    },
    "Swansea": {
        "cym": ["Abertawe"],
        "lat": ["Swansia"],
        "non": ["Sveinsey"],
    },
    "Newport": {
        "cym": ["Casnewydd"],
    },
    "Wrexham": {
        "cym": ["Wrecsam"],
    },
    "Merthyr Tydfil": {
        "cym": ["Merthyr Tudful"],
    },
    "Barry": {
        "cym": ["y Barri"],
    },
    "Neath": {
        "cym": ["Castell-nedd"],
        "lat": ["Nidum"],
    },
    "Bridgend": {
        "cym": ["Pen-y-bont ar Ogwr"],
    },
    "Llanelli": {
        "cym": ["Llanelli"],
    },
    "Rhyl": {
        "cym": ["Y Rhyl"],
    },
    "Bangor": {
        "cym": ["Bangor"],
        "lat": ["Bangor"],
    },
    "Caerphilly": {
        "cym": ["Caerffili"],
    },
    "Aberystwyth": {
        "cym": ["Aberystwyth"],
        "lat": ["Aberystwyth"],
    },
    "Carmarthen": {
        "cym": ["Caerfyrddin"],
        "lat": ["Maridunum", "Carmarthenium"],
    },
    "Brecon": {
        "cym": ["Aberhonddu"],
        "lat": ["Breconia"],
    },
    "Caernarfon": {
        "cym": ["Caernarfon"],
        "lat": ["Segontium"],
        "eng": ["Carnarvon", "Caernarvon"],
    },
    "Pembroke": {
        "cym": ["Penfro"],
        "lat": ["Pembrochia"],
    },
    "Conwy": {
        "cym": ["Conwy"],
        "lat": ["Aberconium"],
        "eng": ["Conway"],
    },
    "Tenby": {
        "cym": ["Dinbych-y-pysgod"],
        "lat": ["Tenbighia"],
    },
    "St Davids": {
        "cym": ["Tyddewi"],
        "lat": ["Menevia"],
    },
    "Harlech": {
        "cym": ["Harlech"],
    },
    "Holyhead": {
        "cym": ["Caergybi"],
        "gle": ["Caer Gybi"],
    },
    "Llandudno": {
        "cym": ["Llandudno"],
    },
    "Machynlleth": {
        "cym": ["Machynlleth"],
        "lat": ["Machynlethum"],
    },
    "Dolgellau": {
        "cym": ["Dolgellau"],
        "eng": ["Dolgelley"],
    },
    "Newtown": {
        "cym": ["Y Drenewydd"],
    },
    "Milford Haven": {
        "cym": ["Aberdaugleddau"],
        "non": ["Milfjǫrðr"],
    },
    # --- Northern Ireland ---
    "Belfast": {
        "gle": ["Béal Feirste"],
        "gla": ["Béal Feirste"],
        "sco": ["Bilfawst"],
        "lat": ["Belfastium"],
    },
    "Derry": {
        "gle": ["Doire", "Doire Cholmcille"],
        "gla": ["Doire"],
        "sco": ["Derry", "Lunnonderry"],
        "eng": ["Londonderry"],
    },
    "Lisburn": {
        "gle": ["Lios na gCearrbhach"],
        "sco": ["Lisburn"],
    },
    "Newry": {
        "gle": ["Iúr Cinn Trá", "An tIúr"],
        "sco": ["Newry"],
    },
    "Craigavon": {
        "gle": ["Craigavon"],
    },
    "Ballymena": {
        "gle": ["An Baile Meánach"],
        "sco": ["Ballymena"],
    },
    "Coleraine": {
        "gle": ["Cúil Raithin"],
        "sco": ["Coleraine"],
    },
    "Omagh": {
        "gle": ["An Ómaigh"],
    },
    "Enniskillen": {
        "gle": ["Inis Ceithleann"],
    },
    "Strabane": {
        "gle": ["An Srath Bán"],
    },
    "Larne": {
        "gle": ["Latharna"],
        "sco": ["Larne"],
    },
    "Armagh": {
        "gle": ["Ard Mhacha"],
        "lat": ["Armachanum"],
    },
    "Downpatrick": {
        "gle": ["Dún Pádraig"],
    },
    "Carrickfergus": {
        "gle": ["Carraig Fhearghais"],
        "sco": ["Carrickfergus"],
        "non": ["Strangford"],
    },
    "Cookstown": {
        "gle": ["An Chorr Chríochach"],
    },
    "Dungannon": {
        "gle": ["Dún Geanainn"],
    },
}


# ---------------------------------------------------------------------------
# Wikidata SPARQL query
# ---------------------------------------------------------------------------
def query_wikidata_british_cities() -> dict[str, dict]:
    """Query Wikidata for British city data using VALUES-based lookup."""
    print("Querying Wikidata SPARQL for British cities...")

    seen_qids: set[str] = set()
    all_qids: list[str] = []
    for _, _, _, qid, _ in BRITISH_CITIES:
        if qid not in seen_qids:
            seen_qids.add(qid)
            all_qids.append(qid)

    # Split into batches of 80 to avoid query size limits
    batches = [all_qids[i : i + 80] for i in range(0, len(all_qids), 80)]
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
            bd:serviceParam wikibase:language "en"
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
def fetch_nominatim_geometry(city_name: str, country: str = "United Kingdom") -> dict | None:
    """Fetch town boundary polygon from OSM Nominatim."""
    # Clean name for searching
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
    """Ingest all British cities and towns with comprehensive metadata."""
    # Deduplicate by QID
    seen_qids: set[str] = set()
    unique_cities = []
    for city_tuple in BRITISH_CITIES:
        qid = city_tuple[3]
        if qid not in seen_qids:
            seen_qids.add(qid)
            unique_cities.append(city_tuple)

    print(f"Ingesting {len(unique_cities)} British cities and towns")
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

    wikidata_lookup = query_wikidata_british_cities()
    print()

    print("Fetching geometry from OSM Nominatim...")
    geometries: dict[str, dict] = {}

    for i, (city, _region, _admin, _qid, _gn) in enumerate(unique_cities):
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
    skipped_existing = 0

    for city, region, admin_area, qid, geonames_id in unique_cities:
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

        alt_names = ALTERNATIVE_NAMES.get(city, {})
        geometry = geometries.get(city)
        population = wd.get("population")
        area_km2 = wd.get("area_km2")
        elevation = wd.get("elevation")
        gn_id = wd.get("geonames_id") or geonames_id

        # Place type classification
        if city == "London":
            place_type = "P.PPLC"
        elif city in ("Edinburgh", "Cardiff", "Belfast"):
            place_type = "P.PPLA"
        elif city in (
            "Birmingham",
            "Manchester",
            "Glasgow",
            "Leeds",
            "Sheffield",
            "Liverpool",
            "Bristol",
            "Aberdeen",
            "Dundee",
            "Swansea",
            "Newport",
            "Derry",
            "Inverness",
            "Stirling",
            "Perth",
            "Nottingham",
            "Leicester",
            "Coventry",
            "Newcastle upon Tyne",
            "Southampton",
            "Plymouth",
            "York",
            "Norwich",
            "Exeter",
            "Oxford",
            "Cambridge",
            "Bath",
            "Canterbury",
            "Winchester",
            "Carlisle",
            "Chester",
            "Lincoln",
            "Salisbury",
            "Worcester",
            "Hereford",
            "Wrexham",
            "Bangor",
            "Caernarfon",
            "Carmarthen",
            "Armagh",
            "Newry",
            "Lisburn",
        ):
            place_type = "P.PPLA2"
        else:
            place_type = "P.PPL"

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
            county=admin_area,
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

    # Stats
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

    # Regional breakdown
    regions: dict[str, int] = {}
    for r in signed_records:
        reg = r.get("region", "unknown")
        regions[reg] = regions.get(reg, 0) + 1

    print("\nBreakdown by constituent country:")
    for reg, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {reg}: {count}")


if __name__ == "__main__":
    main()
