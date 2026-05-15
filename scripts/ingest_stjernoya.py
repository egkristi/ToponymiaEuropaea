#!/usr/bin/env python3
"""Ingest all place names for Stjernøya (Stierdná) in Alta kommune, Norway.

Sources:
- Kartverket SSR (Sentralt stedsnavnregister) - official Norwegian place names
- GeoNames - global geographic database
- Wikidata - linked open data

This script creates comprehensive records for all named features on and
around the island Stjernøya, including Norwegian and Northern Sami names,
geometry classification, and full metadata.
"""

import json
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from toponymia.pipelines.integrity import sign_record  # noqa: E402
from toponymia.pipelines.geometry_classify import (  # noqa: E402
    classify_geometry,
    get_geometry_status,
)

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
    return {
        f"_h3_r{r}": str(h3.latlng_to_cell(lat, lng, r)) for r in (7, 9, 11)
    }


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
# PLACE NAME DATA FOR STJERNØYA AND SURROUNDING FEATURES
# ===========================================================================

PLACES = [
    # -----------------------------------------------------------------------
    # 1. THE ISLAND ITSELF
    # -----------------------------------------------------------------------
    make_record(
        name_form="Stjernøya",
        name_normalized="stjernøya",
        latitude=70.31679,
        longitude=22.66326,
        source_id="kartverket:19466",
        place_type="Øy i sjø",
        language_code="nor",
        alternative_names={
            "nor": ["Stjernøy"],
            "sme": ["Stierdná", "Stierdna"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/19466",
        wikidata_qid="Q3084323",
        geonames_id=777475,
        area_km2=248.1,
        elevation=960.0,
        population=45,
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.66326, 70.31679],
                [22.76738, 70.24818],
                [22.90267, 70.24875],
                [22.63847, 70.31064],
                [22.8444, 70.27704],
                [22.65855, 70.30282],
                [22.79639, 70.25556],
                [22.6594, 70.30369],
                [22.90266, 70.24875],
                [22.9021, 70.27794],
                [22.65899, 70.30396],
                [22.68264, 70.2997],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 2. STRAITS / SOUNDS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Stjernsundet",
        name_normalized="stjernsundet",
        latitude=70.23793,
        longitude=22.71921,
        source_id="kartverket:383518",
        place_type="Fjord",
        language_code="nor",
        alternative_names={
            "nor": ["Stjernøysundet"],
            "sme": ["Joahkku", "Joakko"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/383518",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.71921, 70.23793],
                [22.71843, 70.23849],
                [22.87207, 70.23012],
                [22.46701, 70.27223],
                [22.47951, 70.27675],
                [22.39961, 70.26383],
                [22.29764, 70.28687],
                [22.61739, 70.23768],
                [22.38333, 70.28333],
            ],
        },
    ),
    make_record(
        name_form="Rognsundet",
        name_normalized="rognsundet",
        latitude=70.31601,
        longitude=22.99262,
        source_id="kartverket:201895",
        place_type="Sund i sjø",
        language_code="nor",
        alternative_names={
            "sme": ["Čoalmmenuorri", "Čoalmenouori"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/201895",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.99262, 70.31601],
                [23.0, 70.4],
                [22.97519, 70.32192],
                [23.04248, 70.29361],
                [23.05882, 70.27604],
                [23.10913, 70.26955],
                [23.02279, 70.31142],
                [22.95858, 70.33667],
                [22.81916, 70.34664],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 3. FJORDS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Store Kjerringfjorden",
        name_normalized="store kjerringfjorden",
        latitude=70.37025,
        longitude=22.70762,
        source_id="kartverket:869181",
        place_type="Fjord",
        language_code="nor",
        alternative_names={
            "nor": ["Kjerringfjorden, store"],
            "sme": ["Stuora Várjevuonna", "Stuora Várjevuotna", "Varjevuodna stuora"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/869181",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.70762, 70.37025],
                [22.69429, 70.41045],
            ],
        },
    ),
    make_record(
        name_form="Store Kvalfjorden",
        name_normalized="store kvalfjorden",
        latitude=70.32145,
        longitude=22.89823,
        source_id="kartverket:140913",
        place_type="Fjord",
        language_code="nor",
        alternative_names={
            "nor": ["Kvalfjord", "Kvalfjorden, store"],
            "sme": ["Bossovuonna", "Båssuvuodna", "Bossovuotna"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/140913",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.89823, 70.32145],
                [22.89822, 70.32146],
                [22.90314, 70.32339],
                [22.92758, 70.32637],
            ],
        },
    ),
    make_record(
        name_form="Lille Kvalfjorden",
        name_normalized="lille kvalfjorden",
        latitude=70.30089,
        longitude=22.9278,
        source_id="kartverket:626933",
        place_type="Fjord",
        language_code="nor",
        alternative_names={
            "sme": ["Geavlavuonna", "Gævlavuodna", "Geavlavuotna"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/626933",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.9278, 70.30089],
                [22.91804, 70.29472],
                [22.93621, 70.30763],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 4. SETTLEMENTS / VILLAGES
    # -----------------------------------------------------------------------
    make_record(
        name_form="Store Kvalfjord",
        name_normalized="store kvalfjord",
        latitude=70.31804,
        longitude=22.86834,
        source_id="kartverket:80908",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        alternative_names={
            "sme": ["Bossovuonna"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/80908",
    ),
    make_record(
        name_form="Lille Kvalfjord",
        name_normalized="lille kvalfjord",
        latitude=70.29002,
        longitude=22.90867,
        source_id="kartverket:383921",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/383921",
    ),
    make_record(
        name_form="Lillebukt",
        name_normalized="lillebukt",
        latitude=70.26368,
        longitude=22.62047,
        source_id="kartverket:141109",
        place_type="Bygdelag (bygd)",
        language_code="nor",
        alternative_names={
            "nor": ["Litlbukta", "Lillebukta"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/141109",
    ),
    make_record(
        name_form="Vinterset",
        name_normalized="vinterset",
        latitude=70.33779,
        longitude=22.84762,
        source_id="kartverket:444892",
        place_type="Bruk",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/444892",
    ),
    # -----------------------------------------------------------------------
    # 5. MOUNTAINS / HILLS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Store Kjerringfjordfjellet",
        name_normalized="store kjerringfjordfjellet",
        latitude=70.3808,
        longitude=22.67797,
        source_id="kartverket:930182",
        place_type="Fjell",
        language_code="nor",
        alternative_names={
            "nor": ["Kjerringfjordfjellet, store"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/930182",
        elevation=960.0,
    ),
    make_record(
        name_form="Kvalfjordfjell",
        name_normalized="kvalfjordfjell",
        latitude=70.32429,
        longitude=22.86765,
        source_id="kartverket:86839",
        place_type="Fjell",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/86839",
    ),
    make_record(
        name_form="Nordmannsnesfjell",
        name_normalized="nordmannsnesfjell",
        latitude=70.33498,
        longitude=22.86228,
        source_id="kartverket:747879",
        place_type="Fjell",
        language_code="nor",
        alternative_names={
            "sme": ["Dáččavárri", "Dažžavarri"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/747879",
    ),
    make_record(
        name_form="Kjerringfjordklubben",
        name_normalized="kjerringfjordklubben",
        latitude=70.38652,
        longitude=22.76952,
        source_id="kartverket:809193",
        place_type="Fjell",
        language_code="nor",
        alternative_names={
            "sme": ["Várjevuonneret"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/809193",
    ),
    # -----------------------------------------------------------------------
    # 6. VALLEYS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Kvalfjorddalen",
        name_normalized="kvalfjorddalen",
        latitude=70.30811,
        longitude=22.83694,
        source_id="kartverket:686912",
        place_type="Dal",
        language_code="nor",
        alternative_names={
            "nor": ["Store Kvalfjorddalen", "Kvalfjorddalen, store"],
            "sme": ["Bossovuonvággi", "Båssuvuonvaggi"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/686912",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.83694, 70.30811],
                [22.83694, 70.30811],
                [22.80008, 70.29186],
                [22.85989, 70.30893],
            ],
        },
    ),
    make_record(
        name_form="Lille Kvalfjorddalen",
        name_normalized="lille kvalfjorddalen",
        latitude=70.28305,
        longitude=22.87481,
        source_id="kartverket:445936",
        place_type="Dal",
        language_code="nor",
        alternative_names={
            "nor": ["Kvalfjorddalen, l"],
            "sme": ["Geavlavuonvággi", "Gævlavuonvaggi"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/445936",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.87481, 70.28305],
                [22.87481, 70.28305],
            ],
        },
    ),
    make_record(
        name_form="Kjerringfjorddalen",
        name_normalized="kjerringfjorddalen",
        latitude=70.31773,
        longitude=22.70406,
        source_id="kartverket:688158",
        place_type="Dal",
        language_code="nor",
        alternative_names={
            "sme": ["Várjevuonvággi"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/688158",
    ),
    make_record(
        name_form="Vintersetdalen",
        name_normalized="vintersetdalen",
        latitude=70.33359,
        longitude=22.85164,
        source_id="kartverket:626891",
        place_type="Dal",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/626891",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.85164, 70.33359],
                [22.85789, 70.32548],
                [22.85504, 70.3325],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 7. BAYS / COVES
    # -----------------------------------------------------------------------
    make_record(
        name_form="Store Kjerringfjordbotn",
        name_normalized="store kjerringfjordbotn",
        latitude=70.32466,
        longitude=22.70703,
        source_id="kartverket:323156",
        place_type="Vik i sjø",
        language_code="nor",
        alternative_names={
            "nor": ["Botn", "Kjerringfjordbotn, store"],
            "sme": ["Várjevuonbahta"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/323156",
    ),
    make_record(
        name_form="Lillebukta",
        name_normalized="lillebukta",
        latitude=70.26279,
        longitude=22.61984,
        source_id="kartverket:930104",
        place_type="Vik i sjø",
        language_code="nor",
        alternative_names={
            "sme": ["Unna Muotkkadagaš"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/930104",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.61984, 70.26279],
                [22.61983, 70.26279],
            ],
        },
    ),
    make_record(
        name_form="Gambukta",
        name_normalized="gambukta",
        latitude=70.33022,
        longitude=22.82874,
        source_id="kartverket:693814",
        place_type="Vik i sjø",
        language_code="nor",
        alternative_names={
            "sme": ["Goahtegohppi"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/693814",
    ),
    make_record(
        name_form="Pollen",
        name_normalized="pollen",
        latitude=70.33767,
        longitude=22.82841,
        source_id="kartverket:565888",
        place_type="Vik i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/565888",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.82841, 70.33767],
                [22.82815, 70.33939],
            ],
        },
    ),
    make_record(
        name_form="Pollen",
        name_normalized="pollen",
        latitude=70.34316,
        longitude=22.80058,
        source_id="kartverket:202150",
        place_type="Vik i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/202150",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.80058, 70.34316],
                [22.80999, 70.34411],
            ],
        },
    ),
    make_record(
        name_form="Vintersetbukta",
        name_normalized="vintersetbukta",
        latitude=70.33932,
        longitude=22.8521,
        source_id="kartverket:580148",
        place_type="Vik i sjø",
        language_code="nor",
        alternative_names={
            "sme": ["Gonagasgohppi"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/580148",
    ),
    # -----------------------------------------------------------------------
    # 8. CAPES / HEADLANDS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Stjernodden",
        name_normalized="stjernodden",
        latitude=70.26281,
        longitude=23.0041,
        source_id="kartverket:383551",
        place_type="Nes i sjø",
        language_code="nor",
        alternative_names={
            "nor": ["Stjernøyodden"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/383551",
    ),
    make_record(
        name_form="Nordmannsnes",
        name_normalized="nordmannsnes",
        latitude=70.34041,
        longitude=22.86934,
        source_id="kartverket:626903",
        place_type="Nes i sjø",
        language_code="nor",
        alternative_names={
            "sme": ["Dáččanjárga", "Dažžanjarga"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/626903",
        geometry={
            "type": "MultiPoint",
            "coordinates": [
                [22.86934, 70.34041],
                [22.86924, 70.33994],
            ],
        },
    ),
    make_record(
        name_form="Nordmannsneset",
        name_normalized="nordmannsneset",
        latitude=70.34049,
        longitude=23.29235,
        source_id="kartverket:94596",
        place_type="Nes i sjø",
        language_code="nor",
        alternative_names={
            "sme": ["Guovllasnjárga"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/94596",
    ),
    make_record(
        name_form="Kjerringfjordneset",
        name_normalized="kjerringfjordneset",
        latitude=70.29443,
        longitude=23.28013,
        source_id="kartverket:154612",
        place_type="Nes i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/154612",
    ),
    # -----------------------------------------------------------------------
    # 9. ISLETS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Stjernøyholmen",
        name_normalized="stjernøyholmen",
        latitude=70.26047,
        longitude=23.01619,
        source_id="kartverket:809948",
        place_type="Holme i sjø",
        language_code="nor",
        alternative_names={
            "nor": ["Stjernøyoddholmen"],
            "sme": ["Vinšasuolu", "Vinšasuolo"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/809948",
    ),
    # -----------------------------------------------------------------------
    # 10. LAKES / PONDS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Kvalfjorddalvatna",
        name_normalized="kvalfjorddalvatna",
        latitude=70.302,
        longitude=22.83521,
        source_id="kartverket:262933",
        place_type="Gruppe av vann",
        language_code="nor",
        alternative_names={
            "sme": ["Bossovuonjávrrit", "Båssuvuonjavrit"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/262933",
    ),
    make_record(
        name_form="Øvre Kvalfjordvannet",
        name_normalized="øvre kvalfjordvannet",
        latitude=70.29994,
        longitude=22.81656,
        source_id="kartverket:383111",
        place_type="Vann",
        language_code="nor",
        alternative_names={
            "sme": ["Bossovuohjávri"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/383111",
    ),
    make_record(
        name_form="Lillebuktvannet",
        name_normalized="lillebuktvannet",
        latitude=70.27642,
        longitude=22.61342,
        source_id="kartverket:202100",
        place_type="Vann",
        language_code="nor",
        alternative_names={
            "sme": ["Váttesjávri", "Vaddesjavri"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/202100",
    ),
    # -----------------------------------------------------------------------
    # 11. SHOALS / MARINE FEATURES
    # -----------------------------------------------------------------------
    make_record(
        name_form="Kvalfjordbåen",
        name_normalized="kvalfjordbåen",
        latitude=70.30338,
        longitude=22.94926,
        source_id="kartverket:398675",
        place_type="Grunne i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/398675",
    ),
    # -----------------------------------------------------------------------
    # 12. HILLSIDES / SLOPES
    # -----------------------------------------------------------------------
    make_record(
        name_form="Kvalfjordlien",
        name_normalized="kvalfjordlien",
        latitude=70.32407,
        longitude=22.88051,
        source_id="kartverket:86837",
        place_type="Li",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/86837",
    ),
    # -----------------------------------------------------------------------
    # 13. HARBORS / INFRASTRUCTURE
    # -----------------------------------------------------------------------
    make_record(
        name_form="Kvalfjordhamn",
        name_normalized="kvalfjordhamn",
        latitude=70.31694,
        longitude=22.86722,
        source_id="kartverket:874989",
        place_type="Havn",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/874989",
    ),
    make_record(
        name_form="Kvalfjord kai",
        name_normalized="kvalfjord kai",
        latitude=70.31911,
        longitude=22.87401,
        source_id="kartverket:1094046",
        place_type="Ferjekai",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/1094046",
    ),
    # -----------------------------------------------------------------------
    # 14. ROADS
    # -----------------------------------------------------------------------
    make_record(
        name_form="Kvalfjordveien",
        name_normalized="kvalfjordveien",
        latitude=70.31563,
        longitude=22.86358,
        source_id="kartverket:1055884",
        place_type="Adressenavn",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/1055884",
        geometry={
            "type": "MultiLineString",
            "coordinates": [
                [
                    [22.86358, 70.31563],
                    [22.86272, 70.31477],
                    [22.863, 70.31402],
                    [22.86294, 70.31371],
                    [22.86015, 70.31181],
                ],
                [
                    [22.86358, 70.31563],
                    [22.86439, 70.31528],
                    [22.86555, 70.31498],
                    [22.86649, 70.31456],
                    [22.86724, 70.31392],
                    [22.86743, 70.3135],
                    [22.86812, 70.31315],
                    [22.8696, 70.31312],
                    [22.87073, 70.31351],
                    [22.87359, 70.31395],
                ],
                [
                    [22.86823, 70.31804],
                    [22.86616, 70.31783],
                    [22.86514, 70.31755],
                    [22.86456, 70.31717],
                    [22.86486, 70.31674],
                ],
                [
                    [22.86823, 70.31804],
                    [22.86891, 70.31783],
                    [22.8709, 70.31751],
                    [22.87166, 70.31721],
                    [22.87289, 70.31705],
                    [22.8738, 70.3168],
                    [22.87433, 70.31649],
                    [22.87405, 70.31618],
                ],
                [
                    [22.87349, 70.31926],
                    [22.87148, 70.31885],
                    [22.87144, 70.31864],
                    [22.8688, 70.31822],
                    [22.86823, 70.31804],
                ],
            ],
        },
    ),
    make_record(
        name_form="Nordmannsnes",
        name_normalized="nordmannsnes",
        latitude=70.33867,
        longitude=22.86887,
        source_id="kartverket:1080659",
        place_type="Adressenavn",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/1080659",
    ),
    make_record(
        name_form="Gambukta",
        name_normalized="gambukta",
        latitude=70.33001,
        longitude=22.83058,
        source_id="kartverket:1080666",
        place_type="Adressenavn",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/1080666",
    ),
    make_record(
        name_form="Vinterset",
        name_normalized="vinterset",
        latitude=70.3379,
        longitude=22.84905,
        source_id="kartverket:1080663",
        place_type="Adressenavn",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/1080663",
    ),
    make_record(
        name_form="Pollen",
        name_normalized="pollen",
        latitude=70.34154,
        longitude=22.83153,
        source_id="kartverket:1080664",
        place_type="Adressenavn",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/1080664",
    ),
    make_record(
        name_form="Lillebukt",
        name_normalized="lillebukt",
        latitude=70.26004,
        longitude=22.63477,
        source_id="kartverket:1080651",
        place_type="Adressenavn",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/1080651",
        geometry={
            "type": "MultiLineString",
            "coordinates": [
                [
                    [22.63477, 70.26004],
                    [22.63553, 70.25998],
                    [22.63656, 70.26013],
                    [22.63728, 70.26017],
                    [22.63831, 70.25987],
                    [22.63998, 70.26],
                    [22.64397, 70.26167],
                ],
                [
                    [22.63235, 70.26028],
                    [22.63414, 70.25975],
                    [22.63454, 70.25979],
                    [22.63477, 70.26004],
                ],
                [
                    [22.61512, 70.26298],
                    [22.61645, 70.26364],
                    [22.61835, 70.2638],
                ],
                [
                    [22.62738, 70.2632],
                    [22.62864, 70.26279],
                    [22.62924, 70.26246],
                    [22.63149, 70.26055],
                    [22.6318, 70.26039],
                    [22.63235, 70.26028],
                ],
                [
                    [22.62374, 70.26351],
                    [22.62715, 70.26288],
                    [22.62768, 70.26264],
                ],
            ],
        },
    ),
    # -----------------------------------------------------------------------
    # 15. ADDITIONAL BAYS (on east/north side near Rognsundet)
    # -----------------------------------------------------------------------
    make_record(
        name_form="Gambukta",
        name_normalized="gambukta",
        latitude=70.36101,
        longitude=23.09386,
        source_id="kartverket:808007",
        place_type="Vik i sjø",
        language_code="nor",
        source_url="https://stadnamn.kartverket.no/fakta/808007",
    ),
    # -----------------------------------------------------------------------
    # 16. CHURCH
    # -----------------------------------------------------------------------
    make_record(
        name_form="Rognsund kirke",
        name_normalized="rognsund kirke",
        latitude=70.32686,
        longitude=23.04402,
        source_id="kartverket:882828",
        place_type="Kirke",
        language_code="nor",
        alternative_names={
            "nor": ["Rognsund"],
        },
        source_url="https://stadnamn.kartverket.no/fakta/882828",
    ),
]


def main():
    """Append Stjernøya records to the kartverket.jsonl databank file."""
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

    print(f"Added {len(new_records)} Stjernøya records to {OUTPUT_FILE}")
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

    sami_count = sum(
        1 for r in new_records if r.get("alternative_names", {}).get("sme")
    )
    print(f"\nRecords with Northern Sami names: {sami_count}")
    print(f"Records with geometry: {sum(1 for r in new_records if r.get('geometry'))}")


if __name__ == "__main__":
    main()
