"""Tests for the geometry classification pipeline."""

import pytest

from toponymia.pipelines.geometry_classify import (
    classify_geometry,
    get_geometry_status,
)


class TestClassifyGeometry:
    """Test geometry class determination from place types."""

    @pytest.mark.parametrize(
        ("place_type", "expected"),
        [
            ("P.PPL", "point"),
            ("P.PPLC", "point"),
            ("S.FRM", "point"),
            ("S.CH", "point"),
            ("T.PK", "point"),
            ("T.PT", "point"),
            ("H.FLLS", "point"),
            ("Fyrlykt", "point"),
            ("Gard", "point"),
            ("Foss", "point"),
        ],
    )
    def test_point_features(self, place_type, expected):
        assert classify_geometry(place_type) == expected

    @pytest.mark.parametrize(
        ("place_type", "expected"),
        [
            ("H.STM", "line"),
            ("H.STMX", "line"),
            ("H.CNL", "line"),
            ("T.RDGE", "line"),
            ("T.CLF", "line"),
            ("Elv", "line"),
            ("Vegstrekning", "line"),
            ("Banestrekning", "line"),
        ],
    )
    def test_line_features(self, place_type, expected):
        assert classify_geometry(place_type) == expected

    @pytest.mark.parametrize(
        ("place_type", "expected"),
        [
            ("H.LK", "area"),
            ("H.FJD", "area"),
            ("H.BAY", "area"),
            ("T.ISL", "area"),
            ("T.MTS", "area"),
            ("T.VAL", "area"),
            ("T.PEN", "area"),
            ("V.FRST", "area"),
            ("Myr", "area"),
            ("Dal", "area"),
            ("Vann", "area"),
            ("Fjord", "area"),
            ("Øy i sjø", "area"),
            ("Kommune", "area"),
        ],
    )
    def test_area_features(self, place_type, expected):
        assert classify_geometry(place_type) == expected

    def test_unknown_type(self):
        assert classify_geometry("UNKNOWN.TYPE") == "unknown"

    def test_none_type(self):
        assert classify_geometry(None) == "unknown"

    def test_empty_type(self):
        assert classify_geometry("") == "unknown"


class TestGetGeometryStatus:
    """Test geometry status determination."""

    def test_point_no_geometry(self):
        assert get_geometry_status("point", None) == "point"

    def test_line_no_geometry(self):
        assert get_geometry_status("line", None) == "pending"

    def test_area_no_geometry(self):
        assert get_geometry_status("area", None) == "pending"

    def test_area_with_geometry(self):
        geometry = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}
        assert get_geometry_status("area", geometry) == "defined"

    def test_line_with_geometry(self):
        geometry = {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}
        assert get_geometry_status("line", geometry) == "defined"

    def test_unknown_no_geometry(self):
        assert get_geometry_status("unknown", None) == "unknown"

    def test_empty_geometry_dict(self):
        assert get_geometry_status("area", {}) == "pending"

    def test_geometry_without_type(self):
        assert get_geometry_status("area", {"coordinates": []}) == "pending"
