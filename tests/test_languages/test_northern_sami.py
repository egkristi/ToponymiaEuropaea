"""Tests for the Northern Sámi language module."""

from toponymia.languages.base import SegmentationResult
from toponymia.languages.northern_sami import NorthernSamiModule


class TestNorthernSamiModule:
    """Tests for NorthernSamiModule."""

    def setup_method(self):
        self.module = NorthernSamiModule()

    def test_metadata(self):
        assert self.module.language_code == "sme"
        assert self.module.language_name == "Northern Sámi"
        assert self.module.family == "Uralic"
        assert "Sámi" in self.module.branch

    def test_classify_javri(self):
        """Test classification of lake name."""
        result = self.module.classify("Stuorrajávri")
        assert result.confidence > 0.5
        assert any("jávri" in e for e in result.evidence)

    def test_classify_johka(self):
        """Test classification of river name."""
        result = self.module.classify("Áltajohka")
        assert result.confidence > 0.5
        assert any("johka" in e for e in result.evidence)

    def test_classify_varri(self):
        """Test classification of mountain name."""
        result = self.module.classify("Hálditčohkka")
        assert result.confidence > 0.5

    def test_classify_with_sami_chars(self):
        """Test that Sámi orthographic chars boost confidence."""
        result = self.module.classify("Čáhcesuolu")
        assert result.confidence > 0.5
        assert any("orthographic" in e for e in result.evidence)

    def test_classify_non_sami(self):
        """Test that non-Sámi name scores low."""
        result = self.module.classify("Birmingham")
        assert result.confidence < 0.3

    def test_classify_norwegian_name(self):
        """Test that Norwegian-form name (without Sámi elements) scores low."""
        result = self.module.classify("Trondheim")
        assert result.confidence < 0.3

    def test_segment_lake_name(self):
        """Test segmentation of a lake name."""
        results = self.module.segment("Stuorrajávri")
        assert len(results) == 2
        assert results[0].morph_type == "compound_modifier"
        assert results[1].morph_type == "compound_head"
        assert results[1].lemma == "jávri"
        assert "lake" in results[1].meaning

    def test_segment_river_name(self):
        """Test segmentation of a river name."""
        results = self.module.segment("Áltajohka")
        assert len(results) == 2
        assert results[1].lemma == "johka"
        assert "river" in results[1].meaning

    def test_segment_island_name(self):
        """Test segmentation of an island name."""
        results = self.module.segment("Čáhcesuolu")
        assert len(results) == 2
        assert results[1].lemma == "suolu"
        assert "island" in results[1].meaning

    def test_segment_headland(self):
        """Test segmentation of a headland name."""
        results = self.module.segment("Geavvanjárga")
        assert len(results) >= 1
        # njárga or related form
        assert any(r.morph_type == "compound_head" for r in results)

    def test_segment_unknown_form(self):
        """Test segmentation of unrecognized form."""
        results = self.module.segment("Stockholm")
        assert len(results) == 1
        assert results[0].morph_type == "stem"
        assert results[0].confidence < 0.5

    def test_etymologize_javri(self):
        """Test etymology of lake element."""
        comps = [
            SegmentationResult(
                component="jávri",
                position=1,
                morph_type="compound_head",
                lemma="jávri",
            ),
        ]
        candidates = self.module.etymologize(comps)
        assert len(candidates) >= 1
        assert "lake" in candidates[0].meaning
        assert candidates[0].language_code == "sme"

    def test_etymologize_johka(self):
        """Test etymology of river element."""
        comps = [
            SegmentationResult(
                component="johka",
                position=1,
                morph_type="compound_head",
                lemma="johka",
            ),
        ]
        candidates = self.module.etymologize(comps)
        assert len(candidates) >= 1
        assert "river" in candidates[0].meaning

    def test_etymologize_varri(self):
        """Test etymology of mountain element."""
        comps = [
            SegmentationResult(
                component="várri",
                position=1,
                morph_type="compound_head",
                lemma="várri",
            ),
        ]
        candidates = self.module.etymologize(comps)
        assert len(candidates) >= 1
        assert "mountain" in candidates[0].meaning or "fell" in candidates[0].meaning

    def test_etymologize_with_cognates(self):
        """Test that etymology includes cognate forms."""
        comps = [
            SegmentationResult(
                component="eatnu",
                position=0,
                morph_type="compound_head",
                lemma="eatnu",
            ),
        ]
        candidates = self.module.etymologize(comps)
        assert len(candidates) >= 1
        assert len(candidates[0].cognates) > 0
        assert any("Finnish" in c for c in candidates[0].cognates)
