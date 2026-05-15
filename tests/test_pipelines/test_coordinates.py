"""Tests for multi-source coordinate resolution pipeline."""

from toponymia.pipelines.coordinates import (
    CoordinateSource,
    CoordinateStatus,
    SourcePriority,
    detect_conflicts,
    haversine_distance,
    resolve_coordinates,
)


class TestHaversineDistance:
    """Test haversine distance calculation."""

    def test_same_point_is_zero(self) -> None:
        assert haversine_distance(59.9, 10.7, 59.9, 10.7) == 0.0

    def test_oslo_to_bergen(self) -> None:
        # Oslo (59.91, 10.75) to Bergen (60.39, 5.32) ≈ 305 km
        dist = haversine_distance(59.91, 10.75, 60.39, 5.32)
        assert 300_000 < dist < 310_000

    def test_short_distance(self) -> None:
        # Two points ~100m apart in Oslo
        dist = haversine_distance(59.9127, 10.7461, 59.9133, 10.7461)
        assert 50 < dist < 100

    def test_symmetry(self) -> None:
        d1 = haversine_distance(59.9, 10.7, 60.0, 10.8)
        d2 = haversine_distance(60.0, 10.8, 59.9, 10.7)
        assert abs(d1 - d2) < 0.01


class TestResolveCoordinates:
    """Test coordinate resolution algorithm."""

    def test_single_source(self) -> None:
        sources = [CoordinateSource(59.91, 10.75, "geonames", SourcePriority.GEONAMES)]
        result = resolve_coordinates(sources)
        assert result.status == CoordinateStatus.SINGLE_SOURCE
        assert result.latitude == 59.91
        assert result.source_id == "geonames"

    def test_priority_selection(self) -> None:
        sources = [
            CoordinateSource(59.91, 10.75, "geonames", SourcePriority.GEONAMES),
            CoordinateSource(59.9127, 10.7461, "kartverket", SourcePriority.NATIONAL_AUTHORITY),
        ]
        result = resolve_coordinates(sources)
        # Kartverket should win (higher priority = lower number)
        assert result.source_id == "kartverket"
        assert result.latitude == 59.9127

    def test_minor_divergence_resolved(self) -> None:
        # Two sources ~50m apart
        sources = [
            CoordinateSource(59.9127, 10.7461, "kartverket", SourcePriority.NATIONAL_AUTHORITY),
            CoordinateSource(59.9130, 10.7461, "geonames", SourcePriority.GEONAMES),
        ]
        result = resolve_coordinates(sources)
        assert result.status == CoordinateStatus.RESOLVED
        assert result.max_divergence_m < 100

    def test_major_divergence_conflict(self) -> None:
        # Two sources >1km apart
        sources = [
            CoordinateSource(59.91, 10.75, "kartverket", SourcePriority.NATIONAL_AUTHORITY),
            CoordinateSource(59.93, 10.75, "wikidata", SourcePriority.WIKIDATA),
        ]
        result = resolve_coordinates(sources)
        assert result.status == CoordinateStatus.CONFLICT
        assert result.max_divergence_m > 1000

    def test_provenance_stored(self) -> None:
        sources = [
            CoordinateSource(59.91, 10.75, "geonames", SourcePriority.GEONAMES),
            CoordinateSource(59.9127, 10.7461, "kartverket", SourcePriority.NATIONAL_AUTHORITY),
        ]
        result = resolve_coordinates(sources)
        assert "geonames" in result.provenance
        assert "kartverket" in result.provenance
        assert result.provenance["kartverket"] == [59.9127, 10.7461]

    def test_empty_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="At least one"):
            resolve_coordinates([])


class TestDetectConflicts:
    """Test conflict detection across record groups."""

    def test_no_conflicts(self) -> None:
        records = [
            {"_phonetic_key": "oslo", "latitude": 59.91, "longitude": 10.75, "source_id": "a"},
            {"_phonetic_key": "oslo", "latitude": 59.9101, "longitude": 10.7501, "source_id": "b"},
        ]
        conflicts = detect_conflicts(records)
        assert len(conflicts) == 0

    def test_detects_conflict(self) -> None:
        records = [
            {"_phonetic_key": "oslo", "latitude": 59.91, "longitude": 10.75, "source_id": "a"},
            {"_phonetic_key": "oslo", "latitude": 60.00, "longitude": 10.75, "source_id": "b"},
        ]
        conflicts = detect_conflicts(records)
        assert len(conflicts) == 1
        assert conflicts[0]["group_key"] == "oslo"
        assert conflicts[0]["max_divergence_m"] > 1000

    def test_separate_groups_no_conflict(self) -> None:
        records = [
            {"_phonetic_key": "oslo", "latitude": 59.91, "longitude": 10.75, "source_id": "a"},
            {"_phonetic_key": "bergen", "latitude": 60.39, "longitude": 5.32, "source_id": "b"},
        ]
        conflicts = detect_conflicts(records)
        assert len(conflicts) == 0
