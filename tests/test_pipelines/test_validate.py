"""Tests for the automated validation rules pipeline."""

from toponymia.connectors.base import ConnectorResult
from toponymia.pipelines.validate import (
    ValidationConfig,
    validate_batch,
    validate_record,
)


def _make_record(**kwargs) -> ConnectorResult:
    """Create a valid record with optional overrides."""
    defaults = {
        "latitude": 60.0,
        "longitude": 10.0,
        "name_form": "Trondheim",
        "name_normalized": "trondheim",
        "language_code": "nob",
        "source_id": "geonames-123",
    }
    defaults.update(kwargs)
    return ConnectorResult(**defaults)


class TestCoordinateValidation:
    def test_valid_coordinates(self):
        record = _make_record(latitude=59.9, longitude=10.7)
        errors = validate_record(record)
        coord_errors = [e for e in errors if e.field in ("latitude", "longitude", "coordinates")]
        assert not coord_errors

    def test_latitude_out_of_bounds(self):
        record = _make_record(latitude=95.0)
        errors = validate_record(record)
        assert any(e.field == "latitude" for e in errors)

    def test_latitude_negative_out_of_bounds(self):
        record = _make_record(latitude=-91.0)
        errors = validate_record(record)
        assert any(e.field == "latitude" for e in errors)

    def test_longitude_out_of_bounds(self):
        record = _make_record(longitude=200.0)
        errors = validate_record(record)
        assert any(e.field == "longitude" for e in errors)

    def test_null_island_warning(self):
        record = _make_record(latitude=0.0, longitude=0.0)
        errors = validate_record(record)
        warnings = [e for e in errors if e.field == "coordinates" and e.severity == "warning"]
        assert len(warnings) == 1
        assert "Null Island" in warnings[0].message

    def test_custom_bounds(self):
        config = ValidationConfig(min_lat=57.0, max_lat=72.0, min_lon=4.0, max_lon=32.0)
        record = _make_record(latitude=50.0, longitude=10.0)
        errors = validate_record(record, config)
        assert any(e.field == "latitude" for e in errors)


class TestNameFormValidation:
    def test_valid_name(self):
        record = _make_record(name_form="Bergen")
        errors = validate_record(record)
        name_errors = [e for e in errors if e.field == "name_form"]
        assert not name_errors

    def test_empty_name(self):
        record = _make_record(name_form="")
        errors = validate_record(record)
        assert any(e.field == "name_form" and "empty" in e.message for e in errors)

    def test_whitespace_only_name(self):
        record = _make_record(name_form="   ")
        errors = validate_record(record)
        assert any(e.field == "name_form" and "empty" in e.message for e in errors)

    def test_name_too_long(self):
        record = _make_record(name_form="x" * 501)
        errors = validate_record(record)
        assert any(e.field == "name_form" and "too long" in e.message for e in errors)

    def test_encoding_corruption_replacement_char(self):
        record = _make_record(name_form="Trondheim\ufffd")
        errors = validate_record(record)
        assert any(e.field == "name_form" and "Encoding" in e.message for e in errors)

    def test_encoding_corruption_double_encoding(self):
        record = _make_record(name_form="TrondheimÃ¸")
        errors = validate_record(record)
        assert any(e.field == "name_form" and "Encoding" in e.message for e in errors)

    def test_control_characters(self):
        record = _make_record(name_form="Trond\x00heim")
        errors = validate_record(record)
        assert any(e.field == "name_form" and "control" in e.message for e in errors)

    def test_numeric_name(self):
        record = _make_record(name_form="12345")
        errors = validate_record(record)
        assert any(e.field == "name_form" and "numeric" in e.message for e in errors)

    def test_unicode_nfc_warning(self):
        # NFD form: 'å' as 'a' + combining ring
        nfd_name = "Tr\u0061\u030andheim"  # a + combining ring above
        record = _make_record(name_form=nfd_name)
        errors = validate_record(record)
        warnings = [e for e in errors if e.field == "name_form" and e.severity == "warning"]
        assert any("NFC" in w.message for w in warnings)


class TestLanguageCodeValidation:
    def test_valid_code(self):
        record = _make_record(language_code="nob")
        errors = validate_record(record)
        lang_errors = [e for e in errors if e.field == "language_code"]
        assert not lang_errors

    def test_undetermined_warning(self):
        record = _make_record(language_code="und")
        errors = validate_record(record)
        warnings = [e for e in errors if e.field == "language_code" and e.severity == "warning"]
        assert len(warnings) == 1

    def test_invalid_format_too_long(self):
        record = _make_record(language_code="norsk")
        errors = validate_record(record)
        assert any(e.field == "language_code" and "not valid" in e.message for e in errors)

    def test_invalid_format_uppercase(self):
        record = _make_record(language_code="NOB")
        errors = validate_record(record)
        assert any(e.field == "language_code" and "not valid" in e.message for e in errors)

    def test_invalid_format_two_letter(self):
        record = _make_record(language_code="no")
        errors = validate_record(record)
        assert any(e.field == "language_code" and "not valid" in e.message for e in errors)

    def test_empty_code(self):
        record = _make_record(language_code="")
        errors = validate_record(record)
        assert any(e.field == "language_code" and "missing" in e.message for e in errors)

    def test_disabled_language_check(self):
        config = ValidationConfig(require_valid_language_code=False)
        record = _make_record(language_code="INVALID")
        errors = validate_record(record, config)
        lang_errors = [e for e in errors if e.field == "language_code"]
        assert not lang_errors


class TestSourceValidation:
    def test_valid_source(self):
        record = _make_record(source_id="kartverket-123")
        errors = validate_record(record)
        source_errors = [e for e in errors if e.field == "source_id"]
        assert not source_errors

    def test_missing_source(self):
        record = _make_record(source_id="")
        errors = validate_record(record)
        assert any(e.field == "source_id" for e in errors)

    def test_source_not_required(self):
        config = ValidationConfig(require_source_id=False)
        record = _make_record(source_id="")
        errors = validate_record(record, config)
        source_errors = [e for e in errors if e.field == "source_id"]
        assert not source_errors


class TestTemporalValidation:
    def test_valid_temporal_range(self):
        record = _make_record(year_from=1200, year_to=1400)
        errors = validate_record(record)
        temporal_errors = [e for e in errors if e.field in ("year_from", "year_to")]
        assert not temporal_errors

    def test_inverted_temporal_range(self):
        record = _make_record(year_from=1500, year_to=1200)
        errors = validate_record(record)
        assert any(e.field == "year_from" and "after" in e.message for e in errors)

    def test_far_future_warning(self):
        record = _make_record(year_from=2200)
        errors = validate_record(record)
        warnings = [e for e in errors if e.field == "year_from" and e.severity == "warning"]
        assert len(warnings) == 1

    def test_none_temporal_ok(self):
        record = _make_record(year_from=None, year_to=None)
        errors = validate_record(record)
        temporal_errors = [e for e in errors if e.field in ("year_from", "year_to")]
        assert not temporal_errors


class TestBatchValidation:
    def test_batch_returns_only_invalid(self):
        records = [
            _make_record(name_form="Valid"),
            _make_record(name_form=""),  # invalid
            _make_record(name_form="Also Valid"),
            _make_record(latitude=999.0),  # invalid
        ]
        results = validate_batch(records)
        assert 0 not in results
        assert 1 in results
        assert 2 not in results
        assert 3 in results

    def test_batch_empty_list(self):
        results = validate_batch([])
        assert results == {}
