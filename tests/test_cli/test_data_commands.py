"""Tests for the data onboarding CLI commands."""

from typer.testing import CliRunner

from toponymia.cli import app

runner = CliRunner()


class TestDataPromote:
    """Tests for 'toponymia data promote' command."""

    def test_promote_candidate_to_verified(self):
        result = runner.invoke(
            app,
            [
                "data",
                "promote",
                "test-record-001",
                "--actor",
                "tester",
                "--status",
                "candidate",
                "--has-source",
                "--has-normalized-form",
            ],
        )
        assert result.exit_code == 0
        assert "Promoted" in result.output
        assert "candidate → verified" in result.output

    def test_promote_verified_to_enriched(self):
        result = runner.invoke(
            app,
            [
                "data",
                "promote",
                "test-record-002",
                "--actor",
                "tester",
                "--status",
                "verified",
                "--has-language",
                "--has-components",
            ],
        )
        assert result.exit_code == 0
        assert "verified → enriched" in result.output

    def test_promote_enriched_to_reviewed(self):
        result = runner.invoke(
            app,
            [
                "data",
                "promote",
                "test-record-003",
                "--actor",
                "tester",
                "--status",
                "enriched",
                "--reviewer",
                "reviewer-a",
                "--ingester",
                "ingester-b",
            ],
        )
        assert result.exit_code == 0
        assert "enriched → reviewed" in result.output

    def test_promote_fails_gate_no_source(self):
        result = runner.invoke(
            app,
            [
                "data",
                "promote",
                "test-record-004",
                "--actor",
                "tester",
                "--status",
                "candidate",
            ],
        )
        assert result.exit_code == 1
        assert "Gate check failed" in result.output

    def test_promote_fails_same_reviewer_ingester(self):
        result = runner.invoke(
            app,
            [
                "data",
                "promote",
                "test-record-005",
                "--actor",
                "tester",
                "--status",
                "enriched",
                "--reviewer",
                "same-person",
                "--ingester",
                "same-person",
            ],
        )
        assert result.exit_code == 1
        assert "Gate check failed" in result.output

    def test_promote_invalid_status(self):
        result = runner.invoke(
            app,
            [
                "data",
                "promote",
                "test-record-006",
                "--actor",
                "tester",
                "--status",
                "nonexistent",
            ],
        )
        assert result.exit_code == 1
        assert "Invalid status" in result.output

    def test_promote_already_published(self):
        result = runner.invoke(
            app,
            [
                "data",
                "promote",
                "test-record-007",
                "--actor",
                "tester",
                "--status",
                "published",
            ],
        )
        assert result.exit_code == 1
        assert "Invalid transition" in result.output


class TestDataDemote:
    """Tests for 'toponymia data demote' command."""

    def test_demote_verified_to_candidate(self):
        result = runner.invoke(
            app,
            [
                "data",
                "demote",
                "test-record-010",
                "--actor",
                "tester",
                "--reason",
                "Source found unreliable",
                "--status",
                "verified",
            ],
        )
        assert result.exit_code == 0
        assert "Demoted" in result.output
        assert "verified → candidate" in result.output
        assert "Source found unreliable" in result.output

    def test_demote_cannot_demote_candidate(self):
        result = runner.invoke(
            app,
            [
                "data",
                "demote",
                "test-record-011",
                "--actor",
                "tester",
                "--reason",
                "test",
                "--status",
                "candidate",
            ],
        )
        assert result.exit_code == 1
        assert "Invalid transition" in result.output


class TestDataRetract:
    """Tests for 'toponymia data retract' command."""

    def test_retract_from_published(self):
        result = runner.invoke(
            app,
            [
                "data",
                "retract",
                "test-record-020",
                "--actor",
                "admin",
                "--reason",
                "Fabricated source discovered",
                "--status",
                "published",
            ],
        )
        assert result.exit_code == 0
        assert "Retracted" in result.output
        assert "published → retracted" in result.output
        assert "Fabricated source discovered" in result.output

    def test_retract_already_retracted(self):
        result = runner.invoke(
            app,
            [
                "data",
                "retract",
                "test-record-021",
                "--actor",
                "admin",
                "--reason",
                "test",
                "--status",
                "retracted",
            ],
        )
        assert result.exit_code == 1
        assert "Invalid transition" in result.output
