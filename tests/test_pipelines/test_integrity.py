"""Tests for databank integrity and signing system."""

from __future__ import annotations

import json
from pathlib import Path

from toponymia.pipelines.integrity import (
    canonical_json,
    compute_record_hash,
    generate_manifest,
    sign_jsonl_file,
    sign_record,
    sort_jsonl_file,
    verify_jsonl_file,
    verify_manifest,
    verify_record,
    write_manifest,
)

# === canonical_json tests ===


class TestCanonicalJson:
    def test_sorted_keys(self):
        record = {"z": 1, "a": 2, "m": 3}
        result = canonical_json(record)
        assert result == '{"a":2,"m":3,"z":1}'

    def test_excludes_meta_fields(self):
        record = {"name": "Bergen", "_sha256": "abc123", "_signed_by": "user@example.com"}
        result = canonical_json(record)
        assert "_sha256" not in result
        assert "_signed_by" not in result
        assert '"name":"Bergen"' in result

    def test_nested_dicts_sorted(self):
        record = {"alt": {"z_lang": "val1", "a_lang": "val2"}}
        result = canonical_json(record)
        assert result == '{"alt":{"a_lang":"val2","z_lang":"val1"}}'

    def test_no_whitespace_variance(self):
        record = {"name": "Oslo", "lat": 59.9}
        result = canonical_json(record)
        assert " " not in result.replace('"Oslo"', "")  # No extra spaces

    def test_unicode_preserved(self):
        record = {"name": "Tromsø", "old": "Niðaróss"}
        result = canonical_json(record)
        assert "Tromsø" in result
        assert "Niðaróss" in result

    def test_deterministic(self):
        record = {"b": 2, "a": 1, "c": [{"z": 9, "x": 7}]}
        # Call multiple times, same result
        results = {canonical_json(record) for _ in range(100)}
        assert len(results) == 1

    def test_null_values(self):
        record = {"name": "Test", "year_to": None}
        result = canonical_json(record)
        assert '"year_to":null' in result


# === compute_record_hash tests ===


class TestComputeRecordHash:
    def test_same_data_same_hash(self):
        record1 = {"name_form": "Bergen", "latitude": 60.39, "longitude": 5.32, "source_id": "123"}
        record2 = {"source_id": "123", "longitude": 5.32, "name_form": "Bergen", "latitude": 60.39}
        assert compute_record_hash(record1) == compute_record_hash(record2)

    def test_different_data_different_hash(self):
        record1 = {"name_form": "Bergen", "latitude": 60.39, "longitude": 5.32, "source_id": "123"}
        record2 = {"name_form": "Oslo", "latitude": 59.91, "longitude": 10.74, "source_id": "456"}
        assert compute_record_hash(record1) != compute_record_hash(record2)

    def test_meta_fields_excluded_from_hash(self):
        record_plain = {"name_form": "Test", "source_id": "1"}
        record_with_meta = {
            "name_form": "Test",
            "source_id": "1",
            "_sha256": "whatever",
            "_signed_by": "someone",
        }
        assert compute_record_hash(record_plain) == compute_record_hash(record_with_meta)

    def test_hash_is_sha256_hex(self):
        record = {"name_form": "Test", "source_id": "1"}
        h = compute_record_hash(record)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# === sign_record / verify_record tests ===


class TestSignVerify:
    def test_sign_adds_sha256(self):
        record = {"name_form": "Bergen", "source_id": "123"}
        signed = sign_record(record)
        assert "_sha256" in signed
        assert signed["_sha256"] == compute_record_hash(record)

    def test_sign_does_not_mutate_input(self):
        record = {"name_form": "Bergen", "source_id": "123"}
        sign_record(record)
        assert "_sha256" not in record

    def test_verify_valid_record(self):
        record = {"name_form": "Bergen", "source_id": "123"}
        signed = sign_record(record)
        assert verify_record(signed) is True

    def test_verify_tampered_record(self):
        record = {"name_form": "Bergen", "source_id": "123"}
        signed = sign_record(record)
        signed["name_form"] = "TAMPERED"
        assert verify_record(signed) is False

    def test_verify_missing_hash(self):
        record = {"name_form": "Bergen", "source_id": "123"}
        assert verify_record(record) is False


