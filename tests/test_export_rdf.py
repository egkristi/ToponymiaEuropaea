"""Tests for RDF/Turtle export."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

rdflib = pytest.importorskip("rdflib")


def _make_record(**overrides):
    """Create a minimal test record."""
    base = {
        "name_form": "Bergen",
        "name_normalized": "bergen",
        "country_code": "NO",
        "language_code": "nor",
        "latitude": 60.39299,
        "longitude": 5.32415,
        "place_type": "P.PPL",
        "source_id": "geonames:3161732",
        "source_dataset": "geonames",
        "source_license": "CC-BY-4.0",
        "source_url": "https://www.geonames.org/3161732",
        "geonames_id": 3161732,
        "is_current": True,
        "alternative_names": {"nob": ["Bergen"], "eng": ["Bergen"]},
    }
    base.update(overrides)
    return base


def _make_peak_record():
    """Create a record with topographic metrics."""
    return {
        "name_form": "Galdhøpiggen",
        "name_normalized": "galdhøpiggen",
        "country_code": "NO",
        "language_code": "nor",
        "latitude": 61.633333,
        "longitude": 8.3,
        "elevation": 2469.0,
        "place_type": "T.MT",
        "source_id": "wikidata:Q203942",
        "source_dataset": "wikidata",
        "source_license": "CC0-1.0",
        "source_url": "https://www.wikidata.org/wiki/Q203942",
        "wikidata_qid": "Q203942",
        "geonames_id": 3156206,
        "prominence_m": 2436.0,
        "isolation_km": 1568.3,
        "mountain_range": "Jotunheimen",
        "is_current": True,
    }


def test_export_single_record():
    """Export a single record and verify RDF triples."""
    from toponymia.export.rdf import export_databank_to_rdf

    with tempfile.TemporaryDirectory() as tmpdir:
        # Set up databank structure
        places_dir = Path(tmpdir) / "places" / "NO"
        places_dir.mkdir(parents=True)
        jsonl_file = places_dir / "geonames.jsonl"
        jsonl_file.write_text(json.dumps(_make_record()) + "\n")

        output = Path(tmpdir) / "output.ttl"
        count = export_databank_to_rdf(Path(tmpdir), output)

        assert count == 1
        assert output.exists()

        # Parse and verify
        g = rdflib.Graph()
        g.parse(str(output), format="turtle")

        # Should have triples
        assert len(g) > 0

        # Check for label
        labels = list(g.objects(predicate=rdflib.RDFS.label))
        assert any("Bergen" in str(lbl) for lbl in labels)


def test_export_with_topographic_metrics():
    """Export a peak record with prominence/isolation."""
    from toponymia.export.rdf import export_databank_to_rdf

    with tempfile.TemporaryDirectory() as tmpdir:
        places_dir = Path(tmpdir) / "places" / "NO"
        places_dir.mkdir(parents=True)
        jsonl_file = places_dir / "wikidata.jsonl"
        jsonl_file.write_text(json.dumps(_make_peak_record()) + "\n")

        output = Path(tmpdir) / "output.ttl"
        count = export_databank_to_rdf(Path(tmpdir), output)

        assert count == 1

        g = rdflib.Graph()
        g.parse(str(output), format="turtle")

        # Check cross-references
        from rdflib.namespace import OWL

        same_as = list(g.objects(predicate=OWL.sameAs))
        urls = [str(s) for s in same_as]
        assert any("wikidata.org" in u for u in urls)
        assert any("geonames.org" in u for u in urls)


def test_export_country_filter():
    """Filter export by country code."""
    from toponymia.export.rdf import export_databank_to_rdf

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create records in two countries
        for cc in ("NO", "SE"):
            places_dir = Path(tmpdir) / "places" / cc
            places_dir.mkdir(parents=True)
            jsonl_file = places_dir / "geonames.jsonl"
            record = _make_record(country_code=cc, source_id=f"geonames:{cc}123")
            jsonl_file.write_text(json.dumps(record) + "\n")

        output = Path(tmpdir) / "output.ttl"
        count = export_databank_to_rdf(Path(tmpdir), output, country="NO")

        assert count == 1


def test_export_empty_databank():
    """Handle empty databank gracefully."""
    from toponymia.export.rdf import export_databank_to_rdf

    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "places").mkdir()
        output = Path(tmpdir) / "output.ttl"
        count = export_databank_to_rdf(Path(tmpdir), output)
        assert count == 0
