#!/usr/bin/env python3
"""Full databank analysis across all perspectives.

Runs every available analysis tool against all records in the databank:
- Segmentation pipeline (Old Norse module)
- Cultural/Social perspective (ethnonyms, social class, personal names)
- Substrate detection (phonotactic anomaly)
- Cognate detection (Proto-Germanic sets)
- Historical period assignment
- Geometry validation
- Element discovery and counting

Results are exported to analysis_results/ as JSON.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from toponymia.languages.old_norse import OldNorseModule
from toponymia.nlp.cognates import COGNATE_SETS, CognateDetector
from toponymia.nlp.substrate import SubstrateDetector
from toponymia.perspectives.cultural import analyse_toponym
from toponymia.pipelines.analyze import get_element_summary, load_databank
from toponymia.pipelines.geometry_validate import validate_geometry
from toponymia.pipelines.segment import SegmentationPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Output directory
OUTPUT_DIR = Path("analysis_results")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_all_records() -> list[dict[str, Any]]:
    """Load all databank records."""
    logger.info("Loading databank...")
    records = load_databank()
    n_countries = len({r.get("_country", "?") for r in records})
    logger.info(f"Loaded {len(records)} records from {n_countries} countries")
    return records


def run_segmentation_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Run segmentation and element discovery."""
    logger.info("=== SEGMENTATION & ELEMENT DISCOVERY ===")
    pipeline = SegmentationPipeline()
    pipeline.register_module(OldNorseModule())

    # Element discovery
    summary = get_element_summary(records, pipeline)
    top_elements = sorted(summary.items(), key=lambda x: x[1], reverse=True)[:100]

    logger.info(f"Discovered {len(summary)} distinct elements")
    logger.info(f"Top 20 elements: {top_elements[:20]}")

    # Segment sample for detailed analysis
    segmented_sample = []
    sample_size = min(5000, len(records))
    for record in records[:sample_size]:
        try:
            result = pipeline.segment_record(record)
            if result.best_hypothesis:
                h = result.best_hypothesis
                segmented_sample.append(
                    {
                        "name": record.get("name_form", ""),
                        "country": record.get("_country", ""),
                        "language": h.language.classification if h.language else "",
                        "confidence": h.overall_confidence,
                        "components": [
                            {
                                "component": c.component,
                                "morph_type": c.morph_type,
                                "meaning": c.meaning,
                            }
                            for c in h.components
                        ],
                    }
                )
        except Exception:  # noqa: S112
            continue

    return {
        "total_elements_discovered": len(summary),
        "top_100_elements": [{"element": e, "count": c} for e, c in top_elements],
        "segmented_sample_size": len(segmented_sample),
        "segmented_sample": segmented_sample[:500],  # Cap output size
    }


