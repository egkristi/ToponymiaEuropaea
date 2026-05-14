"""Tests for the databank → analysis bridge."""

import json
import tempfile
from pathlib import Path

import numpy as np

from toponymia.languages.old_norse import OldNorseModule
from toponymia.pipelines.analyze import build_test_data, get_element_summary, load_databank
from toponymia.pipelines.segment import SegmentationPipeline


def _make_pipeline() -> SegmentationPipeline:
    pipeline = SegmentationPipeline()
    pipeline.register_module(OldNorseModule())
    return pipeline


def _make_temp_databank(records: list[dict], country: str = "NO") -> Path:
    """Create a temporary databank directory with records."""
    tmp = Path(tempfile.mkdtemp())
    country_dir = tmp / country
    country_dir.mkdir(parents=True)
    jsonl_file = country_dir / "test.jsonl"
    jsonl_file.write_text("\n".join(json.dumps(r) for r in records))
    return tmp


class TestLoadDatabank:
    def test_load_from_real_databank(self):
        records = load_databank()
        assert len(records) >= 15  # NO (10) + FI (5)
        assert all("name_form" in r for r in records)
        assert all("_country" in r for r in records)

    def test_load_filter_by_country(self):
        records = load_databank(country="NO")
        assert len(records) == 10
        assert all(r["_country"] == "NO" for r in records)

    def test_load_nonexistent_path(self):
        records = load_databank(databank_path=Path("/nonexistent"))
        assert records == []

    def test_load_temp_databank(self):
        data = [
            {"name_form": "TestPlace", "latitude": 60.0, "longitude": 10.0, "source_id": "t1"},
        ]
        tmp = _make_temp_databank(data)
        records = load_databank(databank_path=tmp)
        assert len(records) == 1
        assert records[0]["name_form"] == "TestPlace"


class TestBuildTestData:
    def test_basic_element_detection(self):
        records = [
            {"name_form": "Trondheim", "latitude": 63.4, "longitude": 10.4, "source_id": "1"},
            {"name_form": "Narvik", "latitude": 68.4, "longitude": 16.5, "source_id": "2"},
            {"name_form": "Bergen", "latitude": 60.4, "longitude": 5.3, "source_id": "3"},
        ]
        pipeline = _make_pipeline()
        data = build_test_data(records, "heim", pipeline=pipeline)
        assert data.n_places == 3
        assert data.coordinates.shape == (3, 2)
        assert data.element_present.sum() == 1  # Only Trondheim has -heim
        assert data.element_name == "heim"

    def test_element_detection_vik(self):
        records = [
            {"name_form": "Narvik", "latitude": 68.4, "longitude": 16.5, "source_id": "1"},
            {"name_form": "Tromsø", "latitude": 69.6, "longitude": 19.0, "source_id": "2"},
            {"name_form": "Gjøvik", "latitude": 60.8, "longitude": 10.7, "source_id": "3"},
        ]
        pipeline = _make_pipeline()
        data = build_test_data(records, "vik", pipeline=pipeline)
        # Narvik and Gjøvik both end in -vik
        assert data.element_present.sum() == 2

    def test_attestation_based_detection(self):
        """Element found via attestation form, not modern name."""
        records = [
            {
                "name_form": "Bergen",
                "latitude": 60.4,
                "longitude": 5.3,
                "source_id": "1",
                "attestations": [
                    {"form": "Bjǫrgvin", "language_code": "non"},
                ],
            },
        ]
        pipeline = _make_pipeline()
        data = build_test_data(records, "vin", pipeline=pipeline)
        assert data.element_present[0]  # Found via Bjǫrgvin

    def test_attestation_disabled(self):
        """Without attestation analysis, Bergen doesn't match vin."""
        records = [
            {
                "name_form": "Bergen",
                "latitude": 60.4,
                "longitude": 5.3,
                "source_id": "1",
                "attestations": [
                    {"form": "Bjǫrgvin", "language_code": "non"},
                ],
            },
        ]
        pipeline = _make_pipeline()
        data = build_test_data(records, "vin", pipeline=pipeline, analyze_attestations=False)
        assert not data.element_present[0]

    def test_fallback_string_matching(self):
        """Without pipeline, uses simple suffix matching."""
        records = [
            {"name_form": "Trondheim", "latitude": 63.4, "longitude": 10.4, "source_id": "1"},
            {"name_form": "Bergen", "latitude": 60.4, "longitude": 5.3, "source_id": "2"},
        ]
        data = build_test_data(records, "heim", pipeline=None)
        assert data.element_present[0]  # Trondheim ends with 'heim'
        assert not data.element_present[1]

    def test_signal_field(self):
        records = [
            {
                "name_form": "Trondheim",
                "latitude": 63.4,
                "longitude": 10.4,
                "source_id": "1",
                "elevation": 50.0,
            },
            {
                "name_form": "Bergen",
                "latitude": 60.4,
                "longitude": 5.3,
                "source_id": "2",
                "elevation": 12.0,
            },
        ]
        data = build_test_data(records, "heim", pipeline=None, signal_field="elevation")
        assert data.signal_values is not None
        assert len(data.signal_values) == 2
        np.testing.assert_almost_equal(data.signal_values[0], 50.0)

    def test_empty_records(self):
        data = build_test_data([], "heim")
        assert data.n_places == 0
        assert data.coordinates.shape == (0, 2)

    def test_records_without_coordinates_skipped(self):
        records = [
            {"name_form": "NoCoords", "source_id": "1"},
            {"name_form": "Trondheim", "latitude": 63.4, "longitude": 10.4, "source_id": "2"},
        ]
        data = build_test_data(records, "heim")
        assert data.n_places == 1


class TestGetElementSummary:
    def test_element_summary_from_databank(self):
        pipeline = _make_pipeline()
        records = load_databank(country="NO")
        summary = get_element_summary(records, pipeline)
        assert isinstance(summary, dict)
        assert len(summary) > 0
        # ø, heim, vik, nes should all appear
        assert "ø" in summary or "heim" in summary

    def test_element_summary_custom_records(self):
        pipeline = _make_pipeline()
        records = [
            {"name_form": "Trondheim", "latitude": 63.4, "longitude": 10.4, "source_id": "1"},
            {"name_form": "Solheim", "latitude": 61.0, "longitude": 5.5, "source_id": "2"},
            {"name_form": "Narvik", "latitude": 68.4, "longitude": 16.5, "source_id": "3"},
        ]
        summary = get_element_summary(records, pipeline)
        assert summary.get("heim", 0) == 2
        assert summary.get("vik", 0) == 1
