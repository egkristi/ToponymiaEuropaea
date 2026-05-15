# License Compatibility Matrix

This document maps the licenses of all data sources used in Toponymia Europaea and determines the resulting license obligations for derived datasets.

## Source Licenses

| Source | License | Attribution Required | Share-Alike | Commercial Use |
|--------|---------|---------------------|-------------|----------------|
| GeoNames | CC BY 4.0 | Yes | No | Yes |
| OpenStreetMap | ODbL 1.0 | Yes | Yes (database) | Yes |
| Kartverket (Norway) | CC0 / NLOD 2.0 | No (CC0) / Yes (NLOD) | No | Yes |
| Lantmäteriet (Sweden) | CC0 | No | No | Yes |
| MML (Finland) | CC BY 4.0 | Yes | No | Yes |
| Ordnance Survey (UK) | OGL 3.0 | Yes | No | Yes |
| IGN (France) | Licence Ouverte 2.0 | Yes | No | Yes |
| Wikidata | CC0 | No | No | Yes |
| Wikipedia | CC BY-SA 4.0 | Yes | Yes (content) | Yes |

## Compatibility Matrix

When combining data under different licenses, the most restrictive compatible license applies:

| Combination | Result | Notes |
|-------------|--------|-------|
| CC0 + CC BY | CC BY | Attribution for CC BY source |
| CC0 + ODbL | ODbL | Share-alike for database use |
| CC BY + CC BY | CC BY | Attribution for all sources |
| CC BY + ODbL | ODbL + Attribution | Both obligations apply |
| CC BY + CC BY-SA | CC BY-SA | Share-alike dominates |
| CC0 + CC0 | CC0 | No restrictions |
| ODbL + CC BY-SA | **Incompatible** | Different share-alike mechanisms |

## Our Approach

### Project License
Toponymia Europaea itself is licensed under **CC BY-NC-SA 4.0** (non-commercial, share-alike, attribution).

### Data Layer Obligations

1. **Databank records** (derived from multiple sources):
   - Must comply with ODbL for any records incorporating OSM data
   - Must attribute GeoNames, MML, and other CC BY sources
   - National authority data (CC0/NLOD) imposes no restrictions

2. **Source tracking**:
   - Every record has `source_id` and `source_url` fields
   - The `databank/sources.jsonl` file maps source IDs to licenses
   - Attribution is preserved at the record level

3. **Derived datasets** (analysis results, statistics):
   - Statistical results are facts, not database derivatives → no ODbL obligation
   - Aggregated findings (e.g., "X% of Norwegian place names contain -heim") are not covered by source data licenses
   - Published datasets that include original coordinates may trigger ODbL

### ODbL Compliance for OSM Data

The Open Database License requires:
- **Attribution**: Credit OpenStreetMap contributors
- **Share-Alike**: If you produce a "Produced Work" from the database, the database must remain ODbL
- **Keep Open**: Technical measures must not restrict access

Our compliance:
- OSM source records include `source_url` pointing to OSM
- Any published subset containing OSM-derived coordinates is released under ODbL
- Analysis results (statistics, patterns) are "Produced Works" and are not bound by ODbL

### Record-Level License Tracking

Each record in `sources.jsonl` includes the license:

```json
{
  "source_id": "geonames",
  "license": "CC-BY-4.0",
  "license_url": "https://creativecommons.org/licenses/by/4.0/",
  "attribution": "GeoNames (geonames.org)"
}
```

## Recommendations

1. **Prefer CC0/NLOD sources** for base geographic data (coordinates, place types)
2. **Use OSM data cautiously** — any dataset mixing OSM coordinates becomes ODbL
3. **Track provenance** at record level to enable license-aware data exports
4. **Statistical outputs are safe** — aggregated research findings are not database derivatives
5. **When in doubt, attribute** — over-attribution never creates legal risk

## References

- [Creative Commons License Compatibility Chart](https://creativecommons.org/faq/#can-i-combine-material-under-different-creative-commons-licenses-in-my-work)
- [ODbL 1.0 Full Text](https://opendatacommons.org/licenses/odbl/1-0/)
- [NLOD 2.0](https://data.norge.no/nlod/en/2.0)
- [Open Government Licence 3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
