"""Smoke tests — CLI surface loads and version reports correctly."""

from typer.testing import CliRunner

from forgestack.cli import app
from forgestack.commands.version import cli as version_cli


def test_app_has_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "forgestack" in result.stdout.lower()


def test_version_prints_package_version(capsys) -> None:
    version_cli()
    out = capsys.readouterr().out
    assert "forgestack" in out
    assert "0.1.0" in out


def test_phases_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["phases", "--help"])
    assert result.exit_code == 0
    assert "scaffold" in result.stdout


def test_orchestrate_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["orchestrate", "--help"])
    assert result.exit_code == 0
    assert "--child" in result.stdout
