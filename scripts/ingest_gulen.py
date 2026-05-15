#!/usr/bin/env python3
"""Ingest all place names for Gulen kommune in Vestland, Norway.

Sources:
- Kartverket SSR (Sentralt stedsnavnregister) - official Norwegian place names
- Wikidata - linked open data
- GeoNames - global geographic database

This script creates comprehensive records for all named features in and
around Gulen municipality, including settlements, islands, fjords,
mountains, lakes, churches, farms, and other geographic features.
Gulen is historically significant as the site of Gulatinget, one of
the oldest legislative assemblies in Norway.
"""

import json
import sys
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
OUTPUT_FILE = DATABANK_DIR / "places" / "NO" / "kartverket.jsonl"


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
    language_code: str = "nor",
    alternative_names: dict[str, list[str]] | None = None,
    source_dataset: str = "kartverket_ssr",
    source_license: str = "NLOD-2.0",
    source_url: str | None = None,
    elevation: float | None = None,
    is_current: bool = True,
    wikidata_qid: str | None = None,
    geonames_id: int | None = None,
    area_km2: float | None = None,
    population: int | None = None,
    geometry: dict | None = None,
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
        "country_code": "NO",
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
    if geometry:
        record["geometry"] = geometry
        record["_geometry_status"] = "defined"

    # Add H3 indices
    h3_indices = make_h3(latitude, longitude)
    record.update(h3_indices)

    return record


# ===========================================================================
# PLACE NAME DATA FOR GULEN KOMMUNE
# ===========================================================================

