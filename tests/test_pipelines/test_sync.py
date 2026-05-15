"""Tests for the sync pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from toponymia.pipelines.sync import (
    SyncResult,
    compute_file_checksum,
    compute_records_checksum,
    load_jsonl_records,
    sync_jsonl_to_parquet,
    verify_manifest,
)


@pytest.fixture
def sample_databank(tmp_path: Path) -> Path:
    """Create a sample databank with places and manifest."""
    databank = tmp_path / "databank"
    places = databank / "places" / "NO"
    places.mkdir(parents=True)

    records = [
        {
            "name": "Oslo",
            "country_code": "NO",
            "lat": 59.91,
            "lon": 10.75,
            "source": "geonames",
            "source_id": "3143244",
        },
        {
            "name": "Bergen",
            "country_code": "NO",
            "lat": 60.39,
            "lon": 5.32,
            "source": "geonames",
            "source_id": "3161732",
        },
    ]
    jsonl_file = places / "geonames.jsonl"
    with jsonl_file.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    # Create manifest
    checksum = compute_file_checksum(jsonl_file)
    manifest = databank / "MANIFEST.sha256"
    manifest.write_text(f"{checksum}  places/NO/geonames.jsonl\n")

    return databank


class TestChecksums:
    """Tests for checksum computation."""

    def test_file_checksum(self, tmp_path: Path) -> None:
        """Test file checksum is deterministic."""
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        c1 = compute_file_checksum(f)
        c2 = compute_file_checksum(f)
        assert c1 == c2
        assert len(c1) == 64  # SHA-256 hex

    def test_records_checksum_deterministic(self) -> None:
        """Test records checksum is order-independent."""
        records1 = [{"a": 1, "b": 2}, {"c": 3}]
        records2 = [{"c": 3}, {"a": 1, "b": 2}]
        assert compute_records_checksum(records1) == compute_records_checksum(records2)

    def test_records_checksum_differs(self) -> None:
        """Test different records produce different checksums."""
        r1 = [{"a": 1}]
        r2 = [{"a": 2}]
        assert compute_records_checksum(r1) != compute_records_checksum(r2)


class TestLoadRecords:
    """Tests for loading JSONL records."""

    def test_load_records(self, sample_databank: Path) -> None:
        """Test loading records from databank."""
        records = load_jsonl_records(sample_databank)
        assert len(records) == 2
        assert records[0]["name"] == "Oslo"

    def test_load_empty_databank(self, tmp_path: Path) -> None:
        """Test loading from non-existent places dir."""
        records = load_jsonl_records(tmp_path / "nonexistent")
        assert records == []


class TestVerifyManifest:
    """Tests for manifest verification."""

    def test_valid_manifest(self, sample_databank: Path) -> None:
        """Test verifying a valid manifest."""
        result = verify_manifest(sample_databank)
        assert result.success
        assert result.records_processed == 1

    def test_missing_manifest(self, tmp_path: Path) -> None:
        """Test missing manifest file."""
        result = verify_manifest(tmp_path)
        assert not result.success
        assert "MANIFEST.sha256 not found" in result.errors[0]

    def test_corrupt_file(self, sample_databank: Path) -> None:
        """Test detecting a corrupted file."""
        # Modify the JSONL file after manifest was created
        jsonl_file = sample_databank / "places" / "NO" / "geonames.jsonl"
        with jsonl_file.open("a") as f:
            f.write(json.dumps({"name": "Tromsø"}) + "\n")

        result = verify_manifest(sample_databank)
        assert not result.success
        assert "Checksum mismatch" in result.errors[0]

    def test_missing_file(self, sample_databank: Path) -> None:
        """Test detecting a missing file."""
        jsonl_file = sample_databank / "places" / "NO" / "geonames.jsonl"
        jsonl_file.unlink()

        result = verify_manifest(sample_databank)
        assert not result.success
        assert "Missing file" in result.errors[0]


class TestSyncToParquet:
    """Tests for direct JSONL → Parquet sync."""

    def test_sync_creates_parquet(self, sample_databank: Path, tmp_path: Path) -> None:
        """Test that sync produces Parquet output."""
        output = tmp_path / "parquet_out"
        result = sync_jsonl_to_parquet(sample_databank, output)

        assert result.success
        assert result.records_processed == 2
        assert result.records_inserted == 2
        assert result.checksum != ""
        assert output.exists()

    def test_sync_empty_databank(self, tmp_path: Path) -> None:
        """Test sync with empty databank."""
        databank = tmp_path / "empty"
        databank.mkdir()
        result = sync_jsonl_to_parquet(databank, tmp_path / "out")

        assert result.success
        assert result.records_processed == 0


class TestSyncResult:
    """Tests for SyncResult dataclass."""

    def test_success_when_no_errors(self) -> None:
        """Test success property."""
        result = SyncResult(stage="test")
        assert result.success

    def test_failure_with_errors(self) -> None:
        """Test failure with errors."""
        result = SyncResult(stage="test", errors=["something went wrong"])
        assert not result.success
