"""Tests for the Old High German language module."""

from toponymia.languages.old_high_german import OldHighGermanModule


class TestOldHighGermanModule:
    """Tests for OldHighGermanModule."""

    def setup_method(self):
        self.module = OldHighGermanModule()

    def test_metadata(self):
        assert self.module.language_code == "goh"
        assert "German" in self.module.language_name
        assert self.module.family == "Indo-European"

    def test_prefixes_not_empty(self):
        assert len(self.module.prefixes) >= 10

    def test_suffixes_not_empty(self):
        assert len(self.module.suffixes) >= 20


class TestOldHighGermanSegmentation:
    """Tests for OHG segmentation."""

    def setup_method(self):
        self.module = OldHighGermanModule()

    def test_segment_suffix_heim(self):
        """Should detect -heim suffix."""
        results = self.module.segment("Mannheim")
        assert len(results) == 2
        assert results[1].lemma == "heim"
        assert results[1].morph_type == "derivational_suffix"

    def test_segment_suffix_burg(self):
        """Should detect -burg suffix."""
        results = self.module.segment("Hamburg")
        assert len(results) == 2
        assert results[1].lemma == "burg"

    def test_segment_suffix_dorf(self):
        """Should detect -dorf suffix."""
        results = self.module.segment("Düsseldorf")
        assert any(r.lemma == "dorf" for r in results)

    def test_segment_prefix_neu(self):
        """Should detect Neu- prefix."""
        results = self.module.segment("Neustadt")
        assert len(results) >= 2
        assert results[0].lemma == "neu"
        assert results[0].morph_type == "compound_head"

    def test_segment_prefix_and_suffix(self):
        """Should detect both prefix and suffix."""
        results = self.module.segment("Neuenburg")
        lemmas = [r.lemma for r in results]
        assert "neu" in lemmas
        assert "burg" in lemmas

    def test_segment_suffix_ingen(self):
        """Should detect -ingen patronymic suffix."""
        results = self.module.segment("Tübingen")
        assert any(r.lemma == "ingen" for r in results)

    def test_segment_unknown(self):
        """Should return simplex for unrecognized forms."""
        results = self.module.segment("xyz")
        assert len(results) == 1
        assert results[0].morph_type == "simplex"

    def test_segment_suffix_weiler(self):
        """Should detect -weiler suffix."""
        results = self.module.segment("Badenweiler")
        assert any(r.lemma == "weiler" for r in results)


class TestOldHighGermanClassification:
    """Tests for OHG classification."""

    def setup_method(self):
        self.module = OldHighGermanModule()

    def test_classify_germanic_suffix(self):
        """Should classify name with -burg as Germanic."""
        result = self.module.classify("Salzburg")
        assert result.confidence > 0.2
        assert any("suffix" in e for e in result.evidence)

    def test_classify_germanic_prefix(self):
        """Should classify name with Ober- as Germanic."""
        result = self.module.classify("Oberhausen")
        assert result.confidence > 0.3
        assert any("prefix" in e or "suffix" in e for e in result.evidence)

    def test_classify_german_orthography(self):
        """Should detect German orthographic features."""
        result = self.module.classify("Schönbrunn")
        assert result.confidence > 0.2
        assert any("orthography" in e or "suffix" in e for e in result.evidence)

    def test_classify_non_germanic(self):
        """Should give low confidence for non-Germanic names."""
        result = self.module.classify("Bilbao")
        assert result.confidence < 0.2

    def test_classify_period_estimate(self):
        """Should include period for high-confidence matches."""
        result = self.module.classify("Heidelberg")
        if result.confidence > 0.3:
            assert result.period_estimate is not None


class TestOldHighGermanEtymology:
    """Tests for OHG etymology."""

    def setup_method(self):
        self.module = OldHighGermanModule()

    def test_etymologize_burg(self):
        """Should provide etymology for -burg element."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="burg",
                position=1,
                morph_type="derivational_suffix",
                lemma="burg",
                confidence=0.8,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "fortified" in results[0].meaning or "castle" in results[0].meaning
        assert results[0].language_code == "goh"

    def test_etymologize_heim(self):
        """Should provide etymology for -heim element."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="heim",
                position=1,
                morph_type="derivational_suffix",
                lemma="heim",
                confidence=0.8,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "home" in results[0].meaning or "settlement" in results[0].meaning

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
