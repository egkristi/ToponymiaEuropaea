# Results Matrix

Maps research questions → statistical tests → expected outputs.

## Study 1: *-heim* Distribution in Norway

| ID | Research Question | Hypothesis | Statistical Test | Input Data | Output | Significance |
|----|------------------|-----------|-----------------|------------|--------|--------------|
| RQ1 | Are *-heim* names at lower elevation? | H1 | Welch's t-test, Mann-Whitney U | heim elevations vs. control | p-value, Cohen's d, median comparison | α = 0.01 |
| RQ2 | Are *-heim* names near the coast? | H2 | Welch's t-test, KDE | heim distance-to-coast vs. control | p-value, KDE plot | α = 0.01 |
| RQ3 | Does density vary by region? | H3 | Chi-squared, standardised residuals | counts per fylke, expected under uniform | χ², Cramér's V, residual map | α = 0.01 |
| RQ4 | Are *-heim* on flatter terrain? | H4 | Logistic regression | slope at heim vs. setr locations | OR, 95% CI, AUC | α = 0.01 |
| RQ5 | Do *-heim* cluster spatially? | H5 | Ripley's K, MC envelope | point pattern of heim locations | K(r) plot, significant scales | 95% envelope |

## Descriptive Statistics (always reported)

| Metric | Description |
|--------|-------------|
| N | Total *-heim* names in corpus |
| Geographic extent | Bounding box, centroid |
| Elevation | Mean, median, SD, range |
| Regional counts | Names per fylke |
| Source breakdown | Kartverket vs. GeoNames vs. Wikidata |

## Figure Plan

| Fig # | Type | Content | File |
|-------|------|---------|------|
| 1 | Map | KDE of *-heim* density over Norway | `figures/heim_kde_map.pdf` |
| 2 | Histogram | Elevation distribution: *-heim* vs *-setr* vs control | `figures/heim_elevation_hist.pdf` |
| 3 | Box plot | Distance-to-coast by suffix type | `figures/heim_coast_distance.pdf` |
| 4 | Choropleth | Standardised residuals by fylke | `figures/heim_regional_residuals.pdf` |
| 5 | Line plot | Ripley's K with MC envelope | `figures/heim_ripleys_k.pdf` |
| 6 | Scatter | Elevation vs. latitude for *-heim* names | `figures/heim_elev_lat_scatter.pdf` |

## Table Plan

| Table # | Content | File |
|---------|---------|------|
| 1 | Corpus summary (N by source, region) | `results/heim_corpus_summary.csv` |
| 2 | Descriptive statistics by suffix type | `results/heim_descriptive_stats.csv` |
| 3 | Hypothesis test results | `results/heim_test_results.csv` |
| 4 | Logistic regression coefficients | `results/heim_logistic_model.csv` |
