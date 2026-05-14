"""Command-line interface for Toponymia Europaea."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="toponymia",
    help="Toponymia Europaea: Open research framework for place name analysis",
    no_args_is_help=True,
)
console = Console()

# Sub-command groups
ingest_app = typer.Typer(help="Data ingestion commands")
test_app = typer.Typer(help="Statistical testing commands")
app.add_typer(ingest_app, name="ingest")
app.add_typer(test_app, name="test")


@app.command()
def info():
    """Show project information and status."""
    from toponymia import __version__

    console.print(f"[bold]Toponymia Europaea[/bold] v{__version__}")
    console.print("An open research framework for place name analysis")
    console.print()

    # Check database connectivity
    try:
        from toponymia.config import get_settings

        settings = get_settings()
        console.print(f"Database: {settings.database_url}")
        console.print(f"Ontology version: {settings.ontology_version}")
    except Exception as e:
        console.print(f"[yellow]Configuration warning: {e}[/yellow]")


@ingest_app.command("geonames")
def ingest_geonames(
    country: str = typer.Option(..., "--country", "-c", help="ISO 3166-1 alpha-2 country code"),
    cache_dir: Path | None = typer.Option(
        None, "--cache-dir", help="Cache directory for downloads"
    ),
):
    """Ingest place names from GeoNames for a country."""
    from toponymia.connectors.geonames import GeoNamesConnector

    connector = GeoNamesConnector(cache_dir=cache_dir)
    console.print(f"[bold]Ingesting GeoNames data for {country.upper()}...[/bold]")

    count = 0
    errors = 0
    for record in connector.fetch(country=country):
        validation_errors = connector.validate(record)
        if validation_errors:
            errors += 1
            continue
        count += 1
        if count % 10000 == 0:
            console.print(f"  Processed {count:,} records...")

    console.print(f"[green]Done:[/green] {count:,} valid records, {errors:,} skipped")


@ingest_app.command("wikidata")
def ingest_wikidata(
    country: str | None = typer.Option(None, "--country", "-c", help="Country code"),
    bbox: str | None = typer.Option(
        None, "--bbox", "-b", help="Bounding box: min_lon,min_lat,max_lon,max_lat"
    ),
):
    """Ingest place names from Wikidata."""
    from toponymia.connectors.base import BoundingBox
    from toponymia.connectors.wikidata import WikidataConnector

    parsed_bbox = None
    if bbox:
        parts = [float(x) for x in bbox.split(",")]
        parsed_bbox = BoundingBox(*parts)

    connector = WikidataConnector()
    console.print("[bold]Ingesting Wikidata place names...[/bold]")

    count = 0
    for _record in connector.fetch(bbox=parsed_bbox, country=country):
        count += 1
        if count % 1000 == 0:
            console.print(f"  Processed {count:,} records...")

    console.print(f"[green]Done:[/green] {count:,} records")


@app.command()
def segment(
    region: str = typer.Option(..., "--region", "-r", help="Region/country code to segment"),
    top_k: int = typer.Option(3, "--top-k", "-k", help="Number of hypotheses per name"),
):
    """Run morphological segmentation on ingested names."""
    from toponymia.languages.old_norse import OldNorseModule
    from toponymia.pipelines.segment import SegmentationPipeline

    pipeline = SegmentationPipeline()
    pipeline.register_module(OldNorseModule())

    console.print(f"[bold]Segmentation pipeline for region {region}[/bold]")
    console.print(f"Registered modules: {len(pipeline._modules)}")
    console.print("[yellow]Note: Full implementation requires database connection[/yellow]")


@test_app.command("correspondence")
def test_correspondence(
    element: str = typer.Option(..., "--element", "-e", help="Name element to test (e.g., 'berg')"),
    signal: str = typer.Option(
        ..., "--signal", "-s", help="Signal to test against (e.g., 'elevation')"
    ),
    region: str = typer.Option(..., "--region", "-r", help="Region to test in"),
    n_permutations: int = typer.Option(
        10000, "--permutations", "-n", help="Number of permutations"
    ),
):
    """Run element-signal correspondence test."""
    console.print(f"[bold]Correspondence test: -{element} vs. {signal} in {region}[/bold]")
    console.print(f"Permutations: {n_permutations:,}")
    console.print("[yellow]Note: Full implementation requires database with ingested data[/yellow]")


@test_app.command("validate")
def test_validate(
    test_name: str = typer.Option("correspondence", "--test", "-t", help="Test to validate"),
    n_trials: int = typer.Option(100, "--trials", "-n", help="Number of synthetic trials"),
):
    """Validate a statistical test on synthetic data."""
    from toponymia.statistics.correspondence import ElementSignalCorrespondenceTest
    from toponymia.statistics.spatial import SpatialClusteringTest

    tests = {
        "correspondence": ElementSignalCorrespondenceTest(),
        "spatial_clustering": SpatialClusteringTest(),
    }

    if test_name not in tests:
        console.print(f"[red]Unknown test: {test_name}[/red]")
        console.print(f"Available: {', '.join(tests.keys())}")
        raise typer.Exit(1)

    test = tests[test_name]
    console.print(f"[bold]Validating {test_name} on synthetic data ({n_trials} trials)...[/bold]")

    result = test.validate_synthetic(n_trials=n_trials)

    table = Table(title=f"Synthetic Validation: {test_name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green" if result.passed else "red")
    table.add_row("Statistical Power", f"{result.power:.3f}")
    table.add_row("False Positive Rate", f"{result.false_positive_rate:.3f}")
    table.add_row("Passed", "✓" if result.passed else "✗")
    table.add_row("Details", result.details)
    console.print(table)


@app.command()
def results(
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, csv"
    ),
):
    """View analysis results."""
    console.print("[yellow]No results yet. Run tests first.[/yellow]")
    console.print(
        "Example: toponymia test correspondence --element berg --signal elevation --region NO"
    )


if __name__ == "__main__":
    app()
