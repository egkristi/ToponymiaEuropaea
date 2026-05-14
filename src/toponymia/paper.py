"""Generate a research paper skeleton from databank statistics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_stats(databank_path: Path) -> dict[str, Any]:
    """Compute basic statistics from the databank."""
    places_dir = databank_path / "places"
    by_country: dict[str, int] = {}

    if places_dir.is_dir():
        for country_dir in sorted(places_dir.iterdir()):
            if not country_dir.is_dir():
                continue
            count = 0
            for jsonl_file in country_dir.glob("*.jsonl"):
                with jsonl_file.open() as f:
                    count += sum(1 for line in f if line.strip())
            by_country[country_dir.name] = count

    sources: list[dict[str, Any]] = []
    sources_file = databank_path / "sources.jsonl"
    if sources_file.exists():
        with sources_file.open() as f:
            for line in f:
                if line.strip():
                    sources.append(json.loads(line))

    return {
        "total": sum(by_country.values()),
        "by_country": by_country,
        "sources": sources,
    }


def generate_paper(
    *,
    title: str = "Place-Name Analysis with Toponymia Europaea",
    author: str = "Author Name",
    abstract: str = "This paper presents...",
    databank_path: Path | None = None,
    output_path: Path | None = None,
) -> str:
    """Generate a LaTeX paper from the template with databank statistics filled in."""
    if databank_path is None:
        databank_path = Path(__file__).resolve().parent.parent.parent / "databank"

    template_path = Path(__file__).resolve().parent.parent.parent / "templates" / "paper.tex"
    template = template_path.read_text()

    stats = _load_stats(databank_path)

    # Build country table
    country_rows = []
    for cc, count in sorted(stats["by_country"].items()):
        sources_count = sum(1 for s in stats["sources"] if s.get("coverage") in (cc, "global"))
        country_rows.append(f"{cc} & {count:,} & {sources_count} \\\\")
    total = stats["total"]
    n_sources = len(stats["sources"])
    country_rows.append(f"\\textbf{{Total}} & \\textbf{{{total:,}}} & \\textbf{{{n_sources}}} \\\\")
    country_table = "\n".join(country_rows)

    # Build sources description
    sources_desc_parts = []
    for src in stats["sources"]:
        name = src.get("name", src.get("dataset_id", "Unknown"))
        license_info = src.get("license", "Unknown")
        coverage = src.get("coverage", "Unknown")
        sources_desc_parts.append(
            f"\\textbf{{{name}}} (license: {license_info}, coverage: {coverage})"
        )
    sources_description = "; ".join(sources_desc_parts) + "."

    # Fill template
    result = template
    result = result.replace("<TITLE>", title)
    result = result.replace("<AUTHOR>", author)
    result = result.replace("<ABSTRACT>", abstract)
    result = result.replace("<COUNTRY_TABLE>", country_table)
    result = result.replace("<SOURCES_DESCRIPTION>", sources_description)
    result = result.replace("<RESULTS>", "% TODO: Add analysis results here")
    result = result.replace("<DISCUSSION>", "% TODO: Add discussion here")
    result = result.replace("<CONCLUSION>", "% TODO: Add conclusion here")
    result = result.replace("<COMMAND>", "discover --country NO")

    if output_path:
        output_path.write_text(result)

    return result
