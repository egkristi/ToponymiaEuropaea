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
{"name_form": "Bjørgvin", "latitude": 60.39, "longitude": 5.32, "source_id": "3161732", "language_code": "nno", "country_code": "NO", "source_dataset": "geonames", "etymology_notes": "Old Norse Bjǫrgvin 'mountain meadow'"}
```

The `etymology_notes` field is not in the core schema but is perfectly valid. It will be preserved through all pipelines.

### Historical Name Attestations

For historical/diachronic analysis, use the `attestations` array to record how a place's name has changed over time. This is distinct from `alternative_names` which captures *synchronic* variants (e.g., bilingual names used simultaneously).

```json
{
  "name_form": "Trondheim",
  "latitude": 63.43049,
  "longitude": 10.39506,
  "source_id": "3133880",
  "place_id": "Q25804",
  "attestations": [
    {"form": "Niðaróss", "language_code": "non", "year_from": 997, "year_to": 1217, "source": "Heimskringla", "context": "Original Norse name, 'mouth of river Nid'"},
    {"form": "Trondhjem", "language_code": "dan", "year_from": 1537, "year_to": 1930, "context": "Danish period name"},
    {"form": "Trondheim", "language_code": "nob", "year_from": 1930, "year_to": null, "is_current": true, "context": "Norwegianized spelling"}
  ]
}
```

Each attestation object supports:

| Field | Type | Description |
|-------|------|-------------|
| `form` | string | **Required.** The attested name form |
| `language_code` | string | ISO 639-3 code |
| `year_from` | int/null | First known use (CE; negative for BCE) |
| `year_to` | int/null | Last use (`null` = still current) |
| `is_current` | bool | Whether this form is in use today |
| `source` | string | Citation (e.g. "DN I 23, 1234") |
| `context` | string | Reason for name change |
| `confidence` | number | 0.0–1.0 confidence level |
| `script` | string | ISO 15924 script code |
| `phonetic` | string | IPA transcription |

**Guidelines:**
- Order attestations chronologically (earliest first)
- Use `alternative_names` for concurrent/bilingual names (e.g., Sámi alongside Norwegian)
- Use `attestations` for sequential name changes over time
- Set `place_id` (preferably Wikidata QID) to link records referring to the same physical place across datasets

## Contributing Data

1. **Fork** this repository
2. Add `.jsonl` files under `databank/places/<COUNTRY_CODE>/`
3. Ensure each line is valid JSON conforming to `schema/place.v1.json`
4. Sort records by `source_id` for stable diffs: `uv run toponymia databank sort`
5. Sign all records: `uv run toponymia databank sign`
6. Open a **Pull Request** — CI will validate your data automatically

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

## Data Integrity & Signing

The databank uses a **content-addressable integrity system** to ensure data has not been tampered with and to maintain consistency across branches, forks, and rebases.

### Record-Level Integrity (`_sha256`)

Every record carries a `_sha256` field — a SHA-256 hash computed from the **canonical JSON** of the record (sorted keys, meta-fields excluded). This means:

- Any modification to a record's data will invalidate its hash.
- Two contributors producing identical records independently will get the same hash.
- The hash is **deterministic** and **content-addressable**.

```json
{"name_form": "Bergen", "latitude": 60.39299, "longitude": 5.32415, "source_id": "3161732", "_sha256": "a1b2c3..."}
```

### File-Level Integrity (`MANIFEST.sha256`)

A `MANIFEST.sha256` file at the databank root tracks the SHA-256 of every `.jsonl` file. Format is compatible with `sha256sum -c`:

```
e5f6a7b8...  places/NO/geonames.jsonl
c3d4e5f6...  places/FI/geonames.jsonl
```

### Signing Workflow

```bash
# After adding/modifying data:
uv run toponymia databank sort     # Canonical order (by source_id)
uv run toponymia databank sign     # Compute _sha256 + regenerate MANIFEST

# Before submitting PR:
uv run toponymia databank verify   # Check all hashes are valid
```

### Git Collaboration Model

The JSONL format is specifically chosen for git-based collaboration:

| Feature | How it works |
|---------|-------------|
| **Branching** | Each record is one line → branch changes are per-record |
| **Merging** | `.gitattributes` configures union merge for JSONL (keeps both sides' lines) |
| **Rebasing** | Sorted by `source_id` → minimal conflicts during rebase |
| **Fork & PR** | Fork → add data → sign → PR → CI validates → merge |
| **Tamper detection** | `databank verify` catches modified records instantly |
| **Conflict resolution** | After merge/rebase: `databank sort` then `databank sign` |

### Post-Merge Checklist

After merging a PR or rebasing:
```bash
uv run toponymia databank sort     # Re-sort (union merge may disorder)
uv run toponymia databank sign     # Re-sign (hashes stale after reorder)
uv run toponymia databank verify   # Confirm all green
git add databank/ && git commit -m "chore: re-sign databank after merge"
```

## Validation

CI runs schema validation on every push/PR:

```bash
uv run toponymia databank validate
```

To validate with integrity checking:

```bash
uv run toponymia databank validate --integrity
```

To validate locally before committing:

```bash
uv run toponymia databank validate --path databank/places/NO/kartverket.jsonl
```

## Schema Evolution

- The schema uses `"additionalProperties": true` — new fields never break old data.
- Breaking changes (removing/renaming required fields) require a new schema version (`place.v2.json`).
- Each file may declare its schema version via `_schema_version` metadata (defaults to v1).
