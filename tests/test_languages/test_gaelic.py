"""Tests for the Irish/Scottish Gaelic language module."""

from toponymia.languages.gaelic import GaelicModule


class TestGaelicModuleMetadata:
    def setup_method(self):
        self.module = GaelicModule()

    def test_language_code(self):
        assert self.module.language_code == "ga"

    def test_language_name(self):
        assert self.module.language_name == "Irish/Scottish Gaelic"

    def test_family(self):
        assert self.module.family == "Indo-European"

    def test_branch(self):
        assert "Goidelic" in self.module.branch

    def test_has_prefixes(self):
        assert len(self.module.prefixes) > 20

    def test_has_suffixes(self):
        assert len(self.module.suffixes) > 5


class TestGaelicSegmentation:
    def setup_method(self):
        self.module = GaelicModule()

    def test_segment_baile_prefix(self):
        """Ballycastle = Bally + castle."""
        results = self.module.segment("Ballycastle")
        assert len(results) == 2
        assert results[0].morph_type == "compound_head"
        assert results[0].lemma == "bally"

    def test_segment_kill_prefix(self):
        """Killarney = Kill + arney."""
        results = self.module.segment("Killarney")
        assert len(results) == 2
        assert results[0].lemma == "kill"

    def test_segment_drum_prefix(self):
        """Drumcondra = Drum + condra."""
        results = self.module.segment("Drumcondra")
        assert len(results) == 2
        assert results[0].lemma == "drum"

    def test_segment_glen_prefix(self):
        """Glendalough = Glen + dalough."""
        results = self.module.segment("Glendalough")
        assert len(results) == 2
        assert results[0].lemma == "glen"

    def test_segment_unknown_name(self):
        """Unknown name returns single stem."""
        results = self.module.segment("Xyz")
        assert len(results) == 1
        assert results[0].morph_type == "stem"


class TestGaelicClassification:
    def setup_method(self):
        self.module = GaelicModule()

    def test_classify_bally_prefix(self):
        """Ballymena has clear Gaelic prefix."""
        result = self.module.classify("Ballymena")
        assert result.confidence > 0.4
        assert any("prefix" in e for e in result.evidence)

    def test_classify_derry(self):
        """Derry has Gaelic prefix."""
        result = self.module.classify("Derrymore")
        assert result.confidence > 0.4

    def test_classify_lenition(self):
        """Names with 'bh', 'gh' etc show Gaelic lenition."""
        result = self.module.classify("Ráth Bhoth")
        assert result.confidence > 0.3

    def test_classify_non_gaelic(self):
        """English name should get low confidence."""
        result = self.module.classify("London")
        assert result.confidence < 0.3


class TestGaelicEtymology:
    def setup_method(self):
        self.module = GaelicModule()

    def test_etymologize_baile(self):
        """baile element produces correct etymology."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Bally",
                position=0,
                morph_type="compound_head",
                lemma="bally",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert results[0].meaning == "town, townland (Anglicized)"

    def test_etymologize_loch(self):
        """loch element produces correct etymology."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Loch",
                position=0,
                morph_type="compound_head",
                lemma="loch",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "lake" in results[0].meaning
