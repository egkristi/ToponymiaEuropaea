"""Tests for the Arabic/Moorish language module."""

from toponymia.languages.arabic import ArabicMoorishModule


class TestArabicMoorishModule:
    """Tests for ArabicMoorishModule."""

    def setup_method(self):
        self.module = ArabicMoorishModule()

    def test_metadata(self):
        assert self.module.language_code == "ar"
        assert "Arabic" in self.module.language_name
        assert "Afro-Asiatic" in self.module.family

    def test_prefixes_not_empty(self):
        assert len(self.module.prefixes) >= 10

    def test_suffixes_not_empty(self):
        assert len(self.module.suffixes) >= 5


class TestArabicSegmentation:
    """Tests for Arabic/Moorish segmentation."""

    def setup_method(self):
        self.module = ArabicMoorishModule()

    def test_segment_prefix_al(self):
        """Should detect al- (definite article)."""
        results = self.module.segment("Almería")
        assert len(results) >= 2
        assert results[0].lemma == "al"
        assert results[0].morph_type == "compound_head"

    def test_segment_prefix_guad(self):
        """Should detect Guad- (wadi) prefix."""
        results = self.module.segment("Guadalquivir")
        assert len(results) >= 2
        assert results[0].lemma == "guadal"

    def test_segment_prefix_beni(self):
        """Should detect Beni- (sons of) prefix."""
        results = self.module.segment("Benicàssim")
        assert len(results) >= 2
        assert results[0].lemma == "beni"

    def test_segment_prefix_medina(self):
        """Should detect Medina- (city) prefix."""
        results = self.module.segment("Medinaceli")
        assert len(results) >= 2
        assert results[0].lemma == "medina"

    def test_segment_prefix_alca(self):
        """Should detect Alca- (al-qal'a) prefix."""
        results = self.module.segment("Alcalá")
        assert len(results) >= 2
        assert results[0].lemma == "alca"

    def test_segment_unknown(self):
        """Should return simplex for unrecognized forms."""
        results = self.module.segment("xyz")
        assert len(results) == 1
        assert results[0].morph_type == "simplex"

    def test_segment_suffix_quivir(self):
        """Should detect -quivir (great) suffix."""
        results = self.module.segment("Guadalquivir")
        assert any(r.lemma == "quivir" or r.lemma == "guadal" for r in results)


class TestArabicClassification:
    """Tests for Arabic/Moorish classification."""

    def setup_method(self):
        self.module = ArabicMoorishModule()

    def test_classify_arabic_prefix(self):
        """Should classify name with al- as Arabic."""
        result = self.module.classify("Alhambra")
        assert result.confidence > 0.3
        assert any("prefix" in e for e in result.evidence)

    def test_classify_arabic_guad(self):
        """Should classify Guad- names as Arabic."""
        result = self.module.classify("Guadalajara")
        assert result.confidence > 0.3
        assert any("prefix" in e for e in result.evidence)

    def test_classify_non_arabic(self):
        """Should give low confidence for non-Arabic names."""
        result = self.module.classify("Stockholm")
        assert result.confidence < 0.2

    def test_classify_period_estimate(self):
        """Should include period for high-confidence matches."""
        result = self.module.classify("Alcázar")
        if result.confidence > 0.3:
            assert result.period_estimate is not None

    def test_classify_gibraltar(self):
        """Should classify Gibraltar (jabal Ṭāriq) as Arabic."""
        result = self.module.classify("Gibraltar")
        assert result.confidence > 0.3


class TestArabicEtymology:
    """Tests for Arabic/Moorish etymology."""

    def setup_method(self):
        self.module = ArabicMoorishModule()

    def test_etymologize_guad(self):
        """Should provide etymology for guad- (wadi)."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Guad",
                position=0,
                morph_type="compound_head",
                lemma="guad",
                confidence=0.8,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "river" in results[0].meaning or "valley" in results[0].meaning
        assert results[0].language_code == "ar"

    def test_etymologize_medina(self):
        """Should provide etymology for medina (city)."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Medina",
                position=0,
                morph_type="compound_head",
                lemma="medina",
                confidence=0.8,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "city" in results[0].meaning

    def test_etymologize_unknown(self):
        """Should return empty for unknown elements."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="xyz",
                position=0,
                morph_type="simplex",
                lemma="xyz",
                confidence=0.3,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 0
