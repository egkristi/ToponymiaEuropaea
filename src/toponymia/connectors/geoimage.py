"""Geolocated image connector.

Retrieves links to geotagged photographs near a given coordinate from:
- Wikimedia Commons geosearch API (free, no API key required)

Images are returned as structured links with metadata (title, URL, license,
distance from point) for presentation to the user.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from urllib.parse import quote

logger = logging.getLogger(__name__)

# Rate limiting: minimum seconds between API calls
_MIN_REQUEST_INTERVAL = 2.0

# Retry config for 429 responses
_MAX_RETRIES = 5
_RETRY_BASE_DELAY = 10.0  # seconds, doubles each retry

# Wikimedia Commons API
_COMMONS_API = "https://commons.wikimedia.org/w/api.php"

# Default search radius in meters
_DEFAULT_RADIUS_M = 1000

# Maximum images to return per location
_DEFAULT_MAX_IMAGES = 5


@dataclass
class GeoImage:
    """A geolocated image result."""

    title: str
    page_url: str
    image_url: str
    thumb_url: str
    license: str
    distance_m: float
    lat: float
    lon: float
    source: str = "wikimedia_commons"


@dataclass
class GeoImageResult:
    """Result of a geoimage search for a location."""

    latitude: float
    longitude: float
    radius_m: int
    images: list[GeoImage] = field(default_factory=list)
    source: str = "wikimedia_commons"


class GeoImageConnector:
    """Connector for geolocated images from Wikimedia Commons.

    Uses the MediaWiki geosearch API to find images near a coordinate,
    then fetches image metadata (URL, license, thumbnail).
    """

    def __init__(
        self,
        *,
        timeout: float = 15.0,
        radius_m: int = _DEFAULT_RADIUS_M,
        max_images: int = _DEFAULT_MAX_IMAGES,
    ):
        self._timeout = timeout
        self._radius_m = radius_m
        self._max_images = max_images
        self._last_request_time: float = 0.0

    def _rate_limit(self) -> None:
        """Enforce minimum interval between API calls."""
        elapsed = time.time() - self._last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def _http_get_json(self, url: str) -> dict | None:
        """Perform HTTP GET and parse JSON response, with retry on 429."""
        self._rate_limit()
        req = urllib.request.Request(  # noqa: S310
            url,
            headers={"User-Agent": "ToponymiaEuropaea/0.5 (research; toponymia project)"},
        )
        for attempt in range(_MAX_RETRIES + 1):
            try:
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:  # noqa: S310
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < _MAX_RETRIES:
                    delay = _RETRY_BASE_DELAY * (2**attempt)
                    logger.info("429 rate limited, retrying in %.0fs…", delay)
                    time.sleep(delay)
                    self._last_request_time = time.time()
                    continue
                logger.warning("HTTP request failed: %s — %s", url[:120], exc)
                return None
            except Exception as exc:
                logger.warning("HTTP request failed: %s — %s", url[:120], exc)
                return None
        return None

    def _geosearch(self, lat: float, lon: float) -> list[dict]:
        """Find geotagged files near a coordinate via Commons geosearch."""
        url = (
            f"{_COMMONS_API}?action=query&list=geosearch"
            f"&gscoord={lat}|{lon}"
            f"&gsradius={self._radius_m}"
            f"&gslimit={self._max_images}"
            f"&gsnamespace=6"
            f"&format=json"
        )
        data = self._http_get_json(url)
        if data is None:
            return []
        return data.get("query", {}).get("geosearch", [])

    def _get_image_info(self, titles: list[str]) -> dict[str, dict]:
        """Fetch image URLs and license metadata for a batch of file titles."""
        if not titles:
            return {}

        # Batch up to 50 titles per API call (MediaWiki limit)
        joined = "|".join(quote(t, safe="/:") for t in titles[:50])
        url = (
            f"{_COMMONS_API}?action=query"
            f"&titles={joined}"
            f"&prop=imageinfo"
            f"&iiprop=url|extmetadata"
            f"&iiurlwidth=640"
            f"&format=json"
        )
        data = self._http_get_json(url)
        if data is None:
            return {}

        results: dict[str, dict] = {}
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            title = page.get("title", "")
            imageinfo = page.get("imageinfo", [])
            if imageinfo:
                ii = imageinfo[0]
                license_name = ""
                ext = ii.get("extmetadata", {})
                license_short = ext.get("LicenseShortName", {})
                if isinstance(license_short, dict):
                    license_name = license_short.get("value", "")
                elif isinstance(license_short, str):
                    license_name = license_short

                results[title] = {
                    "image_url": ii.get("url", ""),
                    "thumb_url": ii.get("thumburl", ""),
                    "page_url": ii.get("descriptionurl", ""),
                    "license": license_name,
                }
        return results

    def get_images(self, lat: float, lon: float) -> GeoImageResult | None:
        """Find geolocated images near a coordinate.

        Returns a GeoImageResult with up to max_images images,
        or None if the search fails entirely.
        """
        geo_results = self._geosearch(lat, lon)
        if not geo_results:
            return GeoImageResult(
                latitude=lat,
                longitude=lon,
                radius_m=self._radius_m,
                images=[],
            )

        # Fetch image metadata in batch
        titles = [item["title"] for item in geo_results]
        image_info = self._get_image_info(titles)

        images: list[GeoImage] = []
        for item in geo_results:
            title = item["title"]
            info = image_info.get(title, {})
            if not info.get("image_url"):
                continue

            images.append(
                GeoImage(
                    title=title.removeprefix("File:"),
                    page_url=info.get("page_url", ""),
                    image_url=info["image_url"],
                    thumb_url=info.get("thumb_url", ""),
                    license=info.get("license", ""),
                    distance_m=item.get("dist", 0.0),
                    lat=item.get("lat", lat),
                    lon=item.get("lon", lon),
                )
            )

        return GeoImageResult(
            latitude=lat,
            longitude=lon,
            radius_m=self._radius_m,
            images=images,
        )
