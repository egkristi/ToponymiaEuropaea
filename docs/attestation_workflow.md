# Historical Attestation Curation Workflow

How contributors add dated attestations from primary sources to the databank.

---

## Overview

An **attestation** is a dated record of a place name as it appears in a historical source document. Attestations are the primary evidence for diachronic analysis — tracking how place names evolve over centuries.

```
Source Document → Transcription → Validation → Databank Record → Analysis
```

---

## Step-by-Step Workflow

### 1. Identify the Source

Every attestation must come from a citable primary or secondary source:

| Source Type | Examples | Reliability |
|---|---|---|
| **Primary** | Charters, diplomas, tax rolls, church registers | Highest |
| **Critical Edition** | Diplomatarium Norvegicum, Norske Gaardnavne | High |
| **Secondary** | Scholarly monographs, journal articles | Medium |
| **Gazetteer** | GeoNames, Kartverket SSR, Ordnance Survey | Medium (current names) |
| **Map** | Historical maps with dated production | Medium |
| **Oral** | Dialect recordings, field notes | Low (requires corroboration) |

Before adding attestations, register the source in `databank/sources.jsonl`:

```json
{
  "source_id": "DN_I",
  "title": "Diplomatarium Norvegicum, bind I",
  "type": "critical_edition",
  "date_range": [1050, 1590],
  "language": "non",
  "license": "CC0-1.0",
  "url": "https://www.dokpro.uio.no/dipl_norv/diplom_field_eng.html",
  "accessed_at": "2025-01-15"
}
```

### 2. Transcribe the Attestation

For each name occurrence, record:

| Field | Required | Description |
|---|---|---|
| `form` | **Yes** | Exact spelling as in source (Unicode NFC) |
| `normalized` | No | Lowercase normalized form for matching |
| `language_code` | **Yes** | ISO 639-3 code of the name form |
| `year_from` | **Yes** | Earliest year of attestation |
| `year_to` | No | Latest year (if date range); null = point date |
| `source` | **Yes** | Citation string (e.g., "DN I 23, 1234") |
| `source_page` | No | Page/folio reference |
| `context` | No | Surrounding text or reason for naming |
| `script` | No | ISO 15924 script code |
| `phonetic` | No | IPA transcription (if known) |
| `confidence` | No | 0.0–1.0 reading confidence |
| `lemma` | No | Canonical lemma (e.g., "heim") |
| `lemma_language` | No | Language of lemma if different from attestation |

### 3. Date Assignment Rules

| Situation | Rule | Example |
|---|---|---|
| Exact year in source | Use year | `year_from: 1314` |
| Date range on document | Use range | `year_from: 1150, year_to: 1200` |
| Undated, but datable by context | Estimate + note | `confidence: 0.7, context: "likely 12th c."` |
| Century only | Use century bounds | `year_from: 1200, year_to: 1299` |
| "Before X" | Use earliest plausible | `year_to: X, context: "terminus ante quem"` |
| BCE dates | Negative numbers | `year_from: -500` |

### 4. Validate the Record

Before submitting, run schema validation:

```bash
uv run toponymia databank validate --schema attestation
```

The validator checks:
- Required fields present (`form`, `language_code`, `year_from`, `source`)
- Language code is valid ISO 639-3
- Year values are plausible (−3000 to current year)
- Confidence is in [0.0, 1.0]
- Source ID exists in `sources.jsonl`
- Unicode normalization (NFC)
- No duplicate attestations for same place + year + form

### 5. Submit via Pull Request

Use the **attestation PR template** (`.github/PULL_REQUEST_TEMPLATE/attestation.md`):

```
git checkout -b data/attestations-<source>-<region>
# ... add your records ...
git add databank/
git commit -m "data: add N attestations from <Source>"
git push origin data/attestations-<source>-<region>
# Open PR using the attestation template
```

---

## Quality Control Checklist

Before submitting attestations, verify each item:

### Transcription Quality

