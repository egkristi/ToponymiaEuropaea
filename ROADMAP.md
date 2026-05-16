# Roadmap — Toponymia Europaea

This roadmap tracks the project's development from initial framework to production research platform. Items are organized by milestone and priority.

**Legend:** ✅ Done | 🔄 In Progress | ⬚ Not Started

**Current status:** 4,221 tests passing, 0 warnings, CI green (lint + mypy strict + test py3.12/3.13 + ontology + databank validation). 33,192 records (17 countries × 3 sources). 201 language modules with auto-discovery registry. 15 perspective modules. Gold-standard kernel (8 records). Full 3-layer persistence (JSONL → PostgreSQL → Parquet). End-to-end: `toponymia analyze element nes --country NO` runs databank → segmentation → statistical test → results.

---

## Milestone 0 — Foundation (Complete)

Core framework, architecture, and development infrastructure.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 0.1 | Project structure and packaging | ✅ | pyproject.toml, UV, CLI |
| 0.2 | Core ORM models (Place, NameAttestation, Interpretation, Source) | ✅ | SQLAlchemy 2.0 |
| 0.3 | Connector plugin architecture | ✅ | BaseConnector ABC |
| 0.4 | Language module plugin architecture | ✅ | BaseLanguageModule ABC |
| 0.5 | Statistical test framework | ✅ | BaseTest ABC with synthetic validation |
| 0.6 | Normalization pipeline | ✅ | Unicode NFC, substitutions, ASCII fallback |
| 0.7 | Old Norse language module (reference implementation) | ✅ | 30+ suffixes, segmentation, classification |
| 0.8 | Correspondence test (permutation-based) | ✅ | Power=1.00, FPR=0.00 validated |
| 0.9 | Spatial clustering test | ✅ | Nearest-neighbour permutation |
| 0.10 | GeoNames connector | ✅ | TSV parsing, caching |
| 0.11 | Wikidata connector | ✅ | SPARQL queries, rate limiting |
| 0.12 | OSM connector | ✅ | Overpass API, multilingual |
| 0.13 | SKOS ontology v1.0.0 | ✅ | Name type hierarchy |
| 0.14 | Alembic migration (initial schema) | ✅ | 15 tables, spatial indices |
| 0.15 | CLI (info, ingest, segment, test, results) | ✅ | Typer-based |
| 0.16 | 21 analytical perspectives documented (A–U) | ✅ | README |
| 0.17 | Data Quality & Onboarding Process (5-stage) | ✅ | Documented in README |
| 0.18 | CC BY-NC-SA 4.0 license with contribute-back | ✅ | |
| 0.19 | CONTRIBUTING.md with strict PR process | ✅ | |
| 0.20 | GitHub Actions CI pipeline | ✅ | Lint + test + ontology validation |

---

## Milestone 1 — Data Onboarding Pipeline (Complete)

Implement the 5-stage onboarding process in code.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.1 | Add `status` field to ORM models | ✅ | Enum: candidate/verified/enriched/reviewed/published/retracted |
| 1.2 | Quarantine schema (stage 1 ingestion) | ✅ | databank/ is the quarantine; records start as candidate |
| 1.3 | Automated validation rules (stage 2) | ✅ | Format, encoding, coordinate bounds, language code, source |
| 1.4 | Source attachment enforcement (NOT NULL FK) | ✅ | source_id NOT NULL in ORM |
| 1.5 | Review workflow (stage 4) | ✅ | State machine: promote/demote/retract with gates |
| 1.6 | Promotion/demotion logic | ✅ | core/onboarding.py, 23 tests |
| 1.7 | Retraction mechanism | ✅ | Soft-delete with audit trail, TransitionRecord |
| 1.8 | Quality metrics dashboard | ✅ | CLI: quality summary/validate-file/tests |
| 1.9 | Alembic migration for status fields | ✅ | migration 002 |
| 1.10 | Git-native databank persistence | ✅ | JSONL format, fork→PR workflow |
| 1.11 | Historical name attestations | ✅ | attestations[] array, diachronic support |
| 1.12 | Databank validation CI job | ✅ | validate-databank in CI |

---

## Milestone 2 — Language Modules (Complete)

Add language modules for major European toponymic traditions.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.1 | Proto-Germanic reconstructions | ✅ | ProtoGermanicModule, 19 tests |
| 2.2 | Old English module | ✅ | 40+ suffixes, compounds |
| 2.3 | Sámi (Northern) module | ✅ | NorthernSamiModule, 24 elements, 33 modifiers |
| 2.4 | Finnish module | ✅ | FinnishModule: compounds, -la/-lä, vowel harmony, 26 tests |
| 2.5 | Irish/Scottish Gaelic module | ✅ | GaelicModule: 36 prefixes, 11 suffixes, 42 elements; segment, classify, etymologize |
| 2.6 | Welsh module | ✅ | WelshModule: 31 prefixes, 14 suffixes, 42 elements; P-Celtic with mutation |
| 2.7 | Latin module | ✅ | LatinModule: 11 prefixes, 24 suffixes, 34 elements; Roman-era with reflexes |
| 2.8 | Old Slavic module | ✅ | OldSlavicModule: 16 prefixes, 25 suffixes, 36 elements; possessive/locative patterns. 17 tests. |
| 2.9 | Basque module | ✅ | BasqueModule: 16 prefixes, 20 suffixes, 40 elements; pre-IE isolate. 20 tests. |
| 2.10 | Old High German module | ✅ | OHGModule: 12 prefixes, 30 suffixes, 42 elements; habitative/topographic patterns. 19 tests. |
| 2.11 | Arabic/Moorish module | ✅ | ArabicMoorishModule: 13 prefixes, 7 suffixes, 31 elements; al-Andalus substrate. 18 tests. |
| 2.12 | Danish module | ✅ | -by, -torp/-drup, -toft, -lev, -løse. Segment, classify, etymologize. 22 tests. |
| 2.13 | Swedish module | ✅ | -torp, -rud, -ås, -tuna, -köping. Segment, classify, etymologize. 23 tests. |
| 2.14 | Norwegian module | ✅ | Norwegian-specific phonology (nob/nno) |
| 2.15 | All Nordic languages | ✅ | Icelandic, Faroese, + 7 Sami varieties |
| 2.16 | All European living languages | ✅ | 76 modules: Romance, Slavic, Baltic, Uralic, Turkic, Caucasian, Greek, etc. |
| 2.17 | Ancient/extinct languages | ✅ | 65+ modules: Pre-Roman, Anatolian, Paleo-Balkan, Medieval, Proto-languages |
| 2.18 | Adjacent civilizations | ✅ | 35 modules: Near East, Caucasus, Central Asian Turkic/Iranian |

