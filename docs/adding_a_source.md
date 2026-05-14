# Adding a Data Source

Data source connectors are plugins that bring external place name data into the Toponymia Europaea framework. Each connector normalizes its source's specific format into a standard `ConnectorResult` that the ingestion pipeline can process uniformly.

## Interface

```python
from toponymia.connectors.base import BaseConnector, BoundingBox, ConnectorResult, ValidationError

class MySourceConnector(BaseConnector):
    source_id = "my_source"        # Unique identifier
    source_name = "My Source"      # Human-readable name
    license = "CC-BY-4.0"         # SPDX license identifier
    coverage_region = "NO"         # ISO 3166-1 or "global"
    source_url = "https://..."     # Source documentation URL
    
    def fetch(self, bbox: BoundingBox | None = None, country: str | None = None) -> Iterator[ConnectorResult]:
        """Yield normalized records from the source."""
        ...
    
    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a single record."""
        ...
```

## ConnectorResult Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `latitude` | float | Yes | WGS84 latitude |
| `longitude` | float | Yes | WGS84 longitude |
| `name_form` | str | Yes | Original name form |
| `name_normalized` | str | Yes | Normalized form |
| `language_code` | str | Yes | ISO 639-3 code ("und" if unknown) |
| `source_id` | str | Yes | ID within the source |
| `elevation_m` | float | No | Elevation in metres |
| `uncertainty_m` | float | No | Positional uncertainty |
| `script` | str | No | ISO 15924 script code |
| `year_from` | int | No | Earliest attestation year (CE) |
| `year_to` | int | No | Latest attestation year (CE) |
| `is_current` | bool | No | Whether name is currently in use |
| `place_type` | str | No | Feature type classification |
| `wikidata_qid` | str | No | Wikidata Q-identifier |
| `geonames_id` | int | No | GeoNames ID |
| `osm_id` | int | No | OpenStreetMap ID |
| `alternative_names` | dict | No | lang_code → list of forms |
| `source_url` | str | No | URL for this specific record |
| `source_license` | str | No | License for this record |

## Guidelines

### Licensing
- Document the source's license in the connector class
- Respect rate limits and terms of service
- Cache downloaded data locally to avoid repeated requests

### Data Quality
- Validate coordinates (lat: -90 to 90, lon: -180 to 180)
- Handle missing/null values gracefully
- Log warnings for suspicious records (don't silently drop)

### Performance
- Use streaming/iterators for large datasets (don't load all into memory)
- Implement caching for downloaded files
- Support incremental updates where possible

### Testing
- Write unit tests with sample data fixtures
- Test validation logic with edge cases
- Mock HTTP requests in tests (don't hit real APIs)

## Example: National Registry Connector

```python
class NorwaySSRConnector(BaseConnector):
    """Connector for Norway's Central Place Name Registry (SSR)."""
    
    source_id = "ssr_norway"
    source_name = "Sentralt stedsnavnregister (SSR)"
    license = "NLOD-2.0"
    coverage_region = "NO"
    source_url = "https://www.kartverket.no/en/data/place-names"
    
    def fetch(self, bbox=None, country=None):
        # Download from Kartverket's API or bulk file
        # Parse GML/GeoJSON response
        # Yield ConnectorResult for each place
        ...
```

## Registration

Place your connector in `src/toponymia/connectors/your_source.py`. It will be discoverable by the CLI and pipeline automatically.
