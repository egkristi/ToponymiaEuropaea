"""Diachronic attestation linking pipeline.

Links historical and modern name forms that refer to the same physical place,
creating time-ordered attestation chains. Uses phonetic equivalence and spatial
proximity to identify that e.g. 1340 *Þorshofuum* = 2024 *Torshov*.

Strategy:
1. Group records by phonetic key + spatial proximity (same H3 R9 cell)
2. Within each group, build a chronological sequence of attestations
3. Apply sound change rules to verify linkage plausibility
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from toponymia.pipelines.phonetic import NordicPhoneticNormalizer


@dataclass
class AttestationLink:
    """A single link between two chronological name forms."""

    earlier_form: str
    later_form: str
    year_from: int | None
    year_to: int | None
    phonetic_key: str
    rules_applied: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class AttestationChain:
    """A chronological chain of linked name forms for one place."""

    place_id: str
    current_form: str
    links: list[AttestationLink] = field(default_factory=list)
    all_forms: list[dict[str, Any]] = field(default_factory=list)

    @property
    def span_years(self) -> int | None:
        """Total time span of the chain in years."""
        years: list[int] = [
            f["year_from"] for f in self.all_forms if isinstance(f.get("year_from"), int)
        ]
        if len(years) < 2:
            return None
        return max(years) - min(years)

    @property
    def depth(self) -> int:
        """Number of distinct historical forms."""
        return len(self.all_forms)


@dataclass
class DiachronicReport:
    """Results of diachronic attestation analysis."""

    total_records: int
    chains_found: int
    chains: list[AttestationChain] = field(default_factory=list)
    longest_span: int | None = None

    @property
    def multi_form_chains(self) -> int:
        """Chains with 2+ distinct forms."""
        return sum(1 for c in self.chains if c.depth >= 2)


def _extract_attestation_forms(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract all name forms from a record (main + attestation array)."""
    forms: list[dict[str, Any]] = []

    # Main form
    forms.append(
        {
            "form": record.get("name_form", ""),
            "year_from": record.get("year_from"),
            "year_to": record.get("year_to"),
            "is_current": record.get("is_current", True),
            "source": record.get("source_id", ""),
        }
    )

    # Attestation array if present
    for att in record.get("attestations", []):
        forms.append(
            {
                "form": att.get("form", ""),
                "year_from": att.get("year_from"),
                "year_to": att.get("year_to"),
                "is_current": att.get("is_current", False),
                "source": att.get("source", ""),
            }
        )

    return forms


def _sort_chronologically(forms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort forms by year (earliest first), current forms last."""

    def sort_key(f: dict[str, Any]) -> tuple[int, int]:
        year = f.get("year_from")
        if year is None:
            # Current forms go last, unknown goes after dated forms
            return (9999, 1) if f.get("is_current") else (9998, 0)
        return (year, 0)

    return sorted(forms, key=sort_key)


def build_attestation_chains(
    records: list[dict[str, Any]],
) -> DiachronicReport:
    """Build diachronic attestation chains from databank records.

    Groups records by phonetic key + H3 cell, then constructs
    time-ordered chains of name forms for each place.

    Args:
        records: Databank records (with _phonetic_key and _h3_r9 fields).

    Returns:
        DiachronicReport with all identified chains.
    """
    normalizer = NordicPhoneticNormalizer()

    # Group by phonetic key + H3 R9 cell (same place identity)
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for rec in records:
        key = rec.get("_phonetic_key", "")
        h3_cell = rec.get("_h3_r9", "")
        if not key:
            continue
        group_id = (key, h3_cell)
        if group_id not in groups:
            groups[group_id] = []
        groups[group_id].append(rec)

    chains: list[AttestationChain] = []

    for (phon_key, _h3_cell), group in groups.items():
        # Collect all forms from all records in the group
        all_forms: list[dict[str, Any]] = []
        for rec in group:
            all_forms.extend(_extract_attestation_forms(rec))

        # Deduplicate forms (same form string)
        seen_forms: set[str] = set()
        unique_forms: list[dict[str, Any]] = []
        for f in all_forms:
            form_str = f["form"]
            if form_str and form_str not in seen_forms:
                seen_forms.add(form_str)
                unique_forms.append(f)

        if len(unique_forms) < 2:
            continue

        # Sort chronologically
        sorted_forms = _sort_chronologically(unique_forms)

        # Build links between consecutive forms
        links: list[AttestationLink] = []
        for i in range(len(sorted_forms) - 1):
            earlier = sorted_forms[i]
            later = sorted_forms[i + 1]

            # Verify phonetic equivalence
            key_earlier = normalizer.phonetic_key(earlier["form"])
            key_later = normalizer.phonetic_key(later["form"])

            confidence = 0.9 if key_earlier.key == key_later.key else 0.5

            links.append(
                AttestationLink(
                    earlier_form=earlier["form"],
                    later_form=later["form"],
                    year_from=earlier.get("year_from"),
                    year_to=later.get("year_from"),  # Later form's start
                    phonetic_key=phon_key,
                    rules_applied=key_earlier.rules_applied,
                    confidence=confidence,
                )
            )

        # Determine current form
        current = sorted_forms[-1]["form"]
        place_id = group[0].get("place_id", group[0].get("source_id", phon_key))

        chains.append(
            AttestationChain(
                place_id=str(place_id),
                current_form=current,
                links=links,
                all_forms=sorted_forms,
            )
        )

    # Compute longest span
    spans = [c.span_years for c in chains if c.span_years is not None]
    longest = max(spans) if spans else None

    return DiachronicReport(
        total_records=len(records),
        chains_found=len(chains),
        chains=chains,
        longest_span=longest,
    )
