"""Tests for geometry validation pipeline."""

from toponymia.pipelines.geometry_validate import (
    validate_feature,
    validate_geometry,
)


class TestValidateGeometry:
    """Tests for validate_geometry."""

    def test_valid_point(self):
        geom = {"type": "Point", "coordinates": [10.5, 59.9]}
        result = validate_geometry(geom)
        assert result.valid
        assert result.geometry_type == "Point"
        assert result.vertex_count == 1

    def test_point_out_of_range(self):
        geom = {"type": "Point", "coordinates": [200, 59.9]}
        result = validate_geometry(geom)
        assert not result.valid
        assert any("out of range" in e for e in result.errors)

    def test_valid_linestring(self):
        geom = {"type": "LineString", "coordinates": [[0, 0], [1, 1], [2, 0]]}
        result = validate_geometry(geom)
        assert result.valid
        assert result.vertex_count == 3

    def test_linestring_too_few(self):
        geom = {"type": "LineString", "coordinates": [[0, 0]]}
        result = validate_geometry(geom)
        assert not result.valid
        assert any("at least 2" in e for e in result.errors)

    def test_valid_polygon(self):
        # CCW exterior ring (right-hand rule)
        geom = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
        }
        result = validate_geometry(geom)
        assert result.valid
        assert result.vertex_count == 5

    def test_polygon_not_closed(self):
        geom = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10]]],
        }
        result = validate_geometry(geom)
        assert not result.valid
        assert any("not closed" in e for e in result.errors)

    def test_polygon_clockwise_exterior_warning(self):
        # CW exterior ring - should produce warning
        geom = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]],
        }
        result = validate_geometry(geom)
        assert result.valid  # Still valid, just a warning
        assert any("clockwise" in w for w in result.warnings)

    def test_polygon_self_intersection(self):
        # Bowtie polygon (self-intersecting)
        geom = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 10], [10, 0], [0, 10], [0, 0]]],
        }
        result = validate_geometry(geom)
        assert not result.valid
        assert any("self-intersection" in e for e in result.errors)

    def test_multipoint(self):
        geom = {"type": "MultiPoint", "coordinates": [[1, 2], [3, 4]]}
        result = validate_geometry(geom)
        assert result.valid
        assert result.vertex_count == 2

    def test_unknown_type(self):
        geom = {"type": "Sphere", "coordinates": [0, 0]}
        result = validate_geometry(geom)
        assert not result.valid
        assert any("Unknown" in e for e in result.errors)

    def test_missing_coordinates(self):
        geom = {"type": "Point"}
        result = validate_geometry(geom)
        assert not result.valid

    def test_not_a_dict(self):
        result = validate_geometry("invalid")
        assert not result.valid


class TestValidateFeature:
    """Tests for validate_feature."""

    def test_valid_feature(self):
        feature = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [10, 60]},
            "properties": {"name": "Oslo"},
        }
        result = validate_feature(feature)
        assert result.valid

    def test_null_geometry(self):
        feature = {"type": "Feature", "geometry": None, "properties": {}}
        result = validate_feature(feature)
        assert result.valid
        assert any("null geometry" in w for w in result.warnings)

    def test_invalid_type(self):
        feature = {"type": "FeatureCollection", "geometry": None}
        result = validate_feature(feature)
        assert not result.valid

    def test_multipolygon(self):
        geom = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
            ],
        }
        result = validate_geometry(geom)
        assert result.valid
        assert result.vertex_count == 10
