"""Tests for cross-source deduplication pipeline."""

from toponymia.pipelines.dedup import (
    DedupMatch,
    DedupReport,
    find_cross_source_duplicates,
)


class TestFindCrossSourceDuplicates:
    def _make_record(
        self,
        name: str,
        source: str,
        h3_r9: str = "890999bae1bffff",
        phonetic_key: str | None = None,
    ) -> dict:
        return {
            "name_form": name,
            "name_normalized": name.lower(),
            "_phonetic_key": phonetic_key or name.lower(),
            "_h3_r9": h3_r9,
            "source_dataset": source,
            "source_id": f"{source}:{name.lower()}",
            "latitude": 60.0,
            "longitude": 10.0,
        }

    def test_no_duplicates_same_source(self) -> None:
        """Records from the same source are never flagged."""
        records = [
            self._make_record("Oslo", "geonames"),
            self._make_record("Oslo", "geonames", phonetic_key="oslo"),
        ]
        report = find_cross_source_duplicates(records)
        assert report.duplicate_count == 0

    def test_cross_source_match_same_cell(self) -> None:
        """Same phonetic key + same H3 cell = high confidence match."""
        records = [
            self._make_record("Torshov", "geonames", phonetic_key="torshov"),
            self._make_record("Torshov", "kartverket_ssr", phonetic_key="torshov"),
        ]
        report = find_cross_source_duplicates(records)
        assert report.duplicate_count == 1
        assert report.matches[0].confidence >= 0.9
        assert report.matches[0].h3_distance == 0

    def test_cross_source_match_adjacent_cell(self) -> None:
        """Same phonetic key + adjacent H3 cells = good match."""
        import h3

        center = h3.latlng_to_cell(60.0, 10.0, 9)
        neighbours = h3.grid_disk(center, 1)
        adjacent = [c for c in neighbours if c != center][0]

        records = [
            self._make_record("Bergen", "geonames", h3_r9=center, phonetic_key="bergen"),
            self._make_record("Bergen", "kartverket_ssr", h3_r9=adjacent, phonetic_key="bergen"),
        ]
        report = find_cross_source_duplicates(records)
        assert report.duplicate_count == 1
        assert report.matches[0].confidence >= 0.8

    def test_no_match_distant_cells(self) -> None:
        """Same phonetic key but far apart = no match."""
        import h3

        # Use cells that are far apart but at same resolution
        cell_a = h3.latlng_to_cell(60.0, 10.0, 9)
        cell_b = h3.latlng_to_cell(62.0, 15.0, 9)  # ~200 km away

        records = [
            self._make_record("Vik", "geonames", h3_r9=cell_a, phonetic_key="vik"),
            self._make_record("Vik", "kartverket_ssr", h3_r9=cell_b, phonetic_key="vik"),
        ]
        report = find_cross_source_duplicates(records, max_h3_distance=3)
        # Cells are far apart (>3 H3 hops), so should be filtered out
        assert report.duplicate_count == 0

    def test_different_phonetic_keys_no_match(self) -> None:
        """Different phonetic keys = no match even if close."""
        records = [
            self._make_record("Oslo", "geonames", phonetic_key="oslo"),
            self._make_record("Bergen", "kartverket_ssr", phonetic_key="bergen"),
        ]
        report = find_cross_source_duplicates(records)
        assert report.duplicate_count == 0

    def test_report_statistics(self) -> None:
        """Report contains correct counts."""
        records = [
            self._make_record("Oslo", "geonames", phonetic_key="oslo"),
            self._make_record("Oslo", "kartverket_ssr", phonetic_key="oslo"),
            self._make_record("Bergen", "geonames", phonetic_key="bergen"),
        ]
        report = find_cross_source_duplicates(records)
        assert report.total_records == 3
        assert report.unique_keys == 2
        assert report.duplicate_count == 1
        assert "geonames" in report.sources_compared
        assert "kartverket_ssr" in report.sources_compared

    def test_empty_records(self) -> None:
        """Empty input produces empty report."""
        report = find_cross_source_duplicates([])
        assert report.total_records == 0
        assert report.duplicate_count == 0

    def test_multiple_matches_in_group(self) -> None:
        """Three sources with same key produce multiple pairs."""
        records = [
            self._make_record("Heim", "geonames", phonetic_key="heim"),
            self._make_record("Heim", "kartverket_ssr", phonetic_key="heim"),
            self._make_record("Heim", "wikidata", phonetic_key="heim"),
        ]
        report = find_cross_source_duplicates(records)
        # 3 sources, 3 cross-source pairs: geo↔kart, geo↔wiki, kart↔wiki
        assert report.duplicate_count == 3


class TestDedupMatch:
    def test_source_properties(self) -> None:
        match = DedupMatch(
            record_a={"source_dataset": "geonames", "name_form": "X"},
            record_b={"source_dataset": "kartverket_ssr", "name_form": "X"},
            phonetic_key="x",
            h3_distance=0,
            confidence=0.95,
        )
        assert match.source_a == "geonames"
        assert match.source_b == "kartverket_ssr"


class TestDedupReport:
    def test_high_confidence_count(self) -> None:
        report = DedupReport(
            total_records=10,
            unique_keys=5,
            matches=[
                DedupMatch(
                    record_a={},
                    record_b={},
                    phonetic_key="a",
                    h3_distance=0,
                    confidence=0.95,
                ),
                DedupMatch(
                    record_a={},
                    record_b={},
                    phonetic_key="b",
                    h3_distance=5,
                    confidence=0.3,
                ),
            ],
        )
        assert report.high_confidence_count == 1
        assert report.duplicate_count == 2
