# Roadmap — Toponymia Europaea

This roadmap tracks the project's development from initial framework to production research platform. Items are organized by milestone and priority.

**Legend:** ✅ Done | 🔄 In Progress | ⬚ Not Started

**Current status:** 393 tests passing, 0 warnings, CI green (lint + mypy strict + test py3.12/3.13 + ontology + databank validation). 2500 GeoNames records (5 Nordic countries × 500). 7 language modules. End-to-end: `toponymia analyze element nes --country NO` runs databank → segmentation → statistical test → results.

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

## Milestone 2 — Language Modules

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
| 2.8 | Old Slavic module | ⬚ | Pan-Slavic toponymic suffixes (-ov, -itz, -grad) |
| 2.9 | Basque module | ⬚ | Pre-IE isolate (harri-, mendi-, ibai-) |
| 2.10 | Old High German module | ⬚ | Germanic continental (-heim, -burg, -wald) |
| 2.11 | Arabic/Moorish module | ⬚ | Iberian substrate layer (al-, wadi-, qal'a-) |
| 2.12 | Danish module | ✅ | -by, -torp/-drup, -toft, -lev, -løse. Segment, classify, etymologize. 22 tests. |
| 2.13 | Swedish module | ✅ | -torp, -rud, -ås, -tuna, -köping. Segment, classify, etymologize. 23 tests. |

---

## Milestone 3 — Statistical Tests

Expand the statistical toolkit for all test families.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 3.1 | Temporal layer consistency test | ✅ | Mean NND vs. permutation null, 7 tests |
| 3.2 | Language contact boundary detection | ⬚ | Substrate signal vs. topographic barriers |
| 3.3 | Migration overfrequency test | ✅ | Proportion difference permutation test, 7 tests |
| 3.4 | Political renaming detection | ⬚ | Statistical assimilation signal |
| 3.5 | Bayesian etymology comparison | ⬚ | Posterior over competing interpretations |
| 3.6 | Astronomical alignment test | ✅ | Rayleigh test, mean direction, 11 tests |
| 3.7 | Sacred geometry alignment test | ⬚ | Ley-line hypothesis as statistical test |
| 3.8 | Sensory correspondence test | ⬚ | Colour names vs. spectral data |
| 3.9 | Religious stratigraphy test | ✅ | Proximity co-occurrence permutation test, 7 tests |
| 3.10 | Catastrophe clustering test | ⬚ | Disaster names vs. hazard maps |
| 3.11 | Ripley's K spatial analysis | ⬚ | Multi-scale clustering |
| 3.12 | Name change rate test | ⬚ | Temporal frequency of renamings by region/period |

---

## Milestone 4 — Data Connectors

Connect to additional authoritative data sources.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 4.1 | Kartverket (Norway) connector | ✅ | SSR API, pagination, rate limiting, 11 tests |
| 4.2 | Lantmäteriet (Sweden) connector | ⬚ | Swedish national registry |
| 4.3 | Maanmittauslaitos (Finland) connector | ⬚ | Finnish national registry |
| 4.4 | Ordnance Survey (UK) connector | ⬚ | British national mapping |
| 4.5 | IGN (France) connector | ⬚ | French national mapping |
| 4.6 | Historical map OCR pipeline | ⬚ | Extract names from scanned maps |
| 4.7 | Diplomatarium connector | ⬚ | Medieval charter databases |
| 4.8 | Rundata connector | ⬚ | Scandinavian runic inscription DB |
| 4.9 | DEM/terrain data connector | ⬚ | Elevation, slope, aspect from SRTM/Copernicus |
| 4.10 | Climate data connector | ⬚ | Historical climate (CRU, PAGES2k) |

---

## Milestone 5 — Perspective Modules

Implement coded analysis for each perspective dimension.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 5.1 | Terrain correspondence perspective | ⬚ | Link names to DEM features |
| 5.2 | Hydrological perspective | ⬚ | River/lake/fjord proximity analysis |
| 5.3 | Archaeological site perspective | ⬚ | Correlation with known sites |
| 5.4 | Religious/cult site perspective | ⬚ | Theophoric element distribution |
| 5.5 | Astronomical orientation perspective | ⬚ | Solstice/equinox alignment analysis |
| 5.6 | Colour-landscape perspective | ⬚ | Spectral correlation |
| 5.7 | Acoustic landscape perspective | ⬚ | Sound environment correlation |
| 5.8 | Mortality/catastrophe perspective | ⬚ | Hazard map correlation |
| 5.9 | Migration/diaspora perspective | ⬚ | Origin tracing by name distribution |
| 5.10 | Economic/trade route perspective | ⬚ | Trade path correlation |

---

## Milestone 6 — Output & Visualization

Research output, API, and public-facing tools.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 6.1 | REST API (FastAPI) | ⬚ | Query names, places, interpretations |
| 6.2 | Interactive map visualization | ⬚ | Leaflet/MapLibre with name layers |
| 6.3 | Statistical results dashboard | ⬚ | Effect sizes, distributions, maps |
| 6.4 | Export formats (GeoJSON, CSV, RDF) | ⬚ | Interoperability |
| 6.5 | Research paper template/generator | ⬚ | Reproducible LaTeX output |
| 6.6 | Public web interface | ⬚ | Browse and explore the databank |

---

## Milestone 7 — Infrastructure & Operations

Production readiness, deployment, scaling.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 7.1 | Docker Compose development environment | ✅ | PostgreSQL 16 + PostGIS 3.4 |
| 7.2 | Database backup strategy | ⬚ | Automated, versioned |
| 7.3 | Branch protection rules (GitHub) | ⬚ | Enforce PR process (issue #3) |
| 7.4 | Code coverage reporting | ✅ | pytest-cov in CI, XML artifact, 70% coverage |
| 7.5 | Dependency vulnerability scanning | ⬚ | Dependabot / safety |
| 7.6 | Pre-commit hooks | ✅ | Ruff, trailing whitespace, YAML/TOML lint |
| 7.7 | Release process (semver tags) | ⬚ | Changelog generation |
| 7.8 | Container deployment (staging) | ⬚ | When research output is ready |

---

## Milestone 8 — Community & Outreach

Building the research community.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 8.1 | Project website | ⬚ | GitHub Pages or similar |
| 8.2 | Academic advisory board | ⬚ | Onomastics, linguistics, archaeology |
| 8.3 | First published research paper | ⬚ | Using the framework |
| 8.4 | Community forum/discussion | ⬚ | GitHub Discussions |
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
| 10.4 | Wikidata etymology extraction | ⬚ | MEDIUM | P138 (named after) for all European settlements |
| 10.5 | Norske Gaardnavne (Rygh) digitized | ⬚ | HIGH | 19th-century authoritative Norwegian farm-name corpus |
| 10.6 | EPNS volumes (England) | ⬚ | MEDIUM | English Place-Name Society historical records |
| 10.7 | Attestations from Diplomatarium Norvegicum | ⬚ | HIGH | Medieval charter attestations with dates |
| 10.8 | Seed data for UK/Ireland | ⬚ | MEDIUM | GeoNames + OS data for Celtic language analysis |
| 10.9 | Seed data for Iberia | ⬚ | MEDIUM | Arabic/Moorish substrate layer validation |
| 10.10 | Historical attestation curation workflow | ⬚ | HIGH | How contributors add dated attestations from primary sources |

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
| 11.2.1 | Curated JSONL kernel (gold-standard records) | ⬚ | **HIGH** | Keep in git: ontology, seed data, manually verified. Tens of thousands max. |
| 11.2.2 | PostgreSQL+PostGIS as operational store | ⬚ | **HIGH** | All published records, transactional writes from ingest. Local dev via Docker. |
| 11.2.3 | Parquet/DuckDB analytical layer | ⬚ | **HIGH** | Immutable snapshots for statistical runs (permutation tests over millions of rows) |
| 11.2.4 | Sync pipeline: JSONL → Postgres → Parquet | ⬚ | HIGH | Unidirectional flow with checksums |
| 11.2.5 | Local dev setup: `docker compose up` → full 3-layer | ⬚ | HIGH | Simulate production locally for testing |
| 11.2.6 | JSONL export on release (archival snapshots) | ⬚ | MEDIUM | Git-tagged exports for reproducibility |

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
| 11.4.1 | Evaluate Beider-Morse Phonetic Matching | ⬚ | HIGH | Best for multi-language, but complex |
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
| 11.6.1 | Multi-source coordinate strategy | ⬚ | MEDIUM | When Kartverket, GeoNames, Wikidata disagree — explicit resolution |
| 11.6.2 | Source priority hierarchy for geo | ⬚ | MEDIUM | National authority > GeoNames > OSM > Wikidata |
| 11.6.3 | License compatibility matrix | ⬚ | MEDIUM | CC-BY + ODbL + CC0 → output license determination |
| 11.6.4 | ODbL share-alike compliance | ⬚ | MEDIUM | OSM-derived data must maintain ODbL chain |
| 11.6.5 | GDPR for historical person-names | ⬚ | LOW | Jurisdiction-specific "dead enough" thresholds |

---

## Priority Order (Revised)

The litmus test (May 2025) proved the pipeline works mechanically. Data population (May 2026) delivered 3000 records across 5 countries with 7 language modules. The bottleneck is now **architectural scaling** and **data volume**.

**Milestone 9 is COMPLETE** — all 13 items done.
**Milestone 10.2 COMPLETE** — Kartverket SSR import (500 Oslo records, connector updated to new API).
**Milestone 10.1/10.3 COMPLETE** — GeoNames bulk import (2500 records, 5 Nordic countries).
**Milestone 11.1 COMPLETE** — Name lemma entity, JSONL schema, CLI commands.
**Milestone 11.3 COMPLETE** — H3 hierarchical spatial indexing (R7/R9/R11 on all records).
**Milestone 11.4.2 COMPLETE** — Nordic phonetic normalizer with sound change rules.
**Milestone 11.4.3 COMPLETE** — Phonetic index field on all records.
**Issues #10–13 closed** — mypy fixed, Danish/Swedish modules added, data populated.

**Status: 508 tests passing, mypy strict clean, 3018 databank records.**

### Immediate priorities (current sprint)

1. ~~**Milestone 11.4.4** — Cross-source deduplication pipeline~~ ✅
2. ~~**Milestone 11.4.5** — Diachronic attestation linking~~ ✅
3. ~~**Milestone 11.5.1–11.5.3** — Bayesian etymology framework~~ ✅
4. ~~**Milestone 11.5.4** — Bayesian comparison test~~ ✅
5. **Milestone 11.2.5** — Local 3-layer dev setup (simulate production)

### Next phase

4. **Milestone 11.2.1–11.2.3** — Layered persistence (JSONL kernel + Postgres + Parquet)
5. **Milestone 2.5–2.7** — Celtic/Latin language modules (for UK/France analysis)
6. **Milestone 10.5/10.7** — Historical sources (Norske Gaardnavne, Diplomatarium Norvegicum)
7. **Milestone 3.2, 3.4** — Language contact and political renaming tests

### Later

8. **Milestone 4.2–4.4** — Nordic/UK registry connectors
9. **Milestone 6.1–6.2** — API and basic visualization
10. **Milestone 5.1–5.4** — First perspective implementations
11. **Milestones 7–8** — Infrastructure and community

---

## Versioning

- **v0.1.0** — Framework foundation, architecture, proof-of-concept.
- **v0.2.0** — Expanded dictionaries (120+ ON entries), attestation analysis, analysis bridge, end-to-end workflow command, dependency trim. Pipeline runs from CLI.
- **v0.3.0** (current) — 3018 records (5 Nordic countries, 2 sources), 10 language modules, H3 spatial indexing, phonetic dedup, diachronic linking, Bayesian etymology framework + comparison test, Kartverket SSR import. 508 tests, mypy strict clean.
- **v0.4.0** — Cross-source deduplication, three-layer persistence, Bayesian etymology framework.
- **v0.5.0** — Historical sources (Norske Gaardnavne, Diplomatarium Norvegicum), Celtic/Latin modules.
- **v0.6.0** — API and visualization layer, 6+ perspective modules
- **v0.7.0** — Full Bayesian updating, publication-ready research outputs
- **v1.0.0** — First publishable research result produced using the framework
