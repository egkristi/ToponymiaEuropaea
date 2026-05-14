"""Tests for the normalization pipeline."""

from toponymia.pipelines.normalize import NormalizationConfig, NormalizationPipeline


def test_basic_normalization():
    """Test basic normalization (lowercase, strip, collapse whitespace)."""
    pipeline = NormalizationPipeline()
    assert pipeline.normalize("  Trondheim  ") == "trondheim"
    assert pipeline.normalize("BERGEN") == "bergen"
    assert pipeline.normalize("  multiple   spaces  ") == "multiple spaces"


def test_unicode_normalization():
    """Test Unicode NFC normalization."""
    pipeline = NormalizationPipeline()
    # Composed vs decomposed forms should normalize to same
    composed = "Ålborg"  # å as single character
    result = pipeline.normalize(composed)
    assert result == "ålborg"


def test_ascii_approximation():
    """Test lossy ASCII conversion."""
    pipeline = NormalizationPipeline()
    assert pipeline.to_ascii("Ålborg") == "aalborg"
    assert pipeline.to_ascii("Trøndelag") == "trondelag"
    assert pipeline.to_ascii("Þingvellir") == "thingvellir"
    assert pipeline.to_ascii("Straße") == "strasse"


def test_script_detection_latin():
    """Test script detection for Latin text."""
    pipeline = NormalizationPipeline()
    assert pipeline.detect_script("Trondheim") == "Latn"


def test_script_detection_cyrillic():
    """Test script detection for Cyrillic text."""
    pipeline = NormalizationPipeline()
    assert pipeline.detect_script("Москва") == "Cyrl"


def test_script_detection_greek():
    """Test script detection for Greek text."""
    pipeline = NormalizationPipeline()
    assert pipeline.detect_script("Αθήνα") == "Grek"


def test_custom_substitutions():
    """Test language-specific substitutions."""
    config = NormalizationConfig(substitutions={"ð": "d", "þ": "th"})
    pipeline = NormalizationPipeline(config)
    assert pipeline.normalize("Norðfjord") == "nordfjord"
    assert pipeline.normalize("Þingvellir") == "thingvellir"
