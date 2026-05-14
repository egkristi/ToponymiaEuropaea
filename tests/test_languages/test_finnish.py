"""Tests for the Finnish language module."""

from toponymia.languages.base import SegmentationResult
from toponymia.languages.finnish import FinnishModule


class TestFinnishModuleMetadata:
    def setup_method(self):
        self.module = FinnishModule()

    def test_language_code(self):
        assert self.module.language_code == "fin"

    def test_language_name(self):
        assert self.module.language_name == "Finnish"

    def test_family(self):
        assert self.module.family == "Uralic"

    def test_has_suffixes(self):
        assert len(self.module.suffixes) > 20

    def test_has_prefixes(self):
        assert len(self.module.prefixes) > 20


class TestFinnishSegmentation:
    def setup_method(self):
        self.module = FinnishModule()

    def test_segment_compound_jarvi(self):
        """Mustajärvi = Musta + järvi (Black Lake)."""
        results = self.module.segment("Mustajärvi")
        assert len(results) == 2
        assert results[0].morph_type == "compound_modifier"
        assert results[1].morph_type == "compound_head"
        assert results[1].lemma == "järvi"
        assert results[1].meaning == "lake"

    def test_segment_compound_joki(self):
        """Kalajoki = Kala + joki (Fish River)."""
        results = self.module.segment("Kalajoki")
        assert len(results) == 2
        assert results[1].lemma == "joki"
        assert results[1].meaning == "river"

    def test_segment_compound_maki(self):
        """Kirkkomäki = Kirkko + mäki (Church Hill)."""
        results = self.module.segment("Kirkkomäki")
        assert len(results) == 2
        assert results[1].lemma == "mäki"

    def test_segment_compound_vuori(self):
        """Korkeavaara = Korkea + vaara (High Fell)."""
        results = self.module.segment("Korkeavaara")
        assert len(results) == 2
        assert results[1].lemma == "vaara"
        assert results[1].meaning == "fell/rounded mountain"

    def test_segment_habitative_la(self):
        """Mattila = Matti + la (Matti's place)."""
        results = self.module.segment("Mattila")
        assert len(results) == 2
        assert results[1].morph_type == "suffix"
        assert results[1].lemma == "la"
        assert "habitation" in results[1].meaning

    def test_segment_habitative_la_front(self):
        """Mäkelä = Mäke + lä (Hill place)."""
        results = self.module.segment("Mäkelä")
        assert len(results) == 2
        assert results[1].morph_type == "suffix"
        assert results[1].lemma == "lä"

    def test_segment_unsegmentable(self):
        """Short or foreign names get single-stem result."""
        results = self.module.segment("Oulu")
        assert len(results) >= 1
        assert results[0].morph_type == "stem"

    def test_segment_koski(self):
        """Imatrankoski -> segments with koski."""
        results = self.module.segment("Imatrankoski")
        assert len(results) == 2
        assert results[1].lemma == "koski"
        assert results[1].meaning == "rapids"


class TestFinnishClassification:
    def setup_method(self):
        self.module = FinnishModule()

    def test_classify_obvious_finnish(self):
        """Mustajärvi should classify strongly as Finnish."""
        result = self.module.classify("Mustajärvi")
        assert result.language_code == "fin"
        assert result.confidence >= 0.4
        assert any("järvi" in e for e in result.evidence)

    def test_classify_vaara_element(self):
        """Korkeavaara (High fell) — Finnish."""
        result = self.module.classify("Korkeavaara")
        assert result.confidence >= 0.4

    def test_classify_with_long_vowels(self):
        """Kajaani — contains long vowel aa."""
        result = self.module.classify("Kajaani")
        assert result.confidence > 0
        assert any("Long vowel" in e for e in result.evidence)

    def test_classify_diphthongs(self):
        """Joensuu — contains Finnish diphthong."""
        result = self.module.classify("Joensuu")
        assert result.confidence > 0

    def test_classify_non_finnish(self):
        """Stockholm — clearly not Finnish."""
        result = self.module.classify("Stockholm")
        assert result.confidence < 0.3

    def test_classify_pyhä_prefix(self):
        """Pyhäjärvi — sacred lake, Finnish sacred + generic."""
        result = self.module.classify("Pyhäjärvi")
        assert result.confidence >= 0.5
        assert any("pyhä" in e for e in result.evidence)


class TestFinnishEtymology:
    def setup_method(self):
        self.module = FinnishModule()

    def test_etymologize_generic_element(self):
        """Known generic element gets etymology."""
        segments = self.module.segment("Mustajärvi")
        candidates = self.module.etymologize(segments)
        jarvi_etym = [c for c in candidates if c.lemma == "järvi"]
        assert len(jarvi_etym) == 1
        assert jarvi_etym[0].meaning == "lake"
        assert jarvi_etym[0].confidence >= 0.7

    def test_etymologize_modifier(self):
        """Known modifier gets etymology."""
        segments = [
            SegmentationResult(component="musta", position=0, morph_type="compound_modifier")
        ]
        candidates = self.module.etymologize(segments)
        assert any(c.lemma == "musta" and c.meaning == "black" for c in candidates)

    def test_etymologize_habitative(self):
        """Habitative suffix -la gets etymology."""
        segments = self.module.segment("Mattila")
        candidates = self.module.etymologize(segments)
        la_etym = [c for c in candidates if c.lemma == "la"]
        assert len(la_etym) == 1
        assert "habitation" in la_etym[0].meaning

    def test_etymologize_genitive_modifier(self):
        """Genitive form of modifier (e.g., 'mustan' -> 'musta')."""
        segments = [
            SegmentationResult(component="mustan", position=0, morph_type="compound_modifier")
        ]
        candidates = self.module.etymologize(segments)
        assert any(c.lemma == "musta" and "genitive" in c.meaning for c in candidates)


class TestFinnishNormalize:
    def setup_method(self):
        self.module = FinnishModule()

    def test_lowercase(self):
        assert self.module.normalize("HELSINKI") == "helsinki"

    def test_preserves_umlauts(self):
        assert self.module.normalize("Jyväskylä") == "jyväskylä"

    def test_strips_whitespace(self):
        assert self.module.normalize("  Turku  ") == "turku"
