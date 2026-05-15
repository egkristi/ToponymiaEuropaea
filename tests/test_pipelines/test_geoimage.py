"""Tests for the geoimage connector and enrichment pipeline."""

from __future__ import annotations

import json
from unittest.mock import patch

from toponymia.connectors.geoimage import (
    GeoImage,
    GeoImageConnector,
    GeoImageResult,
)
from toponymia.pipelines.geoimage_enrich import enrich_record, process_file


class TestGeoImageConnector:
    """Test GeoImageConnector logic (with mocked HTTP)."""

    def test_geosearch_parses_response(self):
        connector = GeoImageConnector()
        mock_geosearch = {
            "query": {
                "geosearch": [
                    {
                        "pageid": 12345,
                        "title": "File:Trondheim_view.jpg",
                        "lat": 63.43,
                        "lon": 10.39,
                        "dist": 42.5,
                    }
                ]
            }
        }
        mock_imageinfo = {
            "query": {
                "pages": {
                    "12345": {
                        "title": "File:Trondheim_view.jpg",
                        "imageinfo": [
                            {
                                "url": "https://upload.wikimedia.org/full.jpg",
                                "thumburl": "https://upload.wikimedia.org/thumb.jpg",
                                "descriptionurl": "https://commons.wikimedia.org/wiki/File:Trondheim_view.jpg",
                                "extmetadata": {
                                    "LicenseShortName": {"value": "CC BY-SA 4.0"},
                                },
                            }
                        ],
                    }
                }
            }
        }

        call_count = [0]

        def mock_http(url):
            call_count[0] += 1
            if "geosearch" in url:
                return mock_geosearch
            return mock_imageinfo

        with patch.object(connector, "_http_get_json", side_effect=mock_http):
            result = connector.get_images(63.43, 10.39)

        assert result is not None
        assert len(result.images) == 1
        img = result.images[0]
        assert img.title == "Trondheim_view.jpg"
        assert img.page_url == "https://commons.wikimedia.org/wiki/File:Trondheim_view.jpg"
        assert img.image_url == "https://upload.wikimedia.org/full.jpg"
        assert img.thumb_url == "https://upload.wikimedia.org/thumb.jpg"
        assert img.license == "CC BY-SA 4.0"
        assert img.distance_m == 42.5
        assert img.source == "wikimedia_commons"

    def test_geosearch_no_results(self):
        connector = GeoImageConnector()
        mock_response = {"query": {"geosearch": []}}
        with patch.object(connector, "_http_get_json", return_value=mock_response):
            result = connector.get_images(90.0, 0.0)
        assert result is not None
        assert result.images == []

    def test_geosearch_api_failure(self):
        connector = GeoImageConnector()
        with patch.object(connector, "_http_get_json", return_value=None):
            result = connector.get_images(63.43, 10.39)
        assert result is not None
        assert result.images == []

    def test_multiple_images(self):
        connector = GeoImageConnector(max_images=3)
        mock_geosearch = {
            "query": {
                "geosearch": [
                    {
                        "pageid": i,
                        "title": f"File:img{i}.jpg",
                        "lat": 63.0,
                        "lon": 10.0,
                        "dist": i * 10.0,
                    }
                    for i in range(3)
                ]
            }
        }
        mock_imageinfo = {
            "query": {
                "pages": {
                    str(i): {
                        "title": f"File:img{i}.jpg",
                        "imageinfo": [
                            {
                                "url": f"https://example.com/img{i}.jpg",
                                "thumburl": f"https://example.com/thumb{i}.jpg",
                                "descriptionurl": f"https://commons.wikimedia.org/wiki/File:img{i}.jpg",
                                "extmetadata": {"LicenseShortName": {"value": "CC0"}},
                            }
                        ],
                    }
                    for i in range(3)
                }
            }
        }

        call_count = [0]

        def mock_http(url):
            call_count[0] += 1
            if "geosearch" in url:
                return mock_geosearch
            return mock_imageinfo

        with patch.object(connector, "_http_get_json", side_effect=mock_http):
            result = connector.get_images(63.0, 10.0)

        assert result is not None
        assert len(result.images) == 3
        assert result.images[0].distance_m == 0.0
        assert result.images[2].distance_m == 20.0

    def test_imageinfo_missing_url_skipped(self):
        connector = GeoImageConnector()
        mock_geosearch = {
            "query": {
                "geosearch": [
                    {"pageid": 1, "title": "File:no_url.jpg", "lat": 60.0, "lon": 5.0, "dist": 10.0}
                ]
            }
        }
        mock_imageinfo = {
            "query": {
                "pages": {
                    "1": {
                        "title": "File:no_url.jpg",
                        "imageinfo": [{"url": "", "thumburl": "", "descriptionurl": ""}],
                    }
                }
            }
        }

        def mock_http(url):
            if "geosearch" in url:
                return mock_geosearch
            return mock_imageinfo

        with patch.object(connector, "_http_get_json", side_effect=mock_http):
            result = connector.get_images(60.0, 5.0)

        assert result is not None
        assert result.images == []


