# Multi-Source Coordinate Resolution Strategy

**Issue:** #32  
**Date:** 2025-01-20  
**Status:** DECIDED  

---

## Problem

When multiple sources provide coordinates for the same place, they often disagree:
- Kartverket places "Oslo" at the city hall (59.9127°N, 10.7461°E)
- GeoNames uses the central business district (59.9133°N, 10.7389°E)
- Wikidata may point to the municipality centroid

Divergences of 50-500m are common; larger discrepancies indicate data quality issues.

## Source Priority Hierarchy

Resolution follows a strict priority order based on source authority:

| Priority | Source Type | Example | Rationale |
|----------|-------------|---------|-----------|
| 1 (highest) | National mapping authority | Kartverket, Lantmäteriet, MML | Official geodetic surveys |
| 2 | National gazetteers | SSR, SNIG | Authoritative place name registries |
| 3 | GeoNames | geonames.org | Community-curated, generally reliable |
| 4 | OpenStreetMap | Overpass API | Community-mapped, variable precision |
| 5 (lowest) | Wikidata | wikidata.org | Aggregated, sometimes imprecise |

## Conflict Detection

A **conflict** is defined as:

- **Minor divergence** (< 100m): Normal variation, use highest-priority source
- **Moderate divergence** (100m - 1km): Flag for review, use highest-priority source
- **Major divergence** (> 1km): Likely different reference points or error, flag as data quality issue

Distance calculation uses the Haversine formula.

## Resolution Algorithm

```
1. Group records by place_id (or by phonetic_key + H3 cell)
2. For each group with multiple coordinate sources:
   a. Calculate pairwise distances between all coordinate pairs
   b. Select the coordinate from the highest-priority source
   c. If max divergence > 1km:
      - Flag as "coordinate_conflict"
      - Store all source coordinates in provenance
   d. If max divergence > 100m:
      - Store note: "moderate_divergence"
3. Store chosen coordinate with source provenance
```

## Provenance Storage

Resolved coordinates include provenance metadata:

```json
{
  "latitude": 59.9127,
  "longitude": 10.7461,
  "_coordinate_source": "kartverket",
  "_coordinate_provenance": {
    "kartverket": [59.9127, 10.7461],
    "geonames": [59.9133, 10.7389]
  },
  "_coordinate_divergence_m": 52.3,
  "_coordinate_status": "resolved"
}
```

## Implementation

The resolution is implemented in `src/toponymia/pipelines/coordinates.py` with:
- `resolve_coordinates()`: Apply priority hierarchy to a group of records
- `detect_conflicts()`: Find records with divergent coordinates
- `haversine_distance()`: Calculate distance between coordinate pairs

## Edge Cases

1. **Missing coordinates**: Skip source, fall through to next priority
2. **Identical place_id, different time periods**: Use most recent survey
3. **Islands/offshore features**: Higher tolerance (1km) due to reference point ambiguity
4. **Linear features** (rivers, roads): Coordinates may legitimately differ by kilometers — use source midpoint

## References

- Kartverket positional accuracy: ±1m (EUREF89/UTM)
- GeoNames coordinate precision: ~10-100m (varies by contributor)
- OSM positional guidelines: "node placement at centroid of feature"
