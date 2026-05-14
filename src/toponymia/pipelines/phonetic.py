"""Nordic phonetic normalizer for cross-source deduplication.

Implements sound-change-aware normalization that maps variant spellings
to a common phonetic key. This enables matching across:
- Modern vs. historical orthography (Bjørgvin → Bergen)
- Cross-Nordic variants (SE Helsingborg / DK Helsingør / NO Helsingfors)
- Old Norse → modern reflexes (þ→t, ð→d, ǫ→o, ey→øy)

Uses a simplified Beider-Morse inspired approach adapted for
Scandinavian onomastic material.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class PhoneticKey:
    """A phonetic normalization result."""

    original: str
    key: str
    language: str | None = None
    rules_applied: list[str] = field(default_factory=list)


# ─── Sound change rules ──────────────────────────────────────────────────────
# Ordered: more specific patterns must come before more general ones.

# Old Norse → Modern Scandinavian
ON_TO_MODERN: list[tuple[str, str, str]] = [
    (r"þ", "t", "þ→t"),
    (r"ð", "d", "ð→d"),
    (r"ǫ", "o", "ǫ→o"),
    (r"ę", "e", "ę→e"),
    (r"ǫ́", "ó", "ǫ́→ó"),  # noqa: RUF001
    (r"ey", "øy", "ey→øy"),
    (r"hv", "kv", "hv→kv"),
    (r"au", "øy", "au→øy"),
]

# Cross-Nordic orthographic equivalences
NORDIC_EQUIVALENCES: list[tuple[str, str, str]] = [
    # Swedish/Danish ö → Norwegian ø
    (r"ö", "ø", "ö→ø"),
    # Swedish/Danish ä → Norwegian æ
    (r"ä", "æ", "ä→æ"),
    # Danish aa → Norwegian å
    (r"aa", "å", "aa→å"),
    # Swedish v/w alternation
    (r"w", "v", "w→v"),
    # Danish/Norwegian th → t (modern)
    (r"th", "t", "th→t"),
    # ph → f
    (r"ph", "f", "ph→f"),
    # ck → kk
    (r"ck", "kk", "ck→kk"),
    # Double consonant simplification for matching
    (r"ff", "f", "ff→f"),
    (r"ll", "l", "ll→l"),
    (r"ss", "s", "ss→s"),
    (r"tt", "t", "tt→t"),
    (r"nn", "n", "nn→n"),
    (r"mm", "m", "mm→m"),
    (r"pp", "p", "pp→p"),
]

# Common onomastic suffix normalizations
SUFFIX_EQUIVALENCES: list[tuple[str, str, str]] = [
    # -heim variants
    (r"heim$", "heim", "suffix-heim"),
    (r"hem$", "heim", "hem→heim"),
    (r"um$", "heim", "um→heim"),
    # -stad variants
    (r"sted$", "stad", "sted→stad"),
    (r"städ$", "stad", "städ→stad"),
    # -nes variants
    (r"näs$", "nes", "näs→nes"),
    (r"næs$", "nes", "næs→nes"),
    (r"neset$", "nes", "neset→nes"),
    # -vik variants
    (r"vig$", "vik", "vig→vik"),
    (r"viken$", "vik", "viken→vik"),
    # -berg variants
    (r"bjerg$", "berg", "bjerg→berg"),
    (r"berget$", "berg", "berget→berg"),
    # -fjord variants
    (r"fjorden$", "fjord", "fjorden→fjord"),
    # -by variants (already canonical)
    (r"bye$", "by", "bye→by"),
    # -ø/ö/ö variants
    (r"ö$", "ø", "ö→ø (suffix)"),
    (r"øy$", "ø", "øy→ø (suffix)"),
    (r"øya$", "ø", "øya→ø (suffix)"),
]


class NordicPhoneticNormalizer:
    """Produces phonetic keys for Nordic place names.

    The key is designed so that variant spellings of the same name
    map to the same (or very similar) key, enabling deduplication
    across sources with different orthographic conventions.
    """

    def __init__(
        self,
        *,
        apply_on_rules: bool = True,
        apply_cross_nordic: bool = True,
        apply_suffix_normalization: bool = True,
    ) -> None:
        self.apply_on_rules = apply_on_rules
        self.apply_cross_nordic = apply_cross_nordic
        self.apply_suffix_normalization = apply_suffix_normalization

    def phonetic_key(self, name: str, *, language: str | None = None) -> PhoneticKey:
        """Compute a phonetic key for a place name.

        Args:
            name: Place name in any Nordic orthography.
            language: Optional ISO 639-3 language hint.

        Returns:
            PhoneticKey with the normalized key and applied rules.
        """
        result = name.lower().strip()
        rules_applied: list[str] = []

        # Apply Old Norse → modern rules
        if self.apply_on_rules:
            for pattern, replacement, rule_name in ON_TO_MODERN:
                new_result = re.sub(pattern, replacement, result)
                if new_result != result:
                    rules_applied.append(rule_name)
                    result = new_result

        # Apply cross-Nordic equivalences
        if self.apply_cross_nordic:
            for pattern, replacement, rule_name in NORDIC_EQUIVALENCES:
                new_result = re.sub(pattern, replacement, result)
                if new_result != result:
                    rules_applied.append(rule_name)
                    result = new_result

        # Apply suffix normalizations
        if self.apply_suffix_normalization:
            for pattern, replacement, rule_name in SUFFIX_EQUIVALENCES:
                new_result = re.sub(pattern, replacement, result)
                if new_result != result:
                    rules_applied.append(rule_name)
                    result = new_result
                    break  # Only one suffix rule should apply

        return PhoneticKey(
            original=name,
            key=result,
            language=language,
            rules_applied=rules_applied,
        )

    def are_equivalent(self, name1: str, name2: str) -> bool:
        """Check if two names are phonetically equivalent."""
        return self.phonetic_key(name1).key == self.phonetic_key(name2).key

    def batch_keys(self, names: list[str]) -> dict[str, PhoneticKey]:
        """Compute phonetic keys for a batch of names."""
        return {name: self.phonetic_key(name) for name in names}

    def find_duplicates(self, names: list[str]) -> dict[str, list[str]]:
        """Group names that share the same phonetic key.

        Returns only groups with 2+ members (potential duplicates).
        """
        groups: dict[str, list[str]] = {}
        for name in names:
            key = self.phonetic_key(name).key
            if key not in groups:
                groups[key] = []
            groups[key].append(name)

        return {k: v for k, v in groups.items() if len(v) > 1}
