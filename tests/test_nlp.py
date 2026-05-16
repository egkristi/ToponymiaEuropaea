"""Tests for NLP modules: Morfessor segmentation and cognate detection."""

from __future__ import annotations

import pytest

from toponymia.nlp.cognates import CognateDetector


class TestCognateDetector:
    """Test cross-lingual cognate detection."""

    def setup_method(self) -> None:
        self.detector = CognateDetector()

    def test_detect_known_cognate(self) -> None:
        matches = self.detector.detect("berg", language="nor")
        assert len(matches) >= 1
        assert matches[0].proto_form == "*bergaz"
        assert matches[0].meaning == "mountain, rock"
        assert matches[0].confidence >= 0.7

    def test_detect_english_cognate(self) -> None:
        matches = self.detector.detect("stead", language="eng")
        assert len(matches) >= 1
        assert matches[0].proto_form == "*stadiz"

    def test_detect_heim_cognate(self) -> None:
        matches = self.detector.detect("heim", language="nor")
        assert len(matches) >= 1
        assert matches[0].meaning == "home, settlement"
        # Check that cognate list includes German and English forms
        cognates_str = " ".join(matches[0].cognates)
        assert "deu:Heim" in cognates_str
        assert "eng:ham" in cognates_str

    def test_detect_unknown_element(self) -> None:
        matches = self.detector.detect("xyzzy")
        assert matches == []

    def test_find_cognates_for_name(self) -> None:
        results = self.detector.find_cognates_for_name(["sand", "vik"], language="nor")
        assert "vik" in results
        assert results["vik"][0].proto_form == "*wikō"

    def test_confidence_higher_with_language(self) -> None:
        matches_with_lang = self.detector.detect("berg", language="nor")
        matches_without_lang = self.detector.detect("berg")
        assert matches_with_lang[0].confidence > matches_without_lang[0].confidence


class TestMorfessorSegmenter:
    """Test Morfessor-based segmentation (requires morfessor package)."""

    @pytest.fixture
    def segmenter(self):
        try:
            from toponymia.nlp import MorfessorSegmenter
        except ImportError:
            pytest.skip("morfessor not installed")
        return MorfessorSegmenter()

    def test_train_and_segment(self, segmenter) -> None:
        # Train on a small corpus of Norwegian place names
        corpus = [
            "Trondheim",
            "Solheim",
            "Nordheim",
            "Sandheim",
            "Sandvik",
            "Nordvik",
            "Sørvik",
            "Narvik",
            "Nordfjord",
            "Sognefjord",
            "Hardangerfjord",
            "Nordland",
            "Rogaland",
            "Vestland",
            "Hallingdal",
            "Gudbrandsdal",
            "Østerdal",
            "Lillehammer",
            "Lillestrom",
            "Lillesand",
            "Haugesund",
            "Haugseter",
            "Haugstad",
            "Sandnes",
            "Dramnes",
            "Bygdøynes",
        ] * 5  # Repeat for frequency

        segmenter.train(corpus)
        assert segmenter.trained
        assert segmenter.corpus_size > 0

        # Segment a name
        results = segmenter.segment("Sandheim")
        assert len(results) >= 1
        components = [r.component for r in results]
        # Should find at least some split (exact split depends on model)
        assert len("".join(components)) > 0

    def test_untrained_raises(self, segmenter) -> None:
        with pytest.raises(RuntimeError, match="not trained"):
            segmenter.segment("Nordheim")

    def test_segment_batch(self, segmenter) -> None:
        corpus = ["Nordheim", "Sandvik", "Hallingdal"] * 10
        segmenter.train(corpus)
        results = segmenter.segment_batch(["Nordheim", "Sandvik"])
        assert "Nordheim" in results
        assert "Sandvik" in results