# === File-level operations ===


class TestJsonlFileOperations:
    def test_sign_jsonl_file(self, tmp_path: Path):
        filepath = tmp_path / "test.jsonl"
        records = [
            {"name_form": "Bergen", "source_id": "1", "latitude": 60.39, "longitude": 5.32},
            {"name_form": "Oslo", "source_id": "2", "latitude": 59.91, "longitude": 10.74},
        ]
        filepath.write_text("\n".join(json.dumps(r) for r in records) + "\n")

        count = sign_jsonl_file(filepath)
        assert count == 2

        # Verify all records have _sha256
        with filepath.open() as f:
            for line in f:
                record = json.loads(line.strip())
                assert "_sha256" in record
                assert verify_record(record) is True

    def test_verify_jsonl_file_all_valid(self, tmp_path: Path):
        filepath = tmp_path / "test.jsonl"
        records = [
            sign_record({"name_form": "Bergen", "source_id": "1"}),
            sign_record({"name_form": "Oslo", "source_id": "2"}),
        ]
        filepath.write_text("\n".join(json.dumps(r) for r in records) + "\n")

        total, errors = verify_jsonl_file(filepath)
        assert total == 2
        assert errors == []

    def test_verify_jsonl_file_tampered(self, tmp_path: Path):
        filepath = tmp_path / "test.jsonl"
        signed = sign_record({"name_form": "Bergen", "source_id": "1"})
        signed["name_form"] = "TAMPERED"  # Tamper after signing
        filepath.write_text(json.dumps(signed) + "\n")

        total, errors = verify_jsonl_file(filepath)
        assert total == 1
        assert len(errors) == 1
        assert "FAILED" in errors[0][1]

    def test_verify_jsonl_file_missing_hash(self, tmp_path: Path):
        filepath = tmp_path / "test.jsonl"
        filepath.write_text('{"name_form": "Bergen", "source_id": "1"}\n')

        total, errors = verify_jsonl_file(filepath)
        assert total == 1
        assert len(errors) == 1
        assert "Missing" in errors[0][1]

    def test_sort_jsonl_file(self, tmp_path: Path):
        filepath = tmp_path / "test.jsonl"
        records = [
            {"name_form": "Zaragoza", "source_id": "9"},
            {"name_form": "Bergen", "source_id": "1"},
            {"name_form": "Madrid", "source_id": "5"},
        ]
        filepath.write_text("\n".join(json.dumps(r) for r in records) + "\n")

        count = sort_jsonl_file(filepath)
        assert count == 3

        with filepath.open() as f:
            sorted_records = [json.loads(line) for line in f if line.strip()]
        assert sorted_records[0]["source_id"] == "1"
        assert sorted_records[1]["source_id"] == "5"
        assert sorted_records[2]["source_id"] == "9"

    def test_sort_preserves_data(self, tmp_path: Path):
        filepath = tmp_path / "test.jsonl"
        records = [
            {"name_form": "B", "source_id": "2", "extra": "data"},
            {"name_form": "A", "source_id": "1", "extra": "info"},
        ]
        filepath.write_text("\n".join(json.dumps(r) for r in records) + "\n")

        sort_jsonl_file(filepath)

        with filepath.open() as f:
            sorted_records = [json.loads(line) for line in f if line.strip()]
        assert sorted_records[0]["extra"] == "info"
        assert sorted_records[1]["extra"] == "data"


# === Manifest tests ===


