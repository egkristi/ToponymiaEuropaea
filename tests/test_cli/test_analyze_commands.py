"""Tests for the analyze CLI commands."""

from typer.testing import CliRunner

from toponymia.cli import app

runner = CliRunner()


class TestAnalyzeDiscover:
    def test_discover_no_country(self):
        result = runner.invoke(app, ["analyze", "discover"])
        assert result.exit_code == 0
        assert "Discovering elements" in result.output

    def test_discover_with_country(self):
        result = runner.invoke(app, ["analyze", "discover", "--country", "NO"])
        assert result.exit_code == 0
        assert "Detected Toponymic Elements" in result.output


class TestAnalyzeElement:
    def test_element_nes(self):
        result = runner.invoke(app, ["analyze", "element", "nes", "--country", "NO"])
        assert result.exit_code == 0
        assert "Test Result" in result.output
        assert "nes" in result.output

    def test_element_nonexistent(self):
        result = runner.invoke(app, ["analyze", "element", "zzzzz", "--country", "NO"])
        assert result.exit_code == 1
        assert "No places" in result.output

    def test_element_with_test_type(self):
        result = runner.invoke(
            app, ["analyze", "element", "ø", "--country", "NO", "--test", "spatial"]
        )
        assert result.exit_code == 0
        assert "spatial" in result.output
