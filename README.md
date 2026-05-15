# Toponymia Europaea

> *Where Names Become Knowledge, and Memory Becomes Evidence.*

**An open, data-driven research framework for the systematic analysis of place names across linguistic, historical, geographical, ecological, and cultural dimensions.**

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-green.svg)](https://python.org)

---

## Current Status (v0.5.0)

| Metric | Value |
|--------|-------|
| **Databank records** | 3,018 (5 Nordic countries, 2 sources) |
| **Gold-standard kernel** | 8 verified records with full etymologies |
| **Data sources** | GeoNames (2,507 records), Kartverket SSR (504 records) |
| **Language modules** | 201 auto-discovered (covering all European languages + ancient/extinct) |
| **Perspective modules** | 10 coded (of 21 documented) |
| **Statistical tests** | 12 families (spatial, correspondence, astronomical, religious, temporal, migration, robustness, Bayesian, sensory, Ripley's K, name change rate, catastrophe) |
| **Tests passing** | 4,000+ (incl. 3,184 parametrized module tests) |
| **Type safety** | mypy strict, 0 errors |
| **CI pipeline** | Lint + format + mypy + tests (3.12/3.13) + ontology + databank validation |

**Key capabilities:**
- Language module auto-discovery registry with 201 modules
- Gold-standard kernel with validated etymologies and morphological segmentation
- Cross-source deduplication pipeline (phonetic blocking + H3 spatial verification)
- Diachronic attestation linking (historical → modern name chains)
- H3 hierarchical spatial indexing (R7/R9/R11) for efficient geospatial queries
- Nordic phonetic normalizer for cross-source deduplication (benchmarked vs BMPM, Metaphone, NYSIIS, Soundex)
- Name lemma detection and frequency analysis across 5 countries
- SHA-256 integrity signing with MANIFEST verification
- Full CLI: ingest, analyze, test, databank, lemma commands
- Bayesian etymology framework with hypothesis sets and evidence updating
- JSONL archival snapshots attached to releases with checksums
- 201 language modules spanning 7,000+ years of European linguistic history
- Phonetic algorithm evaluation benchmark (decision: custom normalizer outperforms BMPM for Nordic toponyms)
- **Parquet/DuckDB analytical layer** — SQL queries over databank without loading into memory
- **Docker Compose 3-layer stack** — PostgreSQL+PostGIS, API service, seed pipeline
- **Sync pipeline** — JSONL → PostgreSQL → Parquet with checksum verification at each stage
- **Wikidata etymology extraction** — P138 (named after) for 18 European countries with databank matching
- **Multi-source coordinate resolution** — priority hierarchy, conflict detection (100m/1km thresholds)
- **License compatibility matrix** — ODbL/CC-BY/CC0 compliance documentation

**Language coverage (201 modules):**

| Category | Languages |
|----------|-----------|
| **Germanic** | Old Norse, Proto-Germanic, Old English, Old High German, Danish, Swedish, Norwegian, Icelandic, Faroese, Low German, Luxembourgish, Yiddish, Old Saxon, Middle High German, Middle English, Middle Dutch |
| **Celtic** | Irish/Gaelic, Welsh, Breton, Cornish, Manx, Scots Gaelic, Cumbric, Gaulish, Celtiberian, Lepontic, Galatian, Proto-Celtic |
| **Romance** | Latin, Portuguese, Galician, Spanish, Catalan, Occitan, French, Italian, Romanian, Sardinian, Corsican, Aragonese, Asturian, Mirandese, Friulian, Ladin, Romansh, Aromanian, Dalmatian, Mozarabic, Old Provencal, Ladino |
| **Slavic** | Old Slavic, Russian, Ukrainian, Belarusian, Polish, Czech, Slovak, Serbian, Croatian, Slovenian, Bulgarian, Macedonian, Upper/Lower Sorbian, Kashubian, Old East Slavic, Polabian |
| **Baltic** | Lithuanian, Latvian, Old Prussian, Curonian, Semigallian, Selonian, Galindian, Sudovian, Proto-Balto-Slavic |
| **Uralic/Finnic** | Finnish, Northern Sami, South/Lule/Pite/Ume/Skolt/Kildin/Ter/Inari Sami, Estonian, Hungarian, Karelian, Veps, Livonian, Voro, Kven, Erzya, Moksha, Mari, Udmurt, Komi, Proto-Uralic |
| **Turkic** | Turkish, Azerbaijani, Gagauz, Crimean Tatar, Tatar, Chuvash, Uzbek, Kazakh, Turkmen, Cuman-Kipchak, Pecheneg, Khazar, Volga Bulgar |
| **Ancient/Pre-Roman** | Etruscan, Iberian, Tartessian, Rhaetian, Ancient Ligurian, Lusitanian, Basque |
| **Italic** | Oscan, Umbrian, Faliscan, Proto-Italic |
| **Greek/Anatolian** | Ancient Greek, Mycenaean, Modern Greek, Hittite, Luwian, Lydian, Lycian, Phrygian |
| **Paleo-Balkan** | Thracian, Dacian, Illyrian, Messapian, Venetic |
| **Caucasian** | Georgian, Armenian, Abkhaz, Adyghe, Chechen, Avar (Caucasian), Lezgian, Svan, Laz, Urartian |
| **Semitic/Near East** | Arabic/Moorish, Hebrew, Aramaic, Phoenician, Punic, Ugaritic, Akkadian, Sumerian |
| **Iranian** | Ossetian, Kurdish, Old Persian, Persian, Sogdian, Bactrian, Khwarezmian, Parthian, Avestan, Scythian-Sarmatian, Proto-Indo-Iranian |
| **Other** | Maltese, Romani, Mongolian, Hunnic, Crimean Gothic, Langobardic, Burgundian, Vandalic, Hurrian, Elamite, Kalaallisut, and more |

---

## Abstract

Place names (toponyms) are among humanity's oldest and most resilient cultural artefacts. They survive language shifts, state formations, colonizations, religious conversions, and mass migrations—often persisting for five to seven thousand years. A single toponym simultaneously functions as a *linguistic fossil*, a *geographical witness*, an *ecological memory*, a *historical document*, a *cultural symbol*, a *legal anchor*, and a *political instrument*.

Toponymia Europaea establishes an **open, reproducible, and statistically testable framework** for analysing place names along multiple dimensions simultaneously. The goal is not merely to describe names, but to **test claims about names**—both well-established and contested—against null models, alternative hypotheses, and robustness requirements.

The framework is designed to **start small and scale without rewriting**: every component—from language modules to data connectors to statistical tests—follows stable interfaces that allow extension without compromising existing research integrity.

---

## Table of Contents

- [Research Questions](#research-questions)
- [Architecture](#architecture)
- [Data Model](#data-model)
- [Data Quality & Onboarding Process](#data-quality--onboarding-process)
- [Perspectives](#perspectives)
- [Statistical Framework](#statistical-framework)
- [Data Sources](#data-sources)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Extending the Framework](#extending-the-framework)
- [Ethics and Responsibility](#ethics-and-responsibility)
- [Citation](#citation)
- [License](#license)

---

## Research Questions

### Primary Question

> To what extent, and how robustly, do place names correspond with actual linguistic, historical, geographical, ecological, cultural, and social conditions—compared to what would be expected under chance, and across time and space?

### Testable Sub-Questions

| Domain | Question |
|--------|----------|
| **Linguistics** | Can linguistic layers be identified and dated statistically? Can language contact and substrate be quantified? |
| **History** | Do name distributions reflect known historical processes (migrations, trade routes, Christianization, colonization)? |
| **Geography** | Do topographic, hydrological, and climatic names correspond significantly with actual terrain features? |
| **Ecology** | Are animal and plant elements in names reliable indicators of historical species distribution? |
| **Archaeology** | Do cultic, legal, or sepulchral names cluster significantly near archaeological sites? |
| **Religion** | Can pre-Christian cult names be identified, geographically characterized, and distinguished across religious traditions? |
| **Astrology & Cosmology** | Do solar/lunar/stellar names show statistically significant alignment with actual astronomical orientations? |
| **Power & Politics** | Can renaming and assimilation processes be detected statistically? |
| **Economy** | Do names reflect trade routes, raw materials, and production methods? |
| **Demography** | Do personal names embedded in place names mirror actual population compositions? |
| **Cognition** | Are there universal patterns in how landscapes are categorized through names? |
| **Sensory** | Do colour, sound, and thermal names correlate with measurable landscape properties? |
| **Esoteric** | Do sacred-site names align along geometric patterns more than expected by chance? |
| **Deep-time** | Can PIE sacred vocabulary distributions be correlated with known expansion routes? |

Each sub-question is designed to be **falsifiable**. The framework generates null models and tests observed patterns against them.

---

## Architecture

### Design Principles

1. **Language-agnostic**: No assumptions about alphabet, script direction, or character set.
2. **Boundary-free**: No field assumes a country. Administrative units are time-stamped and versioned.
3. **Layered attestation**: One place may have many simultaneous name attestations in multiple languages and periods.
4. **Plugin-based extensibility**: Every data source, language module, and analysis method is a self-contained plugin with a stable interface.
5. **Versioned ontology**: Name types, categories, and interpretations are semantically versioned (semver) so older analyses remain reproducible.
6. **Uncertainty as first-class citizen**: Probability distributions, not deterministic assertions.
7. **Incremental processing**: Only affected analyses re-run when data updates.
8. **Federated identifiers**: Each place links to GeoNames, Wikidata, OSM, and national IDs where available. No single ID is authoritative.

### Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                 │
│  GeoNames · Wikidata · OSM · National Registries · Historical Maps  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ connectors/
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        INGESTION LAYER                               │
│         Normalize · Deduplicate · Georeference · Validate           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABANK (source of truth)                        │
│     JSONL (git-native) · Diff-friendly · Full provenance            │
│     Optional: PostgreSQL + PostGIS (analysis cache)                 │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ANALYSIS PIPELINE                               │
│  Segment · Classify · Etymologize · Link · Hypothesize · Test      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                                 │
│      Results DB · API · Visualizations · Research Papers            │
└─────────────────────────────────────────────────────────────────────┘
```

### Persistence Model

| Layer | Role | Notes |
|-------|------|-------|
| **JSONL Databank** (`databank/`) | Source of truth (current) | Git-native, diff-friendly, one file per country per source. Every record carries provenance. Validated in CI. |
| **PostgreSQL + PostGIS** | Operational store (planned) | For spatial queries, transactional writes, H3 indexing. Local dev via Docker. |
| **Parquet + DuckDB** | Analytical layer (planned) | Immutable snapshots for large-scale statistical runs (permutation tests over millions of rows). |

The databank is the authoritative persistence layer **during development**. All data enters via the ingestion pipeline (`toponymia ingest`) and is stored as JSONL in `databank/places/<ISO>/`. PostgreSQL is only needed when running spatial queries that benefit from indexing (e.g., nearest-neighbor searches across 100k+ records).

**Scaling path**: At 10M+ records, JSONL remains as a curated gold-standard kernel (tens of thousands of verified records), while PostgreSQL becomes the primary operational store and Parquet provides the analytical layer. See ROADMAP Milestone 11 for details.

---

## Data Model

The data model separates **places** (physical locations) from **names** (linguistic attestations) from **interpretations** (scholarly claims). This three-level separation is fundamental and ensures that:

- Multiple names can coexist for one place (multilingual, historical)
- Multiple interpretations can coexist for one name (competing etymologies)
- Every interpretation carries provenance, confidence, and versioning

### Core Schema (simplified)

```sql
-- A physical location in space
CREATE TABLE places (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    geometry        GEOMETRY(Point, 4326) NOT NULL,
    elevation_m     REAL,
    uncertainty_m   REAL,
    wikidata_qid    TEXT,
    geonames_id     BIGINT,
    osm_id          BIGINT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- A specific attested form of a name for a place
CREATE TABLE name_attestations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    place_id        UUID REFERENCES places(id) NOT NULL,
    form            TEXT NOT NULL,
    normalized_form TEXT NOT NULL,
    language_code   TEXT NOT NULL,  -- ISO 639-3
    script          TEXT,           -- ISO 15924
    year_from       INTEGER,
    year_to         INTEGER,
    source_id       UUID REFERENCES sources(id) NOT NULL,
    confidence      REAL CHECK (confidence BETWEEN 0 AND 1),
    status          TEXT NOT NULL DEFAULT 'candidate'
                    CHECK (status IN ('candidate','verified','enriched','reviewed','published','retracted')),
    is_current      BOOLEAN DEFAULT false,
    reviewed_by     TEXT,
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Morphological decomposition of a name
CREATE TABLE name_components (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attestation_id  UUID REFERENCES name_attestations(id) NOT NULL,
    component       TEXT NOT NULL,
    position        INTEGER NOT NULL,
    morph_type      TEXT NOT NULL,  -- prefix, stem, suffix, compound_head, compound_modifier
    lemma           TEXT,
    language_code   TEXT,
    meaning_uri     TEXT,           -- SKOS concept URI
    confidence      REAL CHECK (confidence BETWEEN 0 AND 1)
);

-- Scholarly interpretations with full provenance
CREATE TABLE interpretations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    place_id        UUID REFERENCES places(id) NOT NULL,
    claim           TEXT NOT NULL,
    probability     REAL CHECK (probability BETWEEN 0 AND 1),
    method          TEXT,
    author          TEXT,
    date            DATE,
    source_id       UUID REFERENCES sources(id),
    supersedes_id   UUID REFERENCES interpretations(id),
    ontology_version TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Provenance tracking for all data
CREATE TABLE sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    citation        TEXT NOT NULL,
    source_type     TEXT NOT NULL,
    reliability     REAL CHECK (reliability BETWEEN 0 AND 1),
    license         TEXT,
    url             TEXT,
    accessed_at     TIMESTAMPTZ
);
```

### Extension Tables

The schema supports unlimited perspective-specific extension tables, all keyed to `place_id`:

```sql
CREATE TABLE terrain_features     (id UUID PRIMARY KEY, place_id UUID REFERENCES places(id), ...);
CREATE TABLE ecological_features  (id UUID PRIMARY KEY, place_id UUID REFERENCES places(id), ...);
CREATE TABLE archaeological_sites (id UUID PRIMARY KEY, place_id UUID REFERENCES places(id), ...);
CREATE TABLE historical_events    (id UUID PRIMARY KEY, place_id UUID REFERENCES places(id), ...);
CREATE TABLE cultural_features    (id UUID PRIMARY KEY, place_id UUID REFERENCES places(id), ...);
CREATE TABLE economic_features    (id UUID PRIMARY KEY, place_id UUID REFERENCES places(id), ...);
CREATE TABLE renaming_events      (id UUID PRIMARY KEY, place_id UUID REFERENCES places(id), ...);
CREATE TABLE administrative_units (id UUID PRIMARY KEY, place_id UUID REFERENCES places(id), ...);
```

New perspectives require only new tables—never modifications to the core schema.

---

## Data Quality & Onboarding Process

Every name entering the databank must pass through a rigorous, staged onboarding pipeline. No record reaches the authoritative dataset without verified provenance and peer-level scrutiny. This is non-negotiable — the scientific value of the entire framework depends on the integrity of every single record.

### Core Principle

> **Nothing enters the databank without at least one correct, verifiable, trustworthy reference attached in metadata.**

This applies equally to:
- Place names and their attested forms
- Morphological segmentations
- Etymological interpretations
- Geographic coordinates
- Historical datings
- All research claims and hypotheses

### Onboarding Stages

Each name record progresses through five stages. A record can only advance forward — never skip a stage.

```
 STAGE 1          STAGE 2          STAGE 3          STAGE 4          STAGE 5
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ CANDIDATE│───▶│ VERIFIED │───▶│ ENRICHED │───▶│ REVIEWED │───▶│PUBLISHED │
│          │    │          │    │          │    │          │    │          │
│ Ingested │    │ Sources  │    │ Analysis │    │ Peer     │    │ Accepted │
│ raw data │    │ confirmed│    │ attached │    │ checked  │    │ into DB  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
  Quarantine      Staging        Staging         Staging        Authoritative
  schema          schema         schema          schema          schema
```

#### Stage 1 — Candidate (Quarantine)

A raw record is ingested from a data source (GeoNames, Wikidata, OSM, historical map, scholarly publication, national registry).

**Requirements to enter Stage 1:**
- Unique candidate ID assigned
- Source connector identified
- Timestamp of ingestion
- Raw form preserved verbatim (no normalization yet)
- Geographic coordinates (even approximate)

**Status:** `candidate` — held in quarantine schema, invisible to analysis pipelines.

#### Stage 2 — Verified (Source Confirmation)

The record's existence and form are confirmed against at least one authoritative reference.

**Requirements to advance:**
- At least **one primary source** attached with full citation (see Reference Requirements below)
- Source reliability score assigned (0.0–1.0)
- Name form confirmed to match the cited source exactly
- Geographic coordinates verified (within stated uncertainty radius)
- Language code assigned (ISO 639-3) with justification
- Duplicate check completed — no existing record for same place+form+period
- Automated validation rules pass (format, encoding, coordinate bounds)

**Status:** `verified` — confirmed to exist, but not yet analysed.

#### Stage 3 — Enriched (Analysis Attached)

The verified record is processed through analytical pipelines.

**Requirements to advance:**
- Unicode normalization applied (NFC) with both raw and normalized forms preserved
- Morphological segmentation completed (or explicitly marked as pending)
- At least one interpretation proposed with:
  - Method documented
  - Confidence score assigned
  - Supporting references attached
  - Ontology version stamped
- Temporal range estimated (year_from / year_to) with source for dating
- Cross-references to related records established (variants, earlier attestations)

**Status:** `enriched` — analysed, awaiting review.

#### Stage 4 — Reviewed (Peer Verification)

An independent check ensures correctness and completeness.

**Requirements to advance:**
- Review performed by a different agent than the ingester/analyst (human or automated)
- All attached references spot-checked for accuracy
- Morphological segmentation validated against known patterns
- Confidence scores reviewed for reasonableness
- No unresolved flags or contradictions
- Review record created with reviewer identity, timestamp, and outcome

**Status:** `reviewed` — quality-assured, ready for publication.

#### Stage 5 — Published (Authoritative)

The record is promoted to the authoritative schema and becomes available to all analysis pipelines, statistical tests, and research outputs.

**Requirements to advance:**
- All Stage 4 criteria satisfied
- Final consistency check against existing authoritative data (no conflicts)
- Record signed with version stamp and promotion timestamp
- Immutable audit trail preserved (all prior stages remain in history)

**Status:** `published` — part of the trusted dataset.

### Reference Requirements

Every record and every research claim must carry references that meet these standards:

#### Minimum Reference Metadata

| Field | Required | Description |
|-------|----------|-------------|
| `citation` | **Yes** | Full bibliographic citation (author, title, year, publisher/journal, pages) |
| `source_type` | **Yes** | One of: `scholarly_publication`, `national_registry`, `historical_document`, `cartographic`, `database`, `inscription`, `oral_tradition` |
| `reliability` | **Yes** | Score 0.0–1.0 based on source type hierarchy (see below) |
| `url` | If available | Persistent URL, DOI, or URN |
| `accessed_at` | If digital | Timestamp of access |
| `license` | **Yes** | License under which the source data may be used |
| `page_or_entry` | **Yes** | Specific page, entry number, or record ID within the source |
| `language` | **Yes** | Language of the source document (ISO 639-3) |

#### Source Reliability Hierarchy

| Score Range | Source Type | Examples |
|-------------|-------------|----------|
| 0.90–1.00 | Primary historical documents | Original charters, diplomas, runic inscriptions, land registers |
| 0.80–0.89 | Peer-reviewed scholarship | Journal articles, monographs from established onomastic researchers |
| 0.70–0.79 | National registries | Kartverket (Norway), Lantmäteriet (Sweden), Ordnance Survey (UK) |
| 0.60–0.69 | Edited compilations | Norske Gaardnavne (Rygh), EPNS volumes, published name dictionaries |
| 0.50–0.59 | Curated databases | GeoNames, Wikidata (with citations), OpenStreetMap (verified) |
| 0.30–0.49 | Secondary/tertiary sources | Wikipedia, travel guides, local history pamphlets |
| 0.10–0.29 | Unverified digital | User-submitted data, crowdsourced without review, social media |
| 0.00–0.09 | Oral/unverifiable | Unrecorded oral tradition, personal communication without corroboration |

#### Reference Validation Rules

1. **No orphan claims**: Every interpretation, segmentation, and dating MUST link to at least one `source_id`.
2. **No circular references**: A record cannot cite itself or another record in this system as its only source.
3. **Recency check**: Digital sources must have `accessed_at` within 2 years, or be re-verified.
4. **Multi-source preference**: Records with ≥2 independent sources score higher in confidence weighting.
5. **Contradiction handling**: When sources disagree, all are preserved with individual reliability scores; the system does not silently pick one.

### Research Documentation Standards

All research conducted within this framework — whether automated pipeline analysis or manual scholarly interpretation — must meet the same standards of diligence and documentation.

#### Every Research Output Must Document:

1. **Question**: What specific, testable question is being investigated?
2. **Data**: Which records were included/excluded, and why? (Reproducible query or filter criteria.)
3. **Method**: What analytical method was applied? (Algorithm, statistical test, manual process.)
4. **References**: What prior work informs this analysis? (Cited with full bibliographic detail.)
5. **Results**: What was found? (Raw numbers, effect sizes, confidence intervals — not just p-values.)
6. **Limitations**: What could be wrong? (Missing data, confounds, alternative explanations.)
7. **Reproducibility**: Can another researcher reproduce this result from the documented inputs? (Yes/No — if No, explain what is missing.)

#### Documentation Format

Research outputs are stored as versioned records in the `interpretations` table with:

```sql
-- Every interpretation carries:
claim           -- The specific claim being made
probability     -- Posterior probability / confidence (0-1)
method          -- Method identifier (links to method registry)
author          -- Who made this claim (human or pipeline ID)
date            -- When the claim was made
source_id       -- What evidence supports it
supersedes_id   -- What prior claim this updates (if any)
ontology_version -- Which version of the classification system was used
```

#### Automated Pipeline Documentation

When an automated pipeline (segmentation, classification, statistical test) produces results:

- Pipeline version is stamped on every output record
- Input data snapshot is recorded (query hash or dataset version)
- Configuration parameters are stored
- Execution log is preserved
- Synthetic validation results are attached (power, false-positive rate)

#### Manual Research Documentation

When a human researcher adds an interpretation:

- Full argumentative chain is preserved in structured form
- All consulted sources are cited (even those that were examined but not used)
- Disagreements with existing interpretations are explicitly stated and argued
- Confidence is honestly self-assessed, not inflated

### Demotion & Retraction

Records can be **demoted** back to earlier stages or **retracted** entirely:

| Action | Trigger | Result |
|--------|---------|--------|
| **Demote to Stage 3** | Review finds errors in analysis | Record returns to enrichment queue |
| **Demote to Stage 2** | Source found unreliable after publication | Record stripped of analysis, re-queued |
| **Demote to Stage 1** | Geographic or identity error discovered | Record returns to quarantine |
| **Retract** | Record is fundamentally flawed (fabricated source, wrong place entirely) | Marked `retracted`, excluded from analysis, preserved for audit |

Retracted records are **never deleted** — they remain in the audit trail with retraction reason, date, and authority.

### Quality Metrics

The system tracks data quality at aggregate level:

| Metric | Target | Description |
|--------|--------|-------------|
| **Source coverage** | 100% | Every published record has ≥1 verified source |
| **Multi-source rate** | ≥50% | Published records with ≥2 independent sources |
| **Review coverage** | 100% | Every published record has been independently reviewed |
| **Mean reliability** | ≥0.65 | Average source reliability score across the databank |
| **Retraction rate** | <1% | Published records later retracted |
| **Staleness** | <5% | Published records with all digital sources older than 2 years |

---

## Perspectives

The framework analyses place names along **21 complementary perspectives**. Each perspective is independently extensible and can be activated or deactivated per analysis run.

### A — Linguistics
Etymology, morphology, historical phonology, dialectology, language contact, substrate detection, onomastic theory, typology (suffix classes across languages), folk etymology, written vs. oral tradition.

### B — History
Prehistory (Bronze/Iron Age), Migration Period, Viking Age expansion, medieval clearing waves, Black Death depopulation, early modern period (unions, reformation, Hansa), nation-state formation, 20th century (assimilation policies, wars), contemporary naming law.

### C — Geography & Physical Environment
Topography (elevation, slope, aspect, landforms), hydrology (rivers, lakes, fjords, fords), geology and soil, climate zones, palaeogeography (shoreline displacement, post-glacial rebound), maritime features, astronomical orientation.

### D — Ecology & Biology
Flora (tree species, plants as name elements), fauna (mammals, birds, fish), historical species distribution, biotopes (bog, heath, deciduous/coniferous forest), habitat change, palaeoecological controls (pollen data, macrofossils).

### E — Archaeology
Burial sites, settlements, cult sites, fortifications, trade sites, rock art, runic inscriptions, assembly sites (thing-sites).

### F — Religion & Mythology (expanded)

A comprehensive analysis of how religious and mythological systems have imprinted themselves on the landscape through naming. Every major belief system that has operated in Europe has left toponymic traces.

#### F.1 — Pre-Christian Germanic/Norse Religion
Deity names (Thor/Þór-, Odin/Óðinn-, Freyr/Frøy-, Freyja-, Njord/Njǫrðr-, Ull/Ullr-, Tyr/Týr-, Baldr-, Heimdall-, Loki-), cult site typology (*-hof/hov* temple, *-vé* sacred enclosure, *-hǫrgr/horg* altar/cairn shrine, *-lundr/lund* sacred grove, *-akr* sacred field), cosmological names (Midgard, Utgard, Hel-, Valhall-), ritual landscape (blót sites, processional routes, seasonal gathering names).

#### F.2 — Sámi Religion & Spirituality
*Sieidi* (sacred stones/natural features), *bassi/basse* (holy), *saivo* (sacred lakes/mountains with spirit inhabitants), *stállu* (mythical giant) sites, noaidi (shaman) practice locations, sacred mountains, reindeer-sacrifice sites, bear-cult toponyms, seasonal sacred sites linked to the reindeer calendar.

#### F.3 — Finno-Karelian & Baltic-Finnic Mythology
*Hiisi* (originally sacred grove, later demonized), *pyhä* (holy), *Ukko* (thunder god), *Tapio* (forest spirit), *Ahti* (water deity), *kalma* (death/burial), *Väinämöinen* traces, sacred springs (*pyhä lähde*), forest temple sites.

#### F.4 — Celtic Religion
*Nemeton* (sacred grove — Drunemeton, Medionemeton, Nemetobriga), deity names (Lugus/Lyon/Leiden/Carlisle, Brigantia, Belenos, Epona), *lann-* (sacred enclosure), triple deity sites, head-cult locations, water cult sites (thermal springs, river goddesses: Seine < Sequana, Marne < Matrona).

#### F.5 — Slavic Paganism
Perun (thunder god — Perunovac, Piorunów), Veles/Volos (underworld — Velesovo, Wołosate), Svarog/Svarožić (fire/sun), Mokosh (earth mother), Triglav (triple deity), Svantevit/Svetovid (Arkona), Radegast, *sveti/święty* (pre-Christian "holy"), grove sanctuaries (*gaj*), hilltop shrines.

#### F.6 — Baltic Paganism
Perkūnas/Pērkons (thunder), Dievas/Dievs (sky god), Laima (fate goddess), *alkas/elks* (sacred groves), *romuva* (temple sites), sacred oaks, fire-cult sites, snake-cult locations (Žaltys), sacred hills (*piliakalnis*).

#### F.7 — Roman Religion & Imperial Cult
Temple dedications (Mars, Mercury/Mercurius, Diana, Apollo, Minerva, Jupiter), *fanum* (shrine), *templum*, hot springs dedicated to deities (Aquae Sulis/Bath, Aachen < Aquae Granni), genius loci dedications, emperor-cult sites (Augusta, Caesarea), Capitolium hills.

#### F.8 — Mithraism
Cave/underground temple sites (*mithraeum*), military garrison associations, "Petra" names near Mithraic sites, bull-cult locations, solstice-aligned temples detectable through orientation analysis.

#### F.9 — Greek Religion & Mystery Cults
Temple sites (Delphi, Olympia, Eleusis), hero shrines (*heroon*), oracle sites, *hieron* (sacred precinct), Dionysian/Bacchic sites, Demeter/Persephone cult locations, sacred springs (Castalia, Hippocrene), mountain-top sanctuaries.

#### F.10 — Judaism in European Toponymy
*Judengasse/Judenstraße* (Jewish quarters), ghetto names (from Venetian *geto*), synagogue-related names, cemetery names (*Beth Haim*), *Judenberg/Judenau*, Hebrew-derived settlement names, expulsion and resettlement traces.

#### F.11 — Islam in European Toponymy
Moorish/Arabic legacy in Iberia (*Al-/El-*: Algarve, Almería, Alhambra, Alcázar, Guadalquivir < *wādī al-kabīr*), Sicily (Marsala < *marsa Allāh*), the Balkans (Ottoman period mosque-names, *dervish/tekke* sites), Hungarian traces, Tatar/Crimean layer.

#### F.12 — Christianity (detailed)
- **Catholic**: Saints dedications (*San/Sant/Saint/St/São*), Virgin Mary names (*Notre-Dame, Marienberg*), monastery orders (Cîteaux > Cistercian, Cluny), crusade-era names (Templar, Hospital)
- **Orthodox**: *Sveti/Sfântu* dedications, monastery foundations (*lavra, skiti*), hermit cells, holy mountain toponymy (Athos, Meteora)
- **Protestant/Reformed**: Reformation-era renamings, iconoclasm traces, Puritan settlement names
- **Irish/Celtic Christianity**: *kil-/cill-* (church), *desert-* (hermitage), monastic *-innis*, early saint dedications (Patrick, Brigid, Columba)
- **Pilgrimage**: Santiago/Compostela route names, Via Francigena, Jerusalem-reference names, *Kreuz-/Croix-* marker names
- **Monasticism by order**: Benedictine, Cistercian, Franciscan, Dominican, Premonstratensian—each with distinctive naming patterns

#### F.13 — Zoroastrianism & Mazdean Traces
Fire temple locations (*ātaš-* in Central Asia/Caucasus), possible diffusion along trade routes, *baga-* (divine) elements, Caucasian traces, Mithraic overlap zones.

#### F.14 — Folk Religion, Magic & the Supernatural
Troll names (*Trollhättan, Trollfjord*), giant/jötunn sites (*Jotunheimen, Riesengebirge*), *huldr/huldra* (hidden folk), fairy/fae sites (*Fairy Glen, Elfhome*), dragon/worm names (*Drake-, Orm-, Worm-, Lindwurm-*), witch sites (*Hex-, Blocksberg/Brocken*), devil names (*Djävuls-, Teufels-, Diable-*), enchantment/spell names (*galdr-, seid-*), haunted sites (*spöke-, gast-*), taboo/euphemistic names (renaming dangerous places), apotropaic names (protective naming against evil), changeling locations.

### G — Culture & Society
Personal names (who owned/cleared/lived?), ethnonyms, occupations and social status, family structures, gender perspectives, class perspectives, minority and indigenous perspectives.

### H — Economics
Trade routes (Hanseatic, Varangian, Silk Road, tin routes), raw materials (iron, salt, fish, timber), agriculture (fields, pastures, transhumance), fishing and maritime economy, crafts, administration and taxation.

### I — Migration & Diaspora
Indo-European expansion, Uralic distribution, Germanic Migration Period, Slavic expansion, Celtic substrates, Viking diaspora (Normandy, Danelaw, Hebrides, Iceland, Dublin, Novgorod), Hanseatic German influence, Jewish/Romani diaspora, early modern colonization.

### J — Law & Administration
Assembly systems (thing-sites), parishes, hundreds, counties, border markers, naming law, UNESCO and indigenous rights, digital place-name governance.

### K — Literary & Textual Sources
Sagas and Eddas, runic inscriptions, medieval diplomas and land registers, cartographic tradition (Ptolemy, Olaus Magnus), travel accounts, folklore collections.

### L — Cognition & Semiotics
Landscape categorization across cultures, spatial cognition, metaphor in nature names (body, kinship, animals), colour terminology, names as identity markers.

### M — Genetics & Palaeoclimate
Correlation between language layers and Y-DNA/mtDNA distributions, ancient DNA and migration reconstruction, palaeoclimatic epochs and name formation, historical population density as confound.

### N — Methodology & Philosophy of Science
Source criticism, uncertainty quantification, homonymy and polysemy, preregistration of hypotheses, open science practices, reproducibility.

### O — Astrology, Astronomy & Cosmology

The sky has been humanity's primary reference system for millennia. Place names encode astronomical knowledge, astrological belief, and cosmological worldviews in ways that are often testable against physical orientation data.

#### O.1 — Solar Toponymy
Names reflecting solar phenomena: *Sol-/Sun-/Sól-* elements, sunrise/sunset observation points, solstice markers (*Solberg, Sonnenberg, Solstrand*), shadow names (*Skugge-, Schatten-*), solar orientation of named features (do south-facing slopes preferentially carry "sun" names?), midwinter/midsummer festival sites, seasonal light conditions (*Mørketid-* polar night references).

#### O.2 — Lunar Toponymy
Moon-related names (*Mån-, Mond-, Luna-, Lune-*), tidal names linked to lunar cycles, monthly market/fair names tied to lunar calendar, *Nýmáni* (new moon) sites, lunar observation points.

#### O.3 — Stellar & Constellation Names
Star-related place names (*Stjerne-, Stern-, Stella-*), navigation-related stellar names (Polaris references for wayfinding), constellation names applied to landscape features, Milky Way references (*Vintergatanveien*), stellar alignment of named sites.

#### O.4 — Planetary Associations
Day-of-week names reflecting planetary dedications (Tuesday/Tyr/Mars, Wednesday/Odin/Mercury, Thursday/Thor/Jupiter, Friday/Freyja/Venus, Saturday/Saturn): correlation between deity-named places and the corresponding planetary day-market traditions. Alchemical-planetary associations in mining district names.

#### O.5 — Astrological Belief Systems
Zodiacal references in place names, astrological house associations, sites named for celestial events (comets, eclipses, meteor showers), *stjerneskudd* (shooting star) names, names referencing celestial omens, horoscopic foundation traditions (cities founded under auspicious alignments).

#### O.6 — Cosmological Worldviews
Axis mundi / world-centre names (omphalos, navel-of-the-world toponyms), world-tree references (Yggdrasil, *ask-/eik-* as cosmic trees), sky-pillar names, underworld/otherworld entries (*Hel-, Hades, Avernus*), cardinal direction cosmologies (east as sacred sunrise direction), three-world cosmology reflected in high/mid/low naming patterns.

#### O.7 — Orientation & Alignment
Testable: Do named sites show statistically significant alignment with solstice axes, equinox axes, or major stellar risings? Correlation between names containing directional elements and actual astronomical azimuth. Church orientations and dedication-day sunrise alignment. Stone row and stone circle names with astronomical function.

#### O.8 — Calendar & Temporal Cycle Names
Market-day names (fixed to astronomical/liturgical calendar), harvest-time names, *vår-/sommar-/høst-/vinter-* seasonal names and their actual climate correspondence, feast-day names (*Mikkels-/Michaelmas*, *Olsok/Olaf's wake*, *Jul-/Yule*), agricultural calendar names tied to stellar observations (Pleiades rising for planting).

### P — Esoteric, Occult & Geomantic Traditions

Beyond mainstream religion, Europe has sustained a rich undercurrent of esoteric practice that has left toponymic traces.

#### P.1 — Sacred Geometry & Ley Lines
Testable: Do named sacred sites (churches, stone circles, holy wells) align along straight lines more than expected by chance? Alfred Watkins' ley theory as a statistical hypothesis. Triangulation names, surveyor-origin names, geometry in planned city naming.

#### P.2 — Alchemy & Hermetic Tradition
Mining-district names with alchemical references (*Gold-, Silber-, Quecksilber/Mercury-*), *Philosopher's-* names, laboratory/furnace names in historical alchemical centres (Prague, Rudolf II era), *Stein-/Stone-* names with possible lapidary associations.

#### P.3 — Geomancy & Earth Divination
European geomantic practices: water-divining place names (*Wünschelrute* associations), dowsing-related names, *feng shui* analogs in Norse *landvætti* (land-spirit) traditions (choosing settlement sites based on spiritual suitability), dragon/serpent lines (*ormr-* as earth energy?).

#### P.4 — Numerological Patterns
Naming patterns based on sacred numbers: three (*Tri-/Tre-/Drei-*), seven (*Sieben-/Sept-/Syv-*), nine (*Nio-/Neun-/Ni-*), twelve. Trinitarian dedications vs. pre-Christian triple patterns. Are numerological name elements distributed non-randomly?

#### P.5 — Freemasonry & Secret Societies
Post-medieval naming: lodge-associated names, Enlightenment-era planned settlements with symbolic naming, compass-and-square references, *Tempel-/Temple-* names of non-crusade origin.

#### P.6 — Taboo, Euphemism & Apotropaic Naming
Dangerous places renamed euphemistically (calling a treacherous strait "the good passage"), bear-taboo names across Eurasia (the bear's *actual* PIE name replaced by euphemisms: bjørn < "the brown one", medved < "honey-eater", arktos < ?), wolf-taboo names, sea-taboo names among fishing communities, protective naming of children and places against evil eye/spirits.

### Q — Sensory & Perceptual Landscape

How non-visual sensory experience of landscape is encoded in place names.

#### Q.1 — Acoustic Toponymy
Echo names (*Ekko-, Echo-*), thunder names (*Torden-, Donner-, Trueno-*), waterfall roar names, wind-sound names (*Vindhyl-*, whistling names), silence/stillness names (*Still-, Stille-*), bell-audibility names (places named for hearing church bells).

#### Q.2 — Olfactory & Gustatory
Smell-based names (*Stink-, Foul-*, sulphur springs, seaweed-rot names), salt names (*Salt-, Sal-*, taste of springs), smoke names (*Reyk-/Reykjavik*, *Smog-*, charcoal-burning sites).

#### Q.3 — Thermal & Tactile
Hot spring names (*Warm-, Varm-, Therm-*, *Heit-/Hot-*), cold names (*Kald-, Kalt-, Cold-*), wind-exposure names (*Vindås, Windy-*), ice names (*Is-, Eis-, Glas-/Glaze-*), fire/burn names (*Brand-, Brenn-*).

#### Q.4 — Colour & Light
Colour toponymy as perceptual record: *Hvit-/White-* (chalk, snow, birch bark?), *Svart-/Black-* (dark soil, shadow, burnt ground?), *Raud-/Red-* (iron-rich, blood-alder, sunset?), *Grøn-/Green-* (fertile, grass, copper?), *Blå-/Blue-* (distance, haze, shadow?). Testable: Do colour names correlate with actual spectral characteristics of landscape?

### R — Mortality, Disease & Catastrophe

Place names as records of death, plague, famine, and disaster.

#### R.1 — Plague & Epidemic
*Pest-/Plague-* names, Black Death deserted farms (*ødegård*), mass burial sites, quarantine names (*Lazaretto*), leper colony names (*Spital-/Hospital-*), plague-saint dedications (*St. Roch, St. Sebastian*).

#### R.2 — Battle & Violence
Battlefield names (*-vallen, -feld*), massacre sites, execution names (*Galge-/Galgen-/Gallows-*), blood names (*Blod-/Blut-/Blood-*), weapons in names (*Sverd-/Schwert-/Sword-*, *Spyd-/Speer-*).

#### R.3 — Natural Disaster
Flood names (*Flom-/Flut-*), landslide names (*Ras-/Rutsch-*), avalanche names (*Lavine-/Laui-*), earthquake traces, volcanic event names, fire names (wildfire, urban conflagration), famine names.

#### R.4 — Boundary of Death
Cemetery names (*Kirke-gård, Fried-hof, Cimitero*), burial mound names (*-haug, -hügel, -tumulus*), execution sites, ghost/haunting names, will-o'-the-wisp/marsh-light names (*Irrlicht-, Lyktgubbe-*), underworld entry points.

### S — Medicinal, Healing & Therapeutic Landscape

#### S.1 — Healing Waters
Holy wells (*hellig kilde*), thermal springs (*Bad-, Bath-, Spa-/Espa*), mineral springs (*Sauer-/Sur-*, *Bitter-*), eye-well names, wart-well names, fever-well names. Statistical test: Do healing-water names cluster near actual mineral springs?

#### S.2 — Medicinal Plants
Herb-garden names, *Apotheker-/Apotek-* names, plant names with known medicinal use (lind/lime for fever, birch for skin, willow/selje for pain), monastic herb-garden locations.

#### S.3 — Hospital & Care
*Hospital-/Spital-* names, leper-house names (*St. Jørgen*), pilgrim hospice names, asylum names, *Hellig-/Heilig-/Holy-* healing dedications.

### T — Temporal Cycles & Ritual Calendar

#### T.1 — Seasonal Festival Sites
Midsummer celebration sites (*Jonsok-/Johannis-/St. Hans-*), winter solstice (*Jul-/Yule-/Weihnacht-*), equinox gatherings, *Valborgsmässoafton/Walpurgis* sites, harvest festival names, Samhain/All Saints boundary sites.

#### T.2 — Market & Assembly Timing
Periodic market names linked to calendar (*Michaelmas fair, Bartholomew fair*), thing-assembly timing, seasonal transhumance names (*seter/alm/alp* as summer-calendar markers), fishing-season names.

#### T.3 — Agricultural Calendar
Plowing-time names, sowing-time names, harvest names, hay-making names (*Slåtter-*), burning-time names (*Brenne-/Svedje-*), frost-date names.

### U — Proto-Indo-European & Deep-Time Sacred Landscape

Reconstructable naming patterns from the deepest linguistic layers accessible.

#### U.1 — PIE Sacred Vocabulary in Toponymy
*\*dʰeh₁-* (to place/establish — theophoric foundations), *\*h₂ṇsu-* (spirit/divine — *áss/Aesir*), *\*wódr̥* (inspiration/fury — Odin/Woden/Wotan), *\*perkʷ-* (oak/thunder — Perun, Perkūnas, Fjǫrgyn, Hercynia), *\*nebʰ-* (sacred/cloud — *nemeton*). Testing: Do PIE-derived sacred elements show geographic distributions consistent with known PIE expansion routes?

#### U.2 — Pre-Indo-European Substrate
Non-IE river names ("Old European hydronymy" — Krahe's theory), Basque substrate in Iberia/Aquitaine, possible Vasconic elements in wider Europe, pre-Sámi substrate in Fennoscandia, Tyrsenian traces (Etruscan), Iberian substrate, Pictish substrate, unclassified "Mediterranean" elements.

#### U.3 — Neolithic & Megalithic Naming
Names associated with megaliths (*Stein-/Stone-*, *Dolmen-*, *Cromlech-*), alignment sites, passage tomb names, *Jættestue/Giant's chamber* (folk-etymological overlay on megaliths), *Hünengrab/Hünenbett* (German giant-grave names for megaliths).

---

## Statistical Framework

The statistical framework is inspired by methods for testing correspondence between cultural patterns and geomorphology, generalized to all signal types. The null hypothesis varies per test but follows the same logic:

> Does observed correspondence deviate significantly from expected under chance, after controlling for known confounds?

### Test Families

| Family | Description | Example |
|--------|-------------|---------|
| **Correspondence** | Name element vs. environmental/cultural signal | *-berg* vs. terrain slope; *-vik* vs. coastal distance |
| **Spatial distribution** | Clustering, direction, gradient | Ripley's K, DBSCAN, Rayleigh test |
| **Temporal** | Chronological layer consistency | Are dated name layers geographically consistent? |
| **Language contact** | Substrate and boundary detection | Substrate signal vs. topographic barrier |
| **Migration** | Diaspora overfrequency | Norse elements in Normandy/Danelaw |
| **Political renaming** | Assimilation detection | Ratio of replaced vs. preserved names in border areas |
| **Bayesian comparison** | Competing etymologies | Posterior over alternative interpretations |
| **Astronomical alignment** | Orientation vs. celestial azimuth | Do *Sol-* names face solstice sunrise? |
| **Sacred geometry** | Site alignment along lines/patterns | Do cult-site names align more than random points? |
| **Sensory correspondence** | Perceptual names vs. measurable properties | Do colour names match spectral landscape data? |
| **Religious stratigraphy** | Cult-site superimposition | Are Christian *kirke-* names over-represented at pre-Christian *hov-* sites? |
| **Catastrophe clustering** | Disaster names vs. hazard maps | Do *ras-/flom-* names cluster in actual landslide/flood zones? |

### Robustness Requirements

Every test must pass:
- **Parameter sensitivity** (Latin Hypercube sweep)
- **Regional jackknife** (leave-one-region-out)
- **Temporal jackknife** (leave-one-period-out)
- **Spelling variant sensitivity**
- **Confound control** (population density, visibility, source bias)
- **Synthetic validation** (planted signal → power; pure noise → false positive rate)

### Preregistration

The framework enforces a clear separation between:
- **Preregistered tests** (hypotheses declared before data analysis)
- **Exploratory tests** (post hoc, clearly labelled as such)

Results are reported in a structured **results matrix** with this distinction explicit.

---

## Data Sources

The project uses a **connector architecture** where each data source is a plugin implementing a standard interface. New sources can be added without modifying core code.

### Available Connectors

| Source | Coverage | License | Status |
|--------|----------|---------|--------|
| GeoNames | Global (12M+ names) | CC-BY | Implemented |
| Wikidata | Global | CC0 | Implemented |
| OpenStreetMap | Global | ODbL | Implemented |
| Copernicus DEM | Global (30m) | Open | Implemented |
| Kartverket SSR (Norway) | Norway | NLOD | Implemented |
| Lantmäteriet (Sweden) | Sweden | CC0 | Planned |
| GST (Denmark) | Denmark | Open | Planned |
| MML (Finland) | Finland | CC-BY | Planned |
| Ordnance Survey (UK) | UK | OGL | Planned |
| Pleiades | Ancient world | CC-BY | Planned |

### Adding a New Source

Implement the `BaseConnector` interface:

```python
from toponymia.connectors.base import BaseConnector, ConnectorResult

class MySourceConnector(BaseConnector):
    """Connector for [Source Name]."""
    
    source_id = "my_source"
    source_name = "My Source"
    license = "CC-BY-4.0"
    coverage_region = "EU"
    
    def fetch(self, bbox: BoundingBox | None = None) -> Iterator[ConnectorResult]:
        """Yield normalized place records from source."""
        ...
    
    def validate(self, record: ConnectorResult) -> list[ValidationError]:
        """Validate a single record against schema."""
        ...
```

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Language | Python 3.12+ | Ecosystem for NLP, geo, statistics |
| Databank | JSONL (git-native) | Diff-friendly, merge-friendly, extensible schema |
| Database | PostgreSQL 16 + PostGIS (optional) | Spatial queries for analysis cache |
| Spatial | H3 hexagonal grid (R7/R9/R11) | Hierarchical spatial indexing for efficient queries |
| Statistics | NumPy, SciPy | Permutation tests, spatial analysis |
| Connectors | httpx | Async HTTP for GeoNames, Wikidata, OSM, Kartverket |
| CLI | Typer + Rich | Type-safe commands with beautiful tables |
| Build | UV | Fast dependency resolution, reproducibility |
| CI | GitHub Actions | Lint + test (py3.12/3.13) + ontology + databank validation |
| Standards | SKOS, ISO 639-3, ISO 15924 | Interoperability |

---

## Getting Started

### Prerequisites

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) (Python package manager)

### Installation

```bash
git clone https://github.com/egkristi/ToponymiaEuropaea.git
cd ToponymiaEuropaea

# Install dependencies (core only)
uv sync

# For development (includes pytest, ruff, etc.)
uv sync --extra dev

# For geospatial features (H3 spatial indexing)
uv sync --extra dev --extra geospatial

# Verify installation
uv run pytest
```

### First Analysis (Quick Start)

```bash
# Discover which elements appear in the databank
uv run toponymia analyze discover --country NO

# Analyze a specific element (e.g., -heim)
uv run toponymia analyze element heim --country NO

# Run with a specific statistical test
uv run toponymia analyze element heim --country NO --test spatial

# Ingest data from Kartverket (Norwegian official registry)
uv run toponymia ingest kartverket --municipality 0301 --limit 500 --output databank/

# Ingest data from GeoNames
uv run toponymia ingest geonames --country NO --output databank/places/NO/source.jsonl --limit 100

# View name lemma statistics
uv run toponymia lemma stats
uv run toponymia lemma list --limit 10

# Sign and verify databank records (enriches with phonetic keys + H3)
uv run toponymia databank sign
uv run toponymia databank verify
```

### REST API

The project includes a FastAPI-based REST API for querying the databank programmatically:

```bash
# Start the API server
uv run uvicorn toponymia.api.app:app --reload

# Endpoints:
# GET /health                  - Health check
# GET /api/v1/places           - List places (filter by country, source_id, name)
# GET /api/v1/places/{sha256}  - Get single place by hash
# GET /api/v1/sources          - List data sources
# GET /api/v1/search?q=oslo    - Search by name
# GET /api/v1/export/geojson   - Export as GeoJSON
# GET /api/v1/export/csv       - Export as CSV
# GET /api/v1/stats            - Databank statistics
```

Set `TOPONYMIA_DATABANK_PATH` to override the default databank directory.

### Optional: PostgreSQL for Analysis Cache

For larger datasets and spatial queries, optionally set up PostgreSQL:

```bash
# Start PostgreSQL + PostGIS (via Docker)
make docker-up

# Run database migrations
make db-migrate
```

### Configuration

Copy the example configuration:

```bash
cp config/settings.example.toml config/settings.toml
```

Edit `config/settings.toml` to configure API keys and analysis parameters.

---

## Project Structure

```
toponymia-europaea/
├── src/
│   └── toponymia/
│       ├── __init__.py
│       ├── cli.py                    # CLI: info, ingest, analyze, test, databank, lemma
│       ├── config.py                 # Configuration management
│       ├── api.py                    # Standalone DuckDB-backed API (Docker)
│       ├── seed.py                   # JSONL → PostgreSQL + Parquet seeder
│       ├── paper.py                  # Research paper LaTeX generator
│       ├── api/                      # FastAPI application
│       │   └── app.py               # REST endpoints (/places, /search, /stats)
│       ├── connectors/               # Data source plugins (14 connectors)
│       │   ├── base.py               # BaseConnector interface
│       │   ├── geonames.py           # GeoNames gazetteer
│       │   ├── kartverket.py         # Norwegian SSR (api.kartverket.no)
│       │   ├── lantmateriet.py       # Swedish Lantmäteriet (Ortnamn)
│       │   ├── maanmittauslaitos.py  # Finnish MML (Paikannimet)
│       │   ├── ordnance_survey.py    # UK Ordnance Survey (OS Names)
│       │   ├── ign.py               # French IGN (BD TOPO)
│       │   ├── wikidata.py          # Wikidata SPARQL
│       │   ├── osm.py              # OpenStreetMap Overpass
│       │   ├── diplomatarium.py     # Medieval charter databases
│       │   ├── rundata.py           # Scandinavian runic inscriptions
│       │   ├── dem.py               # DEM/terrain data (SRTM/Copernicus)
│       │   ├── climate.py           # Historical climate (CRU, PAGES2k)
│       │   └── historical_map_ocr.py # OCR from scanned historical maps
│       ├── core/                     # Core domain model
│       │   ├── database.py           # Database connection
│       │   └── onboarding.py         # Data promotion/demotion workflow
│       ├── pipelines/                # Analysis and data pipeline stages (18 modules)
│       │   ├── normalize.py          # Unicode NFC, substitutions, ASCII fallback
│       │   ├── segment.py            # Morphological segmentation
│       │   ├── analyze.py            # Databank → analysis bridge
│       │   ├── databank.py           # Signing, verification, sorting
│       │   ├── integrity.py          # SHA-256 integrity and MANIFEST
│       │   ├── validate.py           # Schema validation
│       │   ├── lemma.py              # Name lemma registry and detection
│       │   ├── phonetic.py           # Nordic phonetic normalizer
│       │   ├── dedup.py              # Cross-source deduplication
│       │   ├── diachronic.py         # Historical attestation linking
│       │   ├── spatial.py            # H3 hierarchical spatial indexing
│       │   ├── bayesian.py           # Bayesian hypothesis updating
│       │   ├── kernel.py             # Gold-standard kernel management
│       │   ├── analytical.py         # Parquet/DuckDB export and queries
│       │   ├── sync.py              # JSONL → Postgres → Parquet sync
│       │   ├── coordinates.py        # Multi-source coordinate resolution
│       │   └── etymology.py          # Wikidata P138 etymology extraction
│       ├── languages/                # Language-specific modules (201 auto-discovered)
│       │   ├── base.py              # BaseLanguageModule interface
│       │   ├── old_norse.py         # Reference implementation (120+ elements)
│       │   ├── ...                  # 199 more: all European, ancient, Caucasian,
│       │   └── ...                  #   Near Eastern, and Central Asian languages
│       ├── statistics/               # Statistical testing framework (15 modules)
│       │   ├── base.py              # BaseTest, PlaceData, StatFamily, StatStatus
│       │   ├── correspondence.py    # Permutation-based correspondence
│       │   ├── spatial.py           # Nearest-neighbour spatial clustering
│       │   ├── astronomical.py      # Rayleigh alignment test
│       │   ├── religious.py         # Religious stratigraphy proximity
│       │   ├── temporal.py          # Temporal layer consistency
│       │   ├── migration.py         # Migration overfrequency
│       │   ├── language_contact.py  # kNN segregation boundary detection
│       │   ├── political_renaming.py # Temporal clustering detection
│       │   ├── bayesian.py          # Bayesian etymology comparison
│       │   ├── ripleys_k.py         # Multi-scale spatial L(r)-r function
│       │   ├── name_change_rate.py  # Poisson rate ratio test
│       │   ├── sacred_geometry.py   # Ley-line hypothesis test
│       │   ├── catastrophe_clustering.py # Disaster names vs. hazard maps
│       │   └── sensory_correspondence.py # Sound environment correlation
│       └── perspectives/             # Perspective analysis (10 implementations)
│           ├── base.py              # BasePerspective interface
│           ├── terrain.py           # Terrain correspondence (DEM features)
│           ├── hydrological.py      # River/lake/fjord proximity
│           ├── archaeological.py    # Correlation with known sites
│           ├── religious.py         # Theophoric element distribution
│           ├── astronomical.py      # Solstice/equinox alignment
│           ├── colour.py            # Spectral/landscape colour correlation
│           ├── acoustic.py          # Sound environment correlation
│           ├── mortality.py         # Hazard map correlation
│           ├── migration.py         # Origin tracing by name distribution
│           └── economic.py          # Trade route correlation
├── databank/                         # Git-native JSONL persistence (source of truth)
│   ├── MANIFEST.sha256              # Integrity checksums for all data files
│   ├── sources.jsonl                # Source metadata registry
│   ├── schema/
│   │   └── place.v1.json            # JSON Schema for place records
│   ├── kernel/                      # Gold-standard verified records
│   │   ├── gold.jsonl               # 8 manually verified etymologies
│   │   └── criteria.json            # Validation criteria
│   └── places/                      # 3,018 records across 5 countries
│       ├── DK/geonames.jsonl        # 500 Danish records
│       ├── FI/geonames.jsonl        # 500 Finnish records
│       ├── IS/geonames.jsonl        # 500 Icelandic records
│       ├── NO/geonames.jsonl        # 500 Norwegian (GeoNames) records
│       ├── NO/kartverket.jsonl      # 504 Norwegian (Kartverket SSR) records
│       └── SE/geonames.jsonl        # 500 Swedish records
├── docker/                           # Container build files
│   ├── Dockerfile.api               # API service container
│   ├── Dockerfile.seed              # Seed/migration container
│   └── initdb/
│       └── 02-schema.sql            # PostgreSQL+PostGIS operational schema
├── docker-compose.yml                # Full 3-layer dev stack (db + api + seed)
├── Dockerfile                        # Main application container
├── migrations/                       # Database migrations (Alembic)
│   ├── env.py
│   └── versions/
├── config/
│   ├── settings.example.toml
│   └── ontology/
│       └── v1.0.0/
│           ├── name_types.skos.ttl  # SKOS name type hierarchy
│           └── perspectives.skos.ttl
├── web/                              # Static web frontend
│   ├── index.html                   # Public browse interface
│   ├── map.html                     # Interactive map (Leaflet/MapLibre)
│   └── dashboard.html               # Statistical results dashboard
├── benchmarks/
│   └── phonetic_evaluation.py       # BMPM vs Nordic normalizer benchmark
├── templates/
│   └── paper.tex                    # Research paper LaTeX template
├── tests/                            # 4,000+ tests, mypy strict clean
│   ├── conftest.py
│   ├── test_api/                    # API endpoint tests
│   ├── test_cli/                    # CLI command tests
│   ├── test_connectors/             # Connector tests (13 test files)
│   ├── test_core/                   # Core domain tests
│   ├── test_languages/              # Language module tests (3,184 parametrized)
│   ├── test_perspectives/           # Perspective module tests
│   ├── test_pipelines/              # Pipeline tests (17 test files)
│   └── test_statistics/             # Statistical test validation (13 test files)
├── docs/
│   ├── methodology.md              # Research methodology
│   ├── adding_a_language.md        # Guide: new language modules
│   ├── adding_a_source.md          # Guide: new data connectors
│   ├── ethics.md                   # Ethical considerations
│   ├── backup_strategy.md          # Database backup strategy
│   ├── LICENSING.md                # License compatibility matrix
│   └── decisions/                   # Architecture Decision Records
│       ├── 002-phonetic-matching.md
│       └── 003-coordinate-resolution.md
├── pyproject.toml                    # Project config (UV, dependencies, extras)
├── Makefile                          # Common dev commands
├── ROADMAP.md
├── CONTRIBUTING.md
├── CITATION.cff
├── LICENSE                           # CC BY-NC-SA 4.0
└── README.md
```

---

## Extending the Framework

### Adding a Language Module

```python
from toponymia.languages.base import BaseLanguageModule, SegmentationResult

class BasqueModule(BaseLanguageModule):
    """Language module for Basque (euskara) toponyms."""
    
    language_code = "eus"  # ISO 639-3
    language_name = "Basque"
    family = "Language isolate"
    
    # Known toponymic suffixes
    suffixes = ["-eta", "-aga", "-uri", "-berri", "-gorri", "-zuri"]
    
    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Basque toponym into morphological components."""
        ...
    
    def classify(self, components: list[str]) -> LanguageClassification:
        """Classify components as Basque with confidence."""
        ...
```

### Adding a Statistical Test

```python
from toponymia.statistics.base import BaseTest, TestResult

class CoastalDistanceTest(BaseTest):
    """Test correspondence between maritime name elements and coastal proximity."""
    
    test_id = "coastal_distance"
    description = "Tests whether maritime-related name elements cluster near coastlines"
    null_hypothesis = "Maritime elements are distributed independently of coastal distance"
    
    def run(self, data: TestData, n_permutations: int = 10000) -> TestResult:
        """Execute the test with permutation-based null model."""
        ...
    
    def validate_synthetic(self, n_trials: int = 100) -> SyntheticValidation:
        """Validate test on synthetic data before applying to real data."""
        ...
```

### Adding a Perspective

```python
from toponymia.perspectives.base import BasePerspective

class MaritimePerspective(BasePerspective):
    """Perspective for maritime and coastal toponymy."""
    
    perspective_id = "maritime"
    name = "Maritime & Coastal"
    required_data = ["coastline", "bathymetry", "historical_sea_routes"]
    
    def extract_features(self, place_id: UUID) -> dict:
        """Extract maritime-relevant features for a place."""
        ...
    
    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate testable hypotheses from maritime perspective."""
        ...
```

---

## Ethics and Responsibility

### Principles

- **Indigenous and minority languages** (Sámi, Basque, Sorbian, Romani, Cornish, etc.) are treated with particular care and in consultation with relevant communities.
- **Colonial and assimilation history** is documented explicitly. Norwegianization (*fornorskning*), Russification, Germanization, and parallel processes are never hidden.
- **Disputed territories**: No automatic privileging of one state's official name form over others. All historical attestations are equal as data.
- **Uncertainty**: Interpretations are always presented with confidence levels.
- **Openness**: Code, data (where license permits), ontology, and results are open.
- **Attribution**: All sources are credited according to their requirements.

### Data Governance

- Each record carries a `license` field; aggregated results respect the most restrictive input license.
- Personal data (living persons) is excluded unless publicly available in official registries.
- Indigenous sacred site information is only included with community consent.

---

## Citation

```bibtex
@software{toponymia_europaea,
  title = {Toponymia Europaea: An Open Research Framework for Place Name Analysis},
  author = {Kristiansen, Erling},
  year = {2025},
  url = {https://github.com/egkristi/ToponymiaEuropaea},
  license = {MIT}
}
```

Or use the [CITATION.cff](CITATION.cff) file for automated citation.

---

## License

This project is licensed under **[CC BY-NC-SA 4.0](LICENSE)** with a contribute-back clause:

- **Attribution** — You must give appropriate credit and link to this repository.
- **NonCommercial** — Commercial use requires prior written approval from the copyright holder.
- **ShareAlike** — Derivative works must be distributed under the same license.
- **Contribute Back** — All modifications and extensions must be made available to the original project.

Academic use in non-commercial research and teaching is expressly permitted.

For commercial licensing inquiries, see [LICENSE](LICENSE).

---

## Contributing

This project is open to contributions from anyone. The `main` branch is protected — all contributions go through Pull Requests with mandatory peer review.

**The standard is absolute**: every contribution must be scientific, verifiable, testable, and provable. Data requires references. Code requires tests. Claims require evidence.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full process, including branch strategy, PR requirements by contribution type, review checklist, and scientific integrity standards.

---

## Acknowledgements

This project builds upon decades of toponymic research across Europe. Key inspirations include the Nordic onomastic tradition (Rygh, Sandnes, Stemshaug, Helleland), English place-name studies (Ekwall, Watts), Germanic toponymy (Udolph), Slavic studies (Vasmer), and the broader computational humanities movement toward reproducible, testable research.
