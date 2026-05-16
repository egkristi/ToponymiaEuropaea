"""Publication-quality figure generation for Toponymia Europaea research.

Provides consistent styling, export settings, and helper functions
for generating figures suitable for academic journals.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matplotlib.figure import Figure

try:
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.use("Agg")
except ImportError as e:
    raise ImportError(
        "Figure generation requires matplotlib. "
        "Install with: pip install toponymia-europaea[research]"
    ) from e


# Publication defaults
STYLE: dict[str, Any] = {
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "lines.linewidth": 1.5,
    "axes.grid": False,
}

# Journal column widths (inches)
COLUMN_WIDTH = 3.5  # single column
DOUBLE_COLUMN = 7.0  # full width
PAGE_HEIGHT = 9.0

# Colour palette (colourblind-safe, based on Wong 2011)
PALETTE = {
    "heim": "#0072B2",
    "stad": "#E69F00",
    "setr": "#009E73",
    "vik": "#CC79A7",
    "control": "#999999",
    "highlight": "#D55E00",
}


def apply_style() -> None:
    """Apply publication style to all subsequent matplotlib figures."""
    plt.rcParams.update(STYLE)


def new_figure(
    width: float = COLUMN_WIDTH,
    height: float | None = None,
    *,
    aspect: float = 0.75,
) -> tuple[Figure, Any]:
    """Create a new figure with publication dimensions.

    Args:
        width: Figure width in inches.
        height: Figure height in inches (computed from aspect if None).
        aspect: Height/width ratio (default 0.75 = 3:4).

    Returns:
        (fig, ax) tuple.
    """
    if height is None:
        height = width * aspect
    apply_style()
    fig, ax = plt.subplots(figsize=(width, height))
    return fig, ax


def save_figure(
    fig: Figure,
    name: str,
    *,
    output_dir: Path | None = None,
    formats: tuple[str, ...] = ("pdf", "png"),
) -> list[Path]:
    """Save figure in multiple formats.

    Args:
        fig: Matplotlib figure to save.
        name: Base filename (without extension).
        output_dir: Directory to save to (default: research/figures/).
        formats: File formats to export.

    Returns:
        List of saved file paths.
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent.parent / "research" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for fmt in formats:
        path = output_dir / f"{name}.{fmt}"
        fig.savefig(path, format=fmt)
        saved.append(path)

    plt.close(fig)
    return saved
