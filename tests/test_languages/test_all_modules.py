"""Parametrized tests for all language modules (issue #39).

Verifies that every registered language module conforms to the
BaseLanguageModule interface contract.
"""

import pytest

from toponymia.languages import get_all_modules
from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)

# Collect all modules once for parametrization
_ALL_MODULES = get_all_modules()
_MODULE_IDS = sorted(_ALL_MODULES.keys())


@pytest.fixture(params=_MODULE_IDS)
def language_module(request):
    """Fixture that yields each registered language module."""
    return _ALL_MODULES[request.param]


class TestModuleMetadata:
    """Every module must have required metadata fields."""

    def test_is_base_subclass(self, language_module):
        assert isinstance(language_module, BaseLanguageModule)

    def test_has_language_code(self, language_module):
        assert language_module.language_code, "language_code must be non-empty"

    def test_has_language_name(self, language_module):
        assert language_module.language_name, "language_name must be non-empty"

    def test_has_family(self, language_module):
        assert language_module.family, "family must be non-empty"

    def test_has_branch(self, language_module):
        assert language_module.branch, "branch must be non-empty"


class TestClassifyInterface:
    """classify() must return a LanguageClassification."""

    def test_classify_returns_classification(self, language_module):
        result = language_module.classify("test")
        assert isinstance(result, LanguageClassification)

    def test_classify_has_valid_confidence(self, language_module):
        result = language_module.classify("test")
        assert 0.0 <= result.confidence <= 1.0

    def test_classify_language_code_matches(self, language_module):
        result = language_module.classify("test")
        assert result.language_code == language_module.language_code


class TestSegmentInterface:
    """segment() must return a list of SegmentationResult."""

    def test_segment_returns_list(self, language_module):
        result = language_module.segment("test")
        assert isinstance(result, list)

    def test_segment_items_are_segmentation_results(self, language_module):
        result = language_module.segment("testplace")
        for item in result:
            assert isinstance(item, SegmentationResult)

    def test_segment_results_have_valid_fields(self, language_module):
        results = language_module.segment("testplace")
        for r in results:
            assert isinstance(r.component, str)
            assert isinstance(r.position, int)
            assert r.position >= 0
            assert r.morph_type in (
                "prefix",
                "stem",
                "suffix",
                "compound_head",
                "compound_modifier",
                "infix",
                "genitive",
                "simplex",
            )
            assert 0.0 <= r.confidence <= 1.0


class TestEtymologizeInterface:
    """etymologize() must return a list of EtymologyCandidate."""

    def test_etymologize_returns_list(self, language_module):
        components = [SegmentationResult(component="test", position=0, morph_type="stem")]
        result = language_module.etymologize(components)
        assert isinstance(result, list)

    def test_etymologize_items_are_candidates(self, language_module):
        components = [SegmentationResult(component="test", position=0, morph_type="stem")]
        result = language_module.etymologize(components)
        for item in result:
            assert isinstance(item, EtymologyCandidate)

    def test_etymologize_candidates_have_valid_fields(self, language_module):
        components = [SegmentationResult(component="test", position=0, morph_type="stem")]
        results = language_module.etymologize(components)
        for r in results:
            assert isinstance(r.lemma, str)
            assert isinstance(r.meaning, str)
            assert isinstance(r.language_code, str)
            assert 0.0 <= r.confidence <= 1.0


class TestNormalizeInterface:
    """normalize() must return a string."""

    def test_normalize_returns_string(self, language_module):
        result = language_module.normalize("Test Place")
        assert isinstance(result, str)

    def test_normalize_lowercases(self, language_module):
        result = language_module.normalize("UPPER")
        assert result == result.lower()
