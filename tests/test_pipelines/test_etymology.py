"""Tests for the Wikidata etymology extraction pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from toponymia.pipelines.etymology import (
    COUNTRY_QIDS,
    EtymologyRecord,
    _parse_etymology_binding,
    export_etymologies,
    extract_etymologies,
    match_to_databank,
)


@pytest.fixture
def sample_binding() -> dict:
    """A realistic SPARQL result binding for a Norwegian place."""
    return {
        "place": {"value": "http://www.wikidata.org/entity/Q585"},
        "placeLabel": {"value": "Oslo"},
        "coord": {"value": "Point(10.75 59.913889)"},
        "namedAfter": {"value": "http://www.wikidata.org/entity/Q17486662"},
        "namedAfterLabel": {"value": "Ló"},
        "namedAfterDescription": {"value": "river in Norway"},
    }


@pytest.fixture
def sample_databank(tmp_path: Path) -> Path:
    """Create a sample databank for matching tests."""
    places = tmp_path / "places" / "NO"
    places.mkdir(parents=True)
    records = [
        {"name": "Oslo", "country_code": "NO", "lat": 59.91, "lon": 10.75},
        {"name": "Bergen", "country_code": "NO", "lat": 60.39, "lon": 5.32},
        {"name": "Trondheim", "country_code": "NO", "lat": 63.43, "lon": 10.39},
    ]
    with (places / "geonames.jsonl").open("w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    return tmp_path


class TestParseEtymologyBinding:
    """Tests for SPARQL binding parsing."""

    def test_valid_binding(self, sample_binding: dict) -> None:
        """Test parsing a valid SPARQL binding."""
        record = _parse_etymology_binding(sample_binding, "NO")

        assert record is not None
        assert record.place_qid == "Q585"
        assert record.place_name == "Oslo"
        assert record.lat == pytest.approx(59.913889)
        assert record.lon == pytest.approx(10.75)
        assert record.named_after_qid == "Q17486662"
        assert record.named_after_label == "Ló"
        assert record.named_after_description == "river in Norway"
        assert record.country_code == "NO"

    def test_missing_coordinates(self) -> None:
        """Test that missing coordinates returns None."""
        binding = {
            "place": {"value": "http://www.wikidata.org/entity/Q585"},
            "placeLabel": {"value": "Oslo"},
            "coord": {"value": ""},
            "namedAfter": {"value": "http://www.wikidata.org/entity/Q123"},
            "namedAfterLabel": {"value": "Something"},
        }
        assert _parse_etymology_binding(binding, "NO") is None

    def test_label_is_qid(self) -> None:
        """Test that QID-as-label results are skipped."""
        binding = {
            "place": {"value": "http://www.wikidata.org/entity/Q585"},
            "placeLabel": {"value": "Q585"},
            "coord": {"value": "Point(10.75 59.91)"},
            "namedAfter": {"value": "http://www.wikidata.org/entity/Q123"},
            "namedAfterLabel": {"value": "Something"},
        }
        assert _parse_etymology_binding(binding, "NO") is None

    def test_invalid_coordinates(self) -> None:
        """Test that invalid WKT coordinates return None."""
        binding = {
            "place": {"value": "http://www.wikidata.org/entity/Q585"},
            "placeLabel": {"value": "Oslo"},
            "coord": {"value": "Point(invalid)"},
            "namedAfter": {"value": "http://www.wikidata.org/entity/Q123"},
            "namedAfterLabel": {"value": "Something"},
        }
        assert _parse_etymology_binding(binding, "NO") is None


class TestExtractEtymologies:
    """Tests for the extraction pipeline (mocked network)."""

    def test_unknown_country(self) -> None:
        """Test that unknown country returns empty list."""
        result = extract_etymologies("XX")
        assert result == []

    @patch("toponymia.pipelines.etymology.execute_sparql")
    def test_successful_extraction(self, mock_sparql: object, sample_binding: dict) -> None:
        """Test successful etymology extraction."""
        mock_sparql.return_value = [sample_binding]  # type: ignore[attr-defined]

        results = extract_etymologies("NO", limit=100)

        assert len(results) == 1
        assert results[0].place_name == "Oslo"
        assert results[0].named_after_label == "Ló"

    @patch("toponymia.pipelines.etymology.execute_sparql")
    def test_empty_results(self, mock_sparql: object) -> None:
        """Test empty SPARQL results."""
        mock_sparql.return_value = []  # type: ignore[attr-defined]

        results = extract_etymologies("NO")
        assert results == []


class TestMatchToDatabank:
    """Tests for matching etymology to databank records."""

    def test_match_by_name_and_coords(self, sample_databank: Path) -> None:
        """Test matching etymology records to databank places."""
        etymology_records = [
            EtymologyRecord(
                place_qid="Q585",
                place_name="Oslo",
                lat=59.91,
                lon=10.75,
                named_after_qid="Q17486662",
                named_after_label="Ló",
                named_after_description="river in Norway",
                country_code="NO",
            )
        ]

        matched = match_to_databank(etymology_records, sample_databank, distance_threshold_m=1000)

        assert len(matched) == 1
        assert matched[0]["name"] == "Oslo"
        assert matched[0]["_etymology_qid"] == "Q17486662"
        assert matched[0]["_etymology_label"] == "Ló"

    def test_no_match_far_coordinates(self, sample_databank: Path) -> None:
        """Test that distant coordinates don't match."""
        etymology_records = [
            EtymologyRecord(
                place_qid="Q585",
                place_name="Oslo",
                lat=60.5,  # Far from actual Oslo
                lon=10.75,
                named_after_qid="Q17486662",
                named_after_label="Ló",
                country_code="NO",
            )
        ]

        matched = match_to_databank(etymology_records, sample_databank, distance_threshold_m=1000)
        assert len(matched) == 0

    def test_no_match_different_name(self, sample_databank: Path) -> None:
        """Test that different names don't match."""
        etymology_records = [
            EtymologyRecord(
                place_qid="Q999",
                place_name="Stavanger",
                lat=59.91,
                lon=10.75,
                named_after_qid="Q123",
                named_after_label="Something",
                country_code="NO",
            )
        ]

        matched = match_to_databank(etymology_records, sample_databank, distance_threshold_m=1000)
        assert len(matched) == 0


