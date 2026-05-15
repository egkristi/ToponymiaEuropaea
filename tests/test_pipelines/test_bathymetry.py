"""Tests for the bathymetry connector and enrichment pipeline."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from toponymia.connectors.bathymetry import (
    DEPTH_ELIGIBLE_TYPES,
    LAKE_TYPES,
    MARINE_TYPES,
    BathymetryConnector,
    DepthResult,
)
from toponymia.pipelines.bathymetry_enrich import enrich_record, process_file


class TestDepthEligibleTypes:
    """Test type classification for depth eligibility."""

    def test_marine_types_are_eligible(self):
        for t in MARINE_TYPES:
            assert t in DEPTH_ELIGIBLE_TYPES

    def test_lake_types_are_eligible(self):
        for t in LAKE_TYPES:
            assert t in DEPTH_ELIGIBLE_TYPES

    def test_non_hydro_types_not_eligible(self):
        non_hydro = ["P.PPL", "S.FRM", "T.MT", "T.ISL", "Myr"]
        for t in non_hydro:
            assert t not in DEPTH_ELIGIBLE_TYPES

    def test_rivers_not_eligible(self):
        rivers = ["H.STM", "H.STMX", "Elv"]
        for t in rivers:
            assert t not in DEPTH_ELIGIBLE_TYPES


class TestBathymetryConnector:
    """Test BathymetryConnector logic (with mocked HTTP)."""

    def test_gebco_parses_response(self):
        connector = BathymetryConnector()
        mock_response = {
            "table": {
                "columnNames": ["latitude", "longitude", "elevation"],
                "rows": [[60.0, 5.0, -320.5]],
            }
        }
        with patch.object(connector, "_http_get_json", return_value=mock_response):
            result = connector.query_gebco(60.0, 5.0)
        assert result is not None
        assert result.depth_m == 320.5
        assert result.source == "gebco"
        assert result.resolution_m == 450.0

    def test_gebco_positive_elevation_returns_none(self):
        """Positive elevation = above sea level, no depth."""
        connector = BathymetryConnector()
        mock_response = {
            "table": {
                "rows": [[60.0, 5.0, 150.0]],
            }
        }
        with patch.object(connector, "_http_get_json", return_value=mock_response):
            result = connector.query_gebco(60.0, 5.0)
        assert result is None

    def test_gebco_api_failure_returns_none(self):
        connector = BathymetryConnector()
        with patch.object(connector, "_http_get_json", return_value=None):
            result = connector.query_gebco(60.0, 5.0)
        assert result is None

    def test_emodnet_parses_response(self):
        connector = BathymetryConnector()
        mock_response = {"depth": -85.3, "avg": -83.1}
        with patch.object(connector, "_http_get_json", return_value=mock_response):
            result = connector.query_emodnet(60.0, 5.0)
        assert result is not None
        assert result.depth_m == 85.3
        assert result.source == "emodnet"

    def test_emodnet_positive_depth_returns_none(self):
        connector = BathymetryConnector()
        mock_response = {"depth": 5.0}
        with patch.object(connector, "_http_get_json", return_value=mock_response):
            result = connector.query_emodnet(60.0, 5.0)
        assert result is None

    def test_nve_lake_parses_response(self):
        connector = BathymetryConnector()
        mock_response = {
            "features": [
                {
                    "attributes": {
                        "Max_Dyp": 453.0,
                        "Middeldyp": 178.0,
                        "Areal_km2": 362.0,
                        "vatnLnr": 1100,
                        "Navn": "Mjøsa",
                    }
                }
            ]
        }
        with patch.object(connector, "_http_get_json", return_value=mock_response):
            result = connector.query_nve_lake(60.7, 10.7)
        assert result is not None
        assert result.depth_m == 453.0
        assert result.depth_max_m == 453.0
        assert result.depth_mean_m == 178.0
        assert result.source == "nve"

    def test_nve_lake_no_features_returns_none(self):
        connector = BathymetryConnector()
        mock_response = {"features": []}
        with patch.object(connector, "_http_get_json", return_value=mock_response):
            result = connector.query_nve_lake(60.0, 5.0)
        assert result is None

    def test_get_depth_norwegian_lake_uses_nve(self):
        connector = BathymetryConnector()
        nve_result = DepthResult(latitude=60.7, longitude=10.7, depth_m=453.0, source="nve")
        with patch.object(connector, "query_nve_lake", return_value=nve_result):
            result = connector.get_depth(60.7, 10.7, place_type="H.LK", country_code="NO")
        assert result is not None
        assert result.source == "nve"

    def test_get_depth_marine_europe_tries_emodnet_first(self):
        connector = BathymetryConnector()
        emodnet_result = DepthResult(latitude=60.0, longitude=5.0, depth_m=200.0, source="emodnet")
        with patch.object(connector, "query_emodnet", return_value=emodnet_result) as mock_emodnet:
            result = connector.get_depth(60.0, 5.0, place_type="H.FJD", country_code="NO")
        assert result is not None
        assert result.source == "emodnet"
        mock_emodnet.assert_called_once()

    def test_get_depth_marine_europe_falls_back_to_gebco(self):
        connector = BathymetryConnector()
        gebco_result = DepthResult(latitude=60.0, longitude=5.0, depth_m=150.0, source="gebco")
        with (
            patch.object(connector, "query_emodnet", return_value=None),
            patch.object(connector, "query_gebco", return_value=gebco_result),
        ):
            result = connector.get_depth(60.0, 5.0, place_type="H.BAY", country_code="NO")
        assert result is not None
        assert result.source == "gebco"

    def test_get_depth_non_europe_marine_uses_gebco(self):
        connector = BathymetryConnector()
        gebco_result = DepthResult(latitude=30.0, longitude=-80.0, depth_m=500.0, source="gebco")
        with patch.object(connector, "query_gebco", return_value=gebco_result):
            result = connector.get_depth(30.0, -80.0, place_type="H.BAY", country_code="US")
        assert result is not None
        assert result.source == "gebco"

    def test_is_europe(self):
        assert BathymetryConnector._is_europe(60.0, 10.0) is True
        assert BathymetryConnector._is_europe(65.0, 25.0) is True
        assert BathymetryConnector._is_europe(30.0, -80.0) is False
        assert BathymetryConnector._is_europe(10.0, 100.0) is False


class TestEnrichRecord:
    """Test the enrich_record function."""

    def test_enriches_eligible_record(self):
        connector = MagicMock()
        connector.get_depth.return_value = DepthResult(
            latitude=60.0, longitude=5.0, depth_m=200.0, source="gebco", resolution_m=450.0
        )
        record = {
            "name_form": "Sognefjorden",
            "place_type": "H.FJD",
            "latitude": 61.1,
            "longitude": 5.5,
            "country_code": "NO",
        }
        assert enrich_record(record, connector) is True
        assert record["_depth_m"] == 200.0
        assert record["_depth_source"] == "gebco"
        assert record["_depth_resolution_m"] == 450.0

    def test_skips_non_eligible_type(self):
        connector = MagicMock()
        record = {"place_type": "P.PPL", "latitude": 60.0, "longitude": 5.0}
        assert enrich_record(record, connector) is False
        connector.get_depth.assert_not_called()

    def test_skips_record_without_coordinates(self):
        connector = MagicMock()
        record = {"place_type": "H.LK"}
        assert enrich_record(record, connector) is False
        connector.get_depth.assert_not_called()

    def test_skips_record_already_enriched(self):
        connector = MagicMock()
        record = {
            "place_type": "H.LK",
            "latitude": 60.0,
            "longitude": 5.0,
            "_depth_m": 100.0,
            "_depth_source": "nve",
        }
        assert enrich_record(record, connector) is False
        connector.get_depth.assert_not_called()

    def test_returns_false_when_no_depth_found(self):
        connector = MagicMock()
        connector.get_depth.return_value = None
        record = {
            "place_type": "H.LK",
            "latitude": 60.0,
            "longitude": 5.0,
            "country_code": "NO",
        }
        assert enrich_record(record, connector) is False
        assert "_depth_m" not in record

    def test_adds_mean_depth_when_available(self):
        connector = MagicMock()
        connector.get_depth.return_value = DepthResult(
            latitude=60.7,
            longitude=10.7,
            depth_m=453.0,
            depth_max_m=453.0,
            depth_mean_m=178.0,
            source="nve",
        )
        record = {
            "place_type": "H.LK",
            "latitude": 60.7,
            "longitude": 10.7,
            "country_code": "NO",
        }
        enrich_record(record, connector)
        assert record["_depth_m"] == 453.0
        assert record["_depth_max_m"] == 453.0
        assert record["_depth_mean_m"] == 178.0
        assert record["_depth_source"] == "nve"


class TestProcessFile:
    """Test the process_file function."""

    def test_dry_run_does_not_modify_file(self, tmp_path):
        records = [
            {"name_form": "TestLake", "place_type": "H.LK", "latitude": 60.0, "longitude": 5.0},
            {"name_form": "TestTown", "place_type": "P.PPL", "latitude": 61.0, "longitude": 6.0},
        ]
        path = tmp_path / "test.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in records) + "\n")

        connector = MagicMock()
        stats = process_file(path, connector, dry_run=True)

        assert stats["total"] == 2
        assert stats["eligible"] == 1
        assert stats["enriched"] == 0
        # File should be unchanged
        lines = path.read_text().strip().split("\n")
        assert len(lines) == 2
        connector.get_depth.assert_not_called()

    def test_enriches_eligible_records_in_file(self, tmp_path):
        records = [
            {"name_form": "Fjord", "place_type": "H.FJD", "latitude": 61.0, "longitude": 5.0},
            {"name_form": "Town", "place_type": "P.PPL", "latitude": 60.0, "longitude": 6.0},
            {"name_form": "Lake", "place_type": "H.LK", "latitude": 60.5, "longitude": 7.0},
        ]
        path = tmp_path / "test.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in records) + "\n")

        connector = BathymetryConnector()
        depth_result = DepthResult(
            latitude=61.0, longitude=5.0, depth_m=300.0, source="gebco", resolution_m=450.0
        )
        with patch.object(connector, "get_depth", return_value=depth_result):
            stats = process_file(path, connector)

        assert stats["enriched"] == 2
        assert stats["eligible"] == 2

        # Verify file was updated
        updated = [json.loads(line) for line in path.read_text().strip().split("\n")]
        assert updated[0]["_depth_m"] == 300.0
        assert "_depth_m" not in updated[1]  # Town not enriched
        assert updated[2]["_depth_m"] == 300.0

    def test_respects_limit(self, tmp_path):
        records = [
            {
                "name_form": f"Lake{i}",
                "place_type": "H.LK",
                "latitude": 60.0 + i * 0.1,
                "longitude": 5.0,
            }
            for i in range(5)
        ]
        path = tmp_path / "test.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in records) + "\n")

        connector = BathymetryConnector()
        depth_result = DepthResult(
            latitude=60.0, longitude=5.0, depth_m=100.0, source="gebco", resolution_m=450.0
        )
        with patch.object(connector, "get_depth", return_value=depth_result):
            stats = process_file(path, connector, limit=2)

        assert stats["enriched"] == 2
        assert stats["eligible"] == 5

    def test_skips_already_enriched(self, tmp_path):
        records = [
            {
                "name_form": "Lake",
                "place_type": "H.LK",
                "latitude": 60.0,
                "longitude": 5.0,
                "_depth_m": 50.0,
                "_depth_source": "nve",
            },
        ]
        path = tmp_path / "test.jsonl"
        path.write_text(json.dumps(records[0]) + "\n")

        connector = MagicMock()
        stats = process_file(path, connector)

        assert stats["skipped_existing"] == 1
        assert stats["enriched"] == 0
        connector.get_depth.assert_not_called()
