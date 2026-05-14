"""Name lemma detection and management.

Extracts canonical lemma forms from segmented place names and manages
the lemma registry. A lemma represents a name as a lexical type
(e.g., "Berg") independent of which places it attaches to.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LemmaEntry:
    """A name lemma with frequency and distribution data."""

    canonical_form: str
    language_code: str
    semantic_field: str | None = None
    meaning: str | None = None
    pie_root: str | None = None
    cognates: list[str] = field(default_factory=list)
    attestation_count: int = 0
    countries: list[str] = field(default_factory=list)


class LemmaRegistry:
    """In-memory registry of name lemmas detected from the databank.

    Operates on JSONL records — no database required. Can be used
    during development (JSONL-primary) and will later sync to Postgres.
    """

    def __init__(self) -> None:
        self._lemmas: dict[str, LemmaEntry] = {}
        self._attestation_map: dict[str, list[str]] = {}

    @property
    def lemmas(self) -> dict[str, LemmaEntry]:
        return self._lemmas

    def register(
        self,
        canonical_form: str,
        language_code: str,
        *,
        semantic_field: str | None = None,
        meaning: str | None = None,
        pie_root: str | None = None,
        cognates: list[str] | None = None,
    ) -> LemmaEntry:
        """Register or update a lemma in the registry."""
        key = f"{canonical_form.lower()}:{language_code}"
        if key in self._lemmas:
            entry = self._lemmas[key]
            if semantic_field:
                entry.semantic_field = semantic_field
            if meaning:
                entry.meaning = meaning
            if pie_root:
                entry.pie_root = pie_root
            if cognates:
                entry.cognates = cognates
            return entry

        entry = LemmaEntry(
            canonical_form=canonical_form.lower(),
            language_code=language_code,
            semantic_field=semantic_field,
            meaning=meaning,
            pie_root=pie_root,
            cognates=cognates or [],
        )
        self._lemmas[key] = entry
        return entry

    def get(self, canonical_form: str, language_code: str) -> LemmaEntry | None:
        """Look up a lemma by form and language."""
        key = f"{canonical_form.lower()}:{language_code}"
        return self._lemmas.get(key)

    def record_attestation(
        self,
        canonical_form: str,
        language_code: str,
        source_id: str,
        country: str | None = None,
    ) -> None:
        """Record that a lemma was attested in a specific record."""
        key = f"{canonical_form.lower()}:{language_code}"
        if key not in self._lemmas:
            self.register(canonical_form, language_code)

        entry = self._lemmas[key]
        entry.attestation_count += 1
        if country and country not in entry.countries:
            entry.countries.append(country)

        if key not in self._attestation_map:
            self._attestation_map[key] = []
        self._attestation_map[key].append(source_id)

    def top_lemmas(self, n: int = 50) -> list[LemmaEntry]:
        """Return the N most frequent lemmas."""
        sorted_lemmas = sorted(
            self._lemmas.values(),
            key=lambda e: e.attestation_count,
            reverse=True,
        )
        return sorted_lemmas[:n]

    def by_semantic_field(self, field_prefix: str) -> list[LemmaEntry]:
        """Return all lemmas matching a semantic field prefix."""
        return [
            e
            for e in self._lemmas.values()
            if e.semantic_field and e.semantic_field.startswith(field_prefix)
        ]

    def stats(self) -> dict[str, Any]:
        """Return summary statistics for the registry."""
        if not self._lemmas:
            return {"total_lemmas": 0, "total_attestations": 0}

        counts = [e.attestation_count for e in self._lemmas.values()]
        return {
            "total_lemmas": len(self._lemmas),
            "total_attestations": sum(counts),
            "max_frequency": max(counts),
            "languages": list({e.language_code for e in self._lemmas.values()}),
            "countries": list({c for e in self._lemmas.values() for c in e.countries}),
        }


def build_lemma_registry_from_databank(
    databank_path: Path | None = None,
    language_modules: dict[str, Any] | None = None,
) -> LemmaRegistry:
    """Build a lemma registry by scanning all databank records.

    For each record, extracts the compound_head (suffix) from segmentation
    and registers it as a lemma.

    Args:
        databank_path: Path to the databank directory.
        language_modules: Optional mapping of language_code → module instance.

    Returns:
        Populated LemmaRegistry.
    """
    if databank_path is None:
        databank_path = Path("databank")

    places_dir = databank_path / "places"
    registry = LemmaRegistry()

    if not places_dir.exists():
        return registry

    for country_dir in sorted(places_dir.iterdir()):
        if not country_dir.is_dir():
            continue
        country = country_dir.name

        for jsonl_file in sorted(country_dir.glob("*.jsonl")):
            with jsonl_file.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    _extract_lemmas_from_record(record, country, registry, language_modules)

    return registry


def _extract_lemmas_from_record(
    record: dict[str, Any],
    country: str,
    registry: LemmaRegistry,
    language_modules: dict[str, Any] | None,
) -> None:
    """Extract lemma candidates from a single record."""
    name_form = record.get("name_form", "")
    source_id = record.get("source_id", "")

    if not name_form:
        return

    # Try to detect suffix-based lemmas from the name
    # Simple heuristic: last element after splitting by common patterns
    name_lower = name_form.lower()

    # Known suffixes to look for (from language modules)
    known_suffixes = _get_known_suffixes(language_modules)

    for suffix, info in known_suffixes.items():
        if name_lower.endswith(suffix) and len(name_lower) > len(suffix):
            registry.record_attestation(
                canonical_form=suffix,
                language_code=info.get("language", "non"),
                source_id=source_id,
                country=country,
            )
            # Register with meaning if not already done
            entry = registry.get(suffix, info.get("language", "non"))
            if entry and not entry.meaning:
                entry.meaning = info.get("meaning")
                entry.semantic_field = info.get("semantic_field")
            break


def _get_known_suffixes(
    language_modules: dict[str, Any] | None,
) -> dict[str, dict[str, str]]:
    """Build suffix lookup from language modules or use defaults."""
    if language_modules:
        suffixes: dict[str, dict[str, str]] = {}
        for lang_code, module in language_modules.items():
            if hasattr(module, "ELEMENT_MEANINGS"):
                for element, info in module.ELEMENT_MEANINGS.items():
                    if len(element) >= 2:
                        lemma, meaning, _ = info
                        suffixes[element] = {
                            "language": lang_code,
                            "meaning": meaning,
                            "semantic_field": _infer_semantic_field(meaning),
                        }
        return suffixes

    # Default Nordic suffixes for standalone operation
    return {
        "heim": {"language": "non", "meaning": "home, settlement", "semantic_field": "settlement"},
        "by": {"language": "non", "meaning": "farm, settlement", "semantic_field": "settlement"},
        "stad": {"language": "non", "meaning": "place, farm", "semantic_field": "settlement"},
        "nes": {"language": "non", "meaning": "headland", "semantic_field": "topography.coast"},
        "vik": {"language": "non", "meaning": "bay, inlet", "semantic_field": "topography.coast"},
        "fjord": {"language": "non", "meaning": "fjord", "semantic_field": "topography.coast"},
        "dal": {"language": "non", "meaning": "valley", "semantic_field": "topography.terrain"},
        "berg": {"language": "non", "meaning": "mountain", "semantic_field": "topography.terrain"},
        "ås": {"language": "non", "meaning": "ridge", "semantic_field": "topography.terrain"},
        "rud": {"language": "non", "meaning": "clearing", "semantic_field": "settlement"},
        "torp": {"language": "non", "meaning": "outlying farm", "semantic_field": "settlement"},
        "lund": {"language": "non", "meaning": "grove", "semantic_field": "vegetation"},
        "skog": {"language": "non", "meaning": "forest", "semantic_field": "vegetation"},
        "vatn": {"language": "non", "meaning": "lake", "semantic_field": "topography.water"},
        "foss": {"language": "non", "meaning": "waterfall", "semantic_field": "topography.water"},
        "ø": {"language": "non", "meaning": "island", "semantic_field": "topography.coast"},
        "holm": {"language": "non", "meaning": "islet", "semantic_field": "topography.coast"},
        "havn": {"language": "non", "meaning": "harbor", "semantic_field": "topography.coast"},
        "sund": {"language": "non", "meaning": "strait", "semantic_field": "topography.coast"},
    }


def _infer_semantic_field(meaning: str) -> str:
    """Infer semantic field from meaning text."""
    meaning_lower = meaning.lower()
    if any(w in meaning_lower for w in ("home", "farm", "settlement", "place", "clearing")):
        return "settlement"
    if any(w in meaning_lower for w in ("bay", "fjord", "harbor", "strait", "island", "headland")):
        return "topography.coast"
    if any(w in meaning_lower for w in ("mountain", "hill", "ridge", "valley", "rock")):
        return "topography.terrain"
    if any(w in meaning_lower for w in ("lake", "river", "water", "stream", "waterfall")):
        return "topography.water"
    if any(w in meaning_lower for w in ("forest", "grove", "wood", "meadow")):
        return "vegetation"
    if any(w in meaning_lower for w in ("temple", "church", "sacred")):
        return "sacred"
    return "other"