def run_cultural_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Run cultural/social perspective on all names."""
    logger.info("=== CULTURAL/SOCIAL ANALYSIS ===")

    social_classes: Counter = Counter()
    ethnonyms: Counter = Counter()
    ownership_types: Counter = Counter()
    personal_names: list[dict[str, str]] = []
    country_ethnonyms: dict[str, Counter] = defaultdict(Counter)

    for record in records:
        name = record.get("name_form", "")
        if not name:
            continue

        features = analyse_toponym(name)

        for ind in features.social_indicators:
            social_classes[ind["class"]] += 1

        for ref in features.ethnonymic_refs:
            ethnonyms[ref["group"]] += 1
            country_ethnonyms[record.get("_country", "?")][ref["group"]] += 1

        if features.ownership_type:
            ownership_types[features.ownership_type] += 1

        if features.possible_personal_name:
            personal_names.append(
                {
                    "name": name,
                    "personal_element": features.personal_name_element,
                    "country": record.get("_country", ""),
                }
            )

    results = {
        "social_class_distribution": dict(social_classes.most_common()),
        "ethnonym_distribution": dict(ethnonyms.most_common()),
        "ownership_type_distribution": dict(ownership_types.most_common()),
        "personal_names_detected": len(personal_names),
        "personal_names_sample": personal_names[:200],
        "ethnonyms_by_country": {
            k: dict(v.most_common()) for k, v in sorted(country_ethnonyms.items())
        },
    }

    logger.info(f"Social class indicators: {dict(social_classes.most_common(10))}")
    logger.info(f"Ethnonyms: {dict(ethnonyms.most_common(10))}")
    logger.info(f"Personal names detected: {len(personal_names)}")
    return results


def run_substrate_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Run substrate detection on all names."""
    logger.info("=== SUBSTRATE DETECTION ===")

    detector = SubstrateDetector()
    detector.train()

    # Collect all unique name elements
    all_names = list({r.get("name_normalized", "") for r in records if r.get("name_normalized")})
    logger.info(f"Analyzing {len(all_names)} unique normalized names for substrate...")

    # Run corpus analysis
    corpus_results = detector.analyze_corpus(all_names, min_length=4)

    # Aggregate by origin
    origin_counts: Counter = Counter()
    sami_candidates: list[dict[str, Any]] = []
    finnic_candidates: list[dict[str, Any]] = []
    preie_candidates: list[dict[str, Any]] = []

    for name, candidates in corpus_results.items():
        for c in candidates:
            origin_counts[c.possible_origin] += 1
            entry = {
                "name": name,
                "element": c.element,
                "score": round(c.score, 3),
                "reasons": c.reasons,
            }
            if c.possible_origin == "sami":
                sami_candidates.append(entry)
            elif c.possible_origin == "finnic":
                finnic_candidates.append(entry)
            elif c.possible_origin == "pre-ie":
                preie_candidates.append(entry)

    # Sort by score (most anomalous first)
    sami_candidates.sort(key=lambda x: x["score"])
    finnic_candidates.sort(key=lambda x: x["score"])
    preie_candidates.sort(key=lambda x: x["score"])

    results = {
        "total_names_analyzed": len(all_names),
        "names_with_substrate_candidates": len(corpus_results),
        "origin_distribution": dict(origin_counts.most_common()),
        "sami_candidates_count": len(sami_candidates),
        "sami_candidates_top50": sami_candidates[:50],
        "finnic_candidates_count": len(finnic_candidates),
        "finnic_candidates_top50": finnic_candidates[:50],
        "preie_candidates_count": len(preie_candidates),
        "preie_candidates_top50": preie_candidates[:50],
    }

    logger.info(f"Substrate candidates: {dict(origin_counts.most_common())}")
    logger.info(
        f"Sami: {len(sami_candidates)}, Finnic: {len(finnic_candidates)},"
        f" Pre-IE: {len(preie_candidates)}"
    )
    return results


def run_cognate_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Run cognate detection across all names."""
    logger.info("=== COGNATE DETECTION ===")

    detector = CognateDetector(cognate_sets=COGNATE_SETS)
    pipeline = SegmentationPipeline()
    pipeline.register_module(OldNorseModule())

    cognate_hits: Counter = Counter()
    proto_form_counts: Counter = Counter()
    cognate_by_country: dict[str, Counter] = defaultdict(Counter)
    examples: list[dict[str, Any]] = []

    sample_size = min(10000, len(records))
    for record in records[:sample_size]:
        name = record.get("name_form", "")
        lang = record.get("language_code", "")
        country = record.get("_country", "")
        if not name:
            continue

        try:
            result = pipeline.segment_record(record)
            if not result.best_hypothesis:
                continue

            morphemes = [c.component for c in result.best_hypothesis.components]
            matches = detector.find_cognates_for_name(morphemes, language=lang)

            for morpheme, cognate_matches in matches.items():
                for match in cognate_matches:
                    cognate_hits[match.proto_form] += 1
                    proto_form_counts[match.meaning] += 1
                    cognate_by_country[country][match.proto_form] += 1

                    if len(examples) < 500:
                        examples.append(
                            {
                                "name": name,
                                "morpheme": morpheme,
                                "proto_form": match.proto_form,
                                "meaning": match.meaning,
                                "confidence": match.confidence,
                                "country": country,
                            }
                        )
        except Exception:  # noqa: S112
            continue

    results = {
        "records_analyzed": sample_size,
        "proto_form_frequency": dict(cognate_hits.most_common()),
        "meaning_frequency": dict(proto_form_counts.most_common()),
        "cognates_by_country": {
            k: dict(v.most_common(20)) for k, v in sorted(cognate_by_country.items())
        },
        "example_matches": examples[:200],
    }

    logger.info(f"Proto-form frequency: {dict(cognate_hits.most_common(15))}")
    return results


def run_historical_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Run historical period classification."""
    logger.info("=== HISTORICAL PERIOD ANALYSIS ===")

    from toponymia.perspectives.historical import _PERIOD_ELEMENTS

    period_counts: Counter = Counter()
    country_periods: dict[str, Counter] = defaultdict(Counter)
    period_examples: dict[str, list[str]] = defaultdict(list)

    for record in records:
        name = record.get("name_normalized", "")
        country = record.get("_country", "")
        if not name:
            continue

        for element, info in _PERIOD_ELEMENTS.items():
            if element in name:
                period = info["period"]
                period_counts[period] += 1
                country_periods[country][period] += 1
                if len(period_examples[period]) < 20:
                    period_examples[period].append(record.get("name_form", name))
                break  # One match per name

    results = {
        "period_distribution": dict(period_counts.most_common()),
        "periods_by_country": {
            k: dict(v.most_common()) for k, v in sorted(country_periods.items())
        },
        "period_examples": dict(period_examples),
    }

    logger.info(f"Period distribution: {dict(period_counts.most_common())}")
    return results


