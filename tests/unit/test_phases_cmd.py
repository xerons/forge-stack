from typer.testing import CliRunner

from forgestack.cli import app
from forgestack.commands.phases_cmd import _agent_command

runner = CliRunner()


def test_phases_group_registered():
    result = runner.invoke(app, ["phases", "--help"])
    assert result.exit_code == 0
    assert "scaffold" in result.output
    assert "design" in result.output
    assert "apply" in result.output


def test_agent_command_map():
    assert _agent_command("codex") == ["codex", "exec"]
    assert _agent_command("unknown-agent") is None


def test_scaffold_writes_project_config(tmp_path, monkeypatch):
    import tomllib

    from forgestack.commands.phases_cmd import _write_scope

    proj = tmp_path / "proj"
    proj.mkdir()
    cfg_path = proj / ".forgestack.toml"

    _write_scope(
        cfg_path,
        phases=[
            {"key": "planning", "agent": "codex"},
            {"key": "running", "agent": "opencode"},
            {"key": "review", "agent": "codex"},
        ],
        research=False,
        cyclic=False,
    )
    raw = tomllib.loads(cfg_path.read_text())
    assert [p["key"] for p in raw["workflow"]["phases"]] == ["planning", "running", "review"]
    assert raw["workflow"]["research"] is False
