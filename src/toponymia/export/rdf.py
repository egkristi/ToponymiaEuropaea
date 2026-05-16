"""RDF/Turtle export from Toponymia Europaea databank.

Maps databank records to Linked Open Data using:
- GeoSPARQL for spatial features
- SKOS for the name type ontology
- Dublin Core for metadata
- Schema.org for place properties
- owl:sameAs for Wikidata/GeoNames cross-references
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

# Namespace definitions
TE = Namespace("https://toponymia-europaea.org/place/")
TE_ONTO = Namespace("https://toponymia-europaea.org/ontology/")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
SF = Namespace("http://www.opengis.net/ont/sf#")
SCHEMA = Namespace("https://schema.org/")
GEONAMES = Namespace("https://sws.geonames.org/")
WD = Namespace("http://www.wikidata.org/entity/")
PLEIADES = Namespace("https://pleiades.stoa.org/places/")

# GeoNames feature class to schema.org type mapping
_FEATURE_TYPE_MAP: dict[str, URIRef] = {
    "P": SCHEMA.City,
    "T": SCHEMA.Landform,
    "H": SCHEMA.BodyOfWater,
    "S": SCHEMA.LandmarksOrHistoricalBuildings,
    "L": SCHEMA.AdministrativeArea,
    "A": SCHEMA.AdministrativeArea,
    "R": SCHEMA.Place,
    "V": SCHEMA.Place,
    "U": SCHEMA.Place,
}


def _record_uri(record: dict[str, Any]) -> URIRef:
    """Generate a stable URI for a databank record."""
    source_id = record.get("source_id", "")
    country = record.get("country_code", "XX")
    # Use source_id hash for stable URIs
    safe_id = source_id.replace(":", "_").replace("/", "_")
    return TE[f"{country}/{safe_id}"]


def _add_record_to_graph(g: Graph, record: dict[str, Any]) -> None:
    """Convert a single databank record to RDF triples."""
    uri = _record_uri(record)

    # Type assertions
    g.add((uri, RDF.type, GEO.Feature))
    place_type = record.get("place_type", "")
    feature_class = place_type.split(".")[0] if "." in place_type else place_type
    schema_type = _FEATURE_TYPE_MAP.get(feature_class, SCHEMA.Place)
    g.add((uri, RDF.type, schema_type))

    # Name properties
    name_form = record.get("name_form", "")
    lang_code = record.get("language_code", "")
    if name_form:
        g.add((uri, RDFS.label, Literal(name_form, lang=lang_code or None)))
        g.add((uri, SCHEMA.name, Literal(name_form, lang=lang_code or None)))

    # Alternative names
    alt_names = record.get("alternative_names", {})
    if isinstance(alt_names, dict):
        for lang, names in alt_names.items():
            # Validate language tag: must be 2-3 letter ASCII code
            is_valid_tag = 2 <= len(lang) <= 3 and lang.isascii() and lang.isalpha()
            for alt_name in names:
                if is_valid_tag:
                    g.add((uri, SCHEMA.alternateName, Literal(alt_name, lang=lang)))
                else:
                    g.add((uri, SCHEMA.alternateName, Literal(alt_name)))

    # Spatial properties (GeoSPARQL)
    lat = record.get("latitude")
    lon = record.get("longitude")
    if lat is not None and lon is not None:
        geom_node = BNode()
        g.add((uri, GEO.hasGeometry, geom_node))
        g.add((geom_node, RDF.type, SF.Point))
        wkt = f"POINT({lon} {lat})"
        g.add((geom_node, GEO.asWKT, Literal(wkt, datatype=GEO.wktLiteral)))
        g.add((uri, SCHEMA.latitude, Literal(lat, datatype=XSD.double)))
        g.add((uri, SCHEMA.longitude, Literal(lon, datatype=XSD.double)))

    # Elevation
    elevation = record.get("elevation")
    if elevation is not None:
        g.add((uri, SCHEMA.elevation, Literal(elevation, datatype=XSD.double)))

    # Country
    country_code = record.get("country_code")
    if country_code:
        g.add((uri, SCHEMA.addressCountry, Literal(country_code)))

    # Feature type from GeoNames
    if place_type:
        g.add((uri, TE_ONTO.placeType, Literal(place_type)))

    # Cross-references (owl:sameAs)
    geonames_id = record.get("geonames_id")
    if geonames_id:
        g.add((uri, OWL.sameAs, GEONAMES[str(geonames_id) + "/"]))

    wikidata_qid = record.get("wikidata_qid")
    if wikidata_qid:
        g.add((uri, OWL.sameAs, WD[wikidata_qid]))

    # Source provenance
    source_url = record.get("source_url")
    if source_url:
        g.add((uri, DCTERMS.source, URIRef(source_url)))

    source_license = record.get("source_license")
    if source_license:
        g.add((uri, DCTERMS.license, Literal(source_license)))

    # Topographic metrics (if present)
    prominence = record.get("prominence_m")
    if prominence is not None:
        g.add((uri, TE_ONTO.prominence_m, Literal(prominence, datatype=XSD.double)))

    isolation = record.get("isolation_km")
    if isolation is not None:
        g.add((uri, TE_ONTO.isolation_km, Literal(isolation, datatype=XSD.double)))

    mountain_range = record.get("mountain_range")
    if mountain_range:
        g.add((uri, TE_ONTO.mountainRange, Literal(mountain_range)))


def export_databank_to_rdf(
    databank_path: Path,
    output_path: Path,
    *,
    country: str | None = None,
    rdf_format: str = "turtle",
) -> int:
    """Export databank records to RDF/Turtle format.

    Args:
        databank_path: Path to the databank directory.
        output_path: Path for the output file.
        country: Optional ISO country code filter.
        rdf_format: RDF serialization format (turtle, xml, n3, nt, jsonld).

    Returns:
        Number of records exported.
    """
    g = Graph()

    # Bind prefixes for readable Turtle output
    g.bind("te", TE)
    g.bind("te-onto", TE_ONTO)
    g.bind("geo", GEO)
    g.bind("sf", SF)
    g.bind("schema", SCHEMA)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("owl", OWL)
    g.bind("geonames", GEONAMES)
    g.bind("wd", WD)

    places_dir = databank_path / "places"
    if not places_dir.exists():
        return 0

    count = 0
    country_dirs = sorted(places_dir.iterdir())

    for country_dir in country_dirs:
        if not country_dir.is_dir():
            continue
        if country and country_dir.name.upper() != country.upper():
            continue

        for jsonl_file in sorted(country_dir.glob("*.jsonl")):
            with jsonl_file.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    _add_record_to_graph(g, record)
                    count += 1

    # Serialize
    output_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(output_path), format=rdf_format)
    return count
