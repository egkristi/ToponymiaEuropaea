"""Tests for the Basque language module."""

from toponymia.languages.basque import BasqueModule


class TestBasqueModule:
    """Tests for BasqueModule."""

    def setup_method(self):
        self.module = BasqueModule()

    def test_metadata(self):
        assert self.module.language_code == "eu"
        assert "Basque" in self.module.language_name
        assert "isolate" in self.module.family.lower()

    def test_prefixes_not_empty(self):
        assert len(self.module.prefixes) > 10

    def test_suffixes_not_empty(self):
        assert len(self.module.suffixes) > 10


class TestBasqueSegmentation:
    """Tests for Basque segmentation."""

    def setup_method(self):
        self.module = BasqueModule()

    def test_segment_prefix_harri(self):
        """Should detect harri- (stone) prefix."""
        results = self.module.segment("Harriaga")
        assert len(results) >= 2
        assert results[0].lemma == "harri"
        assert results[0].morph_type == "compound_head"

    def test_segment_prefix_mendi(self):
        """Should detect mendi- (mountain) prefix."""
        results = self.module.segment("Mendizorrotz")
        assert len(results) >= 2
        assert results[0].lemma == "mendi"

    def test_segment_suffix_aga(self):
        """Should detect -aga (place of) suffix."""
        results = self.module.segment("Arriaga")
        assert any(r.lemma == "aga" for r in results)
        assert any(r.morph_type == "derivational_suffix" for r in results)

    def test_segment_suffix_eta(self):
        """Should detect -eta suffix."""
        results = self.module.segment("Gasteizeta")
        assert any(r.lemma == "eta" for r in results)

    def test_segment_prefix_etxe(self):
        """Should detect etxe- (house) prefix."""
        results = self.module.segment("Etxeberri")
        assert len(results) >= 2
        assert results[0].lemma == "etxe"

    def test_segment_prefix_and_suffix(self):
        """Should detect both prefix and suffix."""
        results = self.module.segment("Ibargoien")
        lemmas = [r.lemma for r in results]
        assert "ibar" in lemmas
        assert "goien" in lemmas

    def test_segment_unknown(self):
        """Should return simplex for unrecognized forms."""
        results = self.module.segment("xyz")
        assert len(results) == 1
        assert results[0].morph_type == "simplex"

    def test_segment_known_element(self):
        """Should recognize whole-form known elements."""
        results = self.module.segment("mendi")
        assert len(results) == 1
        assert results[0].confidence > 0.5


class TestBasqueClassification:
    """Tests for Basque classification."""

    def setup_method(self):
        self.module = BasqueModule()

    def test_classify_basque_element(self):
        """Should classify name with Basque element."""
        result = self.module.classify("Mendizabal")
        assert result.confidence > 0.2
        assert any("element" in e for e in result.evidence)

    def test_classify_basque_suffix(self):
        """Should classify name with Basque suffix."""
        result = self.module.classify("Arriaga")
        assert result.confidence > 0.2
        assert any("suffix" in e or "element" in e for e in result.evidence)

    def test_classify_basque_phonology(self):
        """Should detect Basque phonological features (tx, tz)."""
        result = self.module.classify("Etxebarri")
        assert result.confidence > 0.3
        assert any("phoneme" in e or "element" in e for e in result.evidence)

    def test_classify_non_basque(self):
        """Should give low confidence for non-Basque names."""
        result = self.module.classify("Stockholm")
        assert result.confidence < 0.2

    def test_classify_period_estimate(self):
        """Should include period estimate for high-confidence matches."""
        result = self.module.classify("Mendizabal")
        if result.confidence > 0.3:
            assert result.period_estimate is not None


class TestBasqueEtymology:
    """Tests for Basque etymology."""

    def setup_method(self):
        self.module = BasqueModule()

    def test_etymologize_harri(self):
        """Should provide etymology for harri (stone)."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Harri",
                position=0,
                morph_type="compound_head",
                lemma="harri",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "stone" in results[0].meaning or "rock" in results[0].meaning
        assert results[0].language_code == "eu"

    def test_etymologize_mendi(self):
        """Should provide etymology for mendi (mountain)."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Mendi",
                position=0,
                morph_type="compound_head",
                lemma="mendi",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "mountain" in results[0].meaning

    def test_etymologize_suffix_aga(self):
        """Should provide etymology for -aga (place of)."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="aga",
                position=1,
                morph_type="derivational_suffix",
                lemma="aga",
                confidence=0.8,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "place" in results[0].meaning

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
