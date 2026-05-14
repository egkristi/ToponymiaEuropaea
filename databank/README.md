# Toponymia Europaea — Databank

This directory contains the **primary research databank**: all toponymic records versioned directly in git.

## Design Principles

1. **Git-native**: Data lives in the repo. Fork → add data → PR → merge.
2. **JSONL format**: One JSON object per line. Diff-friendly, merge-friendly.
3. **Extensible schema**: Core fields are validated; additional fields are preserved. Adding new fields requires no schema migration.
4. **Append-only by convention**: New data is appended. Corrections are new lines with the same `source_id` and a later `accessed_at`.
5. **Deterministic ordering**: Records sorted by `source_id` within each file for stable diffs.

## Directory Structure

```
databank/
├── schema/
│   └── place.v1.json          # JSON Schema (extensible, additionalProperties: true)
├── places/
│   ├── NO/                    # ISO 3166-1 alpha-2 country code
│   │   ├── kartverket.jsonl   # One file per source dataset
│   │   └── geonames.jsonl
│   ├── FI/
│   │   └── geonames.jsonl
│   ├── GB/
│   │   └── geonames.jsonl
│   └── _global/               # Records not country-specific
│       └── wikidata.jsonl
├── sources.jsonl              # Source dataset metadata
└── README.md                  # This file
```

## Record Format

Each `.jsonl` file contains one JSON object per line conforming to `schema/place.v1.json`.

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `name_form` | string | Primary name (Unicode NFC) |
| `latitude` | number | WGS84 decimal degrees |
| `longitude` | number | WGS84 decimal degrees |
| `source_id` | string | Unique ID within the source |

### Recommended fields

| Field | Type | Description |
|-------|------|-------------|
| `language_code` | string | ISO 639-3 (3 letters) |
| `country_code` | string | ISO 3166-1 alpha-2 |
| `source_dataset` | string | e.g. "geonames", "kartverket_ssr" |
| `place_type` | string | Feature type classification |
| `year_from` / `year_to` | integer | Attestation period |

### Extensibility

Any additional fields are allowed and preserved. Examples:

```json
{"name_form": "Bjørgvin", "latitude": 60.39, "longitude": 5.32, "source_id": "3161732", "language_code": "nno", "country_code": "NO", "source_dataset": "geonames", "etymology_notes": "Old Norse Bjǫrgvin 'mountain meadow'", "medieval_form": "Bjǫrgvin"}
```

The `etymology_notes` and `medieval_form` fields are not in the core schema but are perfectly valid. They will be preserved through all pipelines.

## Contributing Data

1. **Fork** this repository
2. Add `.jsonl` files under `databank/places/<COUNTRY_CODE>/`
3. Ensure each line is valid JSON conforming to `schema/place.v1.json`
4. Sort records by `source_id` for stable diffs
5. Open a **Pull Request** — CI will validate your data automatically

### File naming

- Use the source dataset name: `geonames.jsonl`, `kartverket.jsonl`, `wikidata.jsonl`
- For manual/curated collections: `<descriptor>.jsonl` (e.g. `norse_cult_sites.jsonl`)

### Quality expectations

| Tier | Requirements |
|------|-------------|
| **Minimum** (candidate) | `name_form`, `latitude`, `longitude`, `source_id` |
| **Verified** | + `language_code`, `country_code`, `source_dataset` |
| **Enriched** | + `place_type`, attestation dates, alternative names |
| **Research-ready** | + cross-references (Wikidata QID), normalized form |

## Validation

CI runs schema validation on every push/PR:

```bash
uv run toponymia databank validate
```

To validate locally before committing:

```bash
uv run toponymia databank validate --path databank/places/NO/kartverket.jsonl
```

## Schema Evolution

- The schema uses `"additionalProperties": true` — new fields never break old data.
- Breaking changes (removing/renaming required fields) require a new schema version (`place.v2.json`).
- Each file may declare its schema version via `_schema_version` metadata (defaults to v1).
