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
data_app = typer.Typer(help="Data onboarding lifecycle commands")
quality_app = typer.Typer(help="Data quality metrics and reporting")
app.add_typer(ingest_app, name="ingest")
app.add_typer(test_app, name="test")
app.add_typer(data_app, name="data")
app.add_typer(quality_app, name="quality")


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


@data_app.command("promote")
def data_promote(
    record_id: str = typer.Argument(..., help="UUID of the record to promote"),
    actor: str = typer.Option(..., "--actor", "-a", help="Who is performing the promotion"),
    has_source: bool = typer.Option(False, "--has-source", help="Record has source_id"),
    has_normalized_form: bool = typer.Option(
        False, "--has-normalized-form", help="Record has normalized_form"
    ),
    has_language: bool = typer.Option(False, "--has-language", help="Record has language_code"),
    has_components: bool = typer.Option(
        False, "--has-components", help="Record has parsed components"
    ),
    reviewer: str | None = typer.Option(None, "--reviewer", help="Reviewer identity"),
    ingester: str | None = typer.Option(None, "--ingester", help="Original ingester"),
    current_status: str = typer.Option(..., "--status", "-s", help="Current status of the record"),
):
    """Promote a record to the next onboarding stage."""
    from toponymia.core import RecordStatus
    from toponymia.core.onboarding import GateError, InvalidTransitionError, promote

    try:
        status = RecordStatus(current_status)
    except ValueError:
        console.print(f"[red]Invalid status: {current_status}[/red]")
        valid = ", ".join(s.value for s in RecordStatus)
        console.print(f"Valid statuses: {valid}")
        raise typer.Exit(1) from None

    try:
        new_status, transition = promote(
            status,
            actor=actor,
            record_id=record_id,
            has_source=has_source,
            has_normalized_form=has_normalized_form,
            has_language=has_language,
            has_components=has_components,
            reviewer=reviewer,
            ingester=ingester,
        )
    except GateError as e:
        console.print(f"[red]Gate check failed:[/red] {e}")
        raise typer.Exit(1) from None
    except InvalidTransitionError as e:
        console.print(f"[red]Invalid transition:[/red] {e}")
        raise typer.Exit(1) from None

    console.print(
        f"[green]Promoted[/green] {record_id}: {transition.from_status.value} → {new_status.value}"
    )
    console.print(f"  Actor: {transition.actor}")
    console.print(f"  Time: {transition.timestamp.isoformat()}")


@data_app.command("demote")
def data_demote(
    record_id: str = typer.Argument(..., help="UUID of the record to demote"),
    actor: str = typer.Option(..., "--actor", "-a", help="Who is performing the demotion"),
    reason: str = typer.Option(..., "--reason", "-r", help="Reason for demotion"),
    current_status: str = typer.Option(..., "--status", "-s", help="Current status of the record"),
):
    """Demote a record to the previous onboarding stage."""
    from toponymia.core import RecordStatus
    from toponymia.core.onboarding import InvalidTransitionError, demote

    try:
        status = RecordStatus(current_status)
    except ValueError:
        console.print(f"[red]Invalid status: {current_status}[/red]")
        raise typer.Exit(1) from None

    try:
        new_status, transition = demote(
            status,
            actor=actor,
            record_id=record_id,
            reason=reason,
        )
    except InvalidTransitionError as e:
        console.print(f"[red]Invalid transition:[/red] {e}")
        raise typer.Exit(1) from None

    console.print(
        f"[yellow]Demoted[/yellow] {record_id}: {transition.from_status.value} → {new_status.value}"
    )
    console.print(f"  Actor: {transition.actor}")
    console.print(f"  Reason: {transition.reason}")
    console.print(f"  Time: {transition.timestamp.isoformat()}")


@data_app.command("retract")
def data_retract(
    record_id: str = typer.Argument(..., help="UUID of the record to retract"),
    actor: str = typer.Option(..., "--actor", "-a", help="Who is performing the retraction"),
    reason: str = typer.Option(..., "--reason", "-r", help="Reason for retraction"),
    current_status: str = typer.Option(..., "--status", "-s", help="Current status of the record"),
):
    """Retract a record (soft-delete with audit trail)."""
    from toponymia.core import RecordStatus
    from toponymia.core.onboarding import InvalidTransitionError, retract

    try:
        status = RecordStatus(current_status)
    except ValueError:
        console.print(f"[red]Invalid status: {current_status}[/red]")
        raise typer.Exit(1) from None

    try:
        new_status, transition = retract(
            status,
            actor=actor,
            record_id=record_id,
            reason=reason,
        )
    except InvalidTransitionError as e:
        console.print(f"[red]Invalid transition:[/red] {e}")
        raise typer.Exit(1) from None

    console.print(
        f"[red]Retracted[/red] {record_id}: {transition.from_status.value} → {new_status.value}"
    )
    console.print(f"  Actor: {transition.actor}")
    console.print(f"  Reason: {transition.reason}")
    console.print(f"  Time: {transition.timestamp.isoformat()}")


# === Quality metrics commands ===


