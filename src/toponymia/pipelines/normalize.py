"""Name normalization pipeline.

Handles Unicode normalization, diacritics, transliteration,
historical spelling variants, and OCR error correction.

The normalization pipeline is the first stage after ingestion.
It produces a canonical normalized form for each name attestation
that can be used for matching and comparison across sources.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass
class NormalizationConfig:
    """Configuration for normalization pipeline."""

    # Unicode normalization form (NFC, NFD, NFKC, NFKD)
    unicode_form: str = "NFC"

    # Whether to generate ASCII-only form (lossy)
    generate_ascii: bool = True

    # Whether to lowercase
    lowercase: bool = True

    # Whether to strip leading/trailing whitespace
    strip_whitespace: bool = True

    # Whether to collapse internal whitespace
    collapse_whitespace: bool = True

    # Language-specific substitution rules
    substitutions: dict[str, str] | None = None


class NormalizationPipeline:
    """Pipeline stage for normalizing place name forms.

    Normalization produces a consistent, comparable form while preserving
    the original form for display and provenance. Multiple normalization
    strategies can be applied depending on the analysis context.
    """

    def __init__(self, config: NormalizationConfig | None = None):
        self.config = config or NormalizationConfig()

    def normalize(self, form: str) -> str:
        """Normalize a name form to canonical representation.

        Args:
            form: Raw name form from any source.

        Returns:
            Normalized form suitable for comparison and analysis.
        """
        result = form

        # Unicode normalization
        result = unicodedata.normalize(self.config.unicode_form, result)

        # Strip whitespace
        if self.config.strip_whitespace:
            result = result.strip()

        # Collapse internal whitespace
        if self.config.collapse_whitespace:
            result = re.sub(r"\s+", " ", result)

        # Apply language-specific substitutions (before lowercasing to handle Þ/þ etc.)
        if self.config.substitutions:
            for old, new in self.config.substitutions.items():
                result = result.replace(old, new)
                # Also apply case variants (e.g., þ->th should also handle Þ->Th)
                result = result.replace(old.upper(), new)
                result = result.replace(old.lower(), new)

        # Lowercase
        if self.config.lowercase:
            result = result.lower()

        return result

    def to_ascii(self, form: str) -> str:
        """Generate lossy ASCII approximation for fuzzy matching.

        This is intentionally lossy—it's used for approximate matching
        across different transliteration systems, not as a canonical form.
        """
        # NFKD decomposition separates base characters from combining marks
        decomposed = unicodedata.normalize("NFKD", form)

        # Keep only ASCII characters (strips combining diacritical marks)
        ascii_form = decomposed.encode("ascii", "ignore").decode("ascii")

        # Common substitutions for characters that don't decompose cleanly
        substitutions = {
            "ø": "o",
            "Ø": "O",
            "æ": "ae",
            "Æ": "AE",
            "å": "aa",
            "Å": "AA",
            "ð": "d",
            "Ð": "D",
            "þ": "th",
            "Þ": "TH",
            "ß": "ss",
            "ł": "l",
            "Ł": "L",
        }

        result = form
        for old, new in substitutions.items():
            result = result.replace(old, new)

        # Then strip remaining non-ASCII
        decomposed = unicodedata.normalize("NFKD", result)
        ascii_form = decomposed.encode("ascii", "ignore").decode("ascii")

        return ascii_form.lower().strip()

    def detect_script(self, form: str) -> str:
        """Detect the primary script of a name form (ISO 15924).

        Returns the script code for the majority of characters.
        """
        script_counts: dict[str, int] = {}
        for char in form:
            if char.isalpha():
                # Get Unicode script property
                try:
                    name = unicodedata.name(char, "")
                    if "LATIN" in name:
                        script_counts["Latn"] = script_counts.get("Latn", 0) + 1
                    elif "CYRILLIC" in name:
                        script_counts["Cyrl"] = script_counts.get("Cyrl", 0) + 1
                    elif "GREEK" in name:
                        script_counts["Grek"] = script_counts.get("Grek", 0) + 1
                    elif "ARABIC" in name:
                        script_counts["Arab"] = script_counts.get("Arab", 0) + 1
                    elif "RUNIC" in name:
                        script_counts["Runr"] = script_counts.get("Runr", 0) + 1
                    elif "GEORGIAN" in name:
                        script_counts["Geor"] = script_counts.get("Geor", 0) + 1
                    elif "ARMENIAN" in name:
                        script_counts["Armn"] = script_counts.get("Armn", 0) + 1
                    elif "HEBREW" in name:
                        script_counts["Hebr"] = script_counts.get("Hebr", 0) + 1
                    else:
                        script_counts["Zyyy"] = script_counts.get("Zyyy", 0) + 1
                except ValueError:
                    script_counts["Zyyy"] = script_counts.get("Zyyy", 0) + 1

        if not script_counts:
            return "Zyyy"  # Common/undetermined

        return max(script_counts, key=script_counts.get)  # type: ignore[arg-type]
