"""Bathymetry data connector.

Retrieves water depth data for hydrological features from:
- GEBCO (General Bathymetric Chart of the Oceans) via NOAA ERDDAP — global ocean/sea
- EMODnet Bathymetry REST API — higher-resolution European waters
- NVE Innsjødatabasen — Norwegian lake depths (max, mean)

For marine features (fjords, bays, straits, coves), GEBCO provides global
coverage at ~450m resolution.  For lakes, NVE provides authoritative depth
data for Norwegian lakes with max/mean depth and surface area.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

# Rate limiting: minimum seconds between API calls
_MIN_REQUEST_INTERVAL = 0.25

# GEBCO via NOAA ERDDAP (free, no API key)
_GEBCO_ERDDAP_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/GEBCO_2020.json"

# EMODnet Bathymetry (European waters, higher resolution)
_EMODNET_URL = "https://rest.emodnet-bathymetry.eu/depth_sample"

# NVE Innsjødatabasen (Norwegian lakes)
# NOTE: NVE has migrated their ArcGIS services; this endpoint may need updating.
# See https://kartkatalog.geonorge.no/ UUID 823b8639-9a49-41bf-8571-3608435eb149
_NVE_LAKE_URL = (
    "https://gis3.nve.no/arcgis/rest/services/mapservice/Innsjodatabase2/MapServer/1/query"
)


# Hydrological feature types eligible for depth data
MARINE_TYPES = frozenset(
    [
        "H.SHOL",
        "H.COVE",
        "H.BAY",
        "H.FJD",
        "H.STRT",
        "H.BGHT",
        "H.INLT",
        "H.NRWS",
        "H.SD",
        "H.BNK",
        "H.CAPG",
        # Norwegian marine types
        "Fjord",
        "Vik i sjø",
        "Sund i sjø",
    ]
)

LAKE_TYPES = frozenset(
    [
        "H.LK",
        "H.LKS",
        "H.PND",
        "H.LGN",
        # Norwegian lake types
        "Vann",
        "Gruppe av vann",
    ]
)

# All types that can have depth data
DEPTH_ELIGIBLE_TYPES = MARINE_TYPES | LAKE_TYPES


@dataclass
class DepthResult:
    """Bathymetry result for a single location."""

    latitude: float
    longitude: float
    depth_m: float | None = None  # Positive = below surface
    depth_max_m: float | None = None  # For lakes with detailed data
    depth_mean_m: float | None = None  # For lakes with detailed data
    source: str = ""  # "gebco" | "emodnet" | "nve"
    resolution_m: float | None = None


class BathymetryConnector:
    """Connector for bathymetry (water depth) data.

    Queries multiple sources depending on feature type and location:
    - Norwegian lakes: NVE Innsjødatabasen (authoritative max/mean depth)
    - European marine: EMODnet (higher resolution)
    - Global marine fallback: GEBCO via ERDDAP
    """

    def __init__(self, *, timeout: float = 15.0):
        self._timeout = timeout
        self._last_request_time: float = 0.0

    def _rate_limit(self) -> None:
        """Enforce minimum interval between API calls."""
        elapsed = time.time() - self._last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def _http_get_json(self, url: str) -> Any:
        """Perform HTTP GET and parse JSON response."""
        self._rate_limit()
        req = urllib.request.Request(  # noqa: S310
            url,
            headers={"User-Agent": "ToponymiaEuropaea/0.5 (research)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:  # noqa: S310
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            logger.warning("HTTP request failed: %s — %s", url[:120], exc)
            return None

    def query_gebco(self, lat: float, lon: float) -> DepthResult | None:
        """Query GEBCO grid for ocean/sea depth at a point.

        GEBCO elevation is negative below sea level.  We convert to positive
        depth values (depth_m > 0 means underwater).
        """
        # ERDDAP griddap query: nearest point
        url = f"{_GEBCO_ERDDAP_URL}?elevation[({lat}):1:({lat})][({lon}):1:({lon})]"
        data = self._http_get_json(url)
        if data is None:
            return None

        try:
            rows = data["table"]["rows"]
            if rows:
                elevation = rows[0][2]  # [lat, lon, elevation]
                if elevation is not None and elevation < 0:
                    return DepthResult(
                        latitude=lat,
                        longitude=lon,
                        depth_m=abs(elevation),
                        source="gebco",
                        resolution_m=450.0,
                    )
        except (KeyError, IndexError, TypeError) as exc:
            logger.debug("GEBCO parse error: %s", exc)

        return None

    def query_emodnet(self, lat: float, lon: float) -> DepthResult | None:
        """Query EMODnet Bathymetry for depth at a point (European waters)."""
        params = urlencode({"lat": lat, "lon": lon})
        url = f"{_EMODNET_URL}?{params}"
        data = self._http_get_json(url)
        if data is None:
            return None

        try:
            # EMODnet returns depth as negative (below sea level)
            depth_val = data.get("depth") or data.get("avg")
            if depth_val is not None and depth_val < 0:
                return DepthResult(
                    latitude=lat,
                    longitude=lon,
                    depth_m=abs(depth_val),
                    source="emodnet",
                    resolution_m=115.0,
                )
        except (TypeError, AttributeError) as exc:
            logger.debug("EMODnet parse error: %s", exc)

        return None

    def query_nve_lake(
        self, lat: float, lon: float, *, radius_m: float = 1000.0
    ) -> DepthResult | None:
        """Query NVE Innsjødatabasen for Norwegian lake depth.

        Searches by proximity to the point coordinates.
        """
        # ArcGIS REST query: find lake features near the point
        params = urlencode(
            {
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "spatialRel": "esriSpatialRelIntersects",
                "distance": radius_m,
                "units": "esriSRUnit_Meter",
                "outFields": "Max_Dyp,Middeldyp,Areal_km2,vatnLnr,Navn",
                "returnGeometry": "false",
                "f": "json",
                "inSR": "4326",
            }
        )
        url = f"{_NVE_LAKE_URL}?{params}"
        data = self._http_get_json(url)
        if data is None:
            return None

        try:
            features = data.get("features", [])
            if features:
                attrs = features[0]["attributes"]
                max_depth = attrs.get("Max_Dyp")
                mean_depth = attrs.get("Middeldyp")
                # NVE stores depths as positive meters
                if max_depth is not None and max_depth > 0:
                    return DepthResult(
                        latitude=lat,
                        longitude=lon,
                        depth_m=max_depth,
                        depth_max_m=max_depth,
                        depth_mean_m=mean_depth if mean_depth and mean_depth > 0 else None,
                        source="nve",
                    )
        except (KeyError, IndexError, TypeError) as exc:
            logger.debug("NVE parse error: %s", exc)

        return None

    def get_depth(
        self,
        lat: float,
        lon: float,
        *,
        place_type: str = "",
        country_code: str = "",
    ) -> DepthResult | None:
        """Get depth for a hydrological feature, trying best source first.

        Strategy:
        - Norwegian lakes → NVE first, then skip (NVE is authoritative)
        - Other lakes → GEBCO (lakes may not be in marine databases)
        - Marine features in Europe → EMODnet first, GEBCO fallback
        - Marine features elsewhere → GEBCO
        """
        is_lake = place_type in LAKE_TYPES
        is_marine = place_type in MARINE_TYPES
        is_norway = country_code == "NO"
        is_europe = self._is_europe(lat, lon)

        # Norwegian lakes: NVE is the authoritative source
        if is_lake and is_norway:
            result = self.query_nve_lake(lat, lon)
            if result:
                return result

        # Marine features: try EMODnet for European waters, then GEBCO
        if is_marine:
            if is_europe:
                result = self.query_emodnet(lat, lon)
                if result:
                    return result
            return self.query_gebco(lat, lon)

        # Non-Norwegian lakes: try GEBCO (some large lakes appear)
        if is_lake:
            return self.query_gebco(lat, lon)

        # Fallback for any other eligible type
        return self.query_gebco(lat, lon)

    @staticmethod
    def _is_europe(lat: float, lon: float) -> bool:
        """Rough check if coordinates are in European waters."""
        return 35.0 <= lat <= 72.0 and -25.0 <= lon <= 45.0
