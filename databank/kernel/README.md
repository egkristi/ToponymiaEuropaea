# Curated JSONL Kernel (Gold-Standard Records)

This directory contains manually verified, curated place-name records that serve
as the **gold standard** for the ToponymiaEuropaea project.

## Purpose

- **Regression testing**: ensure pipelines don't corrupt known-good data
- **Benchmark**: measure language module accuracy against verified etymologies
- **Seed data**: bootstrap new analyses with high-confidence records
- **Documentation**: illustrate the data model with real examples

## Inclusion Criteria

A record qualifies for the kernel if it meets **all** of the following:

1. **Verified etymology**: at least one published academic source confirms the
   proposed etymology (cited in `sources`)
2. **Precise coordinates**: location verified against modern maps (uncertainty < 100m)
3. **Language attribution**: ISO 639-3 code verified by a specialist or
   multiple concordant sources
4. **Complete morphology**: segmentation into components is attested or
   unambiguous from phonological analysis
5. **Stable identity**: the place can be linked to Wikidata, GeoNames, or a
   national registry with a persistent ID

## File Organization

```
kernel/
├── README.md           # This file
├── criteria.json       # Machine-readable inclusion criteria
└── gold.jsonl          # Gold-standard records (one per line)
```

## Record Format

Records follow the standard `place.v1` schema (see `../schema/place.v1.json`)
with these additional required fields for kernel records:

| Field | Description |
|-------|-------------|
| `verified_by` | Who verified this record (initials or ORCID) |
| `verified_date` | ISO 8601 date of verification |
| `etymology` | Object with `lemma`, `meaning`, `language_code`, `sources` |
| `segmentation` | Array of morphological components |
| `sources` | Array of academic references (DOI preferred) |

## Contributing

To add a record to the kernel:

1. Ensure it meets all inclusion criteria above
2. Add the record to `gold.jsonl`
3. Run validation: `uv run python -m toponymia.pipelines.kernel validate`
4. Submit a PR with the source references
