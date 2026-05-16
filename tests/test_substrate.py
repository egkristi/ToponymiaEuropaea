"""Tests for substrate detection module."""

from __future__ import annotations

from toponymia.nlp.substrate import PhonotacticModel, SubstrateDetector


class TestPhonotacticModel:
    """Test character n-gram phonotactic model."""

    def test_train_and_score(self) -> None:
        model = PhonotacticModel()
        model.train(["berg", "heim", "stad", "land", "vik"])
        # Known elements should score higher than random strings
        known_score = model.score("berg")
        random_score = model.score("xqzpt")
        assert known_score > random_score

    def test_similar_elements_score_high(self) -> None:
        model = PhonotacticModel()
        model.train(["berg", "borg", "burg", "mark", "stark"])
        # "barg" is similar to training data
        similar_score = model.score("barg")
        dissimilar_score = model.score("zzxx")
        assert similar_score > dissimilar_score

    def test_empty_model(self) -> None:
        model = PhonotacticModel()
        assert model.score("anything") == 0.0


class TestSubstrateDetector:
    """Test substrate detection."""

    def setup_method(self) -> None:
        self.detector = SubstrateDetector()
        self.detector.train()

    def test_known_ie_element_scores_high(self) -> None:
        result = self.detector.analyze("heim")
        # Known IE element should score above threshold
        assert result.score > self.detector.threshold

    def test_known_ie_no_reasons(self) -> None:
        result = self.detector.analyze("berg")
        # Standard IE element should have no substrate reasons
        assert result.possible_origin == ""

    def test_sami_indicator(self) -> None:
        result = self.detector.analyze("njargafjell")
        assert result.possible_origin == "sami"
        assert any("Sami" in r for r in result.reasons)

    def test_finnic_indicator(self) -> None:
        result = self.detector.analyze("lahtivuori")
        assert result.possible_origin == "finnic"
        assert any("Finnic" in r for r in result.reasons)

    def test_detect_batch(self) -> None:
        elements = ["berg", "heim", "njarganes", "stad", "guovdageaidnu"]
        candidates = self.detector.detect_batch(elements)
        # Should find at least the Sami-origin elements
        candidate_elements = [c.element for c in candidates]
        assert "njarganes" in candidate_elements

    def test_analyze_corpus(self) -> None:
        names = ["Nordheim", "Sandvik", "Njargafjell", "Bergen"]
        results = self.detector.analyze_corpus(names)
        # Njargafjell should be flagged
        assert "Njargafjell" in results

    def test_triple_vowel_detected(self) -> None:
        result = self.detector.analyze("kautokeaino")
        assert any("unusual pattern" in r for r in result.reasons)
