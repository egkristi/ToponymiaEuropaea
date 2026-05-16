"""Reproducible analysis: -heim distribution in Norway.

This script implements the full analysis pipeline for the preregistered study
on the spatial distribution of -heim place names in Norway.

Usage:
    uv run python research/notebooks/01_heim_distribution.py

Outputs:
    research/results/heim_*.csv
    research/figures/heim_*.pdf
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import numpy as np

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# --- Configuration ---
DATABANK_PATH = PROJECT_ROOT / "databank" / "places" / "NO"
RESULTS_DIR = PROJECT_ROOT / "research" / "results"
FIGURES_DIR = PROJECT_ROOT / "research" / "figures"

# Suffix patterns for extraction
HEIM_PATTERNS = ("heim", "hem", "um")  # -um from reduced -heim in Eastern NO
STAD_PATTERNS = ("stad", "stað")
SETR_PATTERNS = ("setr", "seter", "sæter", "set", "sætr")
VIK_PATTERNS = ("vik", "vík")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_no_records() -> list[dict]:
    """Load all Norwegian databank records."""
    records = []
    if not DATABANK_PATH.is_dir():
        logger.error(f"Databank path not found: {DATABANK_PATH}")
        return records

    for jsonl_file in sorted(DATABANK_PATH.glob("*.jsonl")):
        with jsonl_file.open() as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    logger.info(f"Loaded {len(records):,} Norwegian records")
    return records


def extract_suffix_group(records: list[dict], patterns: tuple[str, ...]) -> list[dict]:
    """Extract records whose name_form ends with one of the given patterns."""
    matches = []
    for rec in records:
        name = rec.get("name_form", "").lower()
        if any(name.endswith(p) for p in patterns):
            matches.append(rec)
    return matches


def compute_descriptive_stats(group: list[dict], label: str) -> dict[str, float | int | str]:
    """Compute descriptive statistics for a group of records."""
    elevations = [
        r["elevation"] for r in group if r.get("elevation") is not None and r["elevation"] > -9000
    ]
    lats = [r["latitude"] for r in group if r.get("latitude")]
    lons = [r["longitude"] for r in group if r.get("longitude")]

    elev_arr = np.array(elevations) if elevations else np.array([0.0])
    lat_arr = np.array(lats) if lats else np.array([0.0])

    return {
        "group": label,
        "n": len(group),
        "n_with_elevation": len(elevations),
        "elev_mean": float(np.mean(elev_arr)),
        "elev_median": float(np.median(elev_arr)),
        "elev_std": float(np.std(elev_arr)),
        "elev_min": float(np.min(elev_arr)),
        "elev_max": float(np.max(elev_arr)),
        "lat_mean": float(np.mean(lat_arr)),
        "lat_min": float(np.min(lat_arr)),
        "lat_max": float(np.max(lat_arr)),
        "lon_mean": float(np.mean(np.array(lons) if lons else np.array([0.0]))),
    }


def run_analysis() -> None:
    """Run the full -heim distribution analysis."""
    logger.info("=" * 60)
    logger.info("-heim Distribution in Norway: Computational Reanalysis")
    logger.info("=" * 60)

    # 1. Load data
    records = load_no_records()
    if not records:
        logger.error("No records found. Ensure databank is populated.")
        return

    # 2. Extract suffix groups
    heim = extract_suffix_group(records, HEIM_PATTERNS)
    stad = extract_suffix_group(records, STAD_PATTERNS)
    setr = extract_suffix_group(records, SETR_PATTERNS)
    vik = extract_suffix_group(records, VIK_PATTERNS)

    logger.info("\nCorpus extraction:")
    logger.info(f"  -heim names: {len(heim):,}")
    logger.info(f"  -stad names: {len(stad):,}")
    logger.info(f"  -setr names: {len(setr):,}")
    logger.info(f"  -vik names:  {len(vik):,}")
    logger.info(f"  Total NO:    {len(records):,}")

    # 3. Descriptive statistics
    stats = []
    for group, label in [
        (heim, "heim"),
        (stad, "stad"),
        (setr, "setr"),
        (vik, "vik"),
    ]:
        if group:
            stats.append(compute_descriptive_stats(group, label))

    # Save descriptive stats
    stats_path = RESULTS_DIR / "heim_descriptive_stats.csv"
    if stats:
        header = list(stats[0].keys())
        with stats_path.open("w") as f:
            f.write(",".join(header) + "\n")
            for row in stats:
                f.write(",".join(str(row[k]) for k in header) + "\n")
        logger.info(f"\nDescriptive stats saved: {stats_path}")

    # 4. Print summary
    logger.info("\n--- Descriptive Statistics ---")
    for s in stats:
        logger.info(
            f"  {s['group']:>5}: n={s['n']:>5,}  "
            f"elev={s['elev_mean']:>6.0f}m (median {s['elev_median']:.0f}m, "
            f"SD {s['elev_std']:.0f}m)"
        )

    # 5. Hypothesis tests (requires scipy)
    try:
        from scipy import stats as sp_stats

        logger.info("\n--- Hypothesis Tests ---")

        # H1: Elevation comparison (heim vs random control)
        heim_elev = np.array(
            [
                r["elevation"]
                for r in heim
                if r.get("elevation") is not None and r["elevation"] > -9000
            ]
        )
        all_elev = np.array(
            [
                r["elevation"]
                for r in records
                if r.get("elevation") is not None and r["elevation"] > -9000
            ]
        )

        if len(heim_elev) > 5 and len(all_elev) > 5:
            t_stat, p_val = sp_stats.ttest_ind(heim_elev, all_elev, equal_var=False)
            cohens_d = (np.mean(heim_elev) - np.mean(all_elev)) / np.sqrt(
                (np.std(heim_elev) ** 2 + np.std(all_elev) ** 2) / 2
            )
            logger.info(f"  H1 (elevation): t={t_stat:.3f}, p={p_val:.2e}, d={cohens_d:.3f}")

            # Mann-Whitney U
            u_stat, u_p = sp_stats.mannwhitneyu(heim_elev, all_elev, alternative="less")
            logger.info(f"      Mann-Whitney U: U={u_stat:.0f}, p={u_p:.2e}")

        # H4: Terrain comparison (heim vs setr elevation as proxy for slope)
        setr_elev = np.array(
            [
                r["elevation"]
                for r in setr
                if r.get("elevation") is not None and r["elevation"] > -9000
            ]
        )
        if len(heim_elev) > 5 and len(setr_elev) > 5:
            t_stat, p_val = sp_stats.ttest_ind(heim_elev, setr_elev, equal_var=False)
            logger.info(f"  H4 (heim vs setr): t={t_stat:.3f}, p={p_val:.2e}")

        # Save test results
        test_results = RESULTS_DIR / "heim_test_results.csv"
        with test_results.open("w") as f:
            f.write("hypothesis,test,statistic,p_value,effect_size\n")
            if len(heim_elev) > 5 and len(all_elev) > 5:
                f.write(f"H1,welch_t,{t_stat:.6f},{p_val:.2e},{cohens_d:.4f}\n")
                f.write(f"H1,mann_whitney_u,{u_stat:.0f},{u_p:.2e},\n")
            if len(heim_elev) > 5 and len(setr_elev) > 5:
                f.write(f"H4,welch_t,{t_stat:.6f},{p_val:.2e},\n")
        logger.info(f"  Test results saved: {test_results}")

    except ImportError:
        logger.warning("scipy not installed — skipping hypothesis tests")

    # 6. Generate figures (requires matplotlib)
    try:
        from toponymia.research import PALETTE, new_figure, save_figure

        # Figure 2: Elevation histogram
        fig, ax = new_figure()
        for group_data, label, color in [
            (heim, "heim", PALETTE["heim"]),
            (setr, "setr", PALETTE["setr"]),
            (stad, "stad", PALETTE["stad"]),
        ]:
            elevs = [
                r["elevation"]
                for r in group_data
                if r.get("elevation") is not None and r["elevation"] > -9000
            ]
            if elevs:
                ax.hist(
                    elevs,
                    bins=50,
                    alpha=0.6,
                    label=f"-{label} (n={len(elevs)})",
                    color=color,
                    density=True,
                )
        ax.set_xlabel("Elevation (m.a.s.l.)")
        ax.set_ylabel("Density")
        ax.set_title("Elevation Distribution by Place-Name Suffix")
        ax.legend()
        paths = save_figure(fig, "heim_elevation_hist", output_dir=FIGURES_DIR)
        logger.info(f"\n  Figure saved: {paths[0]}")

    except ImportError:
        logger.warning("matplotlib not installed — skipping figures")

    logger.info("\n" + "=" * 60)
    logger.info("Analysis complete.")


if __name__ == "__main__":
    run_analysis()
