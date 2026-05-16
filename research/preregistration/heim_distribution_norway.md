# Preregistration: *-heim* Distribution in Norway — A Computational Reanalysis

**OSF Preregistration Template (Open-Ended Registration)**

## Study Information

### Title
The spatial distribution of *-heim* place names in Norway: a computational
reanalysis using the Toponymia Europaea framework.

### Authors
- Erling Gustav Moland Kristiansen

### Description
This study re-examines the geographic distribution of Norwegian place names
containing the suffix *-heim* (ON *heimr* 'home, settlement') using
computational methods. Previous scholarship (Rygh 1898; Sandnes & Stemshaug
1976; Særheim 2007) has established broad distributional patterns based on
manual surveys. We apply spatial statistics, kernel density estimation, and
elevation/terrain analysis to the full digital corpus of Norwegian *-heim*
names extracted from Kartverket SSR and GeoNames data.

### Hypotheses

**H1 (Elevation):** *-heim* names are concentrated at lower elevations
(< 200 m.a.s.l.) compared to a random sample of Norwegian place names,
reflecting their association with arable settlement sites.

**H2 (Coastal proximity):** *-heim* names show significant clustering near
fjord heads and coastal lowlands (within 20 km of coastline), consistent
with the Norse settlement pattern along navigable waterways.

**H3 (Regional variation):** The density of *-heim* names varies
significantly across Norwegian regions (fylker), with Vestland, Trøndelag,
and Rogaland showing the highest concentrations (replicating Sandnes 1976).

**H4 (Terrain type):** *-heim* names are preferentially located on flat
or gently sloping terrain (slope < 10°), distinguishing them from *-setr*
and *-støl* names which occur at higher elevations on steeper terrain.

**H5 (Clustering):** *-heim* names exhibit statistically significant
spatial clustering (Ripley's K function) at scales of 5–50 km, reflecting
the nucleated settlement pattern of the Viking Age.

## Design Plan

### Study Type
Observational / corpus-based spatial analysis.

### Study Design
Cross-sectional analysis of the complete Norwegian *-heim* name corpus
against control groups of other common place-name suffixes.

### Variables

**Dependent:**
- Presence/absence of *-heim* suffix
- Name density per region (names/km²)

**Independent:**
- Elevation (metres above sea level)
- Distance to coast (km)
- Terrain slope (degrees)
- Administrative region (fylke)
- Latitude/longitude

**Control groups:**
- *-stad* names (comparable settlement indicator)
- *-setr*/*-seter* names (shieling/summer pasture)
- *-vik* names (coastal reference)
- Random sample of all Norwegian place names (n=1000)

## Sampling Plan

### Data Sources
1. **Kartverket SSR** — Complete Norwegian place-name register
2. **GeoNames** — Cross-referenced via Wikidata Q-IDs
3. **Toponymia Europaea databank** — Merged, deduplicated, enriched records

### Inclusion Criteria
- Names ending in *-heim*, *-hem*, *-um* (phonetically reduced *-heim*)
- Located within Norway (country_code = NO)
- Valid coordinates (lat/lon not null)
- Feature class P (populated place) or L (area)

### Exclusion Criteria
- Transferred *-heim* names (street names derived from farm names)
- Names where *-heim* is not the final element (e.g., *Heimdal*)
- Duplicate records (same coordinates within 100m radius)

### Sample Size
Expected corpus: ~800–1,200 *-heim* names based on Sandnes (1976) estimate
of ~1,000 original *-heim* farms in Norway.

## Analysis Plan

### Statistical Methods

| # | Hypothesis | Test | Software |
|---|-----------|------|----------|
| H1 | Elevation | Welch's t-test + Mann-Whitney U | scipy.stats |
| H2 | Coastal proximity | Welch's t-test + KDE comparison | scipy.stats + sklearn |
| H3 | Regional variation | Chi-squared test + standardised residuals | scipy.stats |
| H4 | Terrain type | Logistic regression (heim vs. setr) | statsmodels |
| H5 | Clustering | Ripley's K function + Monte Carlo envelope | pointpats / custom |

### Multiple Comparisons
Bonferroni correction for 5 primary hypotheses (α = 0.01).

### Effect Sizes
Report Cohen's d for continuous comparisons, Cramér's V for categorical.

### Visualization
- Kernel density maps (matplotlib + cartopy)
- Elevation histograms by suffix type
- Ripley's K function plots with simulation envelopes
- Regional choropleth maps

## Script and Samples

### Analysis Code
All analysis code will be in `research/notebooks/01_heim_distribution.py`
and reproducible via:
```bash
uv run python research/notebooks/01_heim_distribution.py
```

### Data Availability
- Input data: `databank/places/NO/` (JSONL records)
- Derived data: `research/results/heim_*.csv`
- Figures: `research/figures/heim_*.pdf`

## Other

### Existing Data
This study uses existing publicly available geographic data (GeoNames,
Kartverket SSR). No new data collection is required.

### Timeline
- Data extraction and filtering: Week 1
- Statistical analysis: Week 2–3
- Manuscript preparation: Week 4–6
- Submission target: Namn och bygd or NORNA-rapporter

### References
- Rygh, O. (1898). *Norske Gaardnavne*. Kristiania.
- Sandnes, J. & Stemshaug, O. (1976). *Norsk stadnamnleksikon*. Oslo.
- Særheim, I. (2007). *Namn og nemne* 24, 7–28.
- Gammeltoft, P. (2001). *The Place-Name Element bólstaðr*. Copenhagen.
