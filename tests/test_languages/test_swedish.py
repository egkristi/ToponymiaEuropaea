"""Tests for the Swedish language module."""

from toponymia.languages.swedish import SwedishModule


class TestSwedishModuleMetadata:
    def setup_method(self):
        self.module = SwedishModule()

    def test_language_code(self):
        assert self.module.language_code == "sv"

    def test_language_name(self):
        assert self.module.language_name == "Swedish"

    def test_family(self):
        assert self.module.family == "Indo-European"

    def test_branch(self):
        assert "East Scandinavian" in self.module.branch

    def test_has_suffixes(self):
        assert len(self.module.suffixes) > 20

    def test_has_prefixes(self):
        assert len(self.module.prefixes) > 5


class TestSwedishSegmentation:
    def setup_method(self):
        self.module = SwedishModule()

    def test_segment_by_suffix(self):
        """Sigtunaby = Sigtuna + by."""
        results = self.module.segment("Karlsby")
        assert len(results) == 2
        assert results[0].morph_type == "compound_modifier"
        assert results[1].morph_type == "compound_head"
        assert results[1].lemma == "by"

    def test_segment_torp_suffix(self):
        """Nytorp = Ny + torp."""
        results = self.module.segment("Nytorp")
        assert len(results) == 2
        assert results[1].lemma == "torp"

    def test_segment_rud_suffix(self):
        """Fagerud = Fage + rud."""
        results = self.module.segment("Fagerud")
        assert len(results) == 2
        assert results[1].lemma == "rud"

    def test_segment_berg_suffix(self):
        """Hallsberg = Halls + berg."""
        results = self.module.segment("Hallsberg")
        assert len(results) == 2
        assert results[1].lemma == "berg"

    def test_segment_holm_suffix(self):
        """Stockholm = Stock + holm."""
        results = self.module.segment("Stockholm")
        assert len(results) == 2
        assert results[1].lemma == "holm"

    def test_segment_sjo_suffix(self):
        """Mälarsjö = Mälar + sjö."""
        results = self.module.segment("Storsjö")
        assert len(results) == 2
        assert results[1].lemma == "sjö"

    def test_segment_lund_suffix(self):
        """Björklund = Björk + lund."""
        results = self.module.segment("Björklund")
        assert len(results) == 2
        assert results[1].lemma == "lund"

    def test_segment_unsegmentable(self):
        """Short names get single-stem result."""
        results = self.module.segment("Ud")
        assert len(results) >= 1
        assert results[0].morph_type == "stem"


class TestSwedishClassification:
    def setup_method(self):
        self.module = SwedishModule()

    def test_classify_torp_suffix(self):
        result = self.module.classify("Nytorp")
        assert result.confidence >= 0.4
        assert result.language_code == "sv"

    def test_classify_swedish_specific(self):
        """Köping is distinctly Swedish."""
        result = self.module.classify("Linköping")
        assert result.confidence >= 0.6
        assert any("Swedish" in e for e in result.evidence)

    def test_classify_with_prefix(self):
        result = self.module.classify("Storberg")
        assert result.confidence >= 0.7
        assert any("prefix" in e for e in result.evidence)

    def test_classify_unknown(self):
        result = self.module.classify("Xyz")
        assert result.confidence < 0.3


class TestSwedishEtymology:
    def setup_method(self):
        self.module = SwedishModule()

    def test_etymology_torp(self):
        etym = self.module.get_etymology("torp")
        assert etym is not None
        assert "farm" in etym.meaning

    def test_etymology_rud(self):
        etym = self.module.get_etymology("rud")
        assert etym is not None
        assert "clearing" in etym.meaning

    def test_etymology_sjo(self):
        etym = self.module.get_etymology("sjö")
        assert etym is not None
        assert "lake" in etym.meaning

    def test_etymology_as(self):
        etym = self.module.get_etymology("ås")
        assert etym is not None
        assert "ridge" in etym.meaning

    def test_etymology_unknown(self):
        etym = self.module.get_etymology("xyzzy")
        assert etym is None
