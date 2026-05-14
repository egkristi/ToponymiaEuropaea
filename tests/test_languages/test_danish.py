"""Tests for the Danish language module."""

from toponymia.languages.danish import DanishModule


class TestDanishModuleMetadata:
    def setup_method(self):
        self.module = DanishModule()

    def test_language_code(self):
        assert self.module.language_code == "da"

    def test_language_name(self):
        assert self.module.language_name == "Danish"

    def test_family(self):
        assert self.module.family == "Indo-European"

    def test_branch(self):
        assert "East Scandinavian" in self.module.branch

    def test_has_suffixes(self):
        assert len(self.module.suffixes) > 20

    def test_has_prefixes(self):
        assert len(self.module.prefixes) > 5


class TestDanishSegmentation:
    def setup_method(self):
        self.module = DanishModule()

    def test_segment_by_suffix(self):
        """Roskildeby = Roskilde + by."""
        results = self.module.segment("Vestby")
        assert len(results) == 2
        assert results[0].morph_type == "compound_modifier"
        assert results[1].morph_type == "compound_head"
        assert results[1].lemma == "by"

    def test_segment_torp_suffix(self):
        """Hylletorp = Hylle + torp."""
        results = self.module.segment("Hylletorp")
        assert len(results) == 2
        assert results[1].lemma == "torp"

    def test_segment_drup_suffix(self):
        """Tåstrup = Tås + trup (lenited torp)."""
        results = self.module.segment("Tåstrup")
        assert len(results) == 2
        assert results[1].lemma == "trup"

    def test_segment_toft_suffix(self):
        """Kirstinetofte = Kirstine + tofte."""
        results = self.module.segment("Kirstinetofte")
        assert len(results) == 2
        assert results[1].lemma == "tofte"

    def test_segment_lev_suffix(self):
        """Herlev = Her + lev."""
        results = self.module.segment("Herlev")
        assert len(results) == 2
        assert results[1].lemma == "lev"

    def test_segment_loese_suffix(self):
        """Kirkeløse = Kirke + løse."""
        results = self.module.segment("Kirkeløse")
        assert len(results) == 2
        assert results[1].lemma == "løse"

    def test_segment_holm_suffix(self):
        """Bornholm = Born + holm."""
        results = self.module.segment("Bornholm")
        assert len(results) == 2
        assert results[1].lemma == "holm"

    def test_segment_unsegmentable(self):
        """Short names get single-stem result."""
        results = self.module.segment("Ry")
        assert len(results) >= 1
        assert results[0].morph_type == "stem"


class TestDanishClassification:
    def setup_method(self):
        self.module = DanishModule()

    def test_classify_by_suffix(self):
        result = self.module.classify("Herlev")
        assert result.confidence >= 0.4
        assert result.language_code == "da"

    def test_classify_danish_lenited(self):
        """Lenited -drup is distinctly Danish."""
        result = self.module.classify("Gadstrup")
        assert result.confidence >= 0.6
        assert any("lenited" in e for e in result.evidence)

    def test_classify_with_prefix(self):
        result = self.module.classify("Nørresundby")
        assert result.confidence >= 0.7
        assert any("prefix" in e for e in result.evidence)

    def test_classify_unknown(self):
        result = self.module.classify("Xyz")
        assert result.confidence < 0.3


class TestDanishEtymology:
    def setup_method(self):
        self.module = DanishModule()

    def test_etymology_by(self):
        etym = self.module.get_etymology("by")
        assert etym is not None
        assert etym.lemma == "býr"
        assert "settlement" in etym.meaning

    def test_etymology_torp(self):
        etym = self.module.get_etymology("torp")
        assert etym is not None
        assert "farm" in etym.meaning

    def test_etymology_lev(self):
        etym = self.module.get_etymology("lev")
        assert etym is not None
        assert "inheritance" in etym.meaning or "estate" in etym.meaning

    def test_etymology_unknown(self):
        etym = self.module.get_etymology("xyzzy")
        assert etym is None