class TestExportEtymologies:
    """Tests for JSONL export."""

    def test_export(self, tmp_path: Path) -> None:
        """Test exporting etymology records to JSONL."""
        records = [
            EtymologyRecord(
                place_qid="Q585",
                place_name="Oslo",
                lat=59.91,
                lon=10.75,
                named_after_qid="Q17486662",
                named_after_label="Ló",
                named_after_description="river in Norway",
                country_code="NO",
            ),
            EtymologyRecord(
                place_qid="Q25416",
                place_name="Trondheim",
                lat=63.43,
                lon=10.39,
                named_after_qid="Q3415092",
                named_after_label="Nidaros",
                country_code="NO",
            ),
        ]

        output = tmp_path / "etymologies.jsonl"
        count = export_etymologies(records, output)

        assert count == 2
        assert output.exists()

        lines = output.read_text().strip().split("\n")
        assert len(lines) == 2

        first = json.loads(lines[0])
        assert first["place_name"] == "Oslo"
        assert first["named_after_label"] == "Ló"


class TestCountryMapping:
    """Tests for country QID mappings."""

    def test_nordic_countries_mapped(self) -> None:
        """Verify all Nordic countries have QID mappings."""
        for code in ("NO", "SE", "DK", "FI", "IS"):
            assert code in COUNTRY_QIDS

    def test_etymology_record_to_dict(self) -> None:
        """Test EtymologyRecord serialization."""
        rec = EtymologyRecord(
            place_qid="Q585",
            place_name="Oslo",
            lat=59.91,
            lon=10.75,
            named_after_qid="Q17486662",
            named_after_label="Ló",
            country_code="NO",
        )
        d = rec.to_dict()
        assert d["place_qid"] == "Q585"
        assert d["named_after_label"] == "Ló"
        assert d["source"] == "wikidata"