**Total: 201 language modules implementing BaseLanguageModule (segment/classify/etymologize).**

---

## Milestone 3 — Statistical Tests

Expand the statistical toolkit for all test families.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 3.1 | Temporal layer consistency test | ✅ | Mean NND vs. permutation null, 7 tests |
| 3.2 | Language contact boundary detection | ✅ | kNN segregation index, permutation test. 8 tests. |
| 3.3 | Migration overfrequency test | ✅ | Proportion difference permutation test, 7 tests |
| 3.4 | Political renaming detection | ✅ | Temporal clustering (max-proportion-in-window), permutation test. 8 tests. |
| 3.5 | Bayesian etymology comparison | ✅ | Implemented in statistics/bayesian.py (BayesianComparisonTest). Log Bayes factor, entropy reduction. |
| 3.6 | Astronomical alignment test | ✅ | Rayleigh test, mean direction, 11 tests |
| 3.7 | Sacred geometry alignment test | ✅ | Ley-line hypothesis as statistical test |
| 3.8 | Sensory correspondence test | ✅ | Two-sided permutation on mean signal difference. 13 tests. |
| 3.9 | Religious stratigraphy test | ✅ | Proximity co-occurrence permutation test, 7 tests |
| 3.10 | Catastrophe clustering test | ✅ | Disaster names vs. hazard maps |
| 3.11 | Ripley's K spatial analysis | ✅ | RipleysKTest: multi-scale L(r)-r function + permutation envelope. 11 tests. |
| 3.12 | Name change rate test | ✅ | NameChangeRateTest: Poisson rate ratio + permutation test. 11 tests. |

---

## Milestone 4 — Data Connectors

Connect to additional authoritative data sources.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4.1 | Kartverket (Norway) connector | ✅ | SSR API, pagination, rate limiting, 11 tests |
| 4.2 | Lantmäteriet (Sweden) connector | ✅ | CC0 license, Ortnamn API, pagination, minority language support. 13 tests. |
| 4.3 | Maanmittauslaitos (Finland) connector | ✅ | CC-BY-4.0, Paikannimet API, Finnish/Swedish/Sámi. 13 tests. |
| 4.4 | Ordnance Survey (UK) connector | ✅ | OGL-3.0, OS Names API, English/Welsh/Gaelic. 13 tests. |
| 4.5 | IGN (France) connector | ✅ | Licence Ouverte 2.0, BD TOPO API, French/Breton/Basque/Occitan. 13 tests. |
| 4.6 | Historical map OCR pipeline | ✅ | Extract names from scanned maps |
| 4.7 | Diplomatarium connector | ✅ | Medieval charter databases |
| 4.8 | Rundata connector | ✅ | Scandinavian runic inscription DB |
| 4.9 | DEM/terrain data connector | ✅ | Elevation, slope, aspect from SRTM/Copernicus |
| 4.10 | Climate data connector | ✅ | Historical climate (CRU, PAGES2k) |
| 4.11 | Bathymetry data connector | ✅ | GEBCO, EMODnet, NVE lake depth. Supports coastal/lake depth queries. |
| 4.12 | Geoimage connector | ✅ | Wikimedia Commons geosearch. Geographically referenced images for places. |

---

## Milestone 5 — Perspective Modules

Implement coded analysis for each perspective dimension.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 5.1 | Terrain correspondence perspective | ✅ | Link names to DEM features |
| 5.2 | Hydrological perspective | ✅ | River/lake/fjord proximity analysis |
| 5.3 | Archaeological site perspective | ✅ | Correlation with known sites |
| 5.4 | Religious/cult site perspective | ✅ | Theophoric element distribution |
| 5.5 | Astronomical orientation perspective | ✅ | Solstice/equinox alignment analysis |
| 5.6 | Colour-landscape perspective | ✅ | Spectral correlation |
| 5.7 | Acoustic landscape perspective | ✅ | Sound environment correlation |
| 5.8 | Mortality/catastrophe perspective | ✅ | Hazard map correlation |
| 5.9 | Migration/diaspora perspective | ✅ | Origin tracing by name distribution |
| 5.10 | Economic/trade route perspective | ✅ | Trade path correlation |

---

## Milestone 6 — Output & Visualization

Research output, API, and public-facing tools.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 6.1 | REST API (FastAPI) | ✅ | Query names, places, interpretations |
| 6.2 | Interactive map visualization | ✅ | Leaflet/MapLibre with name layers |
| 6.3 | Statistical results dashboard | ✅ | Effect sizes, distributions, maps |
| 6.4 | Export formats (GeoJSON, CSV, RDF) | ✅ | Interoperability |
| 6.5 | Research paper template/generator | ✅ | Reproducible LaTeX output |
| 6.6 | Public web interface | ✅ | Browse and explore the databank |

---

## Milestone 7 — Infrastructure & Operations

