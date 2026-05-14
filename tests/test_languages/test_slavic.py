"""Tests for the Old Slavic language module."""

from toponymia.languages.slavic import OldSlavicModule


class TestOldSlavicModule:
    """Tests for OldSlavicModule."""

    def setup_method(self):
        self.module = OldSlavicModule()

    def test_metadata(self):
        assert self.module.language_code == "sla"
        assert "Slavic" in self.module.language_name
        assert self.module.family == "Indo-European"

    def test_prefixes_not_empty(self):
        assert len(self.module.prefixes) > 10

    def test_suffixes_not_empty(self):
        assert len(self.module.suffixes) > 15


class TestOldSlavicSegmentation:
    """Tests for Slavic segmentation."""

    def setup_method(self):
        self.module = OldSlavicModule()

    def test_segment_suffix_ov(self):
        """Should detect -ov possessive suffix."""
        results = self.module.segment("Petrov")
        assert len(results) == 2
        assert results[1].lemma == "ov"
        assert results[1].morph_type == "derivational_suffix"

    def test_segment_suffix_grad(self):
        """Should detect -grad suffix."""
        results = self.module.segment("Beograd")
        assert len(results) == 2
        assert results[1].lemma == "grad"

    def test_segment_prefix_novo(self):
        """Should detect Novo- prefix."""
        results = self.module.segment("Novosibirsk")
        assert len(results) >= 2
        assert results[0].lemma == "novo"
        assert results[0].morph_type == "compound_head"

    def test_segment_prefix_and_suffix(self):
        """Should detect both prefix and suffix."""
        results = self.module.segment("Novogorod")
        assert len(results) >= 2
        # Should find novo- prefix and -gorod suffix
        lemmas = [r.lemma for r in results]
        assert "novo" in lemmas
        assert "gorod" in lemmas

    def test_segment_unknown(self):
        """Should return simplex for unrecognized forms."""
        results = self.module.segment("xyz")
        assert len(results) == 1
        assert results[0].morph_type == "simplex"

    def test_segment_suffix_ice(self):
        """Should detect -ice suffix (Czech place-names)."""
        results = self.module.segment("Budějovice")
        assert any(r.lemma == "ice" for r in results)


class TestOldSlavicClassification:
    """Tests for Slavic classification."""

    def setup_method(self):
        self.module = OldSlavicModule()

    def test_classify_slavic_suffix(self):
        """Should classify name with -grad as Slavic."""
        result = self.module.classify("Beograd")
        assert result.confidence > 0.2
        assert any("suffix" in e for e in result.evidence)

    def test_classify_slavic_prefix(self):
        """Should classify name with Novo- as Slavic."""
        result = self.module.classify("Novosibirsk")
        assert result.confidence > 0.2
        assert any("prefix" in e for e in result.evidence)

    def test_classify_slavic_character(self):
        """Should detect Slavic diacritics."""
        result = self.module.classify("Černigov")
        assert result.confidence > 0.1
        assert any("character" in e or "suffix" in e for e in result.evidence)

    def test_classify_non_slavic(self):
        """Should give low confidence for non-Slavic names."""
        result = self.module.classify("London")
        assert result.confidence < 0.2

    def test_classify_slavic_cluster(self):
        """Should detect Slavic consonant clusters."""
        result = self.module.classify("Strelka")
        assert result.confidence > 0.0


class TestOldSlavicEtymology:
    """Tests for Slavic etymology."""

    def setup_method(self):
        self.module = OldSlavicModule()

    def test_etymologize_grad(self):
        """Should provide etymology for -grad element."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="grad",
                position=1,
                morph_type="derivational_suffix",
                lemma="grad",
                confidence=0.8,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "fortified" in results[0].meaning or "city" in results[0].meaning
        assert results[0].language_code == "sla"

    def test_etymologize_novo(self):
        """Should provide etymology for novo- element."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Novo",
                position=0,
                morph_type="compound_head",
                lemma="novo",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "new" in results[0].meaning

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
