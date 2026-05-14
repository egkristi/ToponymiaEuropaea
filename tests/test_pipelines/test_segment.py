"""Tests for the segmentation pipeline including attestation form analysis."""

from toponymia.languages.old_norse import OldNorseModule
from toponymia.pipelines.segment import RecordAnalysis, SegmentationPipeline


def _make_pipeline() -> SegmentationPipeline:
    pipeline = SegmentationPipeline()
    pipeline.register_module(OldNorseModule())
    return pipeline


class TestSegmentationPipeline:
    """Tests for basic segmentation."""

    def test_segment_known_suffix(self):
        pipeline = _make_pipeline()
        hyps = pipeline.segment("Trondheim")
        assert len(hyps) > 0
        h = hyps[0]
        assert h.form == "Trondheim"
        assert any(c.component == "heim" for c in h.components)

    def test_segment_no_match_returns_empty(self):
        pipeline = _make_pipeline()
        hyps = pipeline.segment("Xyzzyplugh")
        assert hyps == []

    def test_segment_batch(self):
        pipeline = _make_pipeline()
        results = pipeline.segment_batch(["Trondheim", "Narvik"])
        assert "Trondheim" in results
        assert "Narvik" in results
        assert len(results["Trondheim"]) > 0
        assert len(results["Narvik"]) > 0

    def test_hypothesis_confidence(self):
        pipeline = _make_pipeline()
        hyps = pipeline.segment("Trondheim")
        h = hyps[0]
        assert h.overall_confidence > 0.0
        assert h.language.confidence > 0.0


class TestSegmentRecord:
    """Tests for segment_record with attestation forms."""

    def test_segment_record_modern_form(self):
        pipeline = _make_pipeline()
        record = {"name_form": "Trondheim", "source_id": "test"}
        analysis = pipeline.segment_record(record)
        assert isinstance(analysis, RecordAnalysis)
        assert analysis.name_form == "Trondheim"
        assert analysis.is_segmented
        assert analysis.best_form == "Trondheim"

    def test_segment_record_prefers_historical_form(self):
        """Bergen can't be segmented, but Bjǫrgvin can."""
        pipeline = _make_pipeline()
        record = {
            "name_form": "Bergen",
            "place_id": "Q26793",
            "attestations": [
                {"form": "Bjǫrgvin", "language_code": "non", "year_from": 1070},
                {"form": "Bergen", "language_code": "nob", "year_from": 1450},
            ],
        }
        analysis = pipeline.segment_record(record)
        assert analysis.is_segmented
        assert analysis.best_form == "Bjǫrgvin"
        assert analysis.place_id == "Q26793"
        # Should find bjǫrg + vin
        comps = analysis.best_hypothesis.components
        assert any("vin" in c.component.lower() for c in comps)

    def test_segment_record_oslo_historical(self):
        """Oslo modern form now segments (Os+lo), but Ósló also works."""
        pipeline = _make_pipeline()
        record = {
            "name_form": "Oslo",
            "place_id": "Q585",
            "attestations": [
                {"form": "Ósló", "language_code": "non", "year_from": 1048},
                {"form": "Oslo", "language_code": "nob", "year_from": 1925},
            ],
        }
        analysis = pipeline.segment_record(record)
        assert analysis.is_segmented
        # Best should be compound — either Ósló or Oslo
        comps = analysis.best_hypothesis.components
        assert len(comps) == 2

    def test_segment_record_no_attestations(self):
        """Record without attestations still works."""
        pipeline = _make_pipeline()
        record = {"name_form": "Kirkenes", "source_id": "test"}
        analysis = pipeline.segment_record(record)
        assert analysis.is_segmented
        assert analysis.best_form == "Kirkenes"

    def test_segment_record_unsegmentable(self):
        """Record that can't be segmented at all."""
        pipeline = _make_pipeline()
        record = {"name_form": "Xyzzy", "source_id": "test"}
        analysis = pipeline.segment_record(record)
        assert not analysis.is_segmented
        assert analysis.best_hypothesis is None

    def test_all_hypotheses_populated(self):
        """All forms are analyzed and stored."""
        pipeline = _make_pipeline()
        record = {
            "name_form": "Trondheim",
            "attestations": [
                {"form": "Niðaróss", "language_code": "non"},
                {"form": "Trondhjem", "language_code": "dan"},
            ],
        }
        analysis = pipeline.segment_record(record)
        assert "Trondheim" in analysis.all_hypotheses
        assert "Niðaróss" in analysis.all_hypotheses
        assert "Trondhjem" in analysis.all_hypotheses

    def test_segment_record_deduplicates_forms(self):
        """Same form in attestations as name_form is not analyzed twice."""
        pipeline = _make_pipeline()
        record = {
            "name_form": "Trondheim",
            "attestations": [
                {"form": "Trondheim", "language_code": "nob"},
            ],
        }
        analysis = pipeline.segment_record(record)
        # Should only have one entry for Trondheim
        assert len(analysis.all_hypotheses) == 1
