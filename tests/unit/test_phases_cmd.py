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


def test_phase_design_timeout_is_reported_without_writing(tmp_path, monkeypatch, capsys):
    import subprocess

    from forgestack import paths
    from forgestack.commands.phases_cmd import design
    from forgestack.config import Config
    from forgestack.workflow.model import PhaseModel

    monkeypatch.setattr(paths, "git_root", lambda *a, **k: tmp_path)
    monkeypatch.setattr(
        "forgestack.config.load_config",
        lambda _: Config.from_dict({"workflow": {"phases": [{"key": p.key, "agent": "codex"} for p in PhaseModel.default().phases]}}),
    )
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: (_ for _ in ()).throw(subprocess.TimeoutExpired("codex", 120)),
    )

    design(scope="project")
    assert "Agent run failed" in capsys.readouterr().out
    assert not (tmp_path / ".forgestack.toml").exists()


def test_phase_design_nonzero_is_rejected(tmp_path, monkeypatch, capsys):
    from types import SimpleNamespace

    from forgestack import paths
    from forgestack.commands.phases_cmd import design
    from forgestack.config import Config
    from forgestack.workflow.model import PhaseModel

    monkeypatch.setattr(paths, "git_root", lambda *a, **k: tmp_path)
    monkeypatch.setattr(
        "forgestack.config.load_config",
        lambda _: Config.from_dict({"workflow": {"phases": [{"key": p.key, "agent": "codex"} for p in PhaseModel.default().phases]}}),
    )
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: SimpleNamespace(returncode=2, stdout="", stderr="agent failed"),
    )

    design(scope="project")
    output = capsys.readouterr().out
    assert "agent failed" in output
    assert not (tmp_path / ".forgestack.toml").exists()


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


def test_apply_writes_through_manifest(tmp_path, monkeypatch):
    from forgestack import paths
    from forgestack.commands.phases_cmd import apply
    from forgestack.managed import MANIFEST_NAME

    proj = tmp_path / "proj"
    proj.mkdir()
    monkeypatch.setattr(paths, "project_config_path", lambda *a, **k: proj / ".forgestack.toml")
    monkeypatch.setattr(paths, "git_root", lambda *a, **k: proj)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    apply(scope="project")

    plugin = proj / ".agtx" / "plugins" / "forgestack" / "plugin.toml"
    assert plugin.exists()
    manifest = proj / MANIFEST_NAME
    assert manifest.exists()
    import json
    data = json.loads(manifest.read_text())
    assert "files" in data
    rel = plugin.relative_to(proj).as_posix()
    assert rel in data["files"]
    assert data["files"][rel]["source"] == "agtx/plugins/forgestack/plugin.toml"


def test_apply_skipped_when_user_modified(tmp_path, monkeypatch):
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
    plugin.write_text("# user edit\n" + plugin.read_text())

    apply(scope="project")
    content = plugin.read_text()
    assert content.startswith("# user edit\n")