class TestManifest:
    def test_write_and_verify_manifest(self, tmp_path: Path):
        # Create a fake databank structure
        places_dir = tmp_path / "places" / "NO"
        places_dir.mkdir(parents=True)
        (places_dir / "geonames.jsonl").write_text('{"name": "test"}\n')

        manifest_path = write_manifest(tmp_path)
        assert manifest_path.exists()
        assert "places/NO/geonames.jsonl" in manifest_path.read_text()

        is_valid, errors = verify_manifest(tmp_path)
        assert is_valid
        assert errors == []

    def test_verify_manifest_detects_modification(self, tmp_path: Path):
        places_dir = tmp_path / "places" / "NO"
        places_dir.mkdir(parents=True)
        jsonl = places_dir / "geonames.jsonl"
        jsonl.write_text('{"name": "test"}\n')

        write_manifest(tmp_path)

        # Modify file after manifest was written
        jsonl.write_text('{"name": "TAMPERED"}\n')

        is_valid, errors = verify_manifest(tmp_path)
        assert not is_valid
        assert any("mismatch" in e.lower() for e in errors)

    def test_verify_manifest_detects_new_file(self, tmp_path: Path):
        places_dir = tmp_path / "places" / "NO"
        places_dir.mkdir(parents=True)
        (places_dir / "geonames.jsonl").write_text('{"name": "test"}\n')

        write_manifest(tmp_path)

        # Add a new file after manifest
        (places_dir / "extra.jsonl").write_text('{"name": "new"}\n')

        is_valid, errors = verify_manifest(tmp_path)
        assert not is_valid
        assert any("not in manifest" in e.lower() for e in errors)

    def test_verify_manifest_detects_deleted_file(self, tmp_path: Path):
        places_dir = tmp_path / "places" / "NO"
        places_dir.mkdir(parents=True)
        jsonl = places_dir / "geonames.jsonl"
        jsonl.write_text('{"name": "test"}\n')

        write_manifest(tmp_path)
        jsonl.unlink()

        is_valid, errors = verify_manifest(tmp_path)
        assert not is_valid
        assert any("missing" in e.lower() for e in errors)

    def test_verify_manifest_missing(self, tmp_path: Path):
        is_valid, errors = verify_manifest(tmp_path)
        assert not is_valid
        assert any("not found" in e.lower() for e in errors)

    def test_generate_manifest_sorted(self, tmp_path: Path):
        places_dir = tmp_path / "places"
        (places_dir / "NO").mkdir(parents=True)
        (places_dir / "FI").mkdir(parents=True)
        (places_dir / "NO" / "a.jsonl").write_text("a\n")
        (places_dir / "FI" / "b.jsonl").write_text("b\n")

        manifest = generate_manifest(tmp_path)
        keys = list(manifest.keys())
        assert keys == sorted(keys)


# === Content-addressable property ===


class TestContentAddressable:
    """Verify that the same data always produces the same hash,
    regardless of key order, whitespace, or who produces it."""

    def test_identical_records_from_different_sources(self):
        """Simulate two contributors independently adding the same place."""
        contributor_a = {
            "name_form": "Bergen",
            "latitude": 60.39299,
            "longitude": 5.32415,
            "source_id": "3161732",
            "country_code": "NO",
        }
        # Same data, different key order (as might come from a different tool)
        contributor_b = {
            "country_code": "NO",
            "source_id": "3161732",
            "longitude": 5.32415,
            "latitude": 60.39299,
            "name_form": "Bergen",
        }

        hash_a = compute_record_hash(contributor_a)
        hash_b = compute_record_hash(contributor_b)
        assert hash_a == hash_b

    def test_sign_is_idempotent(self):
        """Signing an already-signed record produces the same hash."""
        record = {"name_form": "Oslo", "source_id": "456", "latitude": 59.91, "longitude": 10.74}
        signed_once = sign_record(record)
        signed_twice = sign_record(signed_once)
        assert signed_once["_sha256"] == signed_twice["_sha256"]
