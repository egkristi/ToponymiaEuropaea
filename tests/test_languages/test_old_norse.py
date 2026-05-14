"""Tests for the Old Norse language module."""

from toponymia.languages.old_norse import OldNorseModule


def test_module_metadata():
    """Test module class-level metadata."""
    module = OldNorseModule()
    assert module.language_code == "non"
    assert module.language_name == "Old Norse"
    assert module.family == "Indo-European"


def test_segment_heim_suffix():
    """Test segmentation of -heim names."""
    module = OldNorseModule()
    results = module.segment("Trondheim")
    assert len(results) == 2
    assert results[0].morph_type == "compound_modifier"
    assert results[1].morph_type == "compound_head"
    assert "heim" in results[1].component.lower()


def test_segment_nes_suffix():
    """Test segmentation of -nes names."""
    module = OldNorseModule()
    results = module.segment("Torsnes")
    assert len(results) == 2
    assert results[0].component == "Tors"
    assert "nes" in results[1].component.lower()


def test_segment_unknown_suffix():
    """Test segmentation falls back for unknown forms."""
    module = OldNorseModule()
    results = module.segment("Xyz")
    assert len(results) >= 1
    assert results[0].morph_type == "stem"
    assert results[0].confidence < 0.5


def test_classify_berg_name():
    """Test classification of a clearly Norse name."""
    module = OldNorseModule()
    result = module.classify("Helgeberg")
    assert result.language_code == "non"
    assert result.confidence > 0.3


def test_classify_non_norse():
    """Test classification gives low confidence for non-Norse name."""
    module = OldNorseModule()
    result = module.classify("München")
    assert result.confidence < 0.3


def test_etymologize_known_element():
    """Test etymology generation for known suffix."""
    from toponymia.languages.base import SegmentationResult

    module = OldNorseModule()
    components = [
        SegmentationResult(component="heim", position=1, morph_type="compound_head", lemma="heim"),
    ]
    candidates = module.etymologize(components)
    assert len(candidates) > 0
    assert candidates[0].meaning == "home, settlement"
    assert candidates[0].language_code == "non"


def test_normalize():
    """Test normalization."""
    module = OldNorseModule()
    assert module.normalize("  Trondheim  ") == "trondheim"
    assert module.normalize("BERGEN") == "bergen"
