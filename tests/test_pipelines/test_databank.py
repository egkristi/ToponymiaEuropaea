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


class TestPhoneticKeyEnrichment:
    """Test that _phonetic_key enrichment works on JSONL files."""

    def test_enrich_adds_phonetic_key(self):
        """_enrich_file_phonetic adds _phonetic_key to all records."""
        # Import the helper from CLI module
        import toponymia.cli as cli_mod
        from toponymia.pipelines.phonetic import NordicPhoneticNormalizer

        normalizer = NordicPhoneticNormalizer()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {"name_form": "Bergen", "latitude": 60.39, "longitude": 5.32, "source_id": "1"}
                )
                + "\n"
            )
            f.write(
                json.dumps(
                    {
                        "name_form": "Helsingborg",
                        "latitude": 56.05,
                        "longitude": 12.69,
                        "source_id": "2",
                    }
                )
                + "\n"
            )
            path = Path(f.name)

        cli_mod._enrich_file_phonetic(path, normalizer)

        # Read back
        records = []
        with path.open() as f:
            for line in f:
                records.append(json.loads(line))

        assert len(records) == 2
        assert "_phonetic_key" in records[0]
        assert "_phonetic_key" in records[1]
        # Bergen normalizes to "berg" (suffix norm berget→berg won't apply,
        # but the key should at least be lowercase)
        assert records[0]["_phonetic_key"] == normalizer.phonetic_key("Bergen").key
        assert records[1]["_phonetic_key"] == normalizer.phonetic_key("Helsingborg").key
        path.unlink()

    def test_enrich_preserves_existing_fields(self):
        """Enrichment preserves all existing record fields."""
        import toponymia.cli as cli_mod
        from toponymia.pipelines.phonetic import NordicPhoneticNormalizer

        normalizer = NordicPhoneticNormalizer()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "name_form": "Oslo",
                        "latitude": 59.91,
                        "longitude": 10.75,
                        "source_id": "99",
                        "country_code": "NO",
                        "extra_field": "keep_me",
                    }
                )
                + "\n"
            )
            path = Path(f.name)

        cli_mod._enrich_file_phonetic(path, normalizer)

        with path.open() as f:
            record = json.loads(f.readline())

        assert record["name_form"] == "Oslo"
        assert record["country_code"] == "NO"
        assert record["extra_field"] == "keep_me"
        assert "_phonetic_key" in record
        path.unlink()

    def test_enrich_empty_name_form_skips(self):
        """Records with empty name_form don't get a phonetic key."""
        import toponymia.cli as cli_mod
        from toponymia.pipelines.phonetic import NordicPhoneticNormalizer

        normalizer = NordicPhoneticNormalizer()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps({"name_form": "", "latitude": 60.0, "longitude": 5.0, "source_id": "x"})
                + "\n"
            )
            path = Path(f.name)

        cli_mod._enrich_file_phonetic(path, normalizer)

        with path.open() as f:
            record = json.loads(f.readline())

        assert "_phonetic_key" not in record
        path.unlink()
