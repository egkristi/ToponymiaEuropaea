"""Minimal API placeholder for Toponymia Europaea.

This module provides a lightweight HTTP API for querying the toponymic
databank. In production, this would be backed by PostgreSQL+PostGIS.
For local development, it queries DuckDB/Parquet directly.

Usage:
    python -m toponymia.api

Environment variables:
    DATABASE_URL: PostgreSQL connection string (optional)
    PARQUET_PATH: Path to Parquet files for DuckDB queries
    API_PORT: Port to listen on (default: 8000)
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class ToponymiaHandler(BaseHTTPRequestHandler):
    """HTTP request handler for toponymic queries."""

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/health":
            self._json_response({"status": "ok"})
        elif path == "/api/v1/places":
            self._handle_places(params)
        elif path == "/api/v1/stats":
            self._handle_stats()
        else:
            self._json_response({"error": "not found"}, status=404)

    def _handle_places(self, params: dict) -> None:
        """Query places with optional filters."""
        country = params.get("country", [None])[0]
        name = params.get("name", [None])[0]
        limit = int(params.get("limit", ["100"])[0])

        # Clamp limit to prevent abuse
        limit = min(limit, 1000)

        conditions = []
        if country:
            conditions.append(f"country_code = '{country}'")
        if name:
            # Use ILIKE for case-insensitive partial match
            conditions.append(f"name ILIKE '%{name}%'")

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT * FROM databank {where} LIMIT {limit}"  # noqa: S608

        try:
            from toponymia.pipelines.analytical import query_databank

            databank_path = Path(os.environ.get("DATABANK_PATH", "/data/databank"))
            if not databank_path.exists():
                local = Path(__file__).parent.parent.parent / "databank"
                if local.exists():
                    databank_path = local

            results = query_databank(sql, databank_path=databank_path)
            self._json_response({"count": len(results), "results": results})
        except Exception as e:
            self._json_response({"error": str(e)}, status=500)

    def _handle_stats(self) -> None:
        """Return databank statistics."""
        try:
            from toponymia.pipelines.analytical import query_databank

            databank_path = Path(os.environ.get("DATABANK_PATH", "/data/databank"))
            if not databank_path.exists():
                local = Path(__file__).parent.parent.parent / "databank"
                if local.exists():
                    databank_path = local

            stats_sql = (
                "SELECT country_code, COUNT(*) as count "
                "FROM databank GROUP BY country_code ORDER BY count DESC"
            )
            results = query_databank(
                stats_sql,
                databank_path=databank_path,
            )
            total = sum(r["count"] for r in results)
            self._json_response({"total_records": total, "by_country": results})
        except Exception as e:
            self._json_response({"error": str(e)}, status=500)

    def _json_response(self, data: dict, *, status: int = 200) -> None:
        """Send a JSON response."""
        body = json.dumps(data, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        """Override to use print instead of stderr."""
        print(f"[API] {args[0]}")


def main() -> None:
    """Start the API server."""
    port = int(os.environ.get("API_PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), ToponymiaHandler)  # noqa: S104
    print(f"Toponymia API listening on http://0.0.0.0:{port}")
    print("  GET /health         - Health check")
    print("  GET /api/v1/places  - Query places (?country=NO&name=Oslo&limit=10)")
    print("  GET /api/v1/stats   - Databank statistics")
    server.serve_forever()


if __name__ == "__main__":
    main()
