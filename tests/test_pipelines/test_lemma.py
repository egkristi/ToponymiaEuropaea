"""Tests for the name lemma registry and detection."""

import json
from pathlib import Path

from toponymia.pipelines.lemma import (
    LemmaRegistry,
    _infer_semantic_field,
    build_lemma_registry_from_databank,
)


class TestLemmaRegistry:
    """Unit tests for the LemmaRegistry."""

    def test_register_new_lemma(self):
        reg = LemmaRegistry()
        entry = reg.register("heim", "non", meaning="home, settlement")
        assert entry.canonical_form == "heim"
        assert entry.language_code == "non"
        assert entry.meaning == "home, settlement"

    def test_register_duplicate_updates(self):
        reg = LemmaRegistry()
        reg.register("heim", "non", meaning="home")
        entry = reg.register("heim", "non", pie_root="*ḱey-")
        assert entry.meaning == "home"
        assert entry.pie_root == "*ḱey-"

    def test_get_existing(self):
        reg = LemmaRegistry()
        reg.register("berg", "non", semantic_field="topography.terrain")
        entry = reg.get("berg", "non")
        assert entry is not None
        assert entry.semantic_field == "topography.terrain"

    def test_get_missing(self):
        reg = LemmaRegistry()
        assert reg.get("xyz", "non") is None

    def test_case_insensitive(self):
        reg = LemmaRegistry()
        reg.register("Berg", "non")
        entry = reg.get("BERG", "non")
        assert entry is not None
        assert entry.canonical_form == "berg"

    def test_record_attestation_creates_lemma(self):
        reg = LemmaRegistry()
        reg.record_attestation("nes", "non", "src-1", country="NO")
        entry = reg.get("nes", "non")
        assert entry is not None
        assert entry.attestation_count == 1
        assert "NO" in entry.countries

    def test_record_attestation_increments(self):
        reg = LemmaRegistry()
        reg.record_attestation("vik", "non", "src-1", country="NO")
        reg.record_attestation("vik", "non", "src-2", country="SE")
        entry = reg.get("vik", "non")
        assert entry is not None
        assert entry.attestation_count == 2
        assert set(entry.countries) == {"NO", "SE"}

    def test_top_lemmas_sorted(self):
        reg = LemmaRegistry()
        reg.record_attestation("berg", "non", "1")
        reg.record_attestation("berg", "non", "2")
        reg.record_attestation("berg", "non", "3")
        reg.record_attestation("heim", "non", "4")
        reg.record_attestation("heim", "non", "5")
        reg.record_attestation("nes", "non", "6")

        top = reg.top_lemmas(2)
        assert len(top) == 2
        assert top[0].canonical_form == "berg"
        assert top[1].canonical_form == "heim"

    def test_by_semantic_field(self):
        reg = LemmaRegistry()
        reg.register("berg", "non", semantic_field="topography.terrain")
        reg.register("dal", "non", semantic_field="topography.terrain")
        reg.register("vik", "non", semantic_field="topography.coast")
        reg.register("by", "non", semantic_field="settlement")

        terrain = reg.by_semantic_field("topography.terrain")
        assert len(terrain) == 2
        coast = reg.by_semantic_field("topography")
        assert len(coast) == 3  # terrain + terrain + coast

    def test_stats_empty(self):
        reg = LemmaRegistry()
        s = reg.stats()
        assert s["total_lemmas"] == 0
        assert s["total_attestations"] == 0

    def test_stats_populated(self):
        reg = LemmaRegistry()
        reg.record_attestation("berg", "non", "1", country="NO")
        reg.record_attestation("berg", "non", "2", country="SE")
        reg.record_attestation("heim", "non", "3", country="NO")
        s = reg.stats()
        assert s["total_lemmas"] == 2
        assert s["total_attestations"] == 3
        assert s["max_frequency"] == 2
        assert "non" in s["languages"]


class TestInferSemanticField:
    """Tests for semantic field inference."""

    def test_settlement(self):
        assert _infer_semantic_field("farm, settlement") == "settlement"

    def test_coast(self):
        assert _infer_semantic_field("bay, inlet") == "topography.coast"

    def test_terrain(self):
        assert _infer_semantic_field("mountain, peak") == "topography.terrain"

    def test_water(self):
        assert _infer_semantic_field("lake") == "topography.water"

    def test_vegetation(self):
        assert _infer_semantic_field("forest, grove") == "vegetation"

    def test_unknown(self):
        assert _infer_semantic_field("unknown thing") == "other"


class TestBuildLemmaRegistryFromDatabank:
    """Tests for building registry from JSONL files."""

    def test_empty_dir(self, tmp_path: Path):
        places = tmp_path / "places"
        places.mkdir()
        reg = build_lemma_registry_from_databank(tmp_path)
        assert reg.stats()["total_lemmas"] == 0

    def test_detects_suffixes(self, tmp_path: Path):
        places = tmp_path / "places" / "NO"
        places.mkdir(parents=True)
        records = [
            {"name_form": "Trondheim", "source_id": "s1"},
            {"name_form": "Narvik", "source_id": "s2"},
            {"name_form": "Lilleberg", "source_id": "s3"},
        ]
        with (places / "geonames.jsonl").open("w") as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")

        reg = build_lemma_registry_from_databank(tmp_path)
        # Should detect "heim" from Trondheim and "berg" from Lilleberg
        heim = reg.get("heim", "non")
        berg = reg.get("berg", "non")
        assert heim is not None
        assert berg is not None
        assert heim.attestation_count == 1
        assert "NO" in heim.countries

    def test_nonexistent_path(self, tmp_path: Path):
        reg = build_lemma_registry_from_databank(tmp_path / "nonexistent")
        assert reg.stats()["total_lemmas"] == 0
