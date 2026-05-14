"""Tests for the Latin language module."""

from toponymia.languages.latin import LatinModule


class TestLatinModuleMetadata:
    def setup_method(self):
        self.module = LatinModule()

    def test_language_code(self):
        assert self.module.language_code == "la"

    def test_language_name(self):
        assert self.module.language_name == "Latin"

    def test_family(self):
        assert self.module.family == "Indo-European"

    def test_branch(self):
        assert "Italic" in self.module.branch

    def test_has_suffixes(self):
        assert len(self.module.suffixes) > 15

    def test_has_prefixes(self):
        assert len(self.module.prefixes) > 5


class TestLatinSegmentation:
    def setup_method(self):
        self.module = LatinModule()

    def test_segment_castra_suffix(self):
        """Vinchester = Vin + chester."""
        results = self.module.segment("Winchester")
        assert len(results) == 2
        assert results[1].morph_type == "compound_head"
        assert results[1].lemma == "chester"

    def test_segment_street_suffix(self):
        """Stratford = Strat + ford... but 'street' suffix in Cheapstreet."""
        results = self.module.segment("Cheapstreet")
        assert len(results) == 2
        assert results[1].lemma == "street"

    def test_segment_aquae_prefix(self):
        """Aquae Sulis = Aquae + Sulis."""
        results = self.module.segment("Aquaesulis")
        assert len(results) == 2
        assert results[0].lemma == "aquae"

    def test_segment_unknown_name(self):
        """Unknown name returns single stem."""
        results = self.module.segment("Oslo")
        assert len(results) == 1
        assert results[0].morph_type == "stem"


class TestLatinClassification:
    def setup_method(self):
        self.module = LatinModule()

    def test_classify_chester(self):
        """Manchester has Latin suffix -chester."""
        result = self.module.classify("Manchester")
        assert result.confidence > 0.4
        assert any("suffix" in e for e in result.evidence)

    def test_classify_strata(self):
        """Stratton has Latin element strat-."""
        result = self.module.classify("Stratton")
        assert result.confidence > 0.1

    def test_classify_latin_ending(self):
        """Aquaesulis has Latin prefix."""
        result = self.module.classify("Aquaesulis")
        assert result.confidence > 0.3

    def test_classify_non_latin(self):
        """Pure Norse name should get low confidence."""
        result = self.module.classify("Torshov")
        assert result.confidence < 0.2


class TestLatinEtymology:
    def setup_method(self):
        self.module = LatinModule()

    def test_etymologize_castra(self):
        """castra element produces correct etymology."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="chester",
                position=1,
                morph_type="compound_head",
                lemma="chester",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "fort" in results[0].meaning

    def test_etymologize_strata(self):
        """strata/street element produces correct etymology."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="street",
                position=1,
                morph_type="compound_head",
                lemma="street",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "road" in results[0].meaning
