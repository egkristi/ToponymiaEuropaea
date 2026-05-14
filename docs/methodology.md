# Methodology

## Research Design

Toponymia Europaea follows a **hypothetico-deductive framework** adapted for computational humanities. The core principle is that toponymic claims must be testable against null models and subject to robustness requirements.

### Epistemological Position

- Place name interpretations are **hypotheses**, not facts
- Multiple competing interpretations can coexist with different probability weights
- Uncertainty is quantified and propagated through all analyses
- Claims are falsifiable through statistical testing

## Data Pipeline

### 1. Ingestion

Data enters the system through **connectors**—plugins that normalize heterogeneous sources into a common format. Each record carries:
- Geographic coordinates with uncertainty
- Name form with language code and temporal bounds
- Provenance (source, access date, license)

### 2. Normalization

The normalization pipeline produces canonical forms for comparison:
- Unicode normalization (NFC)
- Script detection (ISO 15924)
- Language-specific orthographic normalization
- ASCII approximation for fuzzy matching

### 3. Morphological Segmentation

Language modules segment names into components:
- Compound head (suffix determining semantic class)
- Compound modifier (specifying element)
- Prefixes, infixes, genitive markers

Multiple segmentation hypotheses are generated and ranked by confidence.

### 4. Language Classification

Each component (and the name as a whole) is classified by probable source language with confidence. This enables detection of:
- Language layers (substrate, superstrate, adstrate)
- Chronological ordering of naming events
- Language contact phenomena

### 5. Etymological Generation

Candidate etymologies are generated from:
- Lexical databases (known word inventories per language/period)
- Sound change rules (historical phonology)
- Machine learning models trained on verified etymologies
- Expert knowledge encoded in language modules

### 6. Statistical Testing

Hypotheses are tested against null models using permutation-based methods, with mandatory robustness checks and synthetic validation.

## Statistical Methods

### Permutation Testing

The primary statistical method. For each test:
1. Compute observed test statistic
2. Generate null distribution by permuting labels (not coordinates)
3. Compute p-value as proportion of null values as extreme as observed
4. Report effect size and confidence intervals

### Null Models

| Test Type | Null Model |
|-----------|-----------|
| Element vs. signal | Element labels randomly distributed among all places |
| Spatial clustering | Random subset of same size from all places |
| Temporal consistency | Random assignment of dates to places |
| Language boundary | Random placement of boundary independent of topography |

### Robustness Requirements

Every test must survive:
1. **Regional jackknife**: Conclusion stable when excluding 10% of data
2. **Bootstrap CI**: Effect size confidence interval excludes zero
3. **Parameter sensitivity**: Result stable across parameter choices
4. **Confound control**: Population density, source density, terrain visibility

### Synthetic Validation

Before applying to real data, every test must demonstrate:
- **Power ≥ 0.80**: Can detect a planted signal of realistic magnitude
- **FPR ≤ 0.10**: Does not reject null when data is pure noise

### Multiple Testing Correction

When running multiple tests, apply:
- Bonferroni correction (conservative)
- Benjamini-Hochberg FDR (when tests are independent)
- Clearly report both corrected and uncorrected p-values

## Ontology Versioning

The controlled vocabulary (name types, perspectives, categories) is versioned with semantic versioning:
- **Major**: Breaking changes (categories removed or fundamentally redefined)
- **Minor**: New categories added (backwards compatible)
- **Patch**: Description clarifications (no structural change)

Every analysis records the ontology version used, enabling reproduction.

## Preregistration Protocol

1. Formulate hypothesis before examining data
2. Specify test method, null model, and significance criterion
3. Record in `analysis/preregistered/` with timestamp
4. Execute test and report results regardless of outcome

## Reproducibility

- All code is versioned (Git)
- Large data files tracked with DVC
- Database migrations versioned (Alembic)
- Random seeds fixed for all stochastic methods
- Full provenance chain from source data to results
