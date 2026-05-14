# Roadmap — Toponymia Europaea

This roadmap tracks the project's development from initial framework to production research platform. Items are organized by milestone and priority.

**Legend:** ✅ Done | 🔄 In Progress | ⬚ Not Started

---

## Milestone 0 — Foundation (Current)

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

## Milestone 1 — Data Onboarding Pipeline (Code Implementation)

Implement the 5-stage onboarding process in code (currently documented in README only).

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1.1 | Add `status` field to ORM models | ✅ | Enum: candidate/verified/enriched/reviewed/published/retracted |
| 1.2 | Quarantine schema (stage 1 ingestion) | ⬚ | Separate from authoritative data |
| 1.3 | Automated validation rules (stage 2) | ⬚ | Format, encoding, coordinate bounds, dedup |
| 1.4 | Source attachment enforcement (NOT NULL FK) | ✅ | source_id NOT NULL in ORM |
| 1.5 | Review workflow (stage 4) | ✅ | State machine: promote/demote/retract with gates |
| 1.6 | Promotion/demotion logic | ✅ | core/onboarding.py, 23 tests |
| 1.7 | Retraction mechanism | ✅ | Soft-delete with audit trail, TransitionRecord |
| 1.8 | Quality metrics dashboard | ⬚ | Source coverage, multi-source rate, staleness |
| 1.9 | Alembic migration for status fields | ✅ | migration 002, committed 6c2c84a |

---

## Milestone 2 — Language Modules

Add language modules for major European toponymic traditions.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 2.1 | Proto-Germanic reconstructions | ✅ | ProtoGermanicModule, 19 tests |
| 2.2 | Old English module | ✅ | OldEnglishModule, 40+ suffixes, compounds |
| 2.3 | Sámi (Northern) module | ✅ | NorthernSamiModule, 24 elements, 33 modifiers |
| 2.4 | Finnish module | ⬚ | Agglutinative morphology |
| 2.5 | Irish/Scottish Gaelic module | ⬚ | Celtic elements |
| 2.6 | Welsh module | ⬚ | Celtic P-branch |
| 2.7 | Latin module | ⬚ | Roman-era names |
| 2.8 | Old Slavic module | ⬚ | Pan-Slavic toponymic suffixes |
| 2.9 | Basque module | ⬚ | Pre-IE isolate |
| 2.10 | Old High German module | ⬚ | Germanic continental |
| 2.11 | Arabic/Moorish module | ⬚ | Iberian substrate layer |

---

## Milestone 3 — Statistical Tests

Expand the statistical toolkit for all test families.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 3.1 | Temporal layer consistency test | ⬚ | Are dated layers geographically coherent? |
| 3.2 | Language contact boundary detection | ⬚ | Substrate signal vs. topographic barriers |
| 3.3 | Migration overfrequency test | ⬚ | Diaspora elements in target areas |
| 3.4 | Political renaming detection | ⬚ | Statistical assimilation signal |
| 3.5 | Bayesian etymology comparison | ⬚ | Posterior over competing interpretations |
| 3.6 | Astronomical alignment test | ✅ | Rayleigh test, mean direction, 11 tests |
| 3.7 | Sacred geometry alignment test | ⬚ | Ley-line hypothesis as statistical test |
| 3.8 | Sensory correspondence test | ⬚ | Colour names vs. spectral data |
| 3.9 | Religious stratigraphy test | ✅ | Proximity co-occurrence permutation test, 7 tests |
| 3.10 | Catastrophe clustering test | ⬚ | Disaster names vs. hazard maps |
| 3.11 | Ripley's K spatial analysis | ⬚ | Multi-scale clustering |
| 3.12 | Rayleigh directional test | ⬚ | Non-uniform orientation distributions |

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
| 7.4 | Code coverage reporting | ⬚ | Codecov or similar |
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

## Priority Order

1. **Milestone 1** — Data onboarding code (the foundation of trust)
2. **Milestone 7.3, 7.6** — Branch protection and pre-commit (process enforcement)
3. **Milestone 2.1–2.3** — First additional language modules
4. **Milestone 4.1** — First national registry connector
5. **Milestone 3.1–3.5** — Core statistical test expansion
6. **Milestone 5.1–5.4** — First perspective implementations
7. **Milestone 6.1–6.2** — API and basic visualization
8. **Milestones 6–8** — Production and community

---

## Versioning

- **v0.1.0** (current) — Framework foundation, architecture, proof-of-concept
- **v0.2.0** — Data onboarding pipeline implemented in code
- **v0.3.0** — 3+ language modules, 5+ statistical tests
- **v0.4.0** — First national registry connector, perspective modules
- **v0.5.0** — API and visualization layer
- **v1.0.0** — First complete research cycle (ingest → analyse → publish results)
