"""Tests for the databank validation pipeline."""

import json
import tempfile
from pathlib import Path

from toponymia.pipelines.databank import (
    validate_databank,
    validate_jsonl_file,
    validate_record_against_schema,
)


class TestValidateRecordAgainstSchema:
    def test_valid_minimal_record(self):
        record = {
            "name_form": "Bergen",
            "latitude": 60.39,
            "longitude": 5.32,
            "source_id": "123",
        }
        errors = validate_record_against_schema(record)
        assert errors == []

    def test_valid_full_record(self):
        record = {
            "name_form": "Bergen",
            "latitude": 60.39,
            "longitude": 5.32,
            "source_id": "123",
            "language_code": "nob",
            "country_code": "NO",
            "source_dataset": "geonames",
            "extra_field": "this is allowed",
        }
        errors = validate_record_against_schema(record)
        assert errors == []

    def test_missing_name_form(self):
        record = {"latitude": 60.0, "longitude": 5.0, "source_id": "x"}
        errors = validate_record_against_schema(record)
        assert any("name_form" in e for e in errors)

    def test_missing_latitude(self):
        record = {"name_form": "Test", "longitude": 5.0, "source_id": "x"}
        errors = validate_record_against_schema(record)
        assert any("latitude" in e for e in errors)

    def test_missing_source_id(self):
        record = {"name_form": "Test", "latitude": 60.0, "longitude": 5.0}
        errors = validate_record_against_schema(record)
        assert any("source_id" in e for e in errors)

    def test_empty_name_form(self):
        record = {"name_form": "", "latitude": 60.0, "longitude": 5.0, "source_id": "x"}
        errors = validate_record_against_schema(record)
        assert any("name_form" in e for e in errors)

    def test_latitude_out_of_bounds(self):
        record = {"name_form": "Test", "latitude": 100.0, "longitude": 5.0, "source_id": "x"}
        errors = validate_record_against_schema(record)
        assert any("latitude" in e for e in errors)

    def test_longitude_out_of_bounds(self):
        record = {"name_form": "Test", "latitude": 60.0, "longitude": 200.0, "source_id": "x"}
        errors = validate_record_against_schema(record)
        assert any("longitude" in e for e in errors)

    def test_invalid_language_code(self):
        record = {
            "name_form": "Test",
            "latitude": 60.0,
            "longitude": 5.0,
            "source_id": "x",
            "language_code": "XX",
        }
        errors = validate_record_against_schema(record)
        assert any("language_code" in e for e in errors)

    def test_valid_language_code(self):
        record = {
            "name_form": "Test",
            "latitude": 60.0,
            "longitude": 5.0,
            "source_id": "x",
            "language_code": "nor",
        }
        errors = validate_record_against_schema(record)
        assert errors == []

    def test_invalid_country_code(self):
        record = {
            "name_form": "Test",
            "latitude": 60.0,
            "longitude": 5.0,
            "source_id": "x",
            "country_code": "no",
        }
        errors = validate_record_against_schema(record)
        assert any("country_code" in e for e in errors)

    def test_additional_properties_allowed(self):
        record = {
            "name_form": "Test",
            "latitude": 60.0,
            "longitude": 5.0,
            "source_id": "x",
            "custom_field_1": "value",
            "etymology_notes": "From Old Norse",
            "nested": {"key": "value"},
        }
        errors = validate_record_against_schema(record)
        assert errors == []


class TestValidateJsonlFile:
    def test_valid_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps({"name_form": "A", "latitude": 60.0, "longitude": 5.0, "source_id": "1"})
                + "\n"
            )
            f.write(
                json.dumps({"name_form": "B", "latitude": 61.0, "longitude": 6.0, "source_id": "2"})
                + "\n"
            )
            path = Path(f.name)

        result = validate_jsonl_file(path)
        assert result.is_valid
        assert result.total_records == 2
        assert result.valid_records == 2
        path.unlink()

    def test_file_with_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("not valid json\n")
            f.write(
                json.dumps({"name_form": "A", "latitude": 60.0, "longitude": 5.0, "source_id": "1"})
                + "\n"
            )
            path = Path(f.name)

        result = validate_jsonl_file(path)
        assert not result.is_valid
        assert result.total_records == 2
        assert result.valid_records == 1
        assert len(result.errors) == 1
        assert result.errors[0].line == 1
        path.unlink()

    def test_file_with_schema_error(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {"name_form": "A", "latitude": 200.0, "longitude": 5.0, "source_id": "1"}
                )
                + "\n"
            )
            path = Path(f.name)

        result = validate_jsonl_file(path)
        assert not result.is_valid
        assert result.total_records == 1
        assert result.valid_records == 0
        path.unlink()

    def test_empty_lines_skipped(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps({"name_form": "A", "latitude": 60.0, "longitude": 5.0, "source_id": "1"})
                + "\n"
            )
            f.write("\n")
            f.write("   \n")
            f.write(
                json.dumps({"name_form": "B", "latitude": 61.0, "longitude": 6.0, "source_id": "2"})
                + "\n"
            )
            path = Path(f.name)

        result = validate_jsonl_file(path)
        assert result.is_valid
        assert result.total_records == 2
        path.unlink()


class TestValidateDatabank:
    def test_validates_real_databank(self):
        """Validate the actual databank in the repo."""
        result = validate_databank()
        assert result.total_files >= 2
        assert result.total_records >= 10
        assert result.is_valid, f"Databank has errors: {result.errors[:3]}"