def run_geometry_validation(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate any geometry fields in records."""
    logger.info("=== GEOMETRY VALIDATION ===")

    total_with_geometry = 0
    valid_count = 0
    invalid_count = 0
    error_types: Counter = Counter()
    warning_types: Counter = Counter()

    for record in records:
        geom = record.get("geometry") or record.get("_geometry")
        if not geom or not isinstance(geom, dict):
            continue

        total_with_geometry += 1
        result = validate_geometry(geom)

        if result.valid:
            valid_count += 1
        else:
            invalid_count += 1
            for err in result.errors:
                error_types[err.split(":")[0] if ":" in err else err] += 1

        for w in result.warnings:
            warning_types[w.split(":")[0] if ":" in w else w] += 1

    results = {
        "total_records": len(records),
        "records_with_geometry": total_with_geometry,
        "valid_geometries": valid_count,
        "invalid_geometries": invalid_count,
        "error_types": dict(error_types.most_common(20)),
        "warning_types": dict(warning_types.most_common(20)),
    }

    logger.info(
        f"Geometry: {total_with_geometry} records, {valid_count} valid, {invalid_count} invalid"
    )
    return results


def run_country_statistics(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute per-country statistics."""
    logger.info("=== COUNTRY STATISTICS ===")

    country_counts: Counter = Counter()
    source_counts: Counter = Counter()
    place_types: Counter = Counter()
    language_codes: Counter = Counter()
    geometry_status: Counter = Counter()

    lat_sum: dict[str, float] = defaultdict(float)
    lon_sum: dict[str, float] = defaultdict(float)

    for record in records:
        country = record.get("_country", record.get("country_code", "?"))
        country_counts[country] += 1
        source_counts[record.get("source_dataset", "unknown")] += 1
        place_types[record.get("place_type", "unknown")] += 1
        language_codes[record.get("language_code", "unknown")] += 1
        geometry_status[record.get("_geometry_status", "unknown")] += 1

        lat = record.get("latitude", 0)
        lon = record.get("longitude", 0)
        if lat and lon:
            lat_sum[country] += lat
            lon_sum[country] += lon

    country_centroids = {}
    for country, count in country_counts.items():
        if count > 0 and lat_sum.get(country):
            country_centroids[country] = {
                "lat": round(lat_sum[country] / count, 4),
                "lon": round(lon_sum[country] / count, 4),
            }

    results = {
        "total_records": len(records),
        "records_by_country": dict(country_counts.most_common()),
        "records_by_source": dict(source_counts.most_common()),
        "place_types_top30": dict(place_types.most_common(30)),
        "language_codes": dict(language_codes.most_common()),
        "geometry_status": dict(geometry_status.most_common()),
        "country_centroids": country_centroids,
    }

    logger.info(f"Total: {len(records)} records across {len(country_counts)} countries")
    logger.info(f"By country: {dict(country_counts.most_common(10))}")
    return results


def run_acoustic_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect acoustic elements in names."""
    logger.info("=== ACOUSTIC PERSPECTIVE ===")

    acoustic_elements = {
        "ljom": "echo/resonance",
        "dur": "rumble/roar",
        "sus": "rushing/whisper",
        "brak": "crash/breaking",
        "gny": "din/noise",
        "song": "singing/melodic",
        "klukk": "gurgling",
        "tord": "thunder",
        "stil": "silence/calm",
    }

    hits: Counter = Counter()
    country_hits: dict[str, Counter] = defaultdict(Counter)
    examples: dict[str, list[str]] = defaultdict(list)

    for record in records:
        name = record.get("name_normalized", "")
        country = record.get("_country", "")
        if not name:
            continue

        for element in acoustic_elements:
            if element in name:
                hits[element] += 1
                country_hits[country][element] += 1
                if len(examples[element]) < 15:
                    examples[element].append(record.get("name_form", name))

    results = {
        "acoustic_element_counts": dict(hits.most_common()),
        "acoustic_by_country": {k: dict(v.most_common()) for k, v in sorted(country_hits.items())},
        "examples": dict(examples),
    }

    logger.info(f"Acoustic elements: {dict(hits.most_common())}")
    return results


def run_terrain_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect terrain elements and correlate with elevation."""
    logger.info("=== TERRAIN PERSPECTIVE ===")

    terrain_elements = {
        "berg": "mountain/cliff",
        "fjell": "mountain",
        "dal": "valley",
        "ås": "ridge/hill",
        "nes": "headland",
        "vik": "bay/inlet",
        "haug": "mound/hill",
        "flat": "flat/plain",
        "mo": "sandy plain",
        "myr": "bog/marsh",
        "sand": "sand",
        "stein": "stone/rock",
        "klippe": "cliff",
        "bakke": "slope/hill",
    }

    hits: Counter = Counter()
    elevation_by_element: dict[str, list[float]] = defaultdict(list)
    country_hits: dict[str, Counter] = defaultdict(Counter)

    for record in records:
        name = record.get("name_normalized", "")
        country = record.get("_country", "")
        elev = record.get("elevation") or record.get("_elevation_m")
        if not name:
            continue

        for element in terrain_elements:
            if element in name:
                hits[element] += 1
                country_hits[country][element] += 1
                if elev is not None and isinstance(elev, (int, float)):
                    elevation_by_element[element].append(elev)
                break  # One terrain element per name

    # Compute elevation statistics per element
    elevation_stats = {}
    for element, elevations in elevation_by_element.items():
        if elevations:
            elevations_sorted = sorted(elevations)
            n = len(elevations)
            elevation_stats[element] = {
                "count": n,
                "mean": round(sum(elevations) / n, 1),
                "median": round(elevations_sorted[n // 2], 1),
                "min": round(min(elevations), 1),
                "max": round(max(elevations), 1),
                "p25": round(elevations_sorted[n // 4], 1),
                "p75": round(elevations_sorted[3 * n // 4], 1),
            }

    results = {
        "terrain_element_counts": dict(hits.most_common()),
        "elevation_statistics": elevation_stats,
        "terrain_by_country": {k: dict(v.most_common(10)) for k, v in sorted(country_hits.items())},
    }

    logger.info(f"Terrain elements: {dict(hits.most_common(10))}")
    if elevation_stats:
        logger.info(
            f"Elevation stats: berg={elevation_stats.get('berg', {})},"
            f" dal={elevation_stats.get('dal', {})}"
        )
    return results


def run_religious_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect religious/theophoric elements."""
    logger.info("=== RELIGIOUS PERSPECTIVE ===")

    deity_elements = {
        "tor": "Thor (thunder god)",
        "odin": "Odin (allfather)",
        "frey": "Freyr (fertility)",
        "frøy": "Freyr (fertility, Norwegian)",
        "njord": "Njord (sea god)",
        "ull": "Ull (winter/archery god)",
        "ty": "Tyr (war god)",
        "balder": "Baldr (light god)",
        "hel": "Hel (death goddess)",
        "frøya": "Freyja (love/war goddess)",
    }

    cult_elements = {
        "hov": "temple/cult house",
        "horg": "outdoor altar/cairn",
        "ve": "sacred enclosure",
        "vi": "sacred enclosure",
        "lund": "sacred grove",
        "kirke": "church",
        "kyrka": "church (Swedish)",
        "kapell": "chapel",
    }

    deity_hits: Counter = Counter()
    cult_hits: Counter = Counter()
    country_deities: dict[str, Counter] = defaultdict(Counter)
    examples: dict[str, list[str]] = defaultdict(list)

    for record in records:
        name = record.get("name_normalized", "")
        country = record.get("_country", "")
        if not name:
            continue

        for element in deity_elements:
            if element in name:
                deity_hits[element] += 1
                country_deities[country][element] += 1
                if len(examples[f"deity:{element}"]) < 10:
                    examples[f"deity:{element}"].append(record.get("name_form", name))

        for element in cult_elements:
            if element in name:
                cult_hits[element] += 1
                if len(examples[f"cult:{element}"]) < 10:
                    examples[f"cult:{element}"].append(record.get("name_form", name))

    results = {
        "deity_element_counts": dict(deity_hits.most_common()),
        "cult_site_counts": dict(cult_hits.most_common()),
        "deities_by_country": {
            k: dict(v.most_common()) for k, v in sorted(country_deities.items())
        },
        "examples": dict(examples),
    }

    logger.info(f"Deity elements: {dict(deity_hits.most_common())}")
    logger.info(f"Cult site elements: {dict(cult_hits.most_common())}")
    return results


def run_ecological_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect ecological (flora/fauna) elements."""
    logger.info("=== ECOLOGICAL PERSPECTIVE ===")

    flora_elements = {
        "bjørk": "birch (Betula)",
        "bjork": "birch (Swedish)",
        "eik": "oak (Quercus)",
        "furu": "pine (Pinus)",
        "gran": "spruce (Picea)",
        "alm": "elm (Ulmus)",
        "ask": "ash (Fraxinus)",
        "lind": "linden (Tilia)",
        "or": "alder (Alnus)",
        "selje": "willow (Salix)",
        "hassel": "hazel (Corylus)",
        "lønn": "maple (Acer)",
        "rogn": "rowan (Sorbus)",
        "bøk": "beech (Fagus)",
    }

    fauna_elements = {
        "ulv": "wolf",
        "bjørn": "bear",
        "elg": "moose",
        "hjort": "deer",
        "rev": "fox",
        "ørn": "eagle",
        "hest": "horse",
        "ku": "cow",
        "sau": "sheep",
        "geit": "goat",
        "laks": "salmon",
        "sel": "seal",
        "hval": "whale",
        "rein": "reindeer",
    }

    flora_hits: Counter = Counter()
    fauna_hits: Counter = Counter()
    country_flora: dict[str, Counter] = defaultdict(Counter)
    country_fauna: dict[str, Counter] = defaultdict(Counter)

    for record in records:
        name = record.get("name_normalized", "")
        country = record.get("_country", "")
        if not name:
            continue

        for element in flora_elements:
            if element in name:
                flora_hits[element] += 1
                country_flora[country][element] += 1

        for element in fauna_elements:
            if element in name:
                fauna_hits[element] += 1
                country_fauna[country][element] += 1

    results = {
        "flora_counts": dict(flora_hits.most_common()),
        "fauna_counts": dict(fauna_hits.most_common()),
        "flora_by_country": {k: dict(v.most_common(10)) for k, v in sorted(country_flora.items())},
        "fauna_by_country": {k: dict(v.most_common(10)) for k, v in sorted(country_fauna.items())},
    }

    logger.info(f"Flora: {dict(flora_hits.most_common(10))}")
    logger.info(f"Fauna: {dict(fauna_hits.most_common(10))}")
    return results


def run_hydrological_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect hydrological elements."""
    logger.info("=== HYDROLOGICAL PERSPECTIVE ===")

    hydro_elements = {
        "elv": "river",
        "bekk": "stream/brook",
        "å": "river (small)",
        "vann": "lake/water",
        "vatn": "lake (Norwegian)",
        "sjø": "sea/lake",
        "tjern": "tarn/pond",
        "foss": "waterfall",
        "stryk": "rapids",
        "bru": "bridge",
        "sund": "strait/sound",
        "fjord": "fjord",
        "bukt": "bay",
        "kilde": "spring",
        "brønn": "well",
    }

    hits: Counter = Counter()
    country_hits: dict[str, Counter] = defaultdict(Counter)
    depth_by_element: dict[str, list[float]] = defaultdict(list)

    for record in records:
        name = record.get("name_normalized", "")
        country = record.get("_country", "")
        depth = record.get("_depth_m")
        if not name:
            continue

        for element in hydro_elements:
            if element in name:
                hits[element] += 1
                country_hits[country][element] += 1
                if depth is not None and isinstance(depth, (int, float)):
                    depth_by_element[element].append(depth)

    # Depth statistics
    depth_stats = {}
    for element, depths in depth_by_element.items():
        if depths:
            n = len(depths)
            depth_stats[element] = {
                "count": n,
                "mean_depth_m": round(sum(depths) / n, 1),
                "max_depth_m": round(max(depths), 1),
            }

    results = {
        "hydro_element_counts": dict(hits.most_common()),
        "hydro_by_country": {k: dict(v.most_common(10)) for k, v in sorted(country_hits.items())},
        "depth_statistics": depth_stats,
    }

    logger.info(f"Hydro elements: {dict(hits.most_common(10))}")
    return results


def run_medicinal_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect medicinal/healing elements."""
    logger.info("=== MEDICINAL PERSPECTIVE ===")

    healing_elements = {
        "bad": "bath/bathing place",
        "kilde": "healing spring",
        "brunn": "well/spring",
        "salt": "salt (mineral)",
        "hospital": "hospital",
        "spital": "hospital (medieval)",
        "apotek": "pharmacy",
        "lind": "linden (medicinal tree)",
        "humle": "hops (medicinal plant)",
        "einer": "juniper (medicinal)",
    }

    hits: Counter = Counter()
    country_hits: dict[str, Counter] = defaultdict(Counter)
    examples: dict[str, list[str]] = defaultdict(list)

    for record in records:
        name = record.get("name_normalized", "")
        country = record.get("_country", "")
        if not name:
            continue

        for element in healing_elements:
            if element in name:
                hits[element] += 1
                country_hits[country][element] += 1
                if len(examples[element]) < 10:
                    examples[element].append(record.get("name_form", name))

    results = {
        "medicinal_element_counts": dict(hits.most_common()),
        "medicinal_by_country": {k: dict(v.most_common()) for k, v in sorted(country_hits.items())},
        "examples": dict(examples),
    }

    logger.info(f"Medicinal elements: {dict(hits.most_common())}")
    return results


def main() -> None:
    """Run full analysis pipeline."""
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("TOPONYMIA EUROPAEA — FULL DATABANK ANALYSIS")
    logger.info("=" * 60)

    # Load all records
    records = load_all_records()

    # Run all analyses
    all_results: dict[str, Any] = {}

    # 1. Country statistics
    all_results["country_statistics"] = run_country_statistics(records)

    # 2. Segmentation & element discovery
    all_results["segmentation"] = run_segmentation_analysis(records)

    # 3. Cultural/Social perspective
    all_results["cultural_social"] = run_cultural_analysis(records)

    # 4. Substrate detection
    all_results["substrate_detection"] = run_substrate_analysis(records)

    # 5. Cognate detection
    all_results["cognate_detection"] = run_cognate_analysis(records)

    # 6. Historical period analysis
    all_results["historical_periods"] = run_historical_analysis(records)

    # 7. Geometry validation
    all_results["geometry_validation"] = run_geometry_validation(records)

    # 8. Terrain perspective
    all_results["terrain"] = run_terrain_analysis(records)

    # 9. Religious/theophoric perspective
    all_results["religious"] = run_religious_analysis(records)

    # 10. Ecological perspective
    all_results["ecological"] = run_ecological_analysis(records)

    # 11. Hydrological perspective
    all_results["hydrological"] = run_hydrological_analysis(records)

    # 12. Acoustic perspective
    all_results["acoustic"] = run_acoustic_analysis(records)

    # 13. Medicinal perspective
    all_results["medicinal"] = run_medicinal_analysis(records)

    # Save results
    elapsed = time.time() - start_time
    all_results["_metadata"] = {
        "analysis_date": "2026-05-16",
        "total_records": len(records),
        "elapsed_seconds": round(elapsed, 1),
        "perspectives_run": len(all_results) - 1,  # Exclude metadata
    }

    output_path = OUTPUT_DIR / "full_analysis.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    logger.info("=" * 60)
    logger.info(f"ANALYSIS COMPLETE in {elapsed:.1f}s")
    logger.info(f"Results written to: {output_path}")
    logger.info(f"Perspectives analyzed: {len(all_results) - 1}")
    logger.info("=" * 60)

    # Print summary
    print("\n\n=== ANALYSIS SUMMARY ===")
    print(f"Total records: {len(records)}")
    print(f"Countries: {all_results['country_statistics']['records_by_country']}")
    print(f"\nTop elements: {all_results['segmentation']['top_100_elements'][:15]}")
    print(f"\nSubstrate candidates: {all_results['substrate_detection']['origin_distribution']}")
    print(f"Cultural - Ethnonyms: {all_results['cultural_social']['ethnonym_distribution']}")
    print(f"Historical periods: {all_results['historical_periods']['period_distribution']}")
    print(f"Terrain elements: {all_results['terrain']['terrain_element_counts']}")
    print(f"Religious: {all_results['religious']['deity_element_counts']}")
    print(f"Ecological flora: {all_results['ecological']['flora_counts']}")
    print(f"Hydrological: {all_results['hydrological']['hydro_element_counts']}")


if __name__ == "__main__":
    main()