@quality_app.command("summary")
def quality_summary():
    """Show overall data quality summary and metrics."""
    from toponymia.pipelines.validate import ValidationConfig

    config = ValidationConfig()

    table = Table(title="Data Quality Configuration")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Min latitude", str(config.min_lat))
    table.add_row("Max latitude", str(config.max_lat))
    table.add_row("Min longitude", str(config.min_lon))
    table.add_row("Max longitude", str(config.max_lon))
    table.add_row("Max name length", str(config.max_name_length))
    table.add_row("Require source_id", str(config.require_source_id))
    console.print(table)

    # Framework statistics
    stats_table = Table(title="Framework Statistics")
    stats_table.add_column("Component", style="cyan")
    stats_table.add_column("Count", style="green")

    # Count language modules
    from toponymia.languages import finnish, northern_sami, old_norse, proto_germanic

    modules = [old_norse.OldNorseModule, proto_germanic.ProtoGermanicModule]
    modules += [northern_sami.NorthernSamiModule, finnish.FinnishModule]
    stats_table.add_row("Language modules", str(len(modules)))

    # Count statistical tests
    from toponymia.statistics import (
        astronomical,
        correspondence,
        migration,
        religious,
        spatial,
        temporal,
    )

    tests = [
        correspondence.ElementSignalCorrespondenceTest,
        spatial.SpatialClusteringTest,
        astronomical.AstronomicalAlignmentTest,
        religious.ReligiousStratigraphyTest,
        temporal.TemporalLayerConsistencyTest,
        migration.MigrationOverfrequencyTest,
    ]
    stats_table.add_row("Statistical tests", str(len(tests)))

    # Count connectors
    from toponymia.connectors import geonames, kartverket, osm, wikidata

    connectors = [
        geonames.GeoNamesConnector,
        wikidata.WikidataConnector,
        osm.OSMConnector,
        kartverket.KartverketConnector,
    ]
    stats_table.add_row("Data connectors", str(len(connectors)))

    # Onboarding stages
    from toponymia.core import RecordStatus

    stats_table.add_row("Onboarding stages", str(len(RecordStatus)))

    console.print(stats_table)


@quality_app.command("validate-file")
def quality_validate_file(
    filepath: Path = typer.Argument(..., help="Path to data file (JSON lines)"),
    strict: bool = typer.Option(False, "--strict", help="Fail on first error"),
):
    """Validate a data file against quality rules."""
    import json

    from toponymia.connectors.base import ConnectorResult
    from toponymia.pipelines.validate import validate_record

    if not filepath.exists():
        console.print(f"[red]File not found: {filepath}[/red]")
        raise typer.Exit(1)

    total = 0
    valid = 0
    errors: dict[str, int] = {}

    with filepath.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                errors["json_parse_error"] = errors.get("json_parse_error", 0) + 1
                if strict:
                    console.print(f"[red]JSON error line {total}: {e}[/red]")
                    raise typer.Exit(1) from None
                continue

            try:
                record = ConnectorResult(
                    latitude=float(data.get("latitude", 0)),
                    longitude=float(data.get("longitude", 0)),
                    name_form=data.get("name_form", ""),
                    language_code=data.get("language_code", "und"),
                    source_id=data.get("source_id", ""),
                )
            except (TypeError, ValueError) as e:
                errors["record_parse_error"] = errors.get("record_parse_error", 0) + 1
                if strict:
                    console.print(f"[red]Record parse error line {total}: {e}[/red]")
                    raise typer.Exit(1) from None
                continue

            validation_errors = validate_record(record)
            if not validation_errors:
                valid += 1
            else:
                for err in validation_errors:
                    errors[err.field] = errors.get(err.field, 0) + 1
                    if strict:
                        console.print(f"[red]Validation error: {err.field} - {err.message}[/red]")
                        raise typer.Exit(1) from None

    # Summary
    table = Table(title=f"Validation Results: {filepath.name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total records", str(total))
    table.add_row("Valid records", str(valid))
    table.add_row("Invalid records", str(total - valid))
    table.add_row("Pass rate", f"{valid / total * 100:.1f}%" if total > 0 else "N/A")
    console.print(table)

    if errors:
        err_table = Table(title="Error Distribution")
        err_table.add_column("Rule", style="cyan")
        err_table.add_column("Count", style="red")
        for rule, count in sorted(errors.items(), key=lambda x: -x[1]):
            err_table.add_row(rule, str(count))
        console.print(err_table)


@quality_app.command("tests")
def quality_tests():
    """List all available statistical tests with validation status."""
    from toponymia.statistics.astronomical import AstronomicalAlignmentTest
    from toponymia.statistics.correspondence import ElementSignalCorrespondenceTest
    from toponymia.statistics.migration import MigrationOverfrequencyTest
    from toponymia.statistics.religious import ReligiousStratigraphyTest
    from toponymia.statistics.spatial import SpatialClusteringTest
    from toponymia.statistics.temporal import TemporalLayerConsistencyTest

    tests = [
        ElementSignalCorrespondenceTest(),
        SpatialClusteringTest(),
        AstronomicalAlignmentTest(),
        ReligiousStratigraphyTest(),
        TemporalLayerConsistencyTest(),
        MigrationOverfrequencyTest(),
    ]

    table = Table(title="Available Statistical Tests")
    table.add_column("ID", style="cyan")
    table.add_column("Family", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Null Hypothesis", style="dim")

    for test in tests:
        table.add_row(
            test.test_id,
            test.test_family.value,
            test.description[:60] + "..." if len(test.description) > 60 else test.description,
            test.null_hypothesis[:50] + "..."
            if len(test.null_hypothesis) > 50
            else test.null_hypothesis,
        )

    console.print(table)
    console.print(f"\n[dim]{len(tests)} tests registered[/dim]")


if __name__ == "__main__":
    app()
