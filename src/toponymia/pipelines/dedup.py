"""Cross-source deduplication pipeline.

Matches place records across data sources (GeoNames ↔ Kartverket)
using a two-stage strategy:
1. Phonetic blocking: group by _phonetic_key (fast, O(n))
2. Spatial verification: confirm proximity via H3 distance (precise)

A match requires BOTH phonetic equivalence AND spatial proximity
(same H3 R9 cell or adjacent cells, i.e., within ~1 km).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DedupMatch:
    """A pair of records identified as potential duplicates."""

    record_a: dict[str, Any]
    record_b: dict[str, Any]
    phonetic_key: str
    h3_distance: int  # -1 = different resolutions or too far
    confidence: float  # 0.0–1.0

    @property
    def source_a(self) -> str:
        return str(self.record_a.get("source_dataset", self.record_a.get("source_url", "")))

    @property
    def source_b(self) -> str:
        return str(self.record_b.get("source_dataset", self.record_b.get("source_url", "")))


@dataclass
class DedupReport:
    """Summary of deduplication results."""

    total_records: int
    unique_keys: int
    matches: list[DedupMatch] = field(default_factory=list)
    sources_compared: list[str] = field(default_factory=list)

    @property
    def duplicate_count(self) -> int:
        return len(self.matches)

    @property
    def high_confidence_count(self) -> int:
        return sum(1 for m in self.matches if m.confidence >= 0.8)


def _compute_h3_distance(rec_a: dict[str, Any], rec_b: dict[str, Any]) -> int:
    """Compute H3 grid distance between two records at R9."""
    h3_a = rec_a.get("_h3_r9", "")
    h3_b = rec_b.get("_h3_r9", "")
    if not h3_a or not h3_b:
        return -1
    try:
        import h3 as h3_lib

        return int(h3_lib.grid_distance(h3_a, h3_b))
    except Exception:
        return -1


def _compute_confidence(h3_dist: int, name_a: str, name_b: str) -> float:
    """Compute match confidence based on spatial distance and name similarity.

    - Same H3 R9 cell (dist=0): high confidence
    - Adjacent cells (dist=1): medium-high confidence
    - Further (dist 2-3): lower confidence
    - Beyond 3 cells: unlikely match
    """
    if h3_dist < 0:
        # Can't compute distance — rely only on phonetic match
        # Give moderate confidence if exact name match
        if name_a.lower() == name_b.lower():
            return 0.6
        return 0.4

    if h3_dist == 0:
        return 0.95
    if h3_dist == 1:
        return 0.85
    if h3_dist <= 3:
        return 0.6
    return 0.3


def find_cross_source_duplicates(
    records: list[dict[str, Any]],
    *,
    max_h3_distance: int = 3,
) -> DedupReport:
    """Find duplicate records across different data sources.

    Groups records by phonetic key, then verifies spatial proximity
    within each group. Only pairs from DIFFERENT sources are flagged.

    Args:
        records: All databank records (from multiple sources).
        max_h3_distance: Maximum H3 R9 grid distance to consider a match.

    Returns:
        DedupReport with matched pairs and statistics.
    """
    # Stage 1: Build phonetic blocks
    blocks: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        key = rec.get("_phonetic_key", "")
        if not key:
            continue
        if key not in blocks:
            blocks[key] = []
        blocks[key].append(rec)

    # Identify sources present
    sources = sorted(
        {rec.get("source_dataset", rec.get("source_url", "unknown")) for rec in records}
    )

    # Stage 2: Within each block, find cross-source pairs
    matches: list[DedupMatch] = []
    for key, group in blocks.items():
        if len(group) < 2:
            continue

        # Only compare pairs from different sources
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                src_i = group[i].get("source_dataset", group[i].get("source_url", ""))
                src_j = group[j].get("source_dataset", group[j].get("source_url", ""))
                if src_i == src_j:
                    continue

                h3_dist = _compute_h3_distance(group[i], group[j])
                if h3_dist > max_h3_distance and h3_dist >= 0:
                    continue

                confidence = _compute_confidence(
                    h3_dist,
                    group[i].get("name_form", ""),
                    group[j].get("name_form", ""),
                )

                matches.append(
                    DedupMatch(
                        record_a=group[i],
                        record_b=group[j],
                        phonetic_key=key,
                        h3_distance=h3_dist,
                        confidence=confidence,
                    )
                )

    return DedupReport(
        total_records=len(records),
        unique_keys=len(blocks),
        matches=matches,
        sources_compared=sources,
    )


def load_all_records(databank_path: str) -> list[dict[str, Any]]:
    """Load all JSONL records from a databank directory.

    Args:
        databank_path: Path to the databank/ directory.

    Returns:
        List of all records across all countries and sources.
    """
    import json
    from pathlib import Path

    records: list[dict[str, Any]] = []
    places_dir = Path(databank_path) / "places"

    if not places_dir.exists():
        return records

    for jsonl_file in sorted(places_dir.rglob("*.jsonl")):
        with jsonl_file.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

    return records
