"""Tests for cultural/social perspective module."""

from uuid import uuid4

from toponymia.perspectives.cultural import (
    CulturalPerspective,
    analyse_toponym,
)


class TestAnalyseToponym:
    """Tests for the analyse_toponym function."""

    def test_social_indicator_royal(self):
        result = analyse_toponym("Kongsberg")
        assert any(i["class"] == "royal" for i in result.social_indicators)

    def test_social_indicator_jarl(self):
        result = analyse_toponym("Jarlsberg")
        assert any(i["element"] == "jarl" for i in result.social_indicators)

    def test_ethnonymic_finn(self):
        result = analyse_toponym("Finnmark")
        assert any(r["group"] == "sami" for r in result.ethnonymic_refs)

    def test_ethnonymic_kven(self):
        result = analyse_toponym("Kvænangen")
        assert any(r["group"] == "finnic" for r in result.ethnonymic_refs)

    def test_ownership_generic(self):
        result = analyse_toponym("Storgard")
        assert result.ownership_type == "owned farmstead"

    def test_personal_name_detection(self):
        result = analyse_toponym("Eriksgard")
        assert result.possible_personal_name
        assert result.personal_name_element == "erik"

    def test_no_personal_name_without_genitive(self):
        result = analyse_toponym("Nygard")
        assert not result.possible_personal_name

    def test_no_matches(self):
        result = analyse_toponym("Oslo")
        assert result.social_indicators == []
        assert result.ethnonymic_refs == []
        assert result.ownership_type == ""
        assert not result.possible_personal_name

    def test_multiple_indicators(self):
        # Name that has both ethnonymic and social elements
        result = analyse_toponym("Finnkarlen")
        assert len(result.ethnonymic_refs) >= 1
        assert len(result.social_indicators) >= 1


class TestCulturalPerspective:
    """Tests for the CulturalPerspective class."""

    def test_perspective_metadata(self):
        p = CulturalPerspective()
        assert p.perspective_id == "cultural_social"
        assert p.name == "Cultural/Social"

    def test_extract_features(self):
        p = CulturalPerspective()
        features = p.extract_features(uuid4())
        assert isinstance(features, dict)

    def test_generate_hypotheses(self):
        p = CulturalPerspective()
        hyps = p.generate_hypotheses(uuid4())
        assert len(hyps) >= 2
        assert all(h.source == "cultural_social" for h in hyps)
