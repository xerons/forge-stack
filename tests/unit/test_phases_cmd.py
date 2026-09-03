import pytest
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
    assert _agent_command("gemini") == ["gemini", "-p"]
    assert _agent_command("agy") == ["agy", "run"]
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


def test_phase_designer_skill_asset():
    from pathlib import Path

    skill = Path("skills/forgestack/phase-designer/SKILL.md")
    assert skill.exists()
    text = skill.read_text()
    assert text.startswith("---\nname: phase-designer")
    assert "coverage matrix" in text


def test_apply_skips_when_model_invalid(tmp_path, monkeypatch):
    from forgestack import paths
    from forgestack.commands.phases_cmd import apply

    proj = tmp_path / "proj"
    proj.mkdir()
    cfg_path = proj / ".forgestack.toml"
    cfg_path.write_text(
        '[workflow]\nresearch = true\ncyclic = false\n\n[[workflow.phases]]\n'
        'key = "populate"\n'
    )
    monkeypatch.setattr(paths, "project_config_path", lambda *a, **k: cfg_path)
    monkeypatch.setattr(paths, "git_root", lambda *a, **k: proj)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "n")
    with pytest.raises(SystemExit):
        apply(scope="project")
    plugin = proj / ".agtx" / "plugins" / "forgestack" / "plugin.toml"
    assert not plugin.exists()


def test_apply_default_model_with_no_config(tmp_path, monkeypatch):
    from forgestack import paths
    from forgestack.commands.phases_cmd import apply

    proj = tmp_path / "proj"
    proj.mkdir()
    monkeypatch.setattr(paths, "project_config_path", lambda *a, **k: proj / ".forgestack.toml")
    monkeypatch.setattr(paths, "git_root", lambda *a, **k: proj)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    apply(scope="project")
    plugin = proj / ".agtx" / "plugins" / "forgestack" / "plugin.toml"
    assert plugin.exists()
    assert "cyclic = false" in plugin.read_text()
