"""Bridge between the git-native databank and the statistical test framework.

Loads JSONL records from the databank, filters by toponymic element,
and produces TestData arrays ready for statistical tests.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from toponymia.languages.base import BaseLanguageModule
from toponymia.pipelines.segment import SegmentationPipeline
from toponymia.statistics.base import PlaceData

logger = logging.getLogger(__name__)


def load_databank(
    databank_path: Path | None = None,
    country: str | None = None,
) -> list[dict[str, Any]]:
    """Load all records from the databank.

    Args:
        databank_path: Path to databank/places/ directory.
            Defaults to the project's databank/places/.
        country: Optional ISO country code to filter (e.g., 'NO').

    Returns:
        List of record dicts.
    """
    if databank_path is None:
        databank_path = Path(__file__).parent.parent.parent.parent / "databank" / "places"

    records: list[dict[str, Any]] = []

    if not databank_path.exists():
        logger.warning(f"Databank path does not exist: {databank_path}")
        return records

    # Iterate country directories
    for country_dir in sorted(databank_path.iterdir()):
        if not country_dir.is_dir():
            continue
        if country and country_dir.name != country:
            continue

        for jsonl_file in sorted(country_dir.glob("*.jsonl")):
            for line in jsonl_file.read_text().splitlines():
                line = line.strip()
                if line:
                    record = json.loads(line)
                    record["_country"] = country_dir.name
                    record["_source_file"] = str(jsonl_file.relative_to(databank_path))
                    records.append(record)

    logger.info(f"Loaded {len(records)} records from databank")
    return records


def build_test_data(
    records: list[dict[str, Any]],
    element: str,
    pipeline: SegmentationPipeline | None = None,
    signal_field: str | None = None,
    analyze_attestations: bool = True,
) -> PlaceData:
    """Build TestData arrays from databank records for a given toponymic element.

    Determines element_present by checking if the segmentation pipeline
    finds the specified element in any form of the place name.

    Args:
        records: List of databank record dicts (from load_databank).
        element: The toponymic element to test (e.g., 'heim', 'vik', 'nes').
        pipeline: SegmentationPipeline with registered language modules.
            If None, uses simple suffix string matching.
        signal_field: Optional field name for signal values (e.g., 'elevation').
        analyze_attestations: Whether to also check attestation forms.

    Returns:
        TestData ready for statistical tests.
    """
    coordinates = []
    element_present = []
    signal_values = [] if signal_field else None

    element_lower = element.lower()

    for record in records:
        lat = record.get("latitude")
        lon = record.get("longitude")
        if lat is None or lon is None:
            continue

        # Determine if element is present
        has_element = _check_element(record, element_lower, pipeline, analyze_attestations)

        coordinates.append([lon, lat])
        element_present.append(has_element)

        if signal_values is not None:
            val = record.get(signal_field)
            signal_values.append(float(val) if val is not None else 0.0)

    if not coordinates:
        return PlaceData(
            coordinates=np.empty((0, 2)),
            element_present=np.empty(0, dtype=bool),
            signal_values=np.empty(0) if signal_field else None,
            element_name=element,
        )

    return PlaceData(
        coordinates=np.array(coordinates),
        element_present=np.array(element_present, dtype=bool),
        signal_values=np.array(signal_values) if signal_values is not None else None,
        element_name=element,
    )


def _check_element(
    record: dict[str, Any],
    element: str,
    pipeline: SegmentationPipeline | None,
    analyze_attestations: bool,
) -> bool:
    """Check if a record contains the specified toponymic element."""
    forms = [record["name_form"]]
    if analyze_attestations:
        for att in record.get("attestations", []):
            form = att.get("form")
            if form and form not in forms:
                forms.append(form)

    if pipeline is not None:
        # Use segmentation pipeline for precise detection
        for form in forms:
            hyps = pipeline.segment(form)
            if hyps:
                for h in hyps:
                    for comp in h.components:
                        comp_key = (
                            comp.lemma.lower().lstrip("-") if comp.lemma else comp.component.lower()
                        )
                        if comp_key == element:
                            return True
    else:
        # Fallback: simple suffix/substring match
        for form in forms:
            if form.lower().endswith(element) or element in form.lower():
                return True

    return False


def get_element_summary(
    records: list[dict[str, Any]],
    pipeline: SegmentationPipeline,
    modules: list[BaseLanguageModule] | None = None,
) -> dict[str, int]:
    """Count occurrences of each detected element across all records.

    Useful for discovering which elements have enough data for testing.

    Args:
        records: Databank records.
        pipeline: Segmentation pipeline.
        modules: Optional modules for etymology lookup.

    Returns:
        Dict mapping element name -> count.
    """
    element_counts: dict[str, int] = {}

    for record in records:
        analysis = pipeline.segment_record(record)
        if analysis.best_hypothesis:
            for comp in analysis.best_hypothesis.components:
                key = comp.lemma.lower().lstrip("-") if comp.lemma else comp.component.lower()
                element_counts[key] = element_counts.get(key, 0) + 1

    return dict(sorted(element_counts.items(), key=lambda x: x[1], reverse=True))
