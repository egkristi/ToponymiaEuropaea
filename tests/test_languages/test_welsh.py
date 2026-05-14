"""Tests for the Welsh language module."""

from toponymia.languages.welsh import WelshModule


class TestWelshModuleMetadata:
    def setup_method(self):
        self.module = WelshModule()

    def test_language_code(self):
        assert self.module.language_code == "cy"

    def test_language_name(self):
        assert self.module.language_name == "Welsh"

    def test_family(self):
        assert self.module.family == "Indo-European"

    def test_branch(self):
        assert "Brythonic" in self.module.branch

    def test_has_prefixes(self):
        assert len(self.module.prefixes) > 20

    def test_has_suffixes(self):
        assert len(self.module.suffixes) > 5


class TestWelshSegmentation:
    def setup_method(self):
        self.module = WelshModule()

    def test_segment_llan_prefix(self):
        """Llandudno = Llan + dudno."""
        results = self.module.segment("Llandudno")
        assert len(results) == 2
        assert results[0].morph_type == "compound_head"
        assert results[0].lemma == "llan"

    def test_segment_aber_prefix(self):
        """Aberystwyth = Aber + ystwyth."""
        results = self.module.segment("Aberystwyth")
        assert len(results) == 2
        assert results[0].lemma == "aber"

    def test_segment_pen_prefix(self):
        """Penrhyn = Pen + rhyn."""
        results = self.module.segment("Penrhyn")
        assert len(results) == 2
        assert results[0].lemma == "pen"

    def test_segment_cwm_prefix(self):
        """Cwmbran = Cwm + bran."""
        results = self.module.segment("Cwmbran")
        assert len(results) == 2
        assert results[0].lemma == "cwm"

    def test_segment_unknown_name(self):
        """Unknown name returns single stem."""
        results = self.module.segment("Xyz")
        assert len(results) == 1
        assert results[0].morph_type == "stem"


class TestWelshClassification:
    def setup_method(self):
        self.module = WelshModule()

    def test_classify_llan_prefix(self):
        """Llanfair has clear Welsh prefix."""
        result = self.module.classify("Llanfair")
        assert result.confidence > 0.5
        assert any("prefix" in e for e in result.evidence)

    def test_classify_ll_digraph(self):
        """Names with 'll' show Welsh orthography."""
        result = self.module.classify("Llangollen")
        assert result.confidence > 0.5

    def test_classify_aber(self):
        """Aber- is distinctly Welsh."""
        result = self.module.classify("Aberdare")
        assert result.confidence > 0.4

    def test_classify_non_welsh(self):
        """English name should get low confidence."""
        result = self.module.classify("London")
        assert result.confidence < 0.3


class TestWelshEtymology:
    def setup_method(self):
        self.module = WelshModule()

    def test_etymologize_llan(self):
        """llan element produces correct etymology."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Llan",
                position=0,
                morph_type="compound_head",
                lemma="llan",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "church" in results[0].meaning

    def test_etymologize_pen(self):
        """pen element produces correct etymology."""
        from toponymia.languages.base import SegmentationResult

        comps = [
            SegmentationResult(
                component="Pen",
                position=0,
                morph_type="compound_head",
                lemma="pen",
                confidence=0.7,
            )
        ]
        results = self.module.etymologize(comps)
        assert len(results) == 1
        assert "head" in results[0].meaning
