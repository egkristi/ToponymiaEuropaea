"""Tests for attestation validation pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from toponymia.pipelines.attestation_validate import (
    validate_attestation_file,
    validate_attestation_record,
)


class TestValidateAttestationRecord:
    """Unit tests for single-record validation."""

    def _valid_record(self, **overrides) -> dict:
        base = {
            "form": "Ásgarðr",
            "language_code": "non",
            "year_from": 1320,
            "source": "DN V 67, 1320",
        }
        base.update(overrides)
        return base

    def test_valid_minimal_record(self):
        errors = validate_attestation_record(self._valid_record())
        assert not any(e.severity == "error" for e in errors)

    def test_valid_full_record(self):
        record = self._valid_record(
            place_id="Q1522648",
            normalized="asgardr",
            script="Latn",
            year_to=1350,
            date_precision="exact",
            confidence=0.95,
            lemma="garðr",
            lemma_language="non",
            collection_method="manual_transcription",
            components=[
                {"component": "ás", "position": 0, "morph_type": "compound_modifier"},
                {"component": "garðr", "position": 1, "morph_type": "compound_head"},
            ],
        )
        errors = validate_attestation_record(record)
        assert not any(e.severity == "error" for e in errors)

    # --- Required field tests ---

    def test_missing_form(self):
        errors = validate_attestation_record(self._valid_record(form=""))
        assert any(e.field == "form" and e.severity == "error" for e in errors)

    def test_missing_language_code(self):
        errors = validate_attestation_record(self._valid_record(language_code=""))
        assert any(e.field == "language_code" and e.severity == "error" for e in errors)

    def test_missing_year_from(self):
        record = self._valid_record()
        del record["year_from"]
        errors = validate_attestation_record(record)
        assert any(e.field == "year_from" and e.severity == "error" for e in errors)

    def test_null_year_from(self):
        errors = validate_attestation_record(self._valid_record(year_from=None))
        assert any(e.field == "year_from" and e.severity == "error" for e in errors)

    def test_missing_source(self):
        errors = validate_attestation_record(self._valid_record(source=""))
        assert any(e.field == "source" and e.severity == "error" for e in errors)

    # --- Language code ---

    def test_invalid_language_code_too_long(self):
        errors = validate_attestation_record(self._valid_record(language_code="nors"))
        assert any(e.field == "language_code" for e in errors)

    def test_invalid_language_code_uppercase(self):
        errors = validate_attestation_record(self._valid_record(language_code="NON"))
        assert any(e.field == "language_code" for e in errors)

    def test_valid_two_letter_code(self):
        errors = validate_attestation_record(self._valid_record(language_code="la"))
        assert not any(e.field == "language_code" for e in errors)

    # --- Year range ---

    def test_year_from_too_old(self):
        errors = validate_attestation_record(self._valid_record(year_from=-5000))
        assert any(e.field == "year_from" for e in errors)

    def test_year_from_too_future(self):
        errors = validate_attestation_record(self._valid_record(year_from=2200))
        assert any(e.field == "year_from" for e in errors)

    def test_year_to_before_year_from(self):
        errors = validate_attestation_record(self._valid_record(year_from=1300, year_to=1200))
        assert any(e.field == "year_to" for e in errors)

    def test_year_to_valid_range(self):
        errors = validate_attestation_record(self._valid_record(year_from=1300, year_to=1400))
        assert not any(e.field == "year_to" for e in errors)

    def test_negative_year_bce(self):
        errors = validate_attestation_record(self._valid_record(year_from=-500))
        assert not any(e.field == "year_from" and e.severity == "error" for e in errors)

    # --- Confidence ---

    def test_confidence_too_high(self):
        errors = validate_attestation_record(self._valid_record(confidence=1.5))
        assert any(e.field == "confidence" for e in errors)

    def test_confidence_negative(self):
        errors = validate_attestation_record(self._valid_record(confidence=-0.1))
        assert any(e.field == "confidence" for e in errors)

    def test_confidence_valid(self):
        errors = validate_attestation_record(self._valid_record(confidence=0.85))
        assert not any(e.field == "confidence" for e in errors)

    # --- Script ---

    def test_invalid_script(self):
        errors = validate_attestation_record(self._valid_record(script="latin"))
        assert any(e.field == "script" for e in errors)

    def test_valid_script(self):
        errors = validate_attestation_record(self._valid_record(script="Runr"))
        assert not any(e.field == "script" for e in errors)

    # --- Date precision ---

    def test_invalid_date_precision(self):
        errors = validate_attestation_record(self._valid_record(date_precision="vague"))
        assert any(e.field == "date_precision" for e in errors)

    def test_valid_date_precision(self):
        for precision in ("exact", "decade", "quarter_century", "century", "estimated"):
            errors = validate_attestation_record(self._valid_record(date_precision=precision))
            assert not any(e.field == "date_precision" for e in errors)

    # --- Collection method ---

    def test_invalid_collection_method(self):
        errors = validate_attestation_record(self._valid_record(collection_method="guessing"))
        assert any(e.field == "collection_method" for e in errors)

    def test_valid_collection_method(self):
        errors = validate_attestation_record(self._valid_record(collection_method="ocr"))
        assert not any(e.field == "collection_method" for e in errors)

    # --- Components ---

    def test_valid_components(self):
        record = self._valid_record(
            components=[
                {"component": "ás", "position": 0, "morph_type": "compound_modifier"},
                {"component": "garðr", "position": 1, "morph_type": "compound_head"},
            ]
        )
        errors = validate_attestation_record(record)
        assert not any("components" in e.field for e in errors)

    def test_component_missing_morph_type(self):
        record = self._valid_record(components=[{"component": "ás", "position": 0}])
        errors = validate_attestation_record(record)
        assert any("morph_type" in e.field for e in errors)

    def test_component_invalid_morph_type(self):
        record = self._valid_record(
            components=[{"component": "ás", "position": 0, "morph_type": "adjective"}]
        )
        errors = validate_attestation_record(record)
        assert any("morph_type" in e.field for e in errors)

    def test_component_missing_text(self):
        record = self._valid_record(
            components=[{"component": "", "position": 0, "morph_type": "stem"}]
        )
        errors = validate_attestation_record(record)
        assert any("component" in e.field for e in errors)

    # --- Unicode NFC ---

    def test_non_nfc_warning(self):
        # e with combining acute (NFD) instead of NFC precomposed
        nfd_form = "Bre\u0301viken"
        errors = validate_attestation_record(self._valid_record(form=nfd_form))
        assert any(e.field == "form" and e.severity == "warning" for e in errors)


class TestValidateAttestationFile:
    """Integration tests for JSONL file validation."""

    def _write_jsonl(self, tmp_path: Path, records: list[dict]) -> Path:
        path = tmp_path / "test.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in records) + ("\n" if records else ""))
        return path

    def test_valid_file(self, tmp_path):
        records = [
            {
                "form": "Ásgarðr",
                "language_code": "non",
                "year_from": 1320,
                "source": "DN V 67",
            },
            {
                "form": "Bjørgvin",
                "language_code": "non",
                "year_from": 1070,
                "source": "Adam of Bremen",
            },
        ]
        path = self._write_jsonl(tmp_path, records)
        report = validate_attestation_file(path)
        assert report.total_records == 2
        assert report.valid_records == 2
        assert report.is_valid

    def test_mixed_valid_invalid(self, tmp_path):
        records = [
            {
                "form": "Ásgarðr",
                "language_code": "non",
                "year_from": 1320,
                "source": "DN V 67",
            },
            {
                "form": "",
                "language_code": "non",
                "year_from": 1320,
                "source": "DN V 67",
            },
        ]
        path = self._write_jsonl(tmp_path, records)
        report = validate_attestation_file(path)
        assert report.total_records == 2
        assert report.valid_records == 1
        assert not report.is_valid

    def test_invalid_json_line(self, tmp_path):
        path = tmp_path / "bad.jsonl"
        path.write_text(
            '{"form": "X", "language_code": "non",'
            ' "year_from": 1320, "source": "x"}\n'
            "not json at all\n"
        )
        report = validate_attestation_file(path)
        assert report.total_records == 2
        assert report.valid_records == 1
        assert any(e.field == "json" for e in report.errors)

    def test_empty_file(self, tmp_path):
        path = self._write_jsonl(tmp_path, [])
        report = validate_attestation_file(path)
        assert report.total_records == 0
        assert report.is_valid

    def test_report_properties(self, tmp_path):
        records = [
            {"form": "A", "language_code": "non", "year_from": 1320, "source": "x"},
            {
                "form": "B",
                "language_code": "INVALID",
                "year_from": 1320,
                "source": "x",
            },
            {"form": "", "language_code": "non", "year_from": 1320, "source": "x"},
        ]
        path = self._write_jsonl(tmp_path, records)
        report = validate_attestation_file(path)
        assert report.total_records == 3
        assert report.valid_records == 1
        assert report.invalid_records == 2
