# Roadmap — Toponymia Europaea

This roadmap tracks the project's development from initial framework to production research platform. Items are organized by milestone and priority.

**Legend:** ✅ Done | 🔄 In Progress | ⬚ Not Started

**Current status:** 244 tests passing, 70% coverage, ~7,500 lines source, 15 databank records. End-to-end workflow functional: `toponymia analyze element heim --country NO` runs databank → segmentation → statistical test → results table.

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
| 2.5 | Irish/Scottish Gaelic module | ⬚ | Celtic elements (baile-, druim-, ard-, loch-, cill-) |
| 2.6 | Welsh module | ⬚ | Celtic P-branch (llan-, aber-, pen-, cwm-, bedd-) |
| 2.7 | Latin module | ⬚ | Roman-era names (-castra, -dunum, via-, aquae-) |
| 2.8 | Old Slavic module | ⬚ | Pan-Slavic toponymic suffixes (-ov, -itz, -grad) |
| 2.9 | Basque module | ⬚ | Pre-IE isolate (harri-, mendi-, ibai-) |
| 2.10 | Old High German module | ⬚ | Germanic continental (-heim, -burg, -wald) |
| 2.11 | Arabic/Moorish module | ⬚ | Iberian substrate layer (al-, wadi-, qal'a-) |
| 2.12 | Danish module | ⬚ | Critical for Danelaw analysis (-by, -thorp, -toft) |
| 2.13 | Swedish module | ⬚ | -torp, -rud, -ås, -holm |

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
| 10.1 | Bulk GeoNames import (Norway) | ⬚ | **HIGH** | ~50,000 Norwegian place names from GeoNames dump |
| 10.2 | Kartverket SSR bulk import | ⬚ | **HIGH** | ~800,000 official Norwegian names (primary authority) |
| 10.3 | Bulk GeoNames import (Nordic) | ⬚ | HIGH | Sweden, Finland, Denmark, Iceland |
| 10.4 | Wikidata etymology extraction | ⬚ | MEDIUM | P138 (named after) for all European settlements |
| 10.5 | Norske Gaardnavne (Rygh) digitized | ⬚ | HIGH | 19th-century authoritative Norwegian farm-name corpus |
| 10.6 | EPNS volumes (England) | ⬚ | MEDIUM | English Place-Name Society historical records |
| 10.7 | Attestations from Diplomatarium Norvegicum | ⬚ | HIGH | Medieval charter attestations with dates |
| 10.8 | Seed data for UK/Ireland | ⬚ | MEDIUM | GeoNames + OS data for Celtic language analysis |
| 10.9 | Seed data for Iberia | ⬚ | MEDIUM | Arabic/Moorish substrate layer validation |
| 10.10 | Historical attestation curation workflow | ⬚ | HIGH | How contributors add dated attestations from primary sources |

---

## Priority Order (Revised)

The litmus test (May 2025) proved the pipeline works mechanically — data loads, segments, and etymologizes. The bottleneck is now **linguistic knowledge** (bigger dictionaries) and **data volume** (15 records → thousands).

1. **Milestone 10.1–10.2** — Real data population (15 records can't validate hypotheses)
2. **Milestone 9.7, 9.9** — CI hardening (mypy) and connector test coverage
3. **Milestone 2.12–2.13** — Danish/Swedish modules (needed for Danelaw and Nordic analysis)
4. **Milestone 2.5–2.7** — More language modules (Celtic, Latin — for UK/France analysis)
5. **Milestone 3.2, 3.4** — Language contact and political renaming tests
8. **Milestone 4.2–4.4** — Nordic/UK registry connectors
9. **Milestone 6.1–6.2** — API and basic visualization
10. **Milestone 5.1–5.4** — First perspective implementations
11. **Milestones 7–8** — Infrastructure and community

---

## Versioning

- **v0.1.0** — Framework foundation, architecture, proof-of-concept.
- **v0.2.0** (current) — Expanded dictionaries (120+ ON entries), attestation analysis, analysis bridge, end-to-end workflow command, dependency trim. Pipeline runs from CLI.
- **v0.3.0** — Bulk data population (10,000+ records from GeoNames/Kartverket). First meaningful statistical results.
- **v0.4.0** — Multi-country data, 6+ language modules, first perspective modules
- **v0.5.0** — API and visualization layer
- **v1.0.0** — First publishable research result produced using the framework