Production readiness, deployment, scaling.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 7.1 | Docker Compose development environment | ✅ | PostgreSQL 16 + PostGIS 3.4 |
| 7.2 | Database backup strategy | ✅ | Automated, versioned |
| 7.3 | Branch protection rules (GitHub) | ⬚ | Enforce PR process (issue #3) |
| 7.4 | Code coverage reporting | ✅ | pytest-cov in CI, XML artifact, 70% coverage |
| 7.5 | Dependency vulnerability scanning | ✅ | Dependabot / safety |
| 7.6 | Pre-commit hooks | ✅ | Ruff, trailing whitespace, YAML/TOML lint |
| 7.7 | Release process (semver tags) | ✅ | Changelog generation |
| 7.8 | Container deployment (staging) | ✅ | When research output is ready |

---

## Milestone 8 — Community & Outreach

Building the research community.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 8.1 | Project website | ✅ | GitHub Pages or similar |
| 8.2 | Academic advisory board | ⬚ | Onomastics, linguistics, archaeology |
| 8.3 | First published research paper | ⬚ | Using the framework |
| 8.4 | Community forum/discussion | ✅ | GitHub Discussions |
| 8.5 | Conference presentation | ⬚ | ICOS, NORNa, or similar |
| 8.6 | Collaboration with national registries | ⬚ | Data sharing agreements |

---

## NEW: Milestone 9 — Architecture Consolidation (Critical)

Address structural debt accumulated during rapid development.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 9.1 | Unify persistence model | ✅ | **HIGH** | Architecture diagram updated, Persistence Model section added to README. Databank = source of truth, PostgreSQL = optional analysis cache. |
| 9.2 | Databank → analysis bridge | ✅ | **HIGH** | `load_databank()` → `build_test_data()` → PlaceData arrays. Pipeline-based element detection with attestation support. |
| 9.3 | Trim unused dependencies | ✅ | **HIGH** | Moved geopandas, rasterio, spacy, duckdb, pyarrow, statsmodels to optional extras [geospatial], [nlp], [warehouse]. |
| 9.4 | Connector → databank ingest pipeline | ✅ | **HIGH** | `toponymia ingest geonames --country NO --output databank/ --limit 100` writes JSONL directly. |
| 9.5 | Fix PytestCollectionWarning | ✅ | LOW | Renamed TestData→PlaceData, TestFamily→StatFamily, TestStatus→StatStatus. 0 warnings (was 15). |
| 9.6 | Fix pydantic-settings toml_file warning | ✅ | LOW | Removed unused `toml_file` from SettingsConfigDict. 0 warnings (was 1). |
| 9.7 | Add mypy to CI | ✅ | MEDIUM | Added as informational step (continue-on-error). 56 errors in strict mode — non-blocking until resolved. |
| 9.8 | End-to-end workflow command | ✅ | **HIGH** | `toponymia analyze element <elem> --country XX --test spatial`. Discover mode: `toponymia analyze discover`. |
| 9.9 | Test untested connectors | ✅ | MEDIUM | 26 mocked unit tests for OSM + Wikidata connectors (fetch, validate, error handling, pagination) |
| 9.10 | Commit uv.lock for reproducibility | ✅ | MEDIUM | uv.lock tracked in git (3549 lines). Ensures exact dependency versions. |
| 9.11 | Clarify Docker vs. databank architecture in README | ✅ | MEDIUM | Architecture diagram + Persistence Model section clarify databank as primary, PostgreSQL as optional. |
| 9.12 | Expand Old Norse suffix/modifier dictionaries | ✅ | **HIGH** | 120+ entries. 9/10 modern names segment; all ON attestations resolve with meanings. |
| 9.13 | Analyze attestation forms in pipeline | ✅ | **HIGH** | `segment_record()` analyzes all forms; picks best compound segmentation (e.g., Bergen→Bjǫrgvin). |

---

## NEW: Milestone 10 — Data Population (Critical for Research Value)

The framework has 15 seed records. To produce real research, it needs real data.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 10.1 | Bulk GeoNames import (Norway) | ✅ | 500 records ingested, sorted, signed, verified |
| 10.2 | Kartverket SSR bulk import | ✅ | **HIGH** | Connector updated to new API, 500 Oslo records ingested. CLI: `toponymia ingest kartverket` |
| 10.3 | Bulk GeoNames import (Nordic) | ✅ | 500 each for SE, FI, DK, IS — 2500 total records |
| 10.4 | Wikidata etymology extraction | ✅ | MEDIUM | P138 pipeline: 18 countries, coordinate matching, JSONL export. See `src/toponymia/pipelines/etymology.py` |
| 10.5 | Norske Gaardnavne (Rygh) digitized | ⬚ | HIGH | 19th-century authoritative Norwegian farm-name corpus |
| 10.6 | EPNS volumes (England) | ⬚ | MEDIUM | English Place-Name Society historical records |
| 10.7 | Attestations from Diplomatarium Norvegicum | ⬚ | HIGH | Medieval charter attestations with dates |
| 10.8 | Seed data for UK/Ireland | ✅ | MEDIUM | GeoNames + OS data for Celtic language analysis |
| 10.9 | Seed data for Iberia | ✅ | MEDIUM | Arabic/Moorish substrate layer validation |
| 10.10 | Historical attestation curation workflow | ✅ | HIGH | How contributors add dated attestations from primary sources |

---

## NEW: Milestone 11 — Architecture for Scale (External Review)

Based on external architectural review (May 2026). Addresses scaling to 100M+ records while preserving the git-native development workflow during early phases.

### Design Principles

1. **JSONL remains primary during development** — until centralized infrastructure is established and migration is complete.
2. **Local PostgreSQL+PostGIS simulates future production** — enables testing and development against the target architecture.
3. **Three-layer persistence** replaces the current two-layer model at scale.

### 11.1 — Name Lemma as First-Class Entity

The current model links attestations to places, but **names as types** (e.g., "Berg" across 40,000 places) have no representation. This is a prerequisite for distributional statistics.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 11.1.1 | Design `name_lemmas` table/model | ✅ | **CRITICAL** | canonical_form, language_code, semantic_field, pie_root, cognates (JSONB) |
| 11.1.2 | Add `lemma_id` FK to attestations | ✅ | **CRITICAL** | Links attestation → lemma (optional, backfilled) |
| 11.1.3 | Lemma auto-detection from segmentation | ✅ | HIGH | LemmaRegistry + suffix detection from databank |
| 11.1.4 | JSONL schema extension for lemma references | ✅ | HIGH | `_lemma`, `_lemma_language`, `_lemma_semantic_field` fields |
| 11.1.5 | CLI: `toponymia lemma list/show/stats` | ✅ | MEDIUM | 15 lemmas, 138 attestations across 5 countries |

### 11.2 — Layered Persistence Architecture

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 11.2.1 | Curated JSONL kernel (gold-standard records) | ✅ | **HIGH** | `databank/kernel/gold.jsonl` with 8 manually verified records. Issue #34. |
| 11.2.2 | PostgreSQL+PostGIS as operational store | ✅ | **HIGH** | Schema in `docker/initdb/02-schema.sql`, spatial indexes, upsert sync. Issue #22. |
| 11.2.3 | Parquet/DuckDB analytical layer | ✅ | **HIGH** | `src/toponymia/pipelines/analytical.py` — export, partition, DuckDB SQL. Issue #23. |
| 11.2.4 | Sync pipeline: JSONL → Postgres → Parquet | ✅ | HIGH | `src/toponymia/pipelines/sync.py` — checksums, manifest verify, full_sync(). Issue #25. |
| 11.2.5 | Local dev setup: `docker compose up` → full 3-layer | ✅ | HIGH | `docker-compose.yml` with db, api, seed services. Issue #26. |
| 11.2.6 | JSONL export on release (archival snapshots) | ✅ | MEDIUM | CI workflow creates JSONL archives on tagged releases. Issue #31. |

### 11.3 — Spatial Indexing (H3/S2)

PostGIS GIST indexes work to ~10M points. Beyond that, hierarchical spatial indexing is needed for queries like "all Tor- names within 5 km of an archaeological site".

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 11.3.1 | Add `h3_index_r7`, `h3_index_r9`, `h3_index_r11` to places | ✅ | **HIGH** | `_h3_r7`, `_h3_r9`, `_h3_r11` on all 3000 records |
| 11.3.2 | H3 computation in ingest pipeline | ✅ | **HIGH** | Auto-enriched during `databank sign --enrich` |
| 11.3.3 | Spatial queries via H3 (neighbour lookup) | ✅ | **MEDIUM** | `find_neighbours()`, `h3_distance()` in spatial.py |
| 11.3.4 | H3 field in JSONL schema | ✅ | **MEDIUM** | `_h3_r7`, `_h3_r9`, `_h3_r11` in place.v1.json |

### 11.4 — Phonetic Indexing & Fuzzy Matching

Soundex/Metaphone are English-centric. For cross-source deduplication (Þórshof = Torshov = Torshof), language-aware phonetic normalization is required.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 11.4.1 | Evaluate Beider-Morse Phonetic Matching | ✅ | HIGH | Evaluated: BMPM 8% TPR vs Nordic normalizer 36% TPR. Decision: keep custom. See docs/decisions/002-phonetic-matching.md |
| 11.4.2 | Nordic phonetic normalizer (ON→modern) | ✅ | **HIGH** | þ→t, ð→d, ǫ→o, hv→kv, ö→ø, -hem→-heim; find_duplicates() |
| 11.4.3 | Phonetic index field on attestations | ✅ | **HIGH** | `_phonetic_key` on all 3000 records, enriched during `databank sign` |
| 11.4.4 | Cross-source deduplication pipeline | ✅ | **HIGH** | Phonetic blocking + H3 spatial verification; `databank dedup` CLI |
| 11.4.5 | Diachronic attestation linking | ✅ | **HIGH** | Phonetic + spatial grouping, chronological chain building; `databank history` CLI |

### 11.5 — Bayesian Etymology Framework

Current `interpretations` table stores flat probabilities. For proper Bayesian hypothesis testing, competing etymologies must be modeled as mutually exclusive sets with explicit priors and evidence.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 11.5.1 | `hypothesis_set` model (competing etymologies) | ✅ | **HIGH** | HypothesisSet with validation, entropy, most_likely |
| 11.5.2 | `evidence` model (what updates which hypothesis) | ✅ | **HIGH** | Evidence with likelihood_ratios, weight, evidence_type |
| 11.5.3 | Prior vs. posterior tracking | ✅ | **HIGH** | EvidenceRecord log, sequential_update, serialization |
| 11.5.4 | Bayesian comparison test using hypothesis sets | ✅ | **MEDIUM** | BayesianComparisonTest (log Bayes factor, Kass-Raftery scale, synthetic validation) |

### 11.6 — Coordinate Conflict Resolution & Legal

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 11.6.1 | Multi-source coordinate strategy | ✅ | MEDIUM | `src/toponymia/pipelines/coordinates.py` — haversine, conflict detection. Issue #32. |
| 11.6.2 | Source priority hierarchy for geo | ✅ | MEDIUM | National authority > gazetteer > GeoNames > OSM > Wikidata. See `docs/decisions/003-coordinate-resolution.md` |
| 11.6.3 | License compatibility matrix | ✅ | MEDIUM | `docs/LICENSING.md` — full source mapping + compatibility matrix. Issue #33. |
| 11.6.4 | ODbL share-alike compliance | ✅ | MEDIUM | Documented in LICENSING.md: derived datasets inherit ODbL for OSM-sourced records. |
| 11.6.5 | GDPR for historical person-names | ✅ | LOW | Jurisdiction-specific "dead enough" thresholds |

---

## Priority Order (Revised)

The litmus test (May 2025) proved the pipeline works mechanically. Data population (May 2026) delivered 3000 records across 5 countries with 7 language modules. The bottleneck is now **architectural scaling** and **data volume**.

**Milestone 9 is COMPLETE** — all 13 items done.
**Milestone 2 is COMPLETE** — 201 language modules covering all of Europe and adjacent civilizations.
**Milestone 10.2 COMPLETE** — Kartverket SSR import (500 Oslo records, connector updated to new API).
**Milestone 10.1/10.3 COMPLETE** — GeoNames bulk import (2500 records, 5 Nordic countries).
**Milestone 11.1 COMPLETE** — Name lemma entity, JSONL schema, CLI commands.
**Milestone 11.3 COMPLETE** — H3 hierarchical spatial indexing (R7/R9/R11 on all records).
**Milestone 11.4.2 COMPLETE** — Nordic phonetic normalizer with sound change rules.
**Milestone 11.4.3 COMPLETE** — Phonetic index field on all records.
**Issues #10–13 closed** — mypy fixed, Danish/Swedish modules added, data populated.

**Status: 4,221 tests passing (incl. 3,184 parametrized module tests), mypy strict clean, 33,192 databank records, 201 language modules with auto-discovery registry, 15 perspective modules, 8 gold-standard kernel records.**

**Milestone 11.2 COMPLETE** — Full 3-layer persistence: JSONL kernel, PostgreSQL+PostGIS, Parquet/DuckDB, sync pipeline with checksums.
**Milestone 11.6 (4/5) COMPLETE** — Coordinate resolution, license matrix, ODbL compliance. Only GDPR analysis remains.
**Issue #19 COMPLETE** — Wikidata P138 etymology extraction pipeline (18 European countries).

### Immediate priorities (current sprint)

1. ~~**Milestone 11.4.4** — Cross-source deduplication pipeline~~ ✅
2. ~~**Milestone 11.4.5** — Diachronic attestation linking~~ ✅
3. ~~**Milestone 11.5.1–11.5.3** — Bayesian etymology framework~~ ✅
4. ~~**Milestone 11.5.4** — Bayesian comparison test~~ ✅
5. ~~**Milestone 3.2, 3.4** — Language contact and political renaming tests~~ ✅
6. ~~**Issue #40** — Language module auto-discovery registry~~ ✅
7. ~~**Issue #39** — Parametrized interface tests for all modules~~ ✅
8. ~~**Issue #31** — JSONL archival snapshots attached to releases~~ ✅
9. ~~**Issue #34** — Gold-standard kernel with validation tooling~~ ✅
10. ~~**Issue #27** — Evaluate Beider-Morse Phonetic Matching (decision: keep Nordic normalizer)~~ ✅
11. ~~**Issue #33** — License compatibility matrix (docs/LICENSING.md)~~ ✅
12. ~~**Issue #32** — Multi-source coordinate resolution strategy~~ ✅
13. ~~**Issue #23** — Parquet/DuckDB analytical layer~~ ✅
14. ~~**Issue #26** — Docker Compose full 3-layer stack~~ ✅
15. ~~**Issue #19** — Wikidata etymology extraction (P138)~~ ✅
16. ~~**Issue #22** — PostgreSQL+PostGIS operational store~~ ✅
17. ~~**Issue #25** — Sync pipeline: JSONL → Postgres → Parquet~~ ✅

### Next phase

1. **Milestone 10.5/10.7** — Historical sources (Norske Gaardnavne, Diplomatarium Norvegicum)
2. **Milestone 10.8–10.9** — Seed data for UK/Ireland and Iberia
3. ~~**Milestone 10.10** — Historical attestation curation workflow~~ ✅
4. **Milestone 12** — Next wave of perspective modules (6 remaining in 12B)
5. **Milestone 13** — NLP & machine learning layer
6. **Milestone 14** — Continental data scaling (100K+ records)

### Later

8. ~~**Milestone 4.2–4.4** — Nordic/UK registry connectors~~ ✅
9. ~~**Milestone 6.1–6.2** — API and basic visualization~~ ✅
10. ~~**Milestone 5.1–5.15** — All 15 perspective implementations~~ ✅
11. **Milestones 7–8** — Infrastructure and community (partial: #3, #35–38 remain)
12. **Milestone 15** — Research output pipeline (preregistration → publication)
13. **Milestone 16** — Linked Data & academic interoperability
14. **Milestone 17** — Geometry & spatial extent (outline acquisition for 1,898 area/line features)

---

## Milestone 12 — Next Wave Perspectives (11 remaining of 21)

The first 10 coded perspectives (terrain, hydrological, archaeological, religious, astronomical, colour, acoustic, mortality, migration, economic) address the most data-ready dimensions. The remaining 11 cover domains that require either new external datasets, novel analysis methods, or cross-disciplinary synthesis.

### 12A — Quantitative Perspectives (testable with near-term data)

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 12.1 | **Historical/Diachronic perspective** (B) | ✅ | **HIGH** | Settlement wave detection, period-specific name formation patterns. Requires dated attestations (→ #21, #24). Outputs: chronological density maps, period-assignment confidence. |
| 12.2 | **Ecological/Biological perspective** (D) | ✅ | **HIGH** | Flora/fauna elements vs. actual species distribution (pollen data, historical surveys). Link *bjørk-/birk-* to birch pollen zones, *ulv-/varg-* to wolf range. Connector: GBIF biodiversity data. |
| 12.3 | **Legal/Administrative perspective** (J) | ✅ | MEDIUM | Thing-sites, parish boundaries, hundred divisions. Spatial clustering of *ting-/thing-*, *by-* (village unit), *herad-*. Connector: historical administrative boundaries. |
| 12.4 | **Temporal/Calendar perspective** (T) | ✅ | MEDIUM | Seasonal names vs. climate data. Do *vår-* names cluster at lower elevations? Do market-day names align with historical fair calendars? Testable with existing DEM + climate connector. |
| 12.5 | **Medicinal/Healing perspective** (S) | ✅ | MEDIUM | Healing wells vs. actual mineral springs (geological survey data). *Bad-/Bath-/Spa-* names vs. thermal spring locations. Connector: geological survey APIs. |

### 12B — Cross-Disciplinary Perspectives (require novel methods or external datasets)

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 12.6 | **Cultural/Social perspective** (G) | ⬚ | MEDIUM | Personal name extraction, ethnonym distribution (*Finn-*, *Kvæn-*, *Lapp-*), occupational names (*Smed-*, *Møller-*). Requires NER for historical documents (→ Milestone 13). |
| 12.7 | **Literary/Textual perspective** (K) | ⬚ | MEDIUM | Cross-reference with saga locations, runic inscriptions, medieval charters. Frequency of place-name mentions in historical texts as significance proxy. Connectors: Rundata (✅), Diplomatarium (✅). |
| 12.8 | **PIE/Deep-Time substrate perspective** (U) | ⬚ | HIGH | Old European hydronymy (Krahe), non-IE substrate detection. Statistical test: Do substrate elements cluster along rivers more than expected? Cross-reference with archaeological culture boundaries. |
| 12.9 | **Esoteric/Geomantic perspective** (P) | ⬚ | LOW | Extend sacred_geometry statistical test to full perspective. Numerological patterns, ley-line hypothesis as rigorous spatial test. Primarily exploratory/negative-result research. |
| 12.10 | **Cognition/Semiotics perspective** (L) | ⬚ | LOW | Metaphor analysis (body-part names for landscape), spatial cognition across cultures. Requires NLP semantic field detection (→ Milestone 13). |
| 12.11 | **Genetics/Palaeoclimate perspective** (M) | ⬚ | LOW | Correlation between linguistic layers and aDNA distributions. Requires external aDNA datasets (Allen Ancient DNA Resource). Climate epochs vs. name formation. Long-term research goal. |

**Note:** Perspectives A (Linguistics) and N (Methodology) are framework-level concerns, not coded modules.

---

## Milestone 13 — NLP & Machine Learning Layer

Move beyond regex/dictionary-based morpheme detection. Enable automated analysis at scale.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 13.1 | **Transformer-based morpheme segmentation** | ⬚ | **HIGH** | Fine-tune on known segmentations from language modules. Handle compounds (Þór+s+hof) without dictionary lookup. |
| 13.2 | **Cross-lingual cognate detection** | ⬚ | **HIGH** | Automated PIE root matching across language modules. Sound correspondence rules as learned embeddings. E.g., detect that Perun/Perkūnas/Fjǫrgyn share *\*perkʷ-*. |
| 13.3 | **Named Entity Recognition for historical texts** | ⬚ | MEDIUM | SpaCy/transformer NER trained on medieval charters, sagas, diplomas. Extract place-name mentions with dates. Feeds perspectives B, G, K. |
| 13.4 | **Automated name-type classification** | ⬚ | MEDIUM | Character-level CNN/RNN to classify name types (habitative, topographic, theophoric, anthroponymic) without explicit rules. Validate against language module classifications. |
| 13.5 | **Substrate detection via distributional analysis** | ⬚ | HIGH | Identify non-IE elements by statistical anomaly in phonotactics. Names that don't fit any known language module → candidate substrate. Feeds perspective U. |
| 13.6 | **Semantic embedding space for name elements** | ⬚ | MEDIUM | Embed name elements in shared space. Cluster semantically similar elements across languages (*berg/fjell/montagna/góra* → "mountain" cluster). Enable cross-lingual queries. |
| 13.7 | **OCR post-correction for historical maps** | ⬚ | LOW | Improve historical_map_ocr connector output using language-model-based correction. Reduce error rate for extracting names from 17th–19th century maps. |

---

## Milestone 14 — Continental Data Scaling (100K+ records)

Scale from 2,936 records (5 Nordic countries) to continental coverage. Prerequisite for statistically meaningful cross-regional analysis.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 14.1 | **Norske Gaardnavne (Rygh) digitized corpus** | ⬚ | **HIGH** | 19th-century authoritative Norwegian farm-name corpus. ~60,000 names with etymologies. Issue #20. |
| 14.2 | **Diplomatarium Norvegicum attestations** | ⬚ | **HIGH** | Medieval charter attestations with dates. ~10,000 dated forms. Issue #21. |
| 14.3 | **EPNS volumes (England)** | ⬚ | HIGH | English Place-Name Society. County-by-county historical analysis. Issue #28. |
| 14.4 | **UK/Ireland seed data** | ✅ | HIGH | GeoNames GB/IE/IM: 9,616 records. Celtic substrate validation. Issue #29. |
| 14.5 | **Iberian seed data** | ✅ | HIGH | GeoNames ES/PT/AD/GI: 11,647 records. Arabic/Mozarabic substrate layer. Issue #30. |
| 14.6 | **Central European expansion** | ✅ | MEDIUM | DE (5,500), AT (4,500), CH (4,500), PL (5,000), CZ (4,000) from GeoNames. Issue #44. |
| 14.7 | **Baltic states** | ✅ | MEDIUM | Estonia (47 cities), Lithuania (81 cities), Latvia (83 cities). Wikidata + OSM polygon geometry. Historical German/Polish/Swedish name layers. |
| 14.8 | **Balkans & Southeast Europe** | ⬚ | LOW | Complex stratigraphy: Illyrian → Latin → Slavic → Ottoman → modern. |
| 14.9 | **Historical attestation curation workflow** | ⬚ | **HIGH** | Web interface for contributors to add dated attestations. Issue #24. |
| 14.10 | **Automated source discovery** | ⬚ | MEDIUM | Crawl/detect national gazetteer APIs and open datasets. |
| 14.11 | **Quality gate automation (ML-assisted)** | ⬚ | MEDIUM | ML classifier for onboarding stages 2–3. Flag dubious records, auto-promote high-confidence ones. |

---

## Milestone 15 — Research Output Pipeline

From raw statistical results to publishable academic output.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 15.1 | **Preregistration workflow** | ✅ | **HIGH** | OSF-format preregistration for *-heim* study. `research/preregistration/`. |
| 15.2 | **Results matrix generator** | ✅ | **HIGH** | Defines hypotheses → tests → outputs mapping. `research/results/README.md`. |
| 15.3 | **Reproducible research notebooks** | ✅ | HIGH | Python analysis script: `research/notebooks/01_heim_distribution.py`. Runs end-to-end. |
| 15.4 | **Automated figure generation** | ✅ | MEDIUM | `src/toponymia/research/` module. Publication-quality PDF/PNG. Colourblind-safe palette. |
| 15.5 | **LaTeX paper pipeline** | ⬚ | MEDIUM | Extend templates/paper.tex. Results → tables/figures → compiled PDF. |
| 15.6 | **First research paper: Norse cult-site distribution** | ⬚ | **HIGH** | Demonstrate framework on testable question: Do *hov-/vé-/hǫrgr-* names cluster at specific landscape features? Target: NORNA/ICOS proceedings. |
| 15.7 | **Negative results documentation** | ⬚ | MEDIUM | Publish null results (e.g., "ley lines show no significant alignment"). Equally valuable. |

---

## Milestone 17 — Geometry & Spatial Extent

Place names often refer to features with spatial extent: rivers (polylines), lakes/islands (polygons), mountain ranges (polygons), valleys (polygons), administrative regions (polygons). This milestone adds outline geometry to the databank so features can be rendered with their actual shape rather than just a centroid point.

### 17.1 — Schema & Classification (✅ DONE)

| # | Item | Status | Notes |
|---|------|--------|-------|
| 17.1.1 | **Geometry type classification** | ✅ | All 2,936 records classified: 1,120 point, 209 line, 1,689 area |
| 17.1.2 | **Schema support for GeoJSON geometry** | ✅ | `geometry` field (GeoJSON Geometry object), `_geometry_class`, `_geometry_status` |
| 17.1.3 | **Classification pipeline** | ✅ | `geometry_classify.py` — automatic classification from place_type |
| 17.1.4 | **Detail page with geometry rendering** | ✅ | `place.html` shows geometry on Leaflet map when present |

### 17.2 — Geometry Acquisition

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 17.2.1 | **OSM geometry fetcher** | ⬚ | **HIGH** | Query Overpass API for matching features by name+type+bbox. Extract way/relation geometry as GeoJSON. |
| 17.2.2 | **Wikidata geometry fetcher** | ⬚ | MEDIUM | Use P625 (coordinate) + P3896 (geoshape) properties. Good coverage for lakes, islands, countries. |
| 17.2.3 | **National mapping authority geometry** | ⬚ | MEDIUM | Kartverket N50 (NO), Lantmäteriet (SE): official outlines for rivers, lakes, coastlines. |
| 17.2.4 | **Geometry simplification** | ⬚ | MEDIUM | Douglas-Peucker or Visvalingam simplification for storage efficiency. Target: <50 vertices for display. |
| 17.2.5 | **Geometry validation** | ⬚ | HIGH | Ensure valid GeoJSON (closed rings, right-hand rule, no self-intersections). Shapely-based validator. |
| 17.2.6 | **Manual geometry upload** | ⬚ | LOW | JSONL patch format for contributor-submitted geometries from GIS tools (QGIS export). |

### 17.3 — Integration & Display

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 17.3.1 | **Map page: render outlines** | ⬚ | HIGH | Show polygon/polyline geometry on the interactive map instead of just markers. |
| 17.3.2 | **Spatial queries with geometry** | ⬚ | MEDIUM | "Within" queries: find all places within a river's watershed, island's boundary, etc. |
| 17.3.3 | **Area calculation** | ⬚ | LOW | Compute and store area (km²) for polygon features, length (km) for linear features. |
| 17.3.4 | **Geometry coverage dashboard** | ⬚ | LOW | Track percentage of pending geometries resolved over time. |

### Current Status

- **1,120** records are spot locations (point) — no geometry needed
- **209** records are linear features — need polyline geometry
- **1,689** records are area features — need polygon geometry
- **1,898 total** records flagged as "geometry pending" (⚠)
- **0** records have defined geometry (acquisition not yet started)

---

## Milestone 18 — Data Enrichment Pipelines (In Progress)

Enrich existing databank records with external data to support richer analysis and user presentation.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 18.1 | **Bathymetry enrichment** | ✅ | HIGH | GEBCO, EMODnet, NVE lake depth. `_depth_m`, `_depth_source` fields. `bathymetry_enrich.py` pipeline. |
| 18.2 | **Geolocated image links** | ✅ | HIGH | Wikimedia Commons geosearch. `_image_links` field with title, URL, license, distance. `geoimage_enrich.py` pipeline. |
| 18.3 | **Elevation enrichment** | ⬚ | MEDIUM | DEM connector already exists; bulk-enrich records missing elevation from Copernicus 30m DEM. |
| 18.4 | **Climate zone classification** | ⬚ | MEDIUM | Assign Köppen climate zone to each record using climate connector. |
| 18.5 | **Land cover classification** | ⬚ | LOW | Corine Land Cover / Copernicus data for habitat context. |
| 18.6 | **Nearest water feature distance** | ⬚ | MEDIUM | Compute distance to nearest river/lake/coast for hydrological perspective support. |

---

## Milestone 16 — Linked Data & Academic Interoperability

Connect the framework to the wider academic data ecosystem.

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 16.1 | **RDF/Linked Data export** | ✅ | MEDIUM | `toponymia databank export-rdf` — GeoSPARQL, Schema.org, SKOS. rdflib-based. |
| 16.2 | **Pleiades cross-references** | ⬚ | MEDIUM | Link ancient place names to Pleiades gazetteer of ancient world. |
| 16.3 | **LOD gazetteer interoperability** | ✅ | MEDIUM | owl:sameAs to GeoNames LOD and Wikidata entities. |
| 16.4 | **IIIF integration for manuscript sources** | ⬚ | LOW | Link attestations to IIIF manifests of source manuscripts. |
| 16.5 | **Collaboration with national registries** | ⬚ | MEDIUM | Formal data sharing agreements. Issue #38. |
| 16.6 | **Graph database layer (optional)** | ⬚ | LOW | Neo4j/NetworkX for etymological family trees, name diffusion networks. |
| 16.7 | **DOI for datasets** | ⬚ | MEDIUM | Zenodo deposit for versioned databank releases. Citeable datasets. |

---

## Versioning

- **v0.1.0** — Framework foundation, architecture, proof-of-concept.
- **v0.2.0** — Expanded dictionaries (120+ ON entries), attestation analysis, analysis bridge, end-to-end workflow command, dependency trim. Pipeline runs from CLI.
- **v0.3.0** — 3018 records (5 Nordic countries, 2 sources), 14 language modules, H3 spatial indexing, phonetic dedup, diachronic linking, Bayesian etymology framework + comparison test, language contact/political renaming tests, Ripley's K spatial + name change rate + sacred geometry + catastrophe clustering + sensory correspondence tests, Kartverket + Lantmäteriet + MML + OS + IGN connectors. 707 tests, mypy strict clean.
- **v0.4.0** — 201 language modules (all European, ancient/extinct, and adjacent civilizations), 820+ tests, full CI pipeline, comprehensive linguistic coverage from Proto-Indo-European to modern minority languages.
- **v0.5.0** (current) — Full 3-layer persistence (JSONL+Postgres+Parquet), sync pipeline, Wikidata etymology extraction, Docker Compose stack, coordinate resolution, license matrix, 15 perspectives (historical through medicinal), bathymetry + geoimage enrichment pipelines, geometry classification, 16 data connectors, attestation validation pipeline. 4,221 tests, 2,936 records.
- **v0.6.0** — Historical sources and attestation curation. Norske Gaardnavne, Diplomatarium Norvegicum, UK/Ireland and Iberian seed data. 50K+ records.
- **v0.7.0** — NLP layer bootstrap (13.1–13.2: morpheme segmentation, cognate detection). Continental data scaling. Geometry acquisition pipeline.
- **v0.8.0** — Continental data scaling (100K+ records). Cross-disciplinary perspectives (12.6–12.11). Full NLP pipeline (13.3–13.6).
- **v0.9.0** — Research output pipeline. Preregistration, results matrix, reproducible notebooks, automated figures.
- **v1.0.0** — First publishable research result produced and submitted. Linked Data export. DOI for datasets.

---

## Milestone 19 — Topographic Metrics for Terrain Features

Enrich mountain/hill/peak records with quantitative topographic data. These metrics enable analysis of naming patterns relative to physical prominence and spatial dominance.

### Wikidata Properties (readily available)

| Property | Description | Coverage |
|----------|-------------|----------|
| P2660 | Topographic prominence (m) | ~50,000 peaks globally |
| P2659 | Topographic isolation (km) | ~30,000 peaks globally |
| P3137 | Parent peak (nearest higher summit) | ~20,000 peaks |
| P4552 | Mountain range membership | Extensive |
| P2044 | Elevation (m) | Very high coverage |

### Implementation Plan

| # | Item | Status | Priority | Notes |
|---|------|--------|----------|-------|
| 19.1 | **Mountain/peak ingestion script** | ✅ | **HIGH** | Norway: 5,402 peaks from Wikidata. 733 with prominence, 574 with isolation, 266 with mountain range. |
| 19.2 | **Schema fields: prominence, isolation** | ✅ | **HIGH** | `prominence_m`, `isolation_km`, `parent_peak_qid`, `mountain_range`, `dominance_ratio` in JSONL records. |
| 19.3 | **Dominance ratio computation** | ⬚ | MEDIUM | `prominence_m / elevation_m` — measures relative significance of a peak. |
| 19.4 | **Nearest-equal-height analysis** | ⬚ | MEDIUM | For peaks without P2659: compute from DEM (Copernicus 30m). |
| 19.5 | **Peak naming pattern analysis** | ⬚ | HIGH | Do prominent peaks have older/more stable names? Is isolation correlated with unique naming? |
| 19.6 | **Mountain range grouping** | ⬚ | MEDIUM | Group peaks by P4552 range. Analyze naming consistency within ranges. |
| 19.7 | **Cross-country peak comparison** | ⬚ | MEDIUM | Compare naming conventions for terrain features across linguistic boundaries (e.g., Scandinavian Mountains). |
| 19.8 | **DEM-based metrics pipeline** | ⬚ | LOW | Bulk computation from Copernicus 30m DEM for peaks lacking Wikidata values. |

### Research Questions

- Do topographically isolated peaks receive unique names more often than clustered peaks?
- Is there a correlation between prominence and name age/stability?
- Do mountain names encode relative height (e.g., "Store-/Lille-" vs actual prominence)?
- Are naming patterns within a mountain range more consistent than across ranges?
