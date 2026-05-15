"""Tests for the Parquet/DuckDB analytical layer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from toponymia.pipelines.analytical import (
    export_databank_to_parquet,
    jsonl_to_parquet,
    query_databank,
    query_parquet,
)


@pytest.fixture
def sample_jsonl(tmp_path: Path) -> Path:
    """Create a sample JSONL file for testing."""
    records = [
        {"name": "Oslo", "country": "NO", "lat": 59.91, "lon": 10.75},
        {"name": "Bergen", "country": "NO", "lat": 60.39, "lon": 5.32},
        {"name": "Stockholm", "country": "SE", "lat": 59.33, "lon": 18.07},
        {"name": "Reykjavík", "country": "IS", "lat": 64.13, "lon": -21.90},
        {"name": "Helsinki", "country": "FI", "lat": 60.17, "lon": 24.94},
    ]
    jsonl_file = tmp_path / "test.jsonl"
    with jsonl_file.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    return jsonl_file


@pytest.fixture
def sample_databank(tmp_path: Path) -> Path:
    """Create a sample databank directory structure."""
    databank = tmp_path / "databank"
    places = databank / "places"

    # NO
    no_dir = places / "NO"
    no_dir.mkdir(parents=True)
    with (no_dir / "geonames.jsonl").open("w") as f:
        f.write(json.dumps({"name": "Oslo", "country": "NO", "lat": 59.91}) + "\n")
        f.write(json.dumps({"name": "Bergen", "country": "NO", "lat": 60.39}) + "\n")

    # SE
    se_dir = places / "SE"
    se_dir.mkdir(parents=True)
    with (se_dir / "geonames.jsonl").open("w") as f:
        f.write(json.dumps({"name": "Stockholm", "country": "SE", "lat": 59.33}) + "\n")

    return databank


class TestJsonlToParquet:
    """Tests for JSONL to Parquet conversion."""

    def test_basic_conversion(self, sample_jsonl: Path, tmp_path: Path) -> None:
        """Test basic JSONL to Parquet conversion."""
        output = tmp_path / "output.parquet"
        count = jsonl_to_parquet(sample_jsonl, output)

        assert count == 5
        assert output.exists()

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test conversion of empty JSONL file."""
        empty = tmp_path / "empty.jsonl"
        empty.write_text("")
        output = tmp_path / "output.parquet"

        count = jsonl_to_parquet(empty, output)
        assert count == 0

    def test_partitioned_output(self, sample_jsonl: Path, tmp_path: Path) -> None:
        """Test partitioned Parquet output."""
        output = tmp_path / "partitioned"
        count = jsonl_to_parquet(sample_jsonl, output, partition_by="country")

        assert count == 5
        assert output.is_dir()


class TestExportDatabank:
    """Tests for full databank export."""

    def test_export(self, sample_databank: Path, tmp_path: Path) -> None:
        """Test exporting databank to Parquet."""
        output = tmp_path / "parquet_out"
        results = export_databank_to_parquet(sample_databank, output)

        assert "places/NO/geonames.jsonl" in results
        assert results["places/NO/geonames.jsonl"] == 2
        assert "places/SE/geonames.jsonl" in results
        assert results["places/SE/geonames.jsonl"] == 1

    def test_empty_databank(self, tmp_path: Path) -> None:
        """Test with non-existent places dir."""
        databank = tmp_path / "empty_databank"
        databank.mkdir()
        results = export_databank_to_parquet(databank, tmp_path / "out")
        assert results == {}


class TestQueryParquet:
    """Tests for DuckDB queries on Parquet."""

    def test_count_query(self, sample_jsonl: Path, tmp_path: Path) -> None:
        """Test counting records via DuckDB."""
        parquet_path = tmp_path / "data.parquet"
        jsonl_to_parquet(sample_jsonl, parquet_path)

        results = query_parquet(parquet_path, "SELECT COUNT(*) as cnt FROM data")
        assert results[0]["cnt"] == 5

    def test_filter_query(self, sample_jsonl: Path, tmp_path: Path) -> None:
        """Test filtering via DuckDB SQL."""
        parquet_path = tmp_path / "data.parquet"
        jsonl_to_parquet(sample_jsonl, parquet_path)

        results = query_parquet(
            parquet_path,
            "SELECT name FROM data WHERE country = 'NO' ORDER BY name",
        )
        assert len(results) == 2
        assert results[0]["name"] == "Bergen"
        assert results[1]["name"] == "Oslo"

    def test_aggregation_query(self, sample_jsonl: Path, tmp_path: Path) -> None:
        """Test aggregation via DuckDB."""
        parquet_path = tmp_path / "data.parquet"
        jsonl_to_parquet(sample_jsonl, parquet_path)

        results = query_parquet(
            parquet_path,
            "SELECT country, COUNT(*) as cnt FROM data GROUP BY country ORDER BY cnt DESC",
        )
        assert results[0]["country"] == "NO"
        assert results[0]["cnt"] == 2


class TestQueryDatabank:
    """Tests for direct JSONL querying via DuckDB."""

    def test_direct_query(self, sample_databank: Path) -> None:
        """Test querying JSONL files directly with DuckDB."""
        results = query_databank(
            "SELECT COUNT(*) as cnt FROM databank",
            databank_path=sample_databank,
        )
        assert results[0]["cnt"] == 3

    def test_filter_direct(self, sample_databank: Path) -> None:
        """Test filtering on direct JSONL query."""
        results = query_databank(
            "SELECT name FROM databank WHERE country = 'NO' ORDER BY name",
            databank_path=sample_databank,
        )
        assert len(results) == 2
        assert results[0]["name"] == "Bergen"

    def test_spatial_query(self, sample_databank: Path) -> None:
        """Test spatial-like query on coordinates."""
        results = query_databank(
            "SELECT name, lat FROM databank WHERE lat > 60 ORDER BY lat DESC",
            databank_path=sample_databank,
        )
        assert len(results) == 1
        assert results[0]["name"] == "Bergen"
