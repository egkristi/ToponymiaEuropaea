"""Base connector interface for all data sources.

Every data source connector must implement this interface. This ensures that
new sources can be added without modifying any core code—only by implementing
the standard interface and registering the connector.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator


@dataclass(frozen=True)
class BoundingBox:
    """Geographic bounding box (WGS84)."""

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    def contains(self, lon: float, lat: float) -> bool:
        return (self.min_lon <= lon <= self.max_lon and
                self.min_lat <= lat <= self.max_lat)


@dataclass
class ValidationError:
    """A validation error for a connector result."""

    field: str
    message: str
    severity: str = "error"  # error, warning


@dataclass
class ConnectorResult:
    """Normalized output from any data source connector.

    This is the universal intermediate format. All connectors must transform
    their source-specific data into this structure before it enters the database.
    """

    # Location
    latitude: float
    longitude: float
    elevation_m: float | None = None
    uncertainty_m: float | None = None

    # Name (at minimum one attestation)
    name_form: str = ""
    name_normalized: str = ""
    language_code: str = "und"  # ISO 639-3, "und" = undetermined
    script: str | None = None

    # Temporal bounds (year CE, negative for BCE)
    year_from: int | None = None
    year_to: int | None = None
    is_current: bool = True

    # Classification
    place_type: str | None = None

    # External identifiers
    source_id: str = ""
    wikidata_qid: str | None = None
    geonames_id: int | None = None
    osm_id: int | None = None

    # Alternative names (language_code -> list of forms)
    alternative_names: dict[str, list[str]] = field(default_factory=dict)

    # Provenance
    source_url: str | None = None
    source_license: str | None = None
    accessed_at: str | None = None


class BaseConnector(ABC):
    """Abstract base class for all data source connectors.

    To add a new data source:
    1. Create a new module in src/toponymia/connectors/
    2. Subclass BaseConnector
    3. Implement all abstract methods
    4. Register in the connector registry (connectors/__init__.py)

    The interface is intentionally minimal. A connector only needs to:
    - Fetch data (optionally filtered by bounding box)
    - Validate individual records
    - Report its coverage and license
    """

    # Class-level metadata (override in subclass)
    source_id: str = ""
    source_name: str = ""
    license: str = ""
    coverage_region: str = ""  # ISO 3166-1 alpha-2, or "global"
    source_url: str = ""

    @abstractmethod
    def fetch(self, bbox: BoundingBox | None = None, country: str | None = None) -> Iterator[ConnectorResult]:
        """Yield normalized place records from source.

        Args:
            bbox: Optional geographic filter.
            country: Optional ISO 3166-1 alpha-2 country filter.

        Yields:
            ConnectorResult instances, one per place/attestation.
        """
        ...

    @abstractmethod
    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a single record against source-specific rules.

        Returns:
            List of validation errors (empty if valid).
        """
        ...

    def count(self, bbox: BoundingBox | None = None, country: str | None = None) -> int | None:
        """Return estimated record count, if available without full fetch.

        Returns None if count is not cheaply available.
        """
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} source_id={self.source_id!r} region={self.coverage_region!r}>"