PLACES = [
    # -----------------------------------------------------------------------
    # 1. THE MUNICIPALITY / LANDSCAPE
    # -----------------------------------------------------------------------
    make_record(
        name_form="Gulen",
        name_normalized="gulen",
        latitude=60.98537,
        longitude=5.12325,
        source_id="kartverket:210813",
        place_type="Landskapsområde",
        language_code="nor",
        alternative_names={
            "nor": ["Guli"],
            "nno": ["Gulen"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/210813",
        wikidata_qid="Q217793",
        geonames_id=3154556,
        area_km2=599.41,
        population=2260,
    ),
    # -----------------------------------------------------------------------
    # 2. SETTLEMENTS / VILLAGES
    # -----------------------------------------------------------------------
    make_record(
        name_form="Eivindvik",
        name_normalized="eivindvik",
        latitude=60.98136,
        longitude=5.07497,
        source_id="kartverket:759646",
        place_type="Tettsted",
        language_code="nor",
        alternative_names={
            "nor": ["Evenvik", "Evindvig"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/759646",
        wikidata_qid="Q2622948",
    ),
    make_record(
        name_form="Brekke",
        name_normalized="brekke",
        latitude=61.02001,
        longitude=5.46153,
        source_id="kartverket:636967",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/636967",
        wikidata_qid="Q23765269",
    ),
    make_record(
        name_form="Byrknes",
        name_normalized="byrknes",
        latitude=60.89916,
        longitude=4.83785,
        source_id="kartverket:615444",
        place_type="Tettbebyggelse",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/615444",
        wikidata_qid="Q23763968",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.83785, 60.89916],
                [4.83871, 60.90033],
            ],
        },
    ),
    make_record(
        name_form="Dalsøyra",
        name_normalized="dalsøyra",
        latitude=60.93324,
        longitude=5.13556,
        source_id="kartverket:919851",
        place_type="Grend",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/919851",
        wikidata_qid="Q23764364",
    ),
    make_record(
        name_form="Mjømna",
        name_normalized="mjømna",
        latitude=60.91831,
        longitude=4.90454,
        source_id="kartverket:9467",
        place_type="Grend",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/9467",
    ),
    make_record(
        name_form="Nordgulen",
        name_normalized="nordgulen",
        latitude=61.00878,
        longitude=5.19499,
        source_id="kartverket:268049",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/268049",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.19499, 61.00878],
                [5.19247, 61.00694],
            ],
        },
    ),
    make_record(
        name_form="Austgulen",
        name_normalized="austgulen",
        latitude=60.98757,
        longitude=5.31632,
        source_id="kartverket:858153",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        alternative_names={
            "nor": ["Øvre Austgulen", "Nedre Austgulen"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/858153",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.31632, 60.98757],
                [5.32465, 60.99117],
                [5.31558, 60.98906],
            ],
        },
    ),
    make_record(
        name_form="Takle",
        name_normalized="takle",
        latitude=61.02683,
        longitude=5.37869,
        source_id="kartverket:268044",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/268044",
    ),
    make_record(
        name_form="Oppedal",
        name_normalized="oppedal",
        latitude=61.05686,
        longitude=5.51196,
        source_id="kartverket:273958",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        alternative_names={
            "nor": ["Ytre Oppedal"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/273958",
    ),
    make_record(
        name_form="Rutledal",
        name_normalized="rutledal",
        latitude=61.06712,
        longitude=5.18826,
        source_id="kartverket:85034",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        alternative_names={
            "nor": ["Rutledalen"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/85034",
    ),
    make_record(
        name_form="Ånneland",
        name_normalized="ånneland",
        latitude=60.88931,
        longitude=4.98096,
        source_id="kartverket:433400",
        place_type="Grend",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/433400",
    ),
    make_record(
        name_form="Sløvåg",
        name_normalized="sløvåg",
        latitude=60.85219,
        longitude=5.06881,
        source_id="kartverket:784876",
        place_type="Industriområde",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/784876",
        wikidata_qid="Q1773754",
    ),
    # -----------------------------------------------------------------------
    # 3. ISLANDS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Byrknesøyna",
        name_normalized="byrknesøyna",
        latitude=60.89393,
        longitude=4.88883,
        source_id="kartverket:676430",
        place_type="Øy i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/676430",
        wikidata_qid="Q3339553",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.88883, 60.89393],
                [4.89408, 60.87066],
                [4.88802, 60.89389],
                [4.88883, 60.89393],
            ],
        },
    ),
    make_record(
        name_form="Hisarøyna",
        name_normalized="hisarøyna",
        latitude=60.98621,
        longitude=4.97324,
        source_id="kartverket:796356",
        place_type="Øy i sjø",
        language_code="nor",
        alternative_names={
            "nor": ["Hiserøyna"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/796356",
        wikidata_qid="Q3339504",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.97324, 60.98621],
                [4.95013, 61.00054],
                [4.96939, 60.9879],
                [4.97324, 60.98621],
                [4.92279, 60.99702],
                [4.97313, 60.98618],
                [4.97322, 60.98605],
                [4.92278, 60.99702],
                [4.9734, 60.98616],
            ],
        },
    ),
    make_record(
        name_form="Sandøyna",
        name_normalized="sandøyna",
        latitude=60.89028,
        longitude=4.9988,
        source_id="kartverket:615425",
        place_type="Øy i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/615425",
        wikidata_qid="Q3339619",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.9988, 60.89028],
                [4.9988, 60.89028],
                [4.99052, 60.89694],
                [4.99839, 60.85978],
            ],
        },
    ),
    make_record(
        name_form="Mjømna",
        name_normalized="mjømna",
        latitude=60.91581,
        longitude=4.93543,
        source_id="kartverket:494431",
        place_type="Øy i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/494431",
        wikidata_qid="Q3339555",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.93542, 60.91581],
                [4.93542, 60.91581],
                [4.94325, 60.89246],
                [4.93108, 60.91138],
                [4.93253, 60.92836],
                [4.91374, 60.93278],
            ],
        },
    ),
    make_record(
        name_form="Guløyna",
        name_normalized="guløyna",
        latitude=60.96614,
        longitude=5.12056,
        source_id="kartverket:312725",
        place_type="Øy i sjø",
        language_code="nor",
        alternative_names={
            "nor": ["Guløy"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/312725",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.12056, 60.96614],
                [5.12056, 60.96614],
                [5.11541, 60.96669],
            ],
        },
    ),
    make_record(
        name_form="Røytinga",
        name_normalized="røytinga",
        latitude=60.86851,
        longitude=4.79855,
        source_id="kartverket:312417",
        place_type="Øy i sjø",
        language_code="nor",
        alternative_names={
            "nor": ["Røytingja"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/312417",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.79855, 60.86851],
                [4.79855, 60.86851],
                [4.79581, 60.86842],
                [4.79634, 60.86472],
                [4.81564, 60.86334],
                [4.79245, 60.87037],
            ],
        },
    ),
    make_record(
        name_form="Grima",
        name_normalized="grima",
        latitude=60.92609,
        longitude=4.8495,
        source_id="kartverket:190500",
        place_type="Øy i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/190500",
    ),
    make_record(
        name_form="Børholmen",
        name_normalized="børholmen",
        latitude=60.91798,
        longitude=4.82706,
        source_id="kartverket:91949",
        place_type="Holme i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/91949",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.82706, 60.91798],
                [4.82706, 60.91799],
                [4.82632, 60.91772],
            ],
        },
    ),
    make_record(
        name_form="Sandøyna",
        name_normalized="sandøyna",
        latitude=60.94241,
        longitude=4.95406,
        source_id="kartverket:571007",
        place_type="Holme i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/571007",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.95406, 60.94241],
                [4.95108, 60.94211],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 4. FJORDS AND SEAS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Gulafjorden",
        name_normalized="gulafjorden",
        latitude=60.96421,
        longitude=5.05661,
        source_id="kartverket:310296",
        place_type="Fjord",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/310296",
        wikidata_qid="Q3095498",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.05661, 60.96421],
                [5.09468, 60.9647],
                [5.04071, 60.96921],
                [5.04071, 60.96921],
            ],
        },
    ),
    make_record(
        name_form="Eidsfjorden",
        name_normalized="eidsfjorden",
        latitude=60.94187,
        longitude=5.12738,
        source_id="kartverket:8959",
        place_type="Fjord",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/8959",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.12738, 60.94187],
                [5.12215, 60.90196],
                [5.12378, 60.89151],
                [5.12321, 60.91522],
                [5.12215, 60.90197],
                [5.11998, 60.90056],
            ],
        },
    ),
    make_record(
        name_form="Sognesjøen",
        name_normalized="sognesjøen",
        latitude=61.07283,
        longitude=4.99257,
        source_id="kartverket:432638",
        place_type="Hav/sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/432638",
        wikidata_qid="Q2269752",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.99257, 61.07283],
                [4.67933, 60.96533],
                [4.75068, 60.97499],
                [4.92655, 61.03036],
                [5.10488, 61.09859],
                [5.18075, 61.13143],
                [4.89302, 61.02084],
                [4.89302, 61.02083],
                [4.93157, 61.03352],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 5. MOUNTAINS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Svadfjellet",
        name_normalized="svadfjellet",
        latitude=60.96433,
        longitude=5.57206,
        source_id="kartverket:676308",
        place_type="Fjell",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/676308",
        elevation=877.44,
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.57206, 60.96432],
                [5.56722, 60.96563],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 6. LAKES
    # -----------------------------------------------------------------------
    make_record(
        name_form="Dingevatnet",
        name_normalized="dingevatnet",
        latitude=61.03601,
        longitude=5.08778,
        source_id="kartverket:252423",
        place_type="Vann",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/252423",
        wikidata_qid="Q3416432",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.08778, 61.03601],
                [5.0856, 61.03651],
                [5.09784, 61.03599],
                [5.08894, 61.03881],
                [5.08108, 61.03944],
                [5.08476, 61.04167],
                [5.0856, 61.03651],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 7. CHURCHES
    # -----------------------------------------------------------------------
    make_record(
        name_form="Gulen kyrkje",
        name_normalized="gulen kyrkje",
        latitude=60.9808,
        longitude=5.07588,
        source_id="kartverket:249318",
        place_type="Kirke",
        language_code="nor",
        alternative_names={
            "nor": ["Gulen", "Eivindvik"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/249318",
        wikidata_qid="Q2595416",
    ),
    make_record(
        name_form="Brekke kyrkje",
        name_normalized="brekke kyrkje",
        latitude=61.01931,
        longitude=5.46013,
        source_id="kartverket:615928",
        place_type="Kirke",
        language_code="nor",
        alternative_names={
            "nor": ["Brekke"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/615928",
        wikidata_qid="Q4082476",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.46013, 61.01931],
                [5.46013, 61.0193],
                [5.46033, 61.01976],
            ],
        },
    ),
    make_record(
        name_form="Mjømna kyrkje",
        name_normalized="mjømna kyrkje",
        latitude=60.92206,
        longitude=4.90094,
        source_id="kartverket:191469",
        place_type="Kirke",
        language_code="nor",
        alternative_names={
            "nor": ["Mjømna"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/191469",
        wikidata_qid="Q12006974",
    ),
    # -----------------------------------------------------------------------
    # 8. HISTORIC / CULTURAL SITES
    # -----------------------------------------------------------------------
    make_record(
        name_form="Floli",
        name_normalized="floli",
        latitude=60.97126,
        longitude=5.12062,
        source_id="kartverket:918164",
        place_type="Gard",
        language_code="nor",
        alternative_names={
            "nor": ["Flolid"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/918164",
    ),
    make_record(
        name_form="Skjerjehamn",
        name_normalized="skjerjehamn",
        latitude=60.94224,
        longitude=4.95649,
        source_id="kartverket:459216",
        place_type="Vik i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/459216",
    ),
    # -----------------------------------------------------------------------
    # 9. TRANSPORT INFRASTRUCTURE
    # -----------------------------------------------------------------------
    make_record(
        name_form="Rutledal ferjekai",
        name_normalized="rutledal ferjekai",
        latitude=61.07435,
        longitude=5.18933,
        source_id="kartverket:349463",
        place_type="Ferjekai",
        language_code="nor",
        alternative_names={
            "nor": ["Rutledal"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/349463",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [5.18933, 61.07435],
                [5.18933, 61.07435],
                [5.18935, 61.07435],
                [5.18934, 61.07435],
                [5.18771, 61.07464],
            ],
        },
    ),
    make_record(
        name_form="Dingenes lykt",
        name_normalized="dingenes lykt",
        latitude=61.03439,
        longitude=5.02138,
        source_id="kartverket:555392",
        place_type="Fyrlykt",
        language_code="nor",
        alternative_names={
            "nor": ["Dingenes"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/555392",
    ),
    # -----------------------------------------------------------------------
    # 10. FARMS (GARD / NAVNEGARD / BRUK) - HISTORICALLY SIGNIFICANT
    # -----------------------------------------------------------------------
    make_record(
        name_form="Eivindvik",
        name_normalized="eivindvik",
        latitude=60.98139,
        longitude=5.07284,
        source_id="kartverket:974718",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/974718",
    ),
    make_record(
        name_form="Verkland",
        name_normalized="verkland",
        latitude=60.95854,
        longitude=5.4215,
        source_id="kartverket:129816",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/129816",
    ),
    make_record(
        name_form="Dingja",
        name_normalized="dingja",
        latitude=61.02556,
        longitude=5.05337,
        source_id="kartverket:130420",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/130420",
    ),
    make_record(
        name_form="Halsvika",
        name_normalized="halsvika",
        latitude=60.84984,
        longitude=5.09936,
        source_id="kartverket:433508",
        place_type="Gard",
        language_code="nor",
        alternative_names={
            "nor": ["Halsvik"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/433508",
    ),
    make_record(
        name_form="Skjerjehamn",
        name_normalized="skjerjehamn",
        latitude=60.93948,
        longitude=4.96289,
        source_id="kartverket:494243",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/494243",
    ),
    make_record(
        name_form="Brossvika",
        name_normalized="brossvika",
        latitude=61.06953,
        longitude=5.14447,
        source_id="kartverket:312583",
        place_type="Gard",
        language_code="nor",
        alternative_names={
            "nor": ["Brosvik"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/312583",
    ),
    make_record(
        name_form="Vilsvika",
        name_normalized="vilsvika",
        latitude=60.98041,
        longitude=4.95608,
        source_id="kartverket:249336",
        place_type="Gard",
        language_code="nor",
        alternative_names={
            "nor": ["Vilsvik"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/249336",
    ),
    make_record(
        name_form="Blidensol",
        name_normalized="blidensol",
        latitude=60.93974,
        longitude=4.95936,
        source_id="kartverket:8307",
        place_type="Bruk",
        language_code="nor",
        alternative_names={
            "nor": ["Blidnesol"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/8307",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [4.95936, 60.93974],
                [4.95936, 60.93975],
                [4.9585, 60.93958],
            ],
        },
    ),
    make_record(
        name_form="Berge",
        name_normalized="berge",
        latitude=60.93909,
        longitude=5.14221,
        source_id="kartverket:493841",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/493841",
    ),
    make_record(
        name_form="Eide",
        name_normalized="eide",
        latitude=60.86404,
        longitude=5.11451,
        source_id="kartverket:797984",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/797984",
    ),
    make_record(
        name_form="Glenja",
        name_normalized="glenja",
        latitude=60.89067,
        longitude=5.11546,
        source_id="kartverket:797949",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/797949",
    ),
    make_record(
        name_form="Høyvika",
        name_normalized="høyvika",
        latitude=60.87795,
        longitude=5.13511,
        source_id="kartverket:736996",
        place_type="Navnegard",
        language_code="nor",
        alternative_names={
            "nor": ["Høyvik"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/736996",
    ),
    make_record(
        name_form="Grinde",
        name_normalized="grinde",
        latitude=60.9063,
        longitude=5.13824,
        source_id="kartverket:129932",
        place_type="Navnegard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/129932",
    ),
    make_record(
        name_form="Nordgulen",
        name_normalized="nordgulen",
        latitude=61.00916,
        longitude=5.19721,
        source_id="kartverket:9873",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/9873",
    ),
    make_record(
        name_form="Austgulen",
        name_normalized="austgulen",
        latitude=60.98945,
        longitude=5.32068,
        source_id="kartverket:974710",
        place_type="Navnegard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/974710",
    ),
    make_record(
        name_form="Ånneland",
        name_normalized="ånneland",
        latitude=60.88704,
        longitude=4.97807,
        source_id="kartverket:267057",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/267057",
    ),
    make_record(
        name_form="Grima",
        name_normalized="grima",
        latitude=60.9312,
        longitude=4.83609,
        source_id="kartverket:190257",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/190257",
    ),
    make_record(
        name_form="Børholmen",
        name_normalized="børholmen",
        latitude=60.91814,
        longitude=4.82759,
        source_id="kartverket:974728",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/974728",
    ),
    make_record(
        name_form="Mjømna",
        name_normalized="mjømna",
        latitude=60.91855,
        longitude=4.90355,
        source_id="kartverket:974725",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/974725",
    ),
    make_record(
        name_form="Byrknes",
        name_normalized="byrknes",
        latitude=60.89702,
        longitude=4.84001,
        source_id="kartverket:974727",
        place_type="Gard",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/974727",
    ),
]


def main():
    """Append Gulen records to the kartverket.jsonl databank file."""
    # Check for duplicates against existing records
    existing_ids: set[str] = set()
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                existing_ids.add(rec.get("source_id", ""))

    # Sign and append new records
    new_records = []
    skipped = 0
    for record in PLACES:
        if record["source_id"] in existing_ids:
            skipped += 1
            continue
        signed = sign_record(record)
        new_records.append(signed)

    if not new_records:
        print(f"No new records to add (all {len(PLACES)} already exist).")
        return

    # Append to file
    with OUTPUT_FILE.open("a") as f:
        for record in new_records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"Added {len(new_records)} Gulen records to {OUTPUT_FILE}")
    if skipped:
        print(f"  (skipped {skipped} already existing)")

    # Summary
    types: dict[str, int] = {}
    for r in new_records:
        t = r.get("place_type", "unknown")
        types[t] = types.get(t, 0) + 1

    print("\nBreakdown by place type:")
    for t, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {count}")

    print(f"\nRecords with geometry: {sum(1 for r in new_records if r.get('geometry'))}")
    print(f"Records with Wikidata QID: {sum(1 for r in new_records if r.get('wikidata_qid'))}")


if __name__ == "__main__":
    main()
