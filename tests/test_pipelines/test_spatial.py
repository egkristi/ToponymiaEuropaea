"""Tests for H3 spatial indexing pipeline."""

import pytest

h3 = pytest.importorskip("h3", reason="h3 not installed")

from toponymia.pipelines.spatial import (  # noqa: E402
    compute_h3_indices,
    enrich_record_h3,
    find_neighbours,
    h3_distance,
    lat_lng_to_h3,
)


class TestLatLngToH3:
    def test_oslo(self) -> None:
        """Oslo should produce a valid H3 index."""
        index = lat_lng_to_h3(59.91, 10.75)
        assert isinstance(index, str)
        assert len(index) == 15  # H3 indices are 15 hex chars

    def test_resolution_affects_length(self) -> None:
        """Different resolutions produce different indices."""
        r7 = lat_lng_to_h3(60.0, 5.0, resolution=7)
        r9 = lat_lng_to_h3(60.0, 5.0, resolution=9)
        r11 = lat_lng_to_h3(60.0, 5.0, resolution=11)
        # All valid but different
        assert r7 != r9 != r11

    def test_nearby_points_same_r7(self) -> None:
        """Points close together share the same R7 cell."""
        # Two points ~100m apart in Bergen
        idx1 = lat_lng_to_h3(60.3913, 5.3221, resolution=7)
        idx2 = lat_lng_to_h3(60.3914, 5.3222, resolution=7)
        assert idx1 == idx2

    def test_distant_points_differ(self) -> None:
        """Oslo and Bergen have different H3 cells at any resolution."""
        oslo = lat_lng_to_h3(59.91, 10.75, resolution=7)
        bergen = lat_lng_to_h3(60.39, 5.32, resolution=7)
        assert oslo != bergen


class TestComputeH3Indices:
    def test_default_resolutions(self) -> None:
        """Returns indices for R7, R9, R11."""
        result = compute_h3_indices(60.0, 10.0)
        assert "h3_r7" in result
        assert "h3_r9" in result
        assert "h3_r11" in result
        assert len(result) == 3

    def test_custom_resolutions(self) -> None:
        """Supports custom resolution tuple."""
        result = compute_h3_indices(60.0, 10.0, resolutions=(5, 8))
        assert "h3_r5" in result
        assert "h3_r8" in result
        assert len(result) == 2


class TestEnrichRecordH3:
    def test_adds_h3_fields(self) -> None:
        """Enrichment adds _h3_r7, _h3_r9, _h3_r11."""
        record = {"name_form": "Bergen", "latitude": 60.39, "longitude": 5.32, "source_id": "1"}
        enriched = enrich_record_h3(record)
        assert "_h3_r7" in enriched
        assert "_h3_r9" in enriched
        assert "_h3_r11" in enriched

    def test_preserves_existing_fields(self) -> None:
        """All original fields are preserved."""
        record = {
            "name_form": "Oslo",
            "latitude": 59.91,
            "longitude": 10.75,
            "source_id": "2",
            "country_code": "NO",
        }
        enriched = enrich_record_h3(record)
        assert enriched["name_form"] == "Oslo"
        assert enriched["country_code"] == "NO"
        assert enriched["source_id"] == "2"

    def test_missing_latitude_skips(self) -> None:
        """Records without lat/lon are returned unchanged."""
        record = {"name_form": "Unknown", "source_id": "x"}
        enriched = enrich_record_h3(record)
        assert "_h3_r7" not in enriched

    def test_missing_longitude_skips(self) -> None:
        """Records with only latitude are returned unchanged."""
        record = {"name_form": "Test", "latitude": 60.0, "source_id": "x"}
        enriched = enrich_record_h3(record)
        assert "_h3_r9" not in enriched

    def test_does_not_mutate_original(self) -> None:
        """Original record is not modified."""
        record = {"name_form": "X", "latitude": 60.0, "longitude": 5.0, "source_id": "1"}
        enrich_record_h3(record)
        assert "_h3_r7" not in record


class TestFindNeighbours:
    def test_ring_size_1(self) -> None:
        """Ring 1 returns 6 neighbours for a hexagonal cell."""
        index = lat_lng_to_h3(60.0, 10.0, resolution=9)
        neighbours = find_neighbours(index, ring_size=1)
        assert len(neighbours) == 6

    def test_ring_size_2(self) -> None:
        """Ring 2 returns more neighbours."""
        index = lat_lng_to_h3(60.0, 10.0, resolution=9)
        neighbours = find_neighbours(index, ring_size=2)
        assert len(neighbours) > 6


class TestH3Distance:
    def test_same_cell(self) -> None:
        """Distance to self is 0."""
        index = lat_lng_to_h3(60.0, 10.0)
        assert h3_distance(index, index) == 0

    def test_adjacent_cells(self) -> None:
        """Adjacent cells have distance 1."""
        index = lat_lng_to_h3(60.0, 10.0, resolution=9)
        neighbours = find_neighbours(index, ring_size=1)
        assert h3_distance(index, neighbours[0]) == 1

    def test_different_resolutions(self) -> None:
        """Different resolutions return -1."""
        r7 = lat_lng_to_h3(60.0, 10.0, resolution=7)
        r9 = lat_lng_to_h3(60.0, 10.0, resolution=9)
        assert h3_distance(r7, r9) == -1