class TestEnrichRecord:
    """Test the enrich_record function."""

    def _make_record(self, **kwargs):
        base = {
            "name_form": "Testplace",
            "latitude": 63.43,
            "longitude": 10.39,
            "place_type": "P.PPL",
        }
        base.update(kwargs)
        return base

    def test_enriches_record_with_images(self):
        record = self._make_record()
        connector = GeoImageConnector()
        mock_result = GeoImageResult(
            latitude=63.43,
            longitude=10.39,
            radius_m=1000,
            images=[
                GeoImage(
                    title="Test.jpg",
                    page_url="https://commons.wikimedia.org/wiki/File:Test.jpg",
                    image_url="https://upload.wikimedia.org/test.jpg",
                    thumb_url="https://upload.wikimedia.org/thumb_test.jpg",
                    license="CC BY-SA 4.0",
                    distance_m=15.0,
                    lat=63.43,
                    lon=10.39,
                )
            ],
        )
        with patch.object(connector, "get_images", return_value=mock_result):
            result = enrich_record(record, connector)

        assert result is True
        assert "_image_links" in record
        assert len(record["_image_links"]) == 1
        link = record["_image_links"][0]
        assert link["title"] == "Test.jpg"
        assert link["page_url"] == "https://commons.wikimedia.org/wiki/File:Test.jpg"
        assert link["thumb_url"] == "https://upload.wikimedia.org/thumb_test.jpg"
        assert link["license"] == "CC BY-SA 4.0"
        assert link["distance_m"] == 15.0
        assert link["source"] == "wikimedia_commons"

    def test_skips_record_without_coordinates(self):
        record = {"name_form": "NoCoords", "place_type": "P.PPL"}
        connector = GeoImageConnector()
        result = enrich_record(record, connector)
        assert result is False
        assert "_image_links" not in record

    def test_skips_record_with_existing_images(self):
        record = self._make_record(_image_links=[{"title": "existing.jpg"}])
        connector = GeoImageConnector()
        result = enrich_record(record, connector)
        assert result is False

    def test_no_images_found(self):
        record = self._make_record()
        connector = GeoImageConnector()
        mock_result = GeoImageResult(latitude=63.43, longitude=10.39, radius_m=1000, images=[])
        with patch.object(connector, "get_images", return_value=mock_result):
            result = enrich_record(record, connector)
        assert result is False
        assert "_image_links" not in record

    def test_connector_returns_none(self):
        record = self._make_record()
        connector = GeoImageConnector()
        with patch.object(connector, "get_images", return_value=None):
            result = enrich_record(record, connector)
        assert result is False


class TestProcessFile:
    """Test the process_file function."""

    def test_process_file_dry_run(self, tmp_path):
        jsonl = tmp_path / "test.jsonl"
        records = [
            {"name_form": "Place1", "latitude": 60.0, "longitude": 5.0, "place_type": "P.PPL"},
            {"name_form": "Place2", "latitude": 61.0, "longitude": 6.0, "place_type": "H.LK"},
        ]
        jsonl.write_text("\n".join(json.dumps(r) for r in records))

        connector = GeoImageConnector()
        stats = process_file(jsonl, connector, dry_run=True)

        assert stats["total"] == 2
        assert stats["enriched"] == 0
        assert stats["skipped_existing"] == 0

    def test_process_file_with_limit(self, tmp_path):
        jsonl = tmp_path / "test.jsonl"
        records = [
            {
                "name_form": f"Place{i}",
                "latitude": 60.0 + i,
                "longitude": 5.0,
                "place_type": "P.PPL",
            }
            for i in range(5)
        ]
        jsonl.write_text("\n".join(json.dumps(r) for r in records))

        connector = GeoImageConnector()
        mock_result = GeoImageResult(
            latitude=60.0,
            longitude=5.0,
            radius_m=1000,
            images=[
                GeoImage(
                    title="img.jpg",
                    page_url="https://example.com",
                    image_url="https://example.com/img.jpg",
                    thumb_url="https://example.com/thumb.jpg",
                    license="CC0",
                    distance_m=10.0,
                    lat=60.0,
                    lon=5.0,
                )
            ],
        )
        with patch.object(connector, "get_images", return_value=mock_result):
            stats = process_file(jsonl, connector, limit=2)

        assert stats["enriched"] == 2
        # Verify file was written with enriched records
        written = [json.loads(line) for line in jsonl.read_text().strip().split("\n")]
        enriched_count = sum(1 for r in written if "_image_links" in r)
        assert enriched_count == 2

    def test_process_file_skips_existing(self, tmp_path):
        jsonl = tmp_path / "test.jsonl"
        records = [
            {
                "name_form": "HasImages",
                "latitude": 60.0,
                "longitude": 5.0,
                "place_type": "P.PPL",
                "_image_links": [{"title": "existing.jpg"}],
            },
        ]
        jsonl.write_text(json.dumps(records[0]))

        connector = GeoImageConnector()
        stats = process_file(jsonl, connector)

        assert stats["skipped_existing"] == 1
        assert stats["enriched"] == 0

    def test_process_file_idempotent(self, tmp_path):
        jsonl = tmp_path / "test.jsonl"
        record = {"name_form": "Place", "latitude": 60.0, "longitude": 5.0, "place_type": "P.PPL"}
        jsonl.write_text(json.dumps(record))

        connector = GeoImageConnector()
        mock_result = GeoImageResult(
            latitude=60.0,
            longitude=5.0,
            radius_m=1000,
            images=[
                GeoImage(
                    title="photo.jpg",
                    page_url="https://example.com",
                    image_url="https://example.com/photo.jpg",
                    thumb_url="https://example.com/thumb.jpg",
                    license="CC BY 4.0",
                    distance_m=5.0,
                    lat=60.0,
                    lon=5.0,
                )
            ],
        )
        with patch.object(connector, "get_images", return_value=mock_result):
            stats1 = process_file(jsonl, connector)
            stats2 = process_file(jsonl, connector)

        assert stats1["enriched"] == 1
        assert stats2["enriched"] == 0
        assert stats2["skipped_existing"] == 1