- [ ] Name form matches source exactly (check: ð/þ/ø/æ/ö, not modernized)
- [ ] Abbreviations expanded with brackets: `S[ancti]`
- [ ] Lacunae marked: `[...]` for illegible text
- [ ] Diacritics preserved (no ASCII approximation)
- [ ] Unicode NFC normalization applied

### Dating Accuracy

- [ ] Year matches source dating (not assumed from publication date)
- [ ] Date precision documented (exact year vs. century estimate)
- [ ] For copies of older documents: use original date, not copy date
- [ ] Calendar system noted if relevant (Julian vs. Gregorian pre-1582)
- [ ] Relative dates resolved to absolute where possible

### Source Integrity

- [ ] Source registered in `sources.jsonl` with full citation
- [ ] Page/folio reference provided for physical sources
- [ ] Source type correctly classified (primary/edition/secondary)
- [ ] License of source data verified (no copyright-infringing transcriptions)
- [ ] Source URL provided where available (stable/persistent link)

### Linguistic Accuracy

- [ ] Language code is correct for the historical period (e.g., `non` for Old Norse, not `nob`)
- [ ] Script code matches actual writing system (runic = `Runr`, not `Latn`)
- [ ] Lemma extraction follows established etymological scholarship
- [ ] Component segmentation verified against scholarly consensus

### Geographic Linking

- [ ] Attestation linked to correct `place_id` (verify coordinates)
- [ ] Name form plausibly refers to the identified place (not homonym confusion)
- [ ] For places with multiple names: each attestation chain is distinct

### Research Ethics

- [ ] No personal data of living individuals
- [ ] Source is legally accessible (no paywalled transcriptions without license)
- [ ] Indigenous/minority language names treated with respect
- [ ] Disputed toponyms: all forms recorded, no political editorial

---

## Batch Import Workflow

For large-scale digitization (hundreds+ attestations):

### 1. Prepare a JSONL file

```
databank/places/<COUNTRY>/attestations_<source>.jsonl
```

Each line: one attestation following `databank/schema/attestation.v1.json`.

### 2. Run batch validation

```bash
uv run toponymia databank validate --file databank/places/NO/attestations_dn.jsonl --schema attestation
```

### 3. Run deduplication check

```bash
uv run toponymia databank dedup --check databank/places/NO/attestations_dn.jsonl
```

### 4. Generate integrity checksums

```bash
uv run toponymia databank integrity --update
```

### 5. Submit PR with summary statistics

Include in PR description:
- Number of attestations added
- Source(s) used
- Date range covered
- Language(s)
- Geographic region
- Any anomalies or uncertain readings

---

## Common Sources by Region

| Region | Key Sources | Approx. Date Range |
|---|---|---|
| Norway | Diplomatarium Norvegicum, Norske Gaardnavne (Rygh), Regesta Norvegica | 1050–1590 |
| Sweden | Svenskt Diplomatarium, Ortnamnsregistret | 1164–1500 |
| Denmark | Diplomatarium Danicum, Danmarks Stednavne | 1085–1450 |
| Iceland | Diplomatarium Islandicum, Landnámabók | 870–1500 |
| England | Domesday Book, EPNS county volumes, Anglo-Saxon charters | 700–1500 |
| Scotland | Retours, RMS, RSS | 1100–1700 |
| Germany | Urkundenbücher (regional), Förstemann | 700–1500 |
| France | Cartulaires, Dictionnaire topographique | 800–1400 |

---

## Error Handling

| Error | Resolution |
|---|---|
| Source not in `sources.jsonl` | Register source first, then re-validate |
| Invalid language code | Check ISO 639-3; use `und` only as last resort |
| Duplicate attestation | Check if truly duplicate vs. independent attestation |
| Year out of range | Verify date; if BCE, use negative number |
| Confidence warning | Add `context` field explaining uncertainty |
| Place ID mismatch | Verify geographic coordinates; may need new place record |
